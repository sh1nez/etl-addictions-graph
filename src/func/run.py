from func.buff_tables import run


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
    print("Functional mode started with arguments:")
    print(
        f"  Directory: {args.directory_path}"
        if args.directory_path
        else f"  SQL code: {args.sql_code}"
    )
    print(f"  Separate graphs: {args.separate_graph}")
    run(
        directory=args.directory_path,
        sql_code=args.sql_code,
        separate_graph=args.separate_graph,
    )
