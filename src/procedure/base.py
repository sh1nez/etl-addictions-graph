from .parser import BufferTableGraphStorage, BufferTableDirectoryParser
from ..base.visualize import GraphVisualizer
from ..base.parse import SqlAst
from typing import List, Optional
from .unit import BufferTable


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
