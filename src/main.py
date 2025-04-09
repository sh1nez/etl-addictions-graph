import os
import networkx as nx
from collections import defaultdict
from typing import Optional, Tuple, List, Union
from matplotlib import pyplot as plt
from sqlglot.expressions import Update, Insert, Table, Delete, Merge, Select, DML, Join
from dialect import safe_parse

class Edge:
    def __init__(self, from_table: str, to_table: str, op: Union[DML, Select]):
        self.from_table = from_table
        self.to_table = to_table
        self.op = op  # operation

class GraphStorage:
    """Class for storing dependency graph data."""

    COLORS = {
        Insert: "red",
        Update: "green",
        Delete: "blue",
        Merge: "yellow",
        Select: "purple",
        Join: "orange"
    }

    def __init__(self):
        self.nodes = set()
        self.edges: list[Edge] = []

    def add_dependencies(self, dependencies: defaultdict):
        for to_table, edges in dependencies.items():
            self.nodes.add(to_table)
            for edge in edges:
                self.nodes.add(edge.from_table)
                op_name = type(edge.op).__name__
                op_color = self.COLORS.get(type(edge.op), "gray")
                self.edges.append(
                    (
                        edge.from_table,
                        edge.to_table,
                        {"operation": op_name, "color": op_color},
                    )
                )

    def clear(self):
        self.nodes.clear()
        self.edges.clear()

class GraphVisualizer:
    """Class for visualizing dependency graphs."""

    def render(self, storage: GraphStorage, title: Optional[str] = None):
        if not storage.nodes:
            print("Graph is empty, no dependencies to display.")
            return
        G = nx.DiGraph()
        G.add_nodes_from(storage.nodes)
        G.add_edges_from(storage.edges)
        plt.figure(figsize=(10, 6))
        try:
            pos = nx.spring_layout(G)
            colors = nx.get_edge_attributes(G, "color").values()
            labels = nx.get_edge_attributes(G, "operation")
            nx.draw(
                G,
                pos,
                with_labels=True,
                node_color="lightblue",
                edge_color=colors,
                font_size=10,
                node_size=2000,
            )
            nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
            if title:
                plt.title(title)
            plt.show()
        except Exception as e:
            print(f"Error visualizing graph: {e}")
            print("You may need to run this in an environment that supports matplotlib display.")

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
        except Exception as e:
            print(f"Error parsing SQL: {e}")
            self.parsed = None
            self.dependencies = defaultdict(set)
            self.corrections.append(f"Error parsing SQL: {str(e)}")

    def _extract_dependencies(self) -> defaultdict:
        """Extracts dependencies between tables and operations including ETL, SELECT and JOIN queries."""
        dependencies = defaultdict(set)
        etl_types = (Insert, Update, Delete, Merge)
        try:
            for statement in self.parsed:
                # Special handling for JOIN operations in SELECT statements
                if isinstance(statement, Select):
                    # Process main SELECT operation
                    if hasattr(statement, "into") and statement.into is not None:
                        try:
                            to_table = self.get_table_name(statement.into)
                            from_table = self.get_first_from(statement) or f"input {self._get_input_id()}"
                            dependencies[to_table].add(Edge(from_table, to_table, statement))
                        except Exception as e:
                            print(f"Error extracting SELECT INTO dependencies: {e}")
                    else:
                        try:
                            from_table = self.get_first_from(statement) or f"input {self._get_input_id()}"
                            to_table = f"result {self._get_output_id()}"
                            dependencies[to_table].add(Edge(from_table, to_table, statement))
                        except Exception as e:
                            print(f"Error extracting SELECT dependency: {e}")

                    # Process JOIN operations in this SELECT
                    self._extract_join_dependencies(statement, dependencies)

                # Process each substatement
                for sub_statement in statement.walk():
                    if isinstance(sub_statement, etl_types):
                        if "this" not in sub_statement.args:
                            continue
                        try:
                            to_table = self.get_table_name(sub_statement)
                            from_table = self.get_first_from(sub_statement) or f"input {self._get_input_id()}"
                            dependencies[to_table].add(Edge(from_table, to_table, sub_statement))
                        except Exception as e:
                            print(f"Error extracting dependencies: {e}")
        except Exception as e:
            print(f"Error in dependency extraction: {e}")
        return dependencies

    def _extract_join_dependencies(self, select_statement, dependencies):
        """Extract JOIN dependencies from a SELECT statement."""
        try:
            if "from" not in select_statement.args:
                return

            # Извлекаем базовую (левую) таблицу из FROM
            from_clause = select_statement.args["from"]
            base_table = self.get_table_name(from_clause)
            print(f"Base table extracted: {base_table}")

            # Обработка списка join'ов, если он присутствует в атрибуте "joins"
            if "joins" in select_statement.args:
                for join_node in select_statement.args["joins"]:
                    join_table = self._extract_table_name(join_node.args.get("this"))
                    print(f"Join table extracted: {join_table}")
                    if base_table and join_table:
                        dependencies[base_table].add(Edge(join_table, base_table, join_node))
                        print(f"Added JOIN dependency: {join_table} -> {base_table}")

            # Если join'ы могут быть вложены в FROM (на всякий случай)
            for node in from_clause.walk():
                if node.__class__.__name__ == "Join":
                    join_table = self._extract_table_name(node.args.get("this"))
                    print(f"Join table extracted from walk: {join_table}")
                    if base_table and join_table:
                        dependencies[base_table].add(Edge(join_table, base_table, node))
                        print(f"Added JOIN dependency (walk): {join_table} -> {base_table}")

        except Exception as e:
            print(f"Error extracting JOIN dependencies: {e}")

    def _process_join(self, join_node, dependencies):
        """Process a single JOIN node and extract table dependencies."""
        try:
            left_expr = join_node.args.get("this")
            right_expr = join_node.args.get("expression")
            if left_expr is None or right_expr is None:
                print(f"Skipping JOIN due to missing expression: left_expr={left_expr}, right_expr={right_expr}")
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
                print(f"Could not extract both tables from JOIN: left={left_table}, right={right_table}")
        except Exception as e:
            print(f"Error processing JOIN: {e}")

    def _extract_table_name(self, expr):
        """Helper method to extract table name from an expression."""
        if expr is None:
            return None
        if isinstance(expr, Table):
            return expr.args["this"].args["this"]
        for table in expr.walk():
            if isinstance(table, Table):
                return table.args["this"].args["this"]
        return None

    def get_dependencies(self) -> defaultdict:
        return self.dependencies

    def get_corrections(self) -> List[str]:
        return self.corrections

    def get_first_from(self, stmt) -> Optional[str]:
        try:
            if "from" in stmt.args:
                return self.get_table_name(stmt.args["from"])
            if "expression" in stmt.args:
                return self.get_first_from(stmt.args["expression"])
        except Exception as e:
            print(f"Error in get_first_from: {e}")
        return None

    def get_table_name(self, parsed) -> str:
        try:
            counter = 0
            while "this" in parsed.args and counter < 100:
                counter += 1
                if isinstance(parsed, Table):
                    return parsed.args["this"].args["this"]
                parsed = parsed.args["this"]
            raise Exception("No table found")
        except Exception as e:
            print(f"Error in get_table_name: {e}")
            return f"unknown {self._get_unknown_id()}"

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

    def __init__(self, sql_ast_cls):
        self.sql_ast_cls = sql_ast_cls

    def parse_directory(
        self, directory: str, sep_parse: bool = False
    ) -> List[Tuple[defaultdict, List[str], str]]:
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
                if file.endswith(".sql"):
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

