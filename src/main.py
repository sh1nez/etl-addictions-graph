import os
import networkx as nx
from collections import defaultdict
from typing import Optional, Tuple, List, Union
from matplotlib import pyplot as plt
from sqlglot import parse, transpile
from sqlglot.expressions import Update, Insert, Table, Delete, Merge, Select, DML

HAS_SQLGLOT = True  # TODO remove it


class Edge:
    def __init__(self, from_table: Table, op: Union[DML, Select]):
        self.from_table = from_table
        self.op = op  # operation


class GraphStorage:
    """Class for storing dependency graph data."""

    COLORS = {
        Insert: "red",
        Update: "green",
        Delete: "blue",
        Merge: "yellow",
        Select: "purple",
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
                        to_table,
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
            # * Есть разные методы layout, в теории потом можно будет использовать nx.multipartite_layout(),
            # * который послойно будет отображать ноды, т.е. можно отображать что-то наподобии этапов
            # * pos = nx.multipartite_layout(G, subset_key="layer")
            # * или можно использовать тот же spring_layout, но с параметрами для большего расстояния между нодами:
            # * n = G.number_of_nodes()
            # * nx.spring_layout(G, k=1 / (n**0.0625), iterations=100, scale=2)
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
                plt.title(title)  # ! window still being named as Figure 1
                # plt.gcf().canvas.manager.set_window_title(title) # was working (at least on Windows)
            plt.show()
        except Exception as e:
            print(f"Error visualizing graph: {e}")
            print(
                "You may need to run this in an environment that supports matplotlib display."
            )


class SqlAst:
    """Class for building AST of SQL queries."""

    _input_id = 0
    _output_id = 0
    _unknown_id = 0

    def __init__(self, sql_code: str, sep_parse: bool = False):
        # self.corrector = EnhancedSQLCorrector()
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
        # self.corrected_sql, self.corrections = self.corrector.correct(sql_code)
        # self.sql_code = self.corrected_sql
        if not HAS_SQLGLOT:
            self.parsed = None
            self.dependencies = defaultdict(set)
            self.corrections.append(
                "sqlglot not installed - dependency extraction skipped"
            )
            return
        try:
            self.parsed = parse(self.corrected_sql)
            self.dependencies = self._extract_dependencies()
        except Exception as e:
            print(f"Error parsing SQL: {e}")
            self.parsed = None
            self.dependencies = defaultdict(set)
            self.corrections.append(f"Error parsing SQL: {str(e)}")

    def _extract_dependencies(self) -> defaultdict:
        """Extracts dependencies between tables and operations including ETL and SELECT queries."""
        dependencies = defaultdict(set)
        if not self.parsed or not HAS_SQLGLOT:
            return dependencies
        etl_types = (Insert, Update, Delete, Merge)
        try:
            for statement in self.parsed:
                for sub_statement in statement.walk():
                    if isinstance(sub_statement, etl_types):
                        if "this" not in sub_statement.args:
                            continue
                        try:
                            to_table = self.get_table_name(sub_statement)
                            from_table = (
                                self.get_first_from(sub_statement)
                                or f"input {self._get_input_id()}"
                            )
                            dependencies[to_table].add(Edge(from_table, sub_statement))
                        except Exception as e:
                            print(f"Error extracting dependencies: {e}")
                    elif isinstance(sub_statement, Select):
                        # Если есть конструкция INTO, обрабатываем как SELECT INTO
                        if (
                            hasattr(sub_statement, "into")
                            and sub_statement.into is not None
                        ):
                            try:
                                to_table = self.get_table_name(sub_statement.into)
                                from_table = (
                                    self.get_first_from(sub_statement)
                                    or f"input {self._get_input_id()}"
                                )
                                dependencies[to_table].add(
                                    Edge(from_table, sub_statement)
                                )
                            except Exception as e:
                                print(f"Error extracting SELECT INTO dependencies: {e}")
                        else:
                            # Для обычного SELECT, считаем целевым псевдо-таблицу "result"
                            try:
                                from_table = (
                                    self.get_first_from(sub_statement)
                                    or f"input {self._get_input_id()}"
                                )
                                to_table = f"result {self._get_output_id()}"
                                dependencies[to_table].add(
                                    Edge(from_table, sub_statement)
                                )
                            except Exception as e:
                                print(f"Error extracting SELECT dependency: {e}")
        except Exception as e:
            print(f"Error in dependency extraction: {e}")
        return dependencies

    def get_dependencies(self) -> defaultdict:
        return self.dependencies

    def get_corrections(self) -> List[str]:
        return self.corrections

    def get_first_from(self, stmt) -> Optional[str]:
        if not HAS_SQLGLOT:
            return None
        try:
            if "from" in stmt.args:
                return self.get_table_name(stmt.args["from"])
            if "expression" in stmt.args:
                return self.get_first_from(stmt.args["expression"])
        except Exception as e:
            print(f"Error in get_first_from: {e}")
        return None

    def get_table_name(self, parsed) -> str:
        if not HAS_SQLGLOT:
            return f"unknown {self._get_unknown_id()}"
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
        results = []  # maybe hashmap better??
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
                    try:  # TODO with заменяет трай кетч блок, насколько я знаю, заменить
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
        results = []  # maybe hashmap better??
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
