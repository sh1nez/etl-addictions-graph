from typing import Optional, Tuple, List
from base.parse import DirectoryParser
from base.storage import GraphStorage
from base.visualize import GraphVisualizer
from base.parse import SqlAst
from logger_config import logger  # Добавлен импорт логгера


class GraphManager:
    """Class for managing graph building and visualization components."""

    def __init__(self, column_mode=False):
        self.storage = GraphStorage()
        self.visualizer = GraphVisualizer()
        self.parser = DirectoryParser(SqlAst)
        logger.debug("GraphManager initialized")

    def process_sql(self, sql_code: str) -> List[str]:
        ast = SqlAst(sql_code, sep_parse=True)
        self.storage.add_dependencies(ast.get_dependencies())
        logger.info(f"Processed SQL code: {len(ast.get_corrections())} corrections")
        return ast.get_corrections()

    def process_directory(self, directory_path: str) -> List[Tuple[str, List[str]]]:
        results = []
        parse_results = self.parser.parse_directory(directory_path)
        for dependencies, corrections, file_path in parse_results:
            self.storage.add_dependencies(dependencies)
            results.append((file_path, corrections))
            logger.debug(f"Processed file: {file_path}")
        logger.info(f"Processed directory: {len(results)} files")
        return results

    def visualize(self, title: Optional[str] = None):
        self.visualizer.render(self.storage, title)
        logger.info("Visualization completed successfully")
