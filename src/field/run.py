import os
from base.manager import GraphManager
from field.storage import ColumnStorage
from logger_config import logger


def process_args(args):
    """Обрабатывает аргументы командной строки для анализа зависимостей между колонками.

    Основные сценарии:
        - Обработка SQL-кода из командной строки
        - Обработка SQL-файлов в директории:
            - Создание отдельных графов для каждого файла
            - Построение единого графа для всех файлов

    Args:
        args: Объект с аргументами командной строки.

            Ожидаемые атрибуты:
                - sql_code (str): SQL-запрос для анализа
                - directory_path (str): Путь к директории с SQL-файлами
                - operators (List[str]): Фильтр операторов (например, ["INSERT", "SELECT"])
                - separate_graph (str): "True"/"False" - раздельная визуализация файлов

    Returns:
        None

    Raises:
        FileNotFoundError: Если директория не существует
        ValueError: Если не указаны sql_code или directory_path

    Example:
        >>> # Анализ SQL-кода
        >>> args.sql_code = "INSERT INTO users (id) VALUES (1)"
        >>> process_args(args)

        >>> # Анализ директории с раздельными графами
        >>> args.directory_path = "./sql_scripts"
        >>> args.separate_graph = "True"
        >>> process_args(args)

    Notes:
        - Логирует корректировки SQL-кода через logger.info
        - Использует ColumnStorage для хранения зависимостей колонок
    """

    manager = GraphManager(column_mode=True, operators=args.operators)
    separate = args.separate_graph.lower() == "true"
    if args.sql_code:
        sql_code = args.sql_code
        corrections = manager.process_sql(sql_code)
        if corrections:
            logger.info("\nCorrections made:")
            for i, correction in enumerate(corrections, 1):
                logger.info(f"{i}. {correction}")
        manager.visualize("Dependencies Graph", mode=args.viz_mode)
        return
    else:
        if separate:
            parse_results = manager.parser.parse_directory(
                args.directory_path, sep_parse=True
            )
            for dependencies, corrections, file_path in parse_results:
                logger.debug(f"\nFile: {file_path}")
                if corrections:
                    logger.info("Corrections made:")
                    for i, correction in enumerate(corrections, 1):
                        logger.info(f"{i}. {correction}")
                temp_storage = ColumnStorage()
                temp_storage.add_dependencies(dependencies)
                manager.visualizer.render(
                    temp_storage,
                    f"Dependencies for {os.path.basename(file_path)}",
                    mode=args.viz_mode,
                )
        else:
            results = manager.process_directory(args.directory_path)
            for file_path, corrections in results:
                logger.debug(f"\nFile: {file_path}")
                if corrections:
                    logger.info("Corrections made:")
                    for i, correction in enumerate(corrections, 1):
                        logger.info(f"{i}. {correction}")
            manager.visualize("Full Dependencies Graph", mode=args.viz_mode)
            return
