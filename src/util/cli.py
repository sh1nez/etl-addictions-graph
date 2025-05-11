import argparse


def parse_arguments():
    """Парсит и валидирует аргументы командной строки для инструмента анализа SQL.

    Конфигурирует парсер аргументов с:
        - Обязательным выбором режима работы
        - Взаимоисключающими источниками данных (директория или сырой SQL-код)
        - Опциями настройки вывода

    Возвращает:
        argparse.Namespace: Объект с аргументами командной строки.

            Ожидаемые атрибуты:
                - mode (str): Выбранный режим работы
                - directory_path (str|None): Путь к директории с SQL-файлами
                - sql_code (str|None): Строка с SQL-кодом
                - separate_graph (str): Режим отображения графиков
                - operators (str|None): Фильтр SQL-операторов

    Примеры использования:
        >>> python cli.py --mode functional --directory_path ./sql --separate_graph true
        >>> python cli.py --mode field --sql_code "SELECT * FROM table" --operators "SELECT,JOIN"

    Примечания:
        - Режимы работы:
            * table: Анализ на уровне таблиц
            * field: Анализ связей между колонками
            * functional: Полное построение зависимостей
        - Требования к директории:
            * Должна содержать .sql файлы
            * Минимум 1 валидный SQL-файл
        - SQL-код должен быть синтаксически корректным
    """
    parser = argparse.ArgumentParser(
        description="SQL Syntax Corrector and Dependency Analyzer"
    )

    parser.add_argument(
        "--mode",
        choices=["table", "field", "functional"],
        required=True,
        help="Program operation mode: table, field or functional",
    )

    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--directory_path",
        type=str,
        help="Path to the directory containing SQL files for processing",
    )
    source_group.add_argument(
        "--sql_code", type=str, help="SQL code for direct processing"
    )

    parser.add_argument(
        "--separate_graph",
        choices=["true", "false"],
        default="false",
        help="Display graphs separately for each file",
    )
    parser.add_argument(
        "--operators",
        type=str,
        help="Comma-separated list of SQL operators to display (e.g., 'SELECT,INSERT,UPDATE'). "
        "If not specified, all operators are shown.",
    )
    return parser.parse_args()
