import os
from collections import defaultdict
from typing import Optional, List, Tuple
from sqlglot.expressions import Update, Insert, Table, Delete, Merge, Select, Join
from util.dialect import safe_parse
from base.storage import Edge
from logger_config import logger


class SqlAst:
    """Class for building AST of SQL queries."""

    _input_id = 0
    _output_id = 0
    _unknown_id = 0
    _join_id = 0
    _transfer_id = 0

    def __init__(self, sql_code: str, sep_parse: bool = False):
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
        self.sep_parse = sep_parse

        try:
            self.parsed, self.dialect = safe_parse(self.corrected_sql)
            assert self.parsed is not None
            self.dependencies = self._extract_dependencies()
            logger.info("SQL parsed and dependencies extracted successfully.")
        except Exception as e:
            logger.error(f"Error parsing SQL: {e}")
            self.parsed = None
            self.dependencies = defaultdict(set)
            self.corrections.append(f"Error parsing SQL: {str(e)}")

    def _extract_dependencies(self) -> defaultdict:
        """Extracts dependencies between tables and operations including ETL, SELECT and JOIN queries."""
        dependencies = defaultdict(set)
        etl_types = (Insert, Update, Delete, Merge)
        try:
            for statement in self.parsed:
                # Сначала определяем целевую таблицу (для операций модификации данных)
                to_table = None
                if isinstance(statement, etl_types):
                    if "this" in statement.args:
                        to_table = self.get_table_name(statement)
                elif (
                    isinstance(statement, Select)
                    and hasattr(statement, "into")
                    and statement.into is not None
                ):
                    to_table = self.get_table_name(statement.into)
                else:
                    to_table = f"result {self._get_output_id()}"

                # Обрабатываем основной запрос и все подзапросы
                self._process_statement_tree(statement, to_table, dependencies)

        except Exception as e:
            logger.error(f"Error in dependency extraction: {e}")

        return dependencies

    def _process_statement_tree(self, statement, to_table, dependencies):
        """Рекурсивно обрабатывает запрос и его подзапросы для извлечения зависимостей."""
        try:
            # Обработка основной таблицы FROM
            if "from" in statement.args and statement.args["from"] is not None:
                from_table = self.get_table_name(statement.args["from"])
                # Добавляем зависимость от основной таблицы к результату
                if isinstance(statement, Select):
                    dependencies[to_table].add(Edge(from_table, to_table, statement))
                else:
                    # Для операций модификации данных (DML)
                    dependencies[to_table].add(Edge(from_table, to_table, statement))

            if isinstance(statement, Merge):
                # Using определяет таблицу источник
                if "using" in statement.args and statement.args["using"]:
                    using_table = self.get_table_name(statement.args["using"])
                    dependencies[to_table].add(Edge(using_table, to_table, statement))

                # Проверка merge условий
                if "on" in statement.args and statement.args["on"]:
                    self._extract_table_dependencies(
                        statement.args["on"], to_table, dependencies
                    )

                # Проверка дополнительных условий
                if "expressions" in statement.args:
                    for expr in statement.args["expressions"]:
                        self._extract_table_dependencies(expr, to_table, dependencies)

            # Обработка JOIN в любых запросах
            if "joins" in statement.args and statement.args["joins"]:
                for join_node in statement.args["joins"]:
                    if "this" in join_node.args:
                        join_table = self.get_table_name(join_node.args["this"])

                        # Создаем объект JOIN для графа
                        simple_join = Join()

                        # Добавляем зависимость от JOIN-таблицы к целевой таблице
                        dependencies[to_table].add(
                            Edge(join_table, to_table, simple_join)
                        )

            # Обработка выражений в запросах UPDATE и INSERT
            if isinstance(statement, Update) and "set" in statement.args:
                # В UPDATE могут быть скрытые зависимости в SET выражениях
                for set_item in statement.args["set"]:
                    if "expression" in set_item.args:
                        self._extract_table_dependencies(
                            set_item.args["expression"], to_table, dependencies
                        )

            elif isinstance(statement, Insert) and "expression" in statement.args:
                # Обработка SELECT внутри INSERT
                expr = statement.args["expression"]
                if isinstance(expr, Select):
                    self._process_statement_tree(expr, to_table, dependencies)

            # Обработка WHERE условий, которые могут содержать подзапросы
            if "where" in statement.args and statement.args["where"] is not None:
                self._extract_table_dependencies(
                    statement.args["where"], to_table, dependencies
                )

        except Exception as e:
            logger.error(f"Error processing statement tree: {e}")

    def _extract_table_dependencies(self, expression, to_table, dependencies):
        """Извлекает зависимости от таблиц из выражения."""
        try:
            # Ищем все подзапросы внутри выражения
            for node in expression.walk():
                if isinstance(node, Select):
                    self._process_statement_tree(node, to_table, dependencies)

                # Ищем прямые ссылки на таблицы
                elif isinstance(node, Table):
                    table_name = self.get_table_name(node)
                    # Добавляем прямую зависимость
                    dependencies[to_table].add(Edge(table_name, to_table, node))

        except Exception as e:
            logger.error(f"Error extracting table dependencies: {e}")

    def _extract_join_dependencies(self, select_statement, dependencies):
        """Extract JOIN dependencies from a SELECT statement."""
        try:
            if "from" not in select_statement.args:
                return

            # Извлекаем базовую таблицу из FROM
            from_clause = select_statement.args["from"]
            base_table = self.get_table_name(from_clause)

            # Обработка списка JOIN'ов
            if "joins" in select_statement.args and select_statement.args["joins"]:
                for join_node in select_statement.args["joins"]:
                    joined_table = self.get_table_name(join_node.args.get("this"))
                    if base_table and joined_table:
                        # Создаем связь между таблицами
                        dependencies[base_table].add(
                            Edge(joined_table, base_table, join_node)
                        )

            # Также проверяем вложенные JOIN'ы в FROM
            self._find_nested_joins(from_clause, dependencies)

        except Exception as e:
            logger.error(f"Error extracting JOIN dependencies: {e}")

    def _find_nested_joins(self, expr, dependencies):
        """Find nested JOIN operations within expressions."""
        try:
            for node in expr.walk():
                if isinstance(node, Join):
                    left_table = self._extract_table_name(node.args.get("this"))
                    right_table = self._extract_table_name(node.args.get("expression"))

                    if left_table and right_table:
                        # Создаем связь между таблицами
                        dependencies[left_table].add(
                            Edge(right_table, left_table, node)
                        )
        except Exception as e:
            logger.error(f"Error processing nested JOINs: {e}")

    def _process_join(self, join_node, dependencies):
        """Process a single JOIN node and extract table dependencies."""
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

            # Добавляем зависимость: из right_table в left_table
            if left_table and right_table:
                dependencies[left_table].add(Edge(right_table, left_table, join_node))
                print(f"Added JOIN dependency: {right_table} -> {left_table}")
            else:
                print(
                    f"Could not extract both tables from JOIN: left={left_table}, right={right_table}"
                )
        except Exception as e:
            logger.error(f"Error processing JOIN: {e}")

    def _extract_table_name(self, expr):
        """Helper method to extract table name from an expression."""
        if expr is None:
            return None

        # Прямая обработка для объектов Table
        if isinstance(expr, Table):
            try:
                return expr.args["this"].args["this"]
            except (KeyError, AttributeError):
                pass

        # Поиск таблиц внутри выражения
        tables = []
        for node in expr.walk():
            if isinstance(node, Table):
                try:
                    table_name = node.args["this"].args["this"]
                    tables.append(table_name)
                except (KeyError, AttributeError):
                    pass

        # Возвращаем первую найденную таблицу или None
        return tables[0] if tables else None

    def get_dependencies(self) -> defaultdict:
        return self.dependencies

    def get_corrections(self) -> List[str]:
        return self.corrections

    def get_table_name(self, parsed) -> str:
        """Улучшенный метод извлечения имени таблицы, поддерживающий алиасы."""
        try:
            # Если это уже строка, вернуть её
            if isinstance(parsed, str):
                return parsed

            # Прямая обработка таблицы
            if isinstance(parsed, Table):
                # Извлекаем основное имя таблицы
                if "this" in parsed.args:
                    table_obj = parsed.args["this"]
                    if hasattr(table_obj, "args") and "this" in table_obj.args:
                        table_name = table_obj.args["this"]

                        # Проверяем наличие алиаса
                        if "alias" in parsed.args and parsed.args["alias"] is not None:
                            alias = parsed.args["alias"].args["this"]
                            return f"{table_name} ({alias})"
                        return table_name

            # Рекурсивный поиск таблицы в цепочке атрибутов
            counter = 0
            current = parsed
            while hasattr(current, "args") and "this" in current.args and counter < 100:
                counter += 1
                if isinstance(current, Table):
                    table_name = current.args["this"].args["this"]
                    # Проверяем наличие алиаса
                    if "alias" in current.args and current.args["alias"] is not None:
                        alias = current.args["alias"].args["this"]
                        return f"{table_name} ({alias})"
                    return table_name
                current = current.args["this"]

            # Поиск в других атрибутах
            if hasattr(parsed, "args"):
                for key, value in parsed.args.items():
                    if isinstance(value, Table):
                        return self.get_table_name(value)

            # Если не нашли таблицу
            return f"unknown {self._get_unknown_id()}"
        except Exception as e:
            logger.error(f"Error in get_table_name: {e}")
            return f"unknown {self._get_unknown_id()}"

    def get_first_from(self, stmt) -> Optional[str]:
        """Улучшенный метод для извлечения первой таблицы FROM в запросе."""
        try:
            # Проверяем наличие FROM
            if "from" in stmt.args and stmt.args["from"] is not None:
                return self.get_table_name(stmt.args["from"])

            # Проверяем наличие выражения (например, в INSERT)
            if "expression" in stmt.args and stmt.args["expression"] is not None:
                expr = stmt.args["expression"]
                if isinstance(expr, Select) and "from" in expr.args:
                    return self.get_table_name(expr.args["from"])
                return self.get_first_from(expr)

            # Ищем подзапросы в дереве
            for key, value in stmt.args.items():
                if isinstance(value, Select) and "from" in value.args:
                    return self.get_table_name(value.args["from"])

        except Exception as e:
            logger.error(f"Error in get_first_from: {e}")
        return None

    def find_all(self, expr_type, obj=None):
        """Helper method to find all instances of a type within an expression tree."""
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


class DirectoryParser:
    """Class for processing SQL files in a directory."""

    def __init__(self, sql_ast_cls: SqlAst):
        self.sql_ast_cls = sql_ast_cls

    def parse_directory(
        self, directory: str, sep_parse: bool = False
    ) -> List[Tuple[defaultdict, List[str], str]]:
        results = []
        if not os.path.exists(directory):
            logger.error(f"Directory {directory} does not exist!")
            return results
        if not os.path.isdir(directory):
            logger.error(f"{directory} is not a directory!")
            return results
        logger.info(f"Processing files in directory: {directory}")

        for root, _, files in os.walk(directory):
            logger.debug(f"Scanning directory: {root}")
            for file in files:
                if file.endswith(".sql"):
                    file_path = os.path.join(root, file)
                    logger.info(f"Reading file: {file_path}")
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
                        logger.error(f"Error processing file {file_path}: {e}")
                        results.append(
                            (defaultdict(set), [f"Error: {str(e)}"], file_path)
                        )
        return results
