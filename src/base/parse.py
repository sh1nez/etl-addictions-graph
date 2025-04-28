from functools import total_ordering
import os
from collections import defaultdict
from os.path import realpath
from typing import Optional, List, Tuple
from sqlglot.expressions import (
    Update,
    Insert,
    Table,
    Delete,
    Merge,
    Select,
    Join,
    Values,
)
from util.dialect import safe_parse
from base.storage import Edge
from logger_config import logger  # Добавлен импорт логгера


class SqlAst:
    """Class for building AST of SQL queries."""

    _input_id = 0
    _output_id = 0
    _unknown_id = 0
    _join_id = 0
    _transfer_id = 0

    def __init__(self, sql_code: str, sep_parse: bool = False):
        logger.debug("Initializing SqlAst")
        if not sql_code or not isinstance(sql_code, str):
            logger.error("Invalid input: Not a valid SQL string")
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
        self._statement_count = 0

        try:
            self.parsed, self.dialect = safe_parse(self.corrected_sql)
            assert self.parsed is not None
            self.dependencies = self._extract_dependencies()
            logger.info(
                f"Parsed SQL and extracted dependencies: {len(self.dependencies)} tables"
            )
        except Exception as e:
            logger.error(f"Error parsing SQL: {e}", exc_info=True)
            self.parsed = None
            self.dependencies = defaultdict(set)
            self.corrections.append(f"Error parsing SQL: {str(e)}")

    def _add_dependency(self, dependencies: defaultdict, edge: Edge):
        if edge.to_table != edge.from_table:
            dependencies[edge.to_table].add(edge)
            logger.debug(
                f"Dependency added: {edge.from_table} -> {edge.to_table} [{type(edge.op).__name__}]"
            )

    def _extract_dependencies(self) -> defaultdict:
        """Extracts dependencies between tables and operations including ETL, SELECT and JOIN queries."""
        logger.debug("Starting dependency extraction")
        dependencies = defaultdict(set)
        etl_types = (Insert, Update, Delete, Merge)
        try:
            for statement in self.parsed:
                # Сначала определяем целевую таблицу
                self._statement_count += 1
                to_table = None
                if isinstance(statement, etl_types) and "this" in statement.args:
                    to_table = self.get_table_name(statement)
                elif (
                    isinstance(statement, Select)
                    and hasattr(statement, "into")
                    and statement.into
                ):
                    to_table = self.get_table_name(statement.into)
                else:
                    to_table = f"result {self._get_output_id()}"

                if isinstance(statement, Insert):
                    input_node = f"input {self._statement_count - 1}"
                    self._add_dependency(
                        dependencies, Edge(input_node, to_table, statement)
                    )

                self._process_statement_tree(statement, to_table, dependencies)

            logger.info(
                f"Extracted dependencies for {self._statement_count} statements"
            )
        except Exception as e:
            logger.error(f"Error in dependency extraction: {e}", exc_info=True)
        return dependencies

    def _process_statement_tree(self, statement, to_table, dependencies):
        """Рекурсивно обрабатывает запрос и его подзапросы для извлечения зависимостей."""
        try:
            # FROM clause
            if "from" in statement.args and statement.args["from"]:
                from_table = self.get_table_name(statement.args["from"])
                self._add_dependency(
                    dependencies, Edge(from_table, to_table, statement)
                )

            # MERGE specific
            if isinstance(statement, Merge):
                if statement.args.get("using"):
                    using_table = self.get_table_name(statement.args["using"])
                    self._add_dependency(
                        dependencies, Edge(using_table, to_table, statement)
                    )

                if statement.args.get("on"):
                    self._extract_table_dependencies(
                        statement.args["on"], to_table, dependencies
                    )

                for expr in statement.args.get("expressions", []):
                    self._extract_table_dependencies(expr, to_table, dependencies)

            # JOINs
            for join_node in statement.args.get("joins", []):
                join_table = self.get_table_name(join_node.args.get("this"))
                simple_join = Join()
                self._add_dependency(
                    dependencies, Edge(join_table, to_table, simple_join)
                )

            # UPDATE set expressions
            if isinstance(statement, Update):
                for set_item in statement.args.get("set", []):
                    expr = set_item.args.get("expression")
                    if expr:
                        self._extract_table_dependencies(expr, to_table, dependencies)

            # INSERT expression
            if isinstance(statement, Insert) and statement.args.get("expression"):
                expr = statement.args["expression"]
                if isinstance(expr, Select):
                    self._process_statement_tree(expr, to_table, dependencies)
                elif isinstance(expr, Values):
                    in_node = f"input {self._get_output_id()}"
                    self._add_dependency(
                        dependencies, Edge(in_node, to_table, statement)
                    )

            # WHERE clause
            if statement.args.get("where"):
                self._extract_table_dependencies(
                    statement.args["where"], to_table, dependencies
                )
        except Exception as e:
            logger.error(f"Error processing statement tree: {e}", exc_info=True)

    def _extract_table_dependencies(self, expression, to_table, dependencies):
        """Извлекает зависимости от таблиц из выражения."""
        try:
            for node in expression.walk():
                if isinstance(node, Select):
                    self._process_statement_tree(node, to_table, dependencies)
                elif isinstance(node, Table):
                    table_name = self.get_table_name(node)
                    self._add_dependency(dependencies, Edge(table_name, to_table, node))
        except Exception as e:
            logger.error(f"Error extracting table dependencies: {e}", exc_info=True)

    def _extract_join_dependencies(self, select_statement, dependencies):
        """Extract JOIN dependencies from a SELECT statement."""
        try:
            base_table = self.get_table_name(select_statement.args.get("from"))
            for join_node in select_statement.args.get("joins", []):
                joined_table = self.get_table_name(join_node.args.get("this"))
                self._add_dependency(
                    dependencies, Edge(joined_table, base_table, join_node)
                )
            self._find_nested_joins(select_statement.args.get("from"), dependencies)
        except Exception as e:
            logger.error(f"Error extracting JOIN dependencies: {e}", exc_info=True)

    def _find_nested_joins(self, expr, dependencies):
        """Find nested JOIN operations within expressions."""
        try:
            for node in expr.walk():
                if isinstance(node, Join):
                    left = self._extract_table_name(node.args.get("this"))
                    right = self._extract_table_name(node.args.get("expression"))
                    if left and right:
                        self._add_dependency(dependencies, Edge(right, left, node))
        except Exception as e:
            logger.error(f"Error processing nested JOINs: {e}", exc_info=True)

    def _process_join(self, join_node, dependencies):
        """Process a single JOIN node and extract table dependencies."""
        try:
            left = self._extract_table_name(join_node.args.get("this"))
            right = self._extract_table_name(join_node.args.get("expression"))
            logger.debug(f"Processing JOIN: left={left}, right={right}")
            if left and right:
                self._add_dependency(dependencies, Edge(right, left, join_node))
                logger.info(f"Added JOIN dependency: {right} -> {left}")
            else:
                logger.warning(
                    f"Skipping JOIN, missing tables: left={left}, right={right}"
                )
        except Exception as e:
            logger.error(f"Error processing JOIN: {e}", exc_info=True)

    def _extract_table_name(self, expr):
        """Helper method to extract table name from an expression."""
        if expr is None:
            return None
        if isinstance(expr, Table):
            try:
                return expr.args["this"].args["this"]
            except Exception:
                pass
        tables = []
        for node in expr.walk():
            if isinstance(node, Table):
                try:
                    tables.append(node.args["this"].args["this"])
                except Exception:
                    pass
        return tables[0] if tables else None

    def get_dependencies(self) -> defaultdict:
        return self.dependencies

    def get_corrections(self) -> List[str]:
        return self.corrections

    def get_table_name(self, parsed) -> str:
        """Улучшенный метод извлечения имени таблицы, поддерживающий алиасы."""
        try:
            if isinstance(parsed, str):
                return parsed
            if isinstance(parsed, Table) and "this" in parsed.args:
                table_obj = parsed.args["this"]
                table_name = table_obj.args.get("this")
                alias = parsed.args.get("alias")
                if alias:
                    return f"{table_name} ({alias.args.get('this')})"
                return table_name
            counter = 0
            current = parsed
            while hasattr(current, "args") and counter < 100:
                if isinstance(current, Table):
                    name = current.args["this"].args.get("this")
                    alias = current.args.get("alias")
                    if alias:
                        return f"{name} ({alias.args.get('this')})"
                    return name
                current = current.args.get("this")
                counter += 1
            if hasattr(parsed, "args"):
                for value in parsed.args.values():
                    if isinstance(value, Table):
                        return self.get_table_name(value)
            return f"unknown {self._get_unknown_id()}"
        except Exception as e:
            logger.error(f"Error in get_table_name: {e}", exc_info=True)
            return f"unknown {self._get_unknown_id()}"

    def get_first_from(self, stmt) -> Optional[str]:
        """Улучшенный метод для извлечения первой таблицы FROM в запросе."""
        try:
            if stmt.args.get("from"):
                return self.get_table_name(stmt.args["from"])
            expr = stmt.args.get("expression")
            if isinstance(expr, Select):
                return self.get_table_name(expr.args.get("from"))
            for value in stmt.args.values():
                if isinstance(value, Select):
                    return self.get_table_name(value.args.get("from"))
        except Exception as e:
            logger.error(f"Error in get_first_from: {e}", exc_info=True)
        return None

    def find_all(self, expr_type, obj=None):
        """Helper method to find all instances of a type within an expression tree."""
        result = []
        items = obj or self.parsed
        if isinstance(items, list):
            for item in items:
                result.extend(self.find_all(expr_type, item))
        elif hasattr(items, "walk"):
            for node in items.walk():
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
        logger.debug("DirectoryParser initialized with SqlAst class")

    def parse_directory(
        self, directory: str, sep_parse: bool = False
    ) -> List[Tuple[defaultdict, List[str], str]]:
        logger.info(f"Parsing directory: {directory}")
        results = []
        if not os.path.exists(directory):
            logger.error(f"Directory does not exist: {directory}")
            return results
        if not os.path.isdir(directory):
            logger.error(f"Not a directory: {directory}")
            return results
        logger.debug(f"Walking directory tree: {realpath(directory)}")
        for root, _, files in os.walk(directory):
            logger.debug(f"Processing directory: {root}")
            for file in files:
                if file.endswith(".ddl"):
                    file_path = os.path.join(root, file)
                    logger.debug(f"Reading file: {file_path}")
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            sql_code = f.read()
                            ast = self.sql_ast_cls(sql_code, sep_parse)
                            deps = ast.get_dependencies()
                            corrs = ast.get_corrections()
                            results.append((deps, corrs, file_path))
                            logger.info(
                                f"Parsed {file_path}: {len(corrs)} corrections, {len(deps)} tables"
                            )
                    except Exception as e:
                        logger.error(
                            f"Error processing file {file_path}: {e}", exc_info=True
                        )
                        results.append(
                            (defaultdict(set), [f"Error: {str(e)}"], file_path)
                        )
        logger.info(f"Completed parsing directory: {len(results)} files processed")
        return results
