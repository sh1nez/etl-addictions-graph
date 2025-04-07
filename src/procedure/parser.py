import os
from collections import defaultdict
from ..base.parse import GraphStorage
from .units import BufferTable, Procedure
from typing import List


class BufferTableDirectoryParser:
    """Class for processing SQL files with buffer tables in a directory."""

    def __init__(self, sql_ast_cls):
        self.sql_ast_cls = sql_ast_cls

    def parse_directory(self, directory: str) -> List[BufferTable]:
        results = []  # maybe hashmap better??
        known_buff_tables = []
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
                            procs = Procedure.extract_procedures(sql_code)
                            known_buff_tables = BufferTable.find_buffer_tables(
                                procs, known_buff_tables
                            )
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")
                        results.append(
                            (defaultdict(set), [f"Error: {str(e)}"], file_path)
                        )
        return known_buff_tables


class BufferTableGraphStorage(GraphStorage):
    """Class for storing dependency graph data for buffer tables."""

    def __init__(self):
        self.buff_tables = []
        self.nodes = set()
        self.edges = []

    def set_buff_tables(self, buff_tables):
        self.buff_tables = buff_tables
        self.nodes = self.get_buf_nodes()
        self.edges = self.get_buf_edges()

    def get_buf_nodes(self):
        nodes = set()

        for table in self.buff_tables:
            nodes.add(table.name)
            for proc in table.write_procedures:
                nodes.add(proc.get_graph_name())

            for proc in table.read_procedures:
                nodes.add(proc.get_graph_name())
        return nodes

    def get_buf_edges(self):
        edges = []

        for table in self.buff_tables:
            for proc in table.write_procedures:
                edges.append((proc.get_graph_name(), table.name))

            for proc in table.read_procedures:
                edges.append((table.name, proc.get_graph_name()))

        return edges

    def clear(self):
        self.nodes.clear()
        self.edges.clear()
