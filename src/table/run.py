from base.run import process_args as base_process_args
from logger_config import logger


def process_args(args):
    """Обрабатывает аргументы командной строки для режима работы с таблицами.

    Является обёрткой над базовой функцией `base_process_args`, добавляя специфичную для таблиц логику:
        - Фильтрация операций по типам (INSERT, UPDATE и т.д.)
        - Настройка визуализации зависимостей между таблицами

    Args:
        args: Объект с аргументами командной строки.

            Ожидаемые атрибуты:
                - sql_code (str): SQL-запрос для анализа
                - directory_path (str): Путь к директории с SQL-файлами
                - operators (List[str]): Фильтр операторов (например, ["SELECT", "INSERT"])
                - separate_graph (bool): Флаг раздельной визуализации файлов

    Returns:
        None

    Example:
        >>> # Запуск из командной строки
        >>> $ python run.py --sql-code "SELECT * FROM users" --operators "SELECT"
    """
    base_process_args(args)
