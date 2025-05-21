from typing import Optional, Tuple, List
from base.parse import DirectoryParser
from base.storage import GraphStorage
from base.visualize import GraphVisualizer
from field.storage import ColumnStorage
from field.visualize import ColumnVisualizer
from base.parse import SqlAst
from logger_config import logger


class GraphManager:
    """Управляет процессом парсинга SQL, хранением зависимостей и визуализацией графов.

    Поддерживает два режима работы:
        - Режим таблиц (по умолчанию): использует GraphStorage и GraphVisualizer.
        - Режим колонок (column_mode=True): использует ColumnStorage и ColumnVisualizer.

    Attributes:
        storage (Union[GraphStorage, ColumnStorage]): Хранилище зависимостей.
        visualizer (Union[GraphVisualizer, ColumnVisualizer]): Генератор графов.
        parser (DirectoryParser): Парсер для обработки директорий с SQL-файлами."""

    def __init__(self, column_mode=False, operators=None, ignore_io=False):
        """Инициализирует компоненты на основе выбранного режима.

        Args:
            column_mode (bool): Если True, активирует режим работы с колонками. По умолчанию False.
            operators (Optional[List[str]]): Фильтр для операторов (например, ['JOIN', 'WHERE']).
        """
        self.ignore_io = ignore_io
        self.storage = (
            GraphStorage(ignore_io=self.ignore_io)
            if not column_mode
            else ColumnStorage(ignore_io=self.ignore_io)
        )
        self.visualizer = GraphVisualizer() if not column_mode else ColumnVisualizer()
        self.parser = DirectoryParser(SqlAst, self.ignore_io)
        if operators:
            self.storage.set_operator_filter(operators)
        logger.debug("GraphManager initialized")

    def process_sql(self, sql_code: str) -> List[str]:
        """Парсит SQL-код, извлекает зависимости и возвращает корректировки.

        Args:
            sql_code (str): SQL-запрос для анализа.

        Returns:
            List[str]: Список предупреждений или предложений по исправлению.

        Example:
            >>> manager.process_sql("SELECT * FROM users")
            ['WARNING: Missing schema prefix in table "users"']
        """

        ast = SqlAst(sql_code, sep_parse=True, ignore_io=self.ignore_io)
        self.storage.add_dependencies(ast.get_dependencies())
        logger.info(f"Processed SQL code: {len(ast.get_corrections())} corrections")
        return ast.get_corrections()

    def process_directory(self, directory_path: str) -> List[Tuple[str, List[str]]]:
        """Обрабатывает все SQL-файлы в указанной директории.

        Args:
            directory_path (str): Путь к директории с SQL-файлами.

        Returns:
            List[Tuple[str, List[str]]]:
                Список кортежей вида (путь_к_файлу, корректировки_для_файла).

        Example:
            >>> manager.process_directory("/data/sql")
            [("/data/sql/query1.sql", ['WARNING: Ambiguous column "id"'])]
        """
        results = []
        parse_results = self.parser.parse_directory(directory_path)
        for dependencies, corrections, file_path in parse_results:
            self.storage.add_dependencies(dependencies)
            results.append((file_path, corrections))
            logger.debug(f"Processed file: {file_path}")
        logger.info(f"Processed directory: {len(results)} files")
        return results

    def visualize(
        self, title: Optional[str] = None, storage: Optional[GraphStorage] = None
    ):
        """Генерирует графическое представление зависимостей.

        Args:
            title (Optional[str]): Заголовок графа. Если не указан, используется значение по умолчанию.

        Example:
            >>> manager.visualize(title="Data Pipeline")
        """
        if storage is None:
            storage = self.storage
        try:
            self.visualizer.render(storage, title)
        except Exception as e:
            logger.error(
                f"Error visualizing graph: {e}\nYou may need to run this in an environment that supports matplotlib display."
            )
        else:
            logger.info("Visualization completed successfully")