class GraphManager:
    """Class for managing graph building and visualization components."""

    def __init__(self):
        self.storage = GraphStorage()
        self.visualizer = GraphVisualizer()
        self.parser = DirectoryParser(SqlAst)

    def process_sql(self, sql_code: str) -> List[str]:
        ast = SqlAst(sql_code, sep_parse=True)
        self.storage.add_dependencies(ast.get_dependencies())
        return ast.get_corrections()

    def process_directory(self, directory_path: str) -> List[Tuple[str, List[str]]]:
        results = []
        parse_results = self.parser.parse_directory(directory_path)
        for dependencies, corrections, file_path in parse_results:
            self.storage.add_dependencies(dependencies)
            results.append((file_path, corrections))
        return results

    def visualize(self, title: Optional[str] = None):
        self.visualizer.render(self.storage, title)

def main():
    manager = GraphManager()
    print("SQL Syntax Corrector and Dependency Analyzer")
    print("-------------------------------------------")
    choice = input("Would you like to enter SQL code manually? (y/n): ")
    if choice.lower() == "y":
        print("Enter your SQL code (type 'END' on a new line to finish):")
        sql_lines = []
        while True:
            line = input()
            if line.upper() == "END":
                break
            sql_lines.append(line)
        sql_code = "\n".join(sql_lines)
        corrections = manager.process_sql(sql_code)
        if corrections:
            print("\nCorrections made:")
            for i, correction in enumerate(corrections, 1):
                print(f"{i}. {correction}")
        manager.visualize("Dependencies Graph")
    else:
        directory = input("Enter the directory path containing SQL files: ")
        choice = input("Display graphs separately for each file? (y/n): ")
        if choice.lower() == "y":
            parse_results = manager.parser.parse_directory(directory, sep_parse=True)
            for dependencies, corrections, file_path in parse_results:
                print(f"\nFile: {file_path}")
                if corrections:
                    print("Corrections made:")
                    for i, correction in enumerate(corrections, 1):
                        print(f"{i}. {correction}")
                temp_storage = GraphStorage()
                temp_storage.add_dependencies(dependencies)
                manager.visualizer.render(
                    temp_storage, f"Dependencies for {os.path.basename(file_path)}"
                )
        else:
            results = manager.process_directory(directory)
            for file_path, corrections in results:
                print(f"\nFile: {file_path}")
                if corrections:
                    print("Corrections made:")
                    for i, correction in enumerate(corrections, 1):
                        print(f"{i}. {correction}")
            manager.visualize("Full Dependencies Graph")

if __name__ == "__main__":
    main()
