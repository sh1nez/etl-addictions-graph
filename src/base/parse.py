from functools import total_ordering
import os
from collections import defaultdict
from typing import Optional, List, Tuple, Dict, Set
from sqlglot.expressions import (
    Update,
    Insert,
    Table,
    Delete,
    Merge,
    Select,
    Join,
    Values,
    Create,
    Drop,
    Alter,
    With,
    CTE,
    Subquery,
    Expression,
)
from util.dialect import safe_parse
from base.storage import Edge
from logger_config import logger


class SqlAst:
    """Парсит SQL-код, строит AST и извлекает зависимости между таблицами/CTE.

    Attributes:
        corrections (List[str]): Корректировки и предупреждения (например, ["Error: syntax error"]).
        dependencies (defaultdict): Граф зависимостей вида {target: {Edge(source, target, node)}}.
        table_schema (Dict[str, Dict]): Схемы таблиц из CREATE-запросов (например, {"users": {"id": "INT"}}).
        recursive_ctes (Set[str]): Множество рекурсивных CTE (например, {"cte1"}).

    Example:
        >>> ast = SqlAst("SELECT * FROM users")
        >>> ast.get_dependencies()
        defaultdict(<class 'set'>, {'result_0': {Edge('users', 'result_0', ...)}})
    """

    _input_id = 0
    _output_id = 0
    _unknown_id = 0
    _join_id = 0
    _transfer_id = 0
    _cte_id = 0  # Counter for CTE nodes

    def __init__(self, sql_code: str, sep_parse: bool = False):
        """Инициализирует парсер SQL и запускает анализ кода.

        Args:
            sql_code (str): SQL-код для анализа.
            sep_parse (bool): Если True, использует отдельные счетчики для каждого экземпляра.

        Raises:
            Exception: Если возникает ошибка при парсинге SQL.
        """
        if not sql_code or not isinstance(sql_code, str):
            self.corrected_sql = ""
            self.corrections = ["Invalid input: Not a valid SQL string"]
            self.sql_code = ""
            self.parsed = None
            self.dependencies = defaultdict(set)
            return
        self.corrections = []
        self.sql_code = sql_code
        self.corrected_sql = self.sql_code
        self.dependencies = defaultdict(set)
        self.input_id = SqlAst._input_id
        self.output_id = SqlAst._output_id
        self.unknown_id = SqlAst._unknown_id
        self.cte_id = SqlAst._cte_id
        self.sep_parse = sep_parse
        self._statement_count = 0
        self.table_schema = {}  # Store table schema information

        # Track CTE definitions and references for recursion detection
        self.cte_definitions = {}  # name -> CTE node
        # CTE name -> set of referencing CTEs
        self.cte_references = defaultdict(set)
        self.recursive_ctes = set()  # Set of recursive CTE names

        try:
            self.parsed, self.dialect = safe_parse(self.corrected_sql)
            assert self.parsed is not None
            # Extract schema information first (when available)
            self._extract_schema_info()
            # First pass to identify all CTEs
            self._identify_all_ctes()
            # Then extract dependencies
            self.dependencies = self._extract_dependencies()
            # Check for recursive CTEs
            self._detect_recursive_ctes()
            logger.info("SQL parsing and dependency extraction completed.")

        except Exception as e:
            print(f"Error parsing SQL: {e}")
            self.parsed = None
            self.dependencies = defaultdict(set)
            self.corrections.append(f"Error parsing SQL: {str(e)}")

    def _extract_schema_info(self):
        """Извлекает схемы таблиц из CREATE-запросов.

        Заполняет атрибут `table_schema` данными о колонках, их типах и ограничениях.
        """

        for statement in self.parsed:
            if isinstance(statement, Create) and statement.args.get("kind") == "TABLE":
                table_name = self.get_table_name(statement.args.get("this"))
                columns = {}

                # Extract column definitions
                if "expressions" in statement.args:
                    for col_def in statement.args["expressions"]:
                        if "this" in col_def.args and "datatype" in col_def.args:
                            col_name = col_def.args["this"].args["this"]
                            data_type = col_def.args["datatype"].sql()
                            columns[col_name] = {
                                "data_type": data_type,
                                "nullable": "not" not in col_def.args
                                or not col_def.args["not"],
                                "primary_key": "primary" in col_def.args
                                and col_def.args["primary"],
                            }

                self.table_schema[table_name] = columns
                logger.debug(f"Extracted schema for table %s: %s", table_name, columns)

    def _identify_all_ctes(self):
        """Идентифицирует все CTE в SQL-коде, включая рекурсивные."""
        for statement in self.parsed:
            # Handle direct WITH statements
            if isinstance(statement, With):
                self._register_ctes_from_with(statement)

            # Handle WITH clauses in other statements
            elif "with" in statement.args and statement.args["with"]:
                self._register_ctes_from_with(statement.args["with"])

            # Check if WITH RECURSIVE is used (explicit recursion)
            is_recursive = False
            if isinstance(statement, With) and "recursive" in statement.args:
                is_recursive = statement.args["recursive"]
            elif (
                "with" in statement.args
                and statement.args["with"]
                and "recursive" in statement.args["with"].args
            ):
                is_recursive = statement.args["with"].args["recursive"]

            if is_recursive:
                # Mark all CTEs in this WITH clause as potentially recursive
                self._mark_ctes_as_recursive(statement)

                logger.debug("Marked CTEs in WITH RECURSIVE as recursive.")

    def _register_ctes_from_with(self, with_statement):
        """Регистрирует CTE из WITH-выражения.

        Args:
            with_statement (With): Узел AST, представляющий WITH-выражение.
        """
        if "expressions" not in with_statement.args:
            return

        for cte in with_statement.args["expressions"]:
            if isinstance(cte, CTE):
                cte_name = cte.args["alias"].args["this"]
                self.cte_definitions[cte_name] = cte

                # Check for references to other CTEs within this CTE
                self._find_cte_references(cte_name, cte.args["this"])

    def _find_cte_references(self, cte_name, expression):
        """Находит ссылки на другие CTE внутри CTE-выражения.

        Args:
            cte_name (str): Имя текущего CTE.
            expression (Expression): Выражение CTE для анализа.
        """
        if expression is None:
            return

        for node in expression.walk():
            if isinstance(node, Table):
                referenced_table = self.get_table_name(node)
                # If this table name matches a CTE name, it's a reference
                if referenced_table in self.cte_definitions:
                    self.cte_references[referenced_table].add(cte_name)

                    # If this is a self-reference, mark as recursive
                    if referenced_table == cte_name:
                        self.recursive_ctes.add(cte_name)

    def _mark_ctes_as_recursive(self, statement):
        """Помечает CTE как рекурсивные при явном объявлении WITH RECURSIVE.

        Args:
            statement: Узел AST WITH-выражения или родительского узла.
        """
        ctes = []
        if isinstance(statement, With):
            ctes = statement.args.get("expressions", [])
        elif "with" in statement.args:
            ctes = statement.args["with"].args.get("expressions", [])

        for cte in ctes:
            if isinstance(cte, CTE):
                cte_name = cte.args["alias"].args["this"]
                # Initially mark all CTEs in a RECURSIVE WITH as potentially recursive
                self.recursive_ctes.add(cte_name)

    def _detect_recursive_ctes(self):
        """Обнаруживает рекурсивные CTE через анализ зависимостей."""
        # Check direct recursion (self-reference)
        for cte_name, cte_node in self.cte_definitions.items():
            # Walk the CTE expression to find self-references
            if cte_node.args["this"]:
                for node in cte_node.args["this"].walk():
                    if isinstance(node, Table):
                        table_name = self.get_table_name(node)
                        if table_name == cte_name:
                            self.recursive_ctes.add(cte_name)
                            break

        # Check for indirect recursion (cycles in CTE references)
        visited = set()
        temp_visited = set()

        def dfs(node):
            if node in temp_visited:  # Found a cycle
                self.recursive_ctes.add(node)
                return True
            if node in visited:
                return False

            visited.add(node)
            temp_visited.add(node)

            # Check all references from this CTE
            for neighbor in self.cte_references.get(node, set()):
                if dfs(neighbor):
                    self.recursive_ctes.add(node)  # Part of a recursive cycle
                    return True

            temp_visited.remove(node)
            return False

        # Run DFS from each CTE
        for cte_name in self.cte_definitions:
            if cte_name not in visited:
                dfs(cte_name)

    def _extract_dependencies(self) -> defaultdict:
        """Извлекает зависимости между таблицами из SQL-операций.

        Returns:
            defaultdict: Словарь зависимостей в формате {target_table: {edges}}.
        """
        dependencies = defaultdict(set)
        etl_types = (Insert, Update, Delete, Merge)

        # Process CTEs first to establish their dependencies
        self._process_all_ctes(dependencies)

        try:
            for statement in self.parsed:
                # First determine the target table (for data modification operations)
                self._statement_count += 1
                to_table = None

                # Handle DDL statements
                if isinstance(statement, Create):
                    to_table = self.get_table_name(statement.args.get("this"))
                    # For CREATE TABLE AS SELECT, extract dependencies from the SELECT
                    if (
                        statement.args.get("kind") == "TABLE"
                        and "expression" in statement.args
                    ):
                        self._process_statement_tree(
                            statement.args["expression"], to_table, dependencies
                        )

                elif isinstance(statement, Drop):
                    # For DROP statements, no dependencies to track
                    continue

                elif isinstance(statement, Alter):
                    to_table = self.get_table_name(statement.args.get("this"))
                    # If ALTER TABLE involves SELECT (e.g., ALTER TABLE ADD COLUMN AS SELECT...)
                    if "expression" in statement.args and isinstance(
                        statement.args["expression"], Select
                    ):
                        self._process_statement_tree(
                            statement.args["expression"], to_table, dependencies
                        )

                # Handle DML statements
                elif isinstance(statement, etl_types):
                    if "this" in statement.args:
                        to_table = self.get_table_name(statement.args.get("this"))

                elif (
                    isinstance(statement, Select)
                    and hasattr(statement, "into")
                    and statement.into is not None
                ):
                    to_table = self.get_table_name(statement.into)

                # For regular SELECT statements without an explicit target
                else:
                    to_table = f"result {self._get_output_id()}"
                if isinstance(statement, Delete):
                    # Process the table being deleted from
                    if "this" in statement.args and statement.args["this"] is not None:
                        from_table = self.get_table_name(statement.args["this"])
                        # Add dependency from the source table to the target
                        dependencies[to_table].add(
                            Edge(from_table, to_table, statement)
                        )

                    # Process WHERE conditions in DELETE statements
                    if (
                        "where" in statement.args
                        and statement.args["where"] is not None
                    ):
                        self._extract_table_dependencies(
                            statement.args["where"], to_table, dependencies
                        )

                    # Check for USING clause in DELETE (some dialects support this)
                    if (
                        "using" in statement.args
                        and statement.args["using"] is not None
                    ):
                        using_tables = self._extract_using_tables(
                            statement.args["using"]
                        )
                        for using_table in using_tables:
                            dependencies[to_table].add(
                                Edge(using_table, to_table, statement)
                            )

                # Handle INSERT statements specifically
                if isinstance(statement, Insert):
                    # For INSERT...VALUES
                    if isinstance(statement.args.get("expression"), Values):
                        input_node = f"input {self._get_input_id()}"
                        dependencies[to_table].add(
                            Edge(input_node, to_table, statement)
                        )
                    # For INSERT...SELECT
                    elif isinstance(statement.args.get("expression"), Select):
                        self._process_statement_tree(
                            statement.args["expression"],
                            to_table,
                            dependencies,
                            statement,
                        )
                # Process WITH clauses (Common Table Expressions)
                if (
                    isinstance(statement, With)
                    or "with" in statement.args
                    and statement.args["with"]
                ):
                    self._process_with_statement(statement, to_table, dependencies)

                # Process the main statement and all subqueries
                self._process_statement_tree(statement, to_table, dependencies)
                # Process the main statement and all subqueries
                self._process_statement_tree(statement, to_table, dependencies)

        except Exception as e:
            print(f"Error in dependency extraction: {e}")

        return dependencies

    def _process_all_ctes(self, dependencies):
        """Обрабатывает все CTE для построения зависимостей.

        Args:
            dependencies: Граф зависимостей для заполнения.
        """
        for cte_name, cte_node in self.cte_definitions.items():
            cte_definition = cte_node.args["this"]
            # Process the CTE query expression
            if cte_definition:
                self._process_statement_tree(cte_definition, cte_name, dependencies)

            # For recursive CTEs, add a self-dependency
            if cte_name in self.recursive_ctes:
                recursive_edge = Edge(cte_name, cte_name, cte_node)
                recursive_edge.is_recursive = True  # Mark edge as recursive
                dependencies[cte_name].add(recursive_edge)

    def _process_with_statement(self, statement, to_table, dependencies):
        """Обрабатывает WITH-конструкции и их связь с основным запросом.

        Args:
            statement: Узел WITH или родительский узел.
            to_table: Целевая таблица основного запроса.
            dependencies: Граф зависимостей для заполнения.
        """
        with_clause = (
            statement if isinstance(statement, With) else statement.args["with"]
        )
        main_query = (
            statement.args.get("this") if isinstance(statement, With) else statement
        )

        # Process each CTE
        if "expressions" in with_clause.args:
            for cte in with_clause.args["expressions"]:
                if isinstance(cte, CTE):
                    cte_name = cte.args["alias"].args["this"]
                    cte_definition = cte.args["this"]

                    # Process the CTE definition
                    if cte_definition:
                        # Add dependency from CTE to the main query
                        if isinstance(main_query, Select):
                            cte_edge = Edge(cte_name, to_table, main_query)
                            dependencies[to_table].add(cte_edge)

    def _process_statement_tree(
        self, statement, to_table, dependencies, original_statement=None
    ):
        """Рекурсивно обрабатывает узлы AST для извлечения зависимостей.

        Args:
            statement: Корневой узел для обработки.
            to_table: Целевая таблица текущего запроса.
            dependencies: Граф зависимостей для заполнения.
        """
        print(f"Processing statement tree: {statement}")
        try:
            # Skip if statement is None
            if statement is None:
                return

            # Handle references to CTEs
            self._handle_cte_references(statement, to_table, dependencies)

            # Process the main FROM table
            if "from" in statement.args and statement.args["from"] is not None:
                from_table = self.get_table_name(statement.args["from"])
                # Add dependency from main table to result
                if isinstance(statement, Select):
                    if original_statement is not None:
                        dependencies[to_table].add(
                            Edge(from_table, to_table, original_statement)
                        )
                    dependencies[to_table].add(Edge(from_table, to_table))
                else:
                    # For data modification operations (DML)
                    dependencies[to_table].add(Edge(from_table, to_table, statement))

            # Process MERGE operations
            if isinstance(statement, Merge):
                # USING defines the source table
                if "using" in statement.args and statement.args["using"]:
                    using_table = self.get_table_name(statement.args["using"])
                    dependencies[to_table].add(Edge(using_table, to_table, statement))

                # Check merge conditions
                if "on" in statement.args and statement.args["on"]:
                    self._extract_table_dependencies(
                        statement.args["on"], to_table, dependencies
                    )

                # Check additional conditions
                if "expressions" in statement.args:
                    for expr in statement.args["expressions"]:
                        self._extract_table_dependencies(expr, to_table, dependencies)

            # Process JOINs in any queries
            if "joins" in statement.args and statement.args["joins"]:
                for join_node in statement.args["joins"]:
                    if "this" in join_node.args:
                        join_table = self.get_table_name(join_node.args["this"])

                        # Create JOIN object for the graph
                        dependencies[to_table].add(
                            Edge(join_table, to_table, join_node)
                        )

                        # Also check for conditions in the JOIN that might reference other tables
                        if "on" in join_node.args and join_node.args["on"]:
                            self._extract_table_dependencies(
                                join_node.args["on"], to_table, dependencies
                            )

            # Process expressions in UPDATE and INSERT queries
            if isinstance(statement, Update) and "set" in statement.args:
                # In UPDATE there may be hidden dependencies in SET expressions
                for set_item in statement.args["set"]:
                    if "expression" in set_item.args:
                        self._extract_table_dependencies(
                            set_item.args["expression"], to_table, dependencies
                        )

            # Process WHERE conditions, which may contain subqueries
            if "where" in statement.args and statement.args["where"] is not None:
                self._extract_table_dependencies(
                    statement.args["where"], to_table, dependencies
                )

            # Process GROUP BY, HAVING, and ORDER BY clauses which may contain subqueries
            for clause_type in ["group", "having", "order"]:
                if clause_type in statement.args and statement.args[clause_type]:
                    self._extract_table_dependencies(
                        statement.args[clause_type], to_table, dependencies
                    )

            # Process SELECT list items for subqueries
            if "expressions" in statement.args and isinstance(statement, Select):
                for expr in statement.args["expressions"]:
                    self._extract_table_dependencies(expr, to_table, dependencies)

        except Exception as e:
            print(f"Error processing statement tree: {e}")

    def _handle_cte_references(self, statement, to_table, dependencies):
        """Обрабатывает ссылки на CTE в запросе.

        Args:
            statement: Узел AST для анализа.
            to_table: Целевая таблица текущего запроса.
            dependencies: Граф зависимостей для заполнения.
        """
        try:
            # Look for all table references that might be CTEs
            for node in statement.walk():
                if isinstance(node, Table):
                    table_name = self.get_table_name(node)

                    # If this table name matches a CTE name, it's a reference
                    if table_name in self.cte_definitions:
                        # Add dependency from CTE to current target
                        dependencies[to_table].add(Edge(table_name, to_table, node))

                        # If this is a recursive CTE and is referencing itself
                        if table_name in self.recursive_ctes and to_table == table_name:
                            # Mark as a recursive edge
                            for edge in dependencies[to_table]:
                                if (
                                    edge.source == table_name
                                    and edge.target == to_table
                                ):
                                    edge.is_recursive = True
        except Exception as e:
            logger.error(f"Error handling CTE references: {e}")

    def _extract_table_dependencies(self, expression, to_table, dependencies):
        """Извлекает зависимости из таблиц в выражениях.

        Args:
            expression: Узел AST для анализа (WHERE, JOIN и т.д.).
            to_table: Целевая таблица.
            dependencies: Граф зависимостей для заполнения.
        """
        try:
            # Look for all subqueries within the expression
            for node in expression.walk():
                if isinstance(node, Select):
                    self._process_statement_tree(node, to_table, dependencies)

                elif isinstance(node, Subquery):
                    if "this" in node.args:
                        self._process_statement_tree(
                            node.args["this"], to_table, dependencies
                        )

                # Look for direct references to tables
                elif isinstance(node, Table):
                    table_name = self.get_table_name(node)
                    # Add direct dependency

                    # Check if this is a CTE reference
                    if table_name in self.cte_definitions:
                        # Add dependency from CTE to current target
                        dependencies[to_table].add(Edge(table_name, to_table, node))
                    else:
                        # Regular table reference
                        dependencies[to_table].add(Edge(table_name, to_table, node))

        except Exception as e:
            print(f"Error extracting table dependencies: {e}")

    def _extract_join_dependencies(self, select_statement, dependencies):
        """Обрабатывает JOIN-операции в SELECT-запросах.

        Args:
            select_statement: Узел SELECT-запроса.
            dependencies: Граф зависимостей для заполнения.
        """
        try:
            if "from" not in select_statement.args:
                return

            # Extract the base table from FROM
            from_clause = select_statement.args["from"]
            base_table = self.get_table_name(from_clause)

            # Process the list of JOINs
            if "joins" in select_statement.args and select_statement.args["joins"]:
                for join_node in select_statement.args["joins"]:
                    joined_table = self.get_table_name(join_node.args.get("this"))
                    if base_table and joined_table:
                        # Create a relationship between tables
                        dependencies[base_table].add(
                            Edge(joined_table, base_table, join_node)
                        )

            # Also check for nested JOINs in FROM
            self._find_nested_joins(from_clause, dependencies)

        except Exception as e:
            print(f"Error extracting JOIN dependencies: {e}")

    def _find_nested_joins(self, expr, dependencies):
        """Находит вложенные JOIN-операции в выражениях.

        Args:
            expr: Узел AST для анализа.
            dependencies: Граф зависимостей для заполнения.
        """
        try:
            for node in expr.walk():
                if isinstance(node, Join):
                    left_table = self._extract_table_name(node.args.get("this"))
                    right_table = self._extract_table_name(node.args.get("expression"))

                    if left_table and right_table:
                        # Create a relationship between tables
                        dependencies[left_table].add(
                            Edge(right_table, left_table, node)
                        )
        except Exception as e:
            print(f"Error processing nested JOINs: {e}")

    def _process_join(self, join_node, dependencies):
        """Обрабатывает отдельный JOIN-узел.

        Args:
            join_node: Узел JOIN-операции.
            dependencies: Граф зависимостей для заполнения.
        """
        try:
            left_expr = join_node.args.get("this")
            right_expr = join_node.args.get("expression")
            if left_expr is None or right_expr is None:
                print(
                    f"Skipping JOIN due to missing expression: left_expr={left_expr}, right_expr={right_expr}"
                )
                return

            left_table = self._extract_table_name(left_expr)
            print(f"Left table extracted: {left_table}")  # Debug statement

            right_table = self._extract_table_name(right_expr)
            print(f"Right table extracted: {right_table}")  # Debug statement

            # Add dependency: from right_table to left_table
            if left_table and right_table:
                dependencies[left_table].add(Edge(right_table, left_table, join_node))
                logger.debug("Added JOIN dependency: %s -> %s", right_table, left_table)

            else:
                print(
                    f"Could not extract both tables from JOIN: left={left_table}, right={right_table}"
                )
        except Exception as e:
            print(f"Error processing JOIN: {e}")

    def _extract_table_name(self, expr):
        """Извлекает имя таблицы из узла AST.

        Args:
            expr: Узел AST, содержащий ссылку на таблицу.

        Returns:
            Имя таблицы или None, если не удалось извлечь.
        """
        if expr is None:
            return None

        # Direct processing for Table objects
        if isinstance(expr, Table):
            try:
                return expr.args["this"].args["this"]
            except (KeyError, AttributeError):
                pass

        # Search for tables within the expression
        tables = []
        for node in expr.walk():
            if isinstance(node, Table):
                try:
                    table_name = node.args["this"].args["this"]
                    tables.append(table_name)
                except (KeyError, AttributeError):
                    pass

        # Return the first table found or None
        return tables[0] if tables else None

    def get_dependencies(self) -> defaultdict:
        """Возвращает граф зависимостей между таблицами.

        Returns:
            defaultdict[set]: Граф в формате {целевая_таблица: {рёбра}}

        Example:
            >>> ast.get_dependencies()["orders"]
            {Edge(source='customers', target='orders', expression=<Merge>)}

        """

        return self.dependencies

    def get_corrections(self) -> List[str]:
        """Возвращает список предупреждений и исправлений.

        Returns:
            List[str]: Список сообщений о проблемах.
        """
        return self.corrections

    def get_table_schema(self) -> Dict[str, Dict[str, Dict]]:
        """Возвращает схему таблиц из CREATE-запросов.

        Returns:
            Dict: Структура вида {'table': {'column': {'type': 'INT'}}}

        Example:
            >>> sql = "CREATE TABLE users (id INT, name VARCHAR(255))"
            >>> ast = SqlAst(sql)
            >>> ast.get_table_schema()
            {'users': {'id': {'data_type': 'INT', ...}, 'name': {...}}}
        """
        return self.table_schema

    def get_recursive_ctes(self) -> Set[str]:
        """Возвращает имена рекурсивных CTE.

        Returns:
            Set[str]: Множество имен. Пусто, если рекурсии нет.

        Example:
            >>> sql = "WITH RECURSIVE cte AS (SELECT * FROM cte)"
            >>> ast = SqlAst(sql)
            >>> ast.get_recursive_ctes()
            {'cte'}
        """
        return self.recursive_ctes

    def get_table_name(self, parsed) -> str:
        """Извлекает имя таблицы из узла AST.

        Args:
            parsed (Expression): Узел AST, например, объект Table.

        Returns:
            str: Имя таблицы или "unknown_{id}". Пример: "users" или "unknown_1".

        Example:
            >>> table_node = sqlglot.parse_one("SELECT * FROM users").find(Table)
            >>> ast.get_table_name(table_node)
            'users'
        """
        try:
            # If it's already a string, return it
            if isinstance(parsed, str):
                return parsed

            # Direct processing of table
            if isinstance(parsed, Table):
                # Extract the main table name
                if "this" in parsed.args:
                    table_obj = parsed.args["this"]
                    if hasattr(table_obj, "args") and "this" in table_obj.args:
                        table_name = table_obj.args["this"]

                        return table_name

            # Recursive search for table in attribute chain
            counter = 0
            current = parsed
            while hasattr(current, "args") and "this" in current.args and counter < 100:
                counter += 1
                if isinstance(current, Table):
                    table_name = current.args["this"].args["this"]
                    return table_name
                current = current.args["this"]

            # Search in other attributes
            if hasattr(parsed, "args"):
                for key, value in parsed.args.items():
                    if isinstance(value, Table):
                        return self.get_table_name(value)

            # If no table found
            return f"unknown {self._get_unknown_id()}"
        except Exception as e:
            print(f"Error in get_table_name: {e}")
            return f"unknown {self._get_unknown_id()}"

    def get_first_from(self, stmt) -> Optional[str]:
        """Возвращает первую таблицу в FROM-клаузе.

        Args:
            stmt: Узел запроса (например, Select)

        Returns:
            Optional[str]: Имя таблицы или None

        Example:
            >>> sql = "SELECT * FROM orders JOIN customers"
            >>> ast = SqlAst(sql)
            >>> select_node = ast.parsed[0]
            >>> ast.get_first_from(select_node)
            'orders'
        """
        try:
            # Check for FROM presence
            if "from" in stmt.args and stmt.args["from"] is not None:
                return self.get_table_name(stmt.args["from"])

            # Check for expression (e.g., in INSERT)
            if "expression" in stmt.args and stmt.args["expression"] is not None:
                expr = stmt.args["expression"]
                if isinstance(expr, Select) and "from" in expr.args:
                    return self.get_table_name(expr.args["from"])
                return self.get_first_from(expr)

            # Search for subqueries in the tree
            for key, value in stmt.args.items():
                if isinstance(value, Select) and "from" in value.args:
                    return self.get_table_name(value.args["from"])

        except Exception as e:
            print(f"Error in get_first_from: {e}")
        return None

    def find_all(self, expr_type, obj=None):
        """Ищет все узлы указанного типа в AST.

        Args:
            expr_type: Тип узла (например, Join)
            obj: Корневой узел для поиска

        Returns:
            List[Expression]: Найденные узлы

        Example:
            >>> sql = "SELECT * FROM a JOIN b WHERE c IN (SELECT d FROM e)"
            >>> ast = SqlAst(sql)
            >>> joins = ast.find_all(Join)
            >>> len(joins)
            1
        """
        if obj is None:
            obj = self.parsed
        result = []
        if isinstance(obj, list):
            for item in obj:
                result.extend(self.find_all(expr_type, item))
        elif hasattr(obj, "walk"):
            for node in obj.walk():
                if isinstance(node, expr_type):
                    result.append(node)
        return result

    def get_cyclic_dependencies(self) -> List[List[str]]:
        """Возвращает циклы в графе зависимостей.

        Returns:
            List[List[str]]: Список циклов

        Example:
            >>> sql = "CREATE TABLE a AS SELECT * FROM b; CREATE TABLE b AS SELECT * FROM a"
            >>> ast = SqlAst(sql)
            >>> ast.get_cyclic_dependencies()
            [['a', 'b', 'a']]
        """
        import networkx as nx

        # Create a directed graph from dependencies
        G = nx.DiGraph()
        for target_table, edges in self.dependencies.items():
            for edge in edges:
                source_table = edge.source
                G.add_edge(source_table, target_table)

        # Find all simple cycles in the graph
        try:
            cycles = list(nx.simple_cycles(G))
            return cycles
        except Exception as e:
            logger.error(f"Error finding cycles: {e}")
            return []

    def _get_input_id(self):
        if self.sep_parse:
            self.input_id += 1
            return self.input_id - 1
        SqlAst._input_id += 1
        return SqlAst._input_id - 1

    def _get_output_id(self):
        if self.sep_parse:
            self.output_id += 1
            return self.output_id - 1
        SqlAst._output_id += 1
        return SqlAst._output_id - 1

    def _get_unknown_id(self):
        if self.sep_parse:
            self.unknown_id += 1
            return self.unknown_id - 1
        SqlAst._unknown_id += 1
        return SqlAst._unknown_id - 1

    def _get_cte_id(self):
        if self.sep_parse:
            self.cte_id += 1
            return self.cte_id - 1
        SqlAst._cte_id += 1
        return SqlAst._cte_id - 1


