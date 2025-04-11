import re
import os
from collections import defaultdict
from typing import Optional, List
from base.storage import GraphStorage
from base.parse import SqlAst
from base.visualize import GraphVisualizer


class Procedure:  # TODO mode it to different files.
    def __init__(self, name: str, code: str) -> None:
        self.name = name
        self.code = code

    def get_graph_name(self) -> str:
        return f"\\${self.name}\\$"

    @staticmethod
    def __extract_procedure_code(sql: str) -> str:
        sql = sql.split("BEGIN", 1)[1]
        sql = sql.rsplit("END", 1)[0]
        sql = sql.strip()

        return sql

    @staticmethod
    def extract_procedures(sql_code: str) -> List["Procedure"]:
        found = re.findall(
            r"PROCEDURE\s+[\"\'?]?(\w+)[\"\'?]?\s*\(.*?\)\s*[^$]+?\$\$(.*?)\$\$",
            sql_code,
            re.DOTALL,
        )
        if not found:
            return []

        procedures = []

        for i in found:
            procedures.append(Procedure(i[0], Procedure.__extract_procedure_code(i[1])))

        return procedures

    def __repr__(self) -> str:
        return f"{self.name}: '{self.code}'"


class BufferTable:
    def __init__(self, name) -> None:
        self.name = name
        self.write_procedures = set()  # procedures that write into the table
        self.read_procedures = set()  # procedures that read from the table

    @staticmethod
    def find_buffer_tables(
        procedures: List[Procedure], known_buff_tables: List["BufferTable"]
    ) -> List["BufferTable"]:
        buff_tables = dict()
        for table in known_buff_tables:
            buff_tables[table.name] = table

        for proc in procedures:
            ast = SqlAst(proc.code)

            for to_table, from_tables in ast.get_dependencies().items():
                if to_table not in buff_tables:
                    buff_tables[to_table] = BufferTable(to_table)

                for from_table in from_tables:
                    if from_table not in buff_tables:
                        buff_tables[from_table] = BufferTable(from_table)

                    buff_tables[to_table].write_procedures.add(proc)
                    buff_tables[from_table].read_procedures.add(proc)

        real_buff_tables = []
        for _, table in buff_tables.items():
            if len(table.write_procedures) > 0 and len(table.read_procedures) > 0:
                real_buff_tables.append(table)

        return real_buff_tables

    def __repr__(self) -> str:
        return f"{self.name}:\nreaders: {(self.read_procedures)}\nwriters: {self.write_procedures}"


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


class BufferTableGraphManager:
    """Class for managing graph building and visualization components."""

    def __init__(self):
        self.storage = BufferTableGraphStorage()
        self.visualizer = GraphVisualizer()
        self.parser = BufferTableDirectoryParser(SqlAst)

    def process_sql(self, sql_code: str) -> List[str]:
        ast = SqlAst(sql_code)
        return ast.get_corrections()

    def process_directory(self, directory_path: str) -> List[BufferTable]:
        tables = self.parser.parse_directory(directory_path)
        self.storage.set_buff_tables(tables)
        return tables

    def visualize(self, title: Optional[str] = None):
        self.visualizer.render(self.storage, title)


def draw_buffer_directory(directory):
    manager = BufferTableGraphManager()
    manager.process_directory(directory)
    manager.visualize("Full Dependencies Graph")


if __name__ == "__main__":
    directory = input("Enter the directory path containing SQL files: ")
    draw_buffer_directory(directory)
