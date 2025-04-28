from typing import Optional, Tuple, List
from base.parse import DirectoryParser
from base.storage import GraphStorage
from base.visualize import GraphVisualizer
from base.parse import SqlAst
from logger_config import logger  # Добавлен импорт логгера


class GraphManager:
    """Class for managing graph building and visualization components."""

    def __init__(self, column_mode=False):
        try:
            self.storage = GraphStorage()
            self.visualizer = GraphVisualizer()
            self.parser = DirectoryParser(SqlAst)
            logger.debug("GraphManager initialized")  # Логирование инициализации
        except Exception as e:
            logger.error(f"Manager initialization failed: {e}")
            raise

    def process_sql(self, sql_code: str) -> List[str]:
        try:
            ast = SqlAst(sql_code, sep_parse=True)
            self.storage.add_dependencies(ast.get_dependencies())
            logger.info(f"Processed SQL code: {len(ast.get_corrections())} corrections")
            return ast.get_corrections()
        except Exception as e:
            logger.error(f"SQL processing error: {e}")
            return [f"Critical error: {str(e)}"]

    def process_directory(self, directory_path: str) -> List[Tuple[str, List[str]]]:
        results = []
        try:
            parse_results = self.parser.parse_directory(directory_path)
            for dependencies, corrections, file_path in parse_results:
                self.storage.add_dependencies(dependencies)
                results.append((file_path, corrections))
                logger.debug(f"Processed file: {file_path}")  # Детальное логирование
            logger.info(f"Processed directory: {len(results)} files")
        except Exception as e:
            logger.error(f"Directory processing failed: {e}")
        return results

    def visualize(self, title: Optional[str] = None):
        try:
            self.visualizer.render(self.storage, title)
            logger.info("Visualization completed successfully")  # Логирование успеха
        except Exception as e:
            logger.error(f"Visualization failed: {e}")  # Логирование ошибок