class DirectoryParser:
    """Обрабатывает SQL-файлы в директории и возвращает результаты анализа.

    Attributes:
        sql_ast_cls (Type[SqlAst]): Класс для анализа SQL (можно заменить на кастомный).

    Example:
        >>> parser = DirectoryParser()
        >>> results = parser.parse_directory("/data/sql")
        >>> results[0]  # (dependencies, corrections, "/data/sql/query.sql")
    """

    def __init__(self, sql_ast_cls=SqlAst):
        """Инициализирует парсер директорий.

        Args:
            sql_ast_cls (type): Класс для анализа SQL. Можно заменить на кастомную реализацию.
        """
        self.sql_ast_cls = sql_ast_cls

    def parse_directory(
        self, directory: str, sep_parse: bool = False
    ) -> List[Tuple[defaultdict, List[str], str]]:
        """Парсит все SQL-файлы в указанной директории.

        Args:
            directory (str): Путь к директории (например, "/data/sql").
            sep_parse (bool): Передается в SqlAst.__init__().

        Returns:
            List[Tuple[defaultdict, List[str], str]:
                Список кортежей: (зависимости, корректировки, путь_к_файлу).

        Raises:
            FileNotFoundError: Если директория не существует.

        Example:
            >>> parser = DirectoryParser()
            >>> results = parser.parse_directory("./data/sql")
            >>> file_path = results[0][2]
            >>> isinstance(file_path, str)
            True
            >>> len(results[0][1])  # Количество корректировок
            0
        """
        results = []
        if not os.path.exists(directory):
            print(f"Error: Directory {directory} does not exist!")
            return results
        if not os.path.isdir(directory):
            print(f"Error: {directory} is not a directory!")
            return results
        print(f"Processing files in directory: {directory}")
        for root, _, files in os.walk(directory):
            print(f"Processing directory: {root}")
            for file in files:
                if file.endswith((".sql", ".ddl")):  # Support both SQL and DDL files
                    file_path = os.path.join(root, file)
                    print(f"Reading file: {file_path}")
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            sql_code = f.read()
                            ast = self.sql_ast_cls(sql_code, sep_parse)
                            results.append(
                                (
                                    ast.get_dependencies(),
                                    ast.get_corrections(),
                                    file_path,
                                )
                            )
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")
                        results.append(
                            (defaultdict(set), [f"Error: {str(e)}"], file_path)
                        )
        return results
