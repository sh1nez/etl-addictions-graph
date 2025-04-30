import logging
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

# Configure module-level logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class SqlAst:
    """Class for building AST of SQL queries."""

    _input_id = 0
    _output_id = 0
    _unknown_id = 0
    _join_id = 0
    _transfer_id = 0
    _cte_id = 0

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
        self.cte_id = SqlAst._cte_id
        self.sep_parse = sep_parse
        self._statement_count = 0
        self.table_schema = {}
        self.cte_definitions = {}
        self.cte_references = defaultdict(set)
        self.recursive_ctes = set()

        logger.debug("Parsing SQL code.")
        self.parsed, self.dialect = safe_parse(self.corrected_sql)
        assert self.parsed is not None, "Parsed result is None"
        self._extract_schema_info()
        self._identify_all_ctes()
        self.dependencies = self._extract_dependencies()
        self._detect_recursive_ctes()
        logger.info("SQL parsing and dependency extraction completed.")

    def _extract_schema_info(self):
        for statement in self.parsed:
            if isinstance(statement, Create) and statement.args.get("kind") == "TABLE":
                table_name = self.get_table_name(statement.args.get("this"))
                columns = {}
                if "expressions" in statement.args:
                    for col_def in statement.args["expressions"]:
                        if "this" in col_def.args and "datatype" in col_def.args:
                            col_name = col_def.args["this"].args["this"]
                            data_type = col_def.args["datatype"].sql()
                            columns[col_name] = {
                                "data_type": data_type,
                                "nullable": "not" not in col_def.args
                                or not col_def.args.get("not", False),
                                "primary_key": col_def.args.get("primary", False),
                            }
                self.table_schema[table_name] = columns
                logger.debug(f"Extracted schema for table %s: %s", table_name, columns)

    def _identify_all_ctes(self):
        for statement in self.parsed:
            if isinstance(statement, With):
                self._register_ctes_from_with(statement)
            elif "with" in statement.args and statement.args["with"]:
                self._register_ctes_from_with(statement.args["with"])
            is_recursive = False
            if isinstance(statement, With) and statement.args.get("recursive"):
                is_recursive = True
            elif statement.args.get("with") and statement.args["with"].args.get(
                "recursive"
            ):
                is_recursive = True
            if is_recursive:
                self._mark_ctes_as_recursive(statement)
                logger.debug("Marked CTEs in WITH RECURSIVE as recursive.")

    def _register_ctes_from_with(self, with_statement):
        if "expressions" not in with_statement.args:
            return
        for cte in with_statement.args["expressions"]:
            if isinstance(cte, CTE):
                cte_name = cte.args["alias"].args["this"]
                self.cte_definitions[cte_name] = cte
                self._find_cte_references(cte_name, cte.args["this"])

    def _find_cte_references(self, cte_name, expression):
        if expression is None:
            return
        for node in expression.walk():
            if isinstance(node, Table):
                referenced_table = self.get_table_name(node)
                if referenced_table in self.cte_definitions:
                    self.cte_references[referenced_table].add(cte_name)
                    if referenced_table == cte_name:
                        self.recursive_ctes.add(cte_name)

    def _mark_ctes_as_recursive(self, statement):
        if isinstance(statement, With):
            ctes = statement.args.get("expressions", [])
        else:
            ctes = statement.args.get("with").args.get("expressions", [])
        for cte in ctes:
            if isinstance(cte, CTE):
                cte_name = cte.args["alias"].args["this"]
                self.recursive_ctes.add(cte_name)

    def _detect_recursive_ctes(self):
        for cte_name, cte_node in self.cte_definitions.items():
            if cte_node.args["this"]:
                for node in cte_node.args["this"].walk():
                    if (
                        isinstance(node, Table)
                        and self.get_table_name(node) == cte_name
                    ):
                        self.recursive_ctes.add(cte_name)
                        break
        visited, temp_visited = set(), set()

        def dfs(node):
            if node in temp_visited:
                self.recursive_ctes.add(node)
                return True
            if node in visited:
                return False
            visited.add(node)
            temp_visited.add(node)
            for neighbor in self.cte_references.get(node, []):
                if dfs(neighbor):
                    self.recursive_ctes.add(node)
                    return True
            temp_visited.remove(node)
            return False

        for cte_name in self.cte_definitions:
            if cte_name not in visited:
                dfs(cte_name)

    def _extract_dependencies(self) -> defaultdict:
        dependencies = defaultdict(set)
        etl_types = (Insert, Update, Delete, Merge)
        self._process_all_ctes(dependencies)
        for statement in self.parsed:
            self._statement_count += 1
            to_table = None
            if isinstance(statement, Create):
                to_table = self.get_table_name(statement.args.get("this"))
                if (
                    statement.args.get("kind") == "TABLE"
                    and "expression" in statement.args
                ):
                    self._process_statement_tree(
                        statement.args["expression"], to_table, dependencies
                    )
            elif isinstance(statement, Drop):
                continue
            elif isinstance(statement, Alter):
                to_table = self.get_table_name(statement.args.get("this"))
                if isinstance(statement.args.get("expression"), Select):
                    self._process_statement_tree(
                        statement.args["expression"], to_table, dependencies
                    )
            elif isinstance(statement, etl_types) and statement.args.get("this"):
                to_table = self.get_table_name(statement.args.get("this"))
            elif (
                isinstance(statement, Select)
                and hasattr(statement, "into")
                and statement.into
            ):
                to_table = self.get_table_name(statement.into)
            else:
                to_table = f"result {self._get_output_id()}"
            if isinstance(statement, Insert):
                expr = statement.args.get("expression")
                if isinstance(expr, Values):
                    input_node = f"input {self._get_input_id()}"
                    dependencies[to_table].add(Edge(input_node, to_table, statement))
                elif isinstance(expr, Select):
                    self._process_statement_tree(expr, to_table, dependencies)
            if isinstance(statement, With) or statement.args.get("with"):
                self._process_with_statement(statement, to_table, dependencies)
            self._process_statement_tree(statement, to_table, dependencies)
        return dependencies

    def _process_all_ctes(self, dependencies):
        for cte_name, cte_node in self.cte_definitions.items():
            cte_def = cte_node.args["this"]
            if cte_def:
                self._process_statement_tree(cte_def, cte_name, dependencies)
            if cte_name in self.recursive_ctes:
                edge = Edge(cte_name, cte_name, cte_node)
                edge.is_recursive = True
                dependencies[cte_name].add(edge)

    def _process_with_statement(self, statement, to_table, dependencies):
        with_clause = (
            statement if isinstance(statement, With) else statement.args["with"]
        )
        main_q = (
            statement.args.get("this") if isinstance(statement, With) else statement
        )
        for cte in with_clause.args.get("expressions", []):
            if isinstance(cte, CTE) and isinstance(main_q, Select):
                edge = Edge(cte.args["alias"].args["this"], to_table, main_q)
                dependencies[to_table].add(edge)

    def _process_statement_tree(self, statement, to_table, dependencies):
        if statement is None:
            return
        self._handle_cte_references(statement, to_table, dependencies)
        if statement.args.get("from"):
            from_tbl = self.get_table_name(statement.args["from"])
            dependencies[to_table].add(Edge(from_tbl, to_table, statement))
        if isinstance(statement, Merge) and statement.args.get("using"):
            dependencies[to_table].add(
                Edge(self.get_table_name(statement.args["using"]), to_table, statement)
            )
            for expr in statement.args.get("expressions", []):
                self._extract_table_dependencies(expr, to_table, dependencies)
        for join in statement.args.get("joins", []):
            jt = self.get_table_name(join.args.get("this"))
            dependencies[to_table].add(Edge(jt, to_table, join))
            if join.args.get("on"):
                self._extract_table_dependencies(
                    join.args.get("on"), to_table, dependencies
                )
        if isinstance(statement, Update):
            for s in statement.args.get("set", []):
                self._extract_table_dependencies(
                    s.args.get("expression"), to_table, dependencies
                )
        for clause in ("where", "group", "having", "order"):
            if statement.args.get(clause):
                self._extract_table_dependencies(
                    statement.args.get(clause), to_table, dependencies
                )
        if isinstance(statement, Select):
            for expr in statement.args.get("expressions", []):
                self._extract_table_dependencies(expr, to_table, dependencies)

    def _handle_cte_references(self, statement, to_table, dependencies):
        for node in statement.walk():
            if isinstance(node, Table):
                tn = self.get_table_name(node)
                if tn in self.cte_definitions:
                    dependencies[to_table].add(Edge(tn, to_table, node))
                    if tn in self.recursive_ctes and to_table == tn:
                        for e in dependencies[to_table]:
                            if e.source == tn and e.target == to_table:
                                e.is_recursive = True

    def _extract_table_dependencies(self, expression, to_table, dependencies):
        for node in expression.walk():
            if isinstance(node, (Select, Subquery)):
                target = node if isinstance(node, Select) else node.args.get("this")
                self._process_statement_tree(target, to_table, dependencies)
            elif isinstance(node, Table):
                tn = self.get_table_name(node)
                dependencies[to_table].add(Edge(tn, to_table, node))

    def _extract_join_dependencies(self, select_statement, dependencies):
        if not select_statement.args.get("from"):
            return
        base = self.get_table_name(select_statement.args["from"])
        for join in select_statement.args.get("joins", []):
            jt = self.get_table_name(join.args.get("this"))
            dependencies[base].add(Edge(jt, base, join))
        self._find_nested_joins(select_statement.args["from"], dependencies)

    def _find_nested_joins(self, expr, dependencies):
        for node in expr.walk():
            if isinstance(node, Join):
                lt = self._extract_table_name(node.args.get("this"))
                rt = self._extract_table_name(node.args.get("expression"))
                if lt and rt:
                    dependencies[lt].add(Edge(rt, lt, node))

    def _process_join(self, join_node, dependencies):
        left_expr = join_node.args.get("this")
        right_expr = join_node.args.get("expression")
        if left_expr is None or right_expr is None:
            logger.warning(
                "Skipping JOIN due to missing expression: left_expr=%s, right_expr=%s",
                left_expr,
                right_expr,
            )
            return
        lt = self._extract_table_name(left_expr)
        rt = self._extract_table_name(right_expr)
        if lt and rt:
            dependencies[lt].add(Edge(rt, lt, join_node))
            logger.debug("Added JOIN dependency: %s -> %s", rt, lt)
        else:
            logger.warning(
                "Could not extract both tables from JOIN: left=%s, right=%s", lt, rt
            )

    def _extract_table_name(self, expr):
        if expr is None:
            return None
        if isinstance(expr, Table):
            return expr.args["this"].args.get("this")
        for node in expr.walk():
            if isinstance(node, Table):
                return node.args["this"].args.get("this")
        return None

    def get_dependencies(self) -> defaultdict:
        return self.dependencies

    def get_corrections(self) -> List[str]:
        return self.corrections

    def get_table_schema(self) -> Dict[str, Dict[str, Dict]]:
        return self.table_schema

    def get_recursive_ctes(self) -> Set[str]:
        return self.recursive_ctes

    def get_table_name(self, parsed) -> str:
        if isinstance(parsed, str):
            return parsed
        if isinstance(parsed, Table):
            tbl = parsed.args["this"].args.get("this")
            alias = parsed.args.get("alias")
            return f"{tbl} ({alias.args['this']})" if alias else tbl
        counter = 0
        current = parsed
        while hasattr(current, "args") and "this" in current.args and counter < 100:
            counter += 1
            current = current.args["this"]
            if isinstance(current, Table):
                tbl = current.args["this"].args.get("this")
                alias = current.args.get("alias")
                return f"{tbl} ({alias.args['this']})" if alias else tbl
        return f"unknown {self._get_unknown_id()}"

    def get_first_from(self, stmt) -> Optional[str]:
        if stmt.args.get("from") is not None:
            return self.get_table_name(stmt.args.get("from"))
        if stmt.args.get("expression"):
            expr = stmt.args.get("expression")
            if isinstance(expr, Select) and expr.args.get("from"):
                return self.get_table_name(expr.args.get("from"))
            return self.get_first_from(expr)
        for val in stmt.args.values():
            if isinstance(val, Select) and val.args.get("from"):
                return self.get_table_name(val.args.get("from"))
        return None

    def find_all(self, expr_type, obj=None):
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
        import networkx as nx

        G = nx.DiGraph()
        for tgt, edges in self.dependencies.items():
            for e in edges:
                G.add_edge(e.source, tgt)
        return list(nx.simple_cycles(G))

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
    """Class for processing SQL files in a directory."""

    def __init__(self, sql_ast_cls=SqlAst):
        self.sql_ast_cls = sql_ast_cls

    def parse_directory(
        self, directory: str, sep_parse: bool = False
    ) -> List[Tuple[defaultdict, List[str], str]]:
        results = []
        if not os.path.exists(directory):
            logger.error("Directory %s does not exist!", directory)
            return results
        if not os.path.isdir(directory):
            logger.error("%s is not a directory!", directory)
            return results
        logger.info("Processing files in directory: %s", directory)
        for root, _, files in os.walk(directory):
            logger.debug("Processing directory: %s", root)
            for file in files:
                if file.endswith((".sql", ".ddl")):
                    file_path = os.path.join(root, file)
                    logger.info("Reading file: %s", file_path)
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
        return results
