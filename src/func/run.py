import os
from func.buff_tables import NewBuffGraphManager, BufferTableGraphStorage
from logger_config import logger


def process_args(args):
    """Обрабатывает аргументы командной строки и инициализирует выполнение функционального режима.

    Парсит переданные аргументы командной строки, отображает конфигурационные параметры
    и запускает основную логику обработки из модуля buff_tables.

    Args:
        args (argparse.Namespace): Объект с аргументами командной строки.

            Ожидаемые атрибуты:
                - directory_path (str|None): Путь к входной директории (взаимоисключающий с sql_code)
                - sql_code (str|None): Сырой SQL-код для обработки (взаимоисключающий с directory_path)
                - separate_graph (bool): Флаг разделения графиков в выводе

    Выводит:
        Сообщение инициализации с конфигурацией переданных аргументов.

    Вызывает:
        func.buff_tables.run() для выполнения основной логики.
    """
    manager = NewBuffGraphManager()
    separate = args.separate_graph.lower() == "true"
    if args.sql_code:
        sql_code = args.sql_code
        corrections = manager.process_sql(sql_code)
        if corrections:
            print("\nCorrections made:")
            for i, correction in enumerate(corrections, 1):
                print(f"{i}. {correction}")
        manager.visualize("Dependencies Graph")
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
                temp_storage = BufferTableGraphStorage()
                temp_storage.add_dependencies(dependencies)
                manager.visualizer.render(
                    temp_storage,
                    f"Dependencies for {os.path.basename(file_path)}",
                )
        else:
            results = manager.process_directory(args.directory_path)
            for file_path, corrections in results:
                logger.debug(f"\nFile: {file_path}")
                if corrections:
                    logger.info("Corrections made:")
                    for i, correction in enumerate(corrections, 1):
                        logger.info(f"{i}. {correction}")
            manager.visualize("Full Dependencies Graph")
            return
