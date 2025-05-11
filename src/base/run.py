import os
from logging import Logger
from typing import List, Tuple
from base.manager import GraphManager
from base.storage import GraphStorage
from logger_config import logger  # Добавляем импорт логгера


def process_args(args):
    """Обрабатывает аргументы командной строки и запускает анализ SQL-зависимостей.

    Основные сценарии:
        1. Обработка SQL-кода из командной строки
        2. Обработка SQL-файлов в директории (единый граф или раздельные)

    Args:
        args:Объект с аргументами командной строки.

            Ожидаемые атрибуты:
                - sql_code (str): SQL-запрос для анализа
                - directory_path (str): Путь к директории с SQL-файлами
                - operators (List[str]): Фильтр операторов для зависимостей
                - separate_graph (str): "True"/"False" - раздельная визуализация файлов

    Returns:
        None

    Example:
        >>> #Обработка SQL-запроса
        >>> args.sql_code = "SELECT * FROM table"
        >>> process_args(args)

        >>> #Обработка директории с объединенным графом
        >>> args.directory_path = "./sql_scripts"
        >>> args.separate_graph = "False"
        >>> process_args(args)

    Raises:
        FileNotFoundError: Если передан несуществующий путь к директории
        ValueError: Если не указаны sql_code или directory_path

    Логирование:
        - INFO: Выводит список корректировок SQL
        - DEBUG: Детали обработки файлов
    """
    manager = GraphManager(operators=args.operators)
    separate = args.separate_graph.lower() == "true"

    if args.sql_code:
        sql_code = args.sql_code
        corrections = manager.process_sql(sql_code)
        if corrections:
            logger.info("\nCorrections made:")
            for i, correction in enumerate(corrections, 1):
                logger.info(f"{i}. {correction}")
        manager.visualize("Dependencies Graph")
        return

    if args.directory_path:
        directory = args.directory_path
        if separate:
            parse_results = manager.parser.parse_directory(directory, sep_parse=True)
            for dependencies, corrections, file_path in parse_results:
                logger.debug(f"\nFile: {file_path}")
                if corrections:
                    logger.info("Corrections made:")
                    for i, correction in enumerate(corrections, 1):
                        logger.info(f"{i}. {correction}")
                temp_storage = GraphStorage()
                temp_storage.add_dependencies(dependencies)
                manager.visualize(
                    f"Dependencies for {os.path.basename(file_path)}", temp_storage
                )
        else:
            results = manager.process_directory(directory)
            for file_path, corrections in results:
                logger.debug(f"\nFile: {file_path}")
                if corrections:
                    logger.info("Corrections made:")
                    for i, correction in enumerate(corrections, 1):
                        logger.info(f"{i}. {correction}")
            manager.visualize("Full Dependencies Graph")
