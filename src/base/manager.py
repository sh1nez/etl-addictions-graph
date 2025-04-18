from typing import Optional, Tuple, List
from base.parse import DirectoryParser
from base.storage import GraphStorage
from base.visualize import GraphVisualizer
from base.parse import SqlAst


class GraphManager:
    """Class for managing graph building and visualization components."""

    def __init__(self, column_mode=False):
        self.storage = GraphStorage(column_mode=column_mode)
        self.visualizer = GraphVisualizer() if not column_mode else None
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
