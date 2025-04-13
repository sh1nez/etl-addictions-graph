from typing import Optional, Tuple, List
from base.parse import DirectoryParser, SqlAst
from base.storage import GraphStorage
from base.visualize import GraphVisualizer
from logger_config import logger


class GraphManager:
    """Class for managing graph building and visualization components."""

    def __init__(self):
        logger.debug("Инициализация GraphManager.")
        self.storage = GraphStorage()
        self.visualizer = GraphVisualizer()
        self.parser = DirectoryParser(SqlAst)

    def process_sql(self, sql_code: str) -> List[str]:
        logger.debug("Обработка SQL-кода вручную.")
        ast = SqlAst(sql_code, sep_parse=True)
        self.storage.add_dependencies(ast.get_dependencies())
        corrections = ast.get_corrections()
        if corrections:
            logger.info(f"Внесено исправлений в SQL: {len(corrections)}")
        else:
            logger.info("SQL не требовал исправлений.")
        return corrections

    def process_directory(self, directory_path: str) -> List[Tuple[str, List[str]]]:
        logger.debug(f"Обработка SQL-файлов в директории: {directory_path}")
        results = []
        parse_results = self.parser.parse_directory(directory_path)
        for dependencies, corrections, file_path in parse_results:
            logger.debug(f"Файл обработан: {file_path}")
            if corrections:
                logger.info(f"{file_path}: найдено исправлений — {len(corrections)}")
            self.storage.add_dependencies(dependencies)
            results.append((file_path, corrections))
        return results

    def visualize(self, title: Optional[str] = None):
        logger.debug(f"Визуализация графа с заголовком: {title}")
        self.visualizer.render(self.storage, title)
