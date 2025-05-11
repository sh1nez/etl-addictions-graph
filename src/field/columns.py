from sqlglot.expressions import (
    Insert,
    Update,
    Delete,
    Merge,
    Select,
    Expression,
    Column,
    Values,
    Alias,
)
from itertools import zip_longest
from typing import Optional, List, Tuple
from logger_config import logger
import traceback


from functools import wraps


def print_ifnt_str(func):
    """Декоратор для логирования входных и выходных данных функций (только для отладки).

    Args:
        func: Оборачиваемая функция

    Returns:
        Обёрнутая функция с логированием.
    """

    @wraps(func)  # Сохраняет метаданные исходной функции
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if not isinstance(result, str):
            logger.debug(f"INPUT: {args[0]}")
            logger.debug(f"OUTPUT: {result}")
        return result

    return wrapper


@print_ifnt_str
def parse_columns(op: Expression) -> Tuple[Optional[List[str]], Optional[List[str]]]:
    #: :meta member:

    """Анализирует SQL-операцию и возвращает информацию о колонках.

    Args:
        op (Expression): SQL-выражение для анализа.

    Returns:
        Tuple:
            - List[str]: Колонки в формате ["источник:цель"]
            - List[str]: Колонки из WHERE-условия (если есть)

    Example:
        >>> expr = sqlglot.parse_one("INSERT INTO table (a, b) VALUES (1, 2)")
        >>> parse_columns(expr)
        (['a:input', 'b:input'], None)
    """

    try:
        if isinstance(op, Insert):
            return _parse_insert(op)
        elif isinstance(op, Update):
            return _parse_update(op)
        elif isinstance(op, Delete):
            return _parse_delete(op)
        elif isinstance(op, Merge):
            return _parse_merge(op)
        elif isinstance(op, Select):
            return _parse_select(op)
        else:
            return None
    except Exception as e:
        logger.error(f"Error parsing column:{e}\n{traceback.format_exc(e)}")
        return (None, None)


def _this_deep_parse(op, prior=None, typesearch=str, star_except=True) -> str:
    """Рекурсивно извлекает имя колонки/таблицы из выражения.

    Args:
        op (Expression): Выражение для анализа.
        prior (str, optional): Приоритетный атрибут для поиска.
        typesearch (type): Ожидаемый тип результата.
        star_except (bool): Обрабатывать ли звездочку (*) как специальный случай.

    Returns:
        str: Извлеченное имя или "unknown" при ошибке.
    """
    if isinstance(op, typesearch):
        return op
    if star_except and isinstance(op, Expression) and op.is_star:
        return "*"
    try:
        counter = 0
        while ("this" in op.args or (prior and prior in op.args)) and counter < 100:
            if prior and prior in op.args:
                op = op.args[prior]
            else:
                op = op.args["this"]
            if isinstance(op, typesearch):
                return op
            if star_except and isinstance(op, Expression) and op.is_star:
                return "*"
            counter += 1
        raise Exception("No type found")
    except Exception as e:
        logger.warning(f"Couldn't  parse column: {e}")
        return f"unknown"


def _where_column_names(op: Expression) -> list[str]:
    """Извлекает имена колонок из WHERE-условия.

    Args:
        op (Expression): WHERE-выражение.

    Returns:
        List[str]: Список колонок. Пример: ["user_id", "created_at"]
    """
    col_names = []
    found_columns = False
    for i in Expression.bfs(op.args["where"]):
        if "this" in i.args:
            this = i.args["this"]
        elif found_columns:
            break
        else:
            continue
        if isinstance(this, Column):
            found_columns = True
            col_names.append(_this_deep_parse(this))
        elif found_columns:
            break
    return col_names


def _parse_insert(op: Insert):
    """Обрабатывает INSERT-операцию.

    Returns:
        Tuple:
            - List[str]: Колонки в формате ["таблица:значение"]
            - None (WHERE отсутствует в INSERT)
    """
    insert_cols = op.args["this"].args.get("expressions", ["*"])
    incoming_cols = []
    if isinstance(op.args["expression"], Values):
        incoming_cols = ["input"] * len(insert_cols)
    else:
        incoming_cols = [
            _this_deep_parse(i) for i in op.args["expression"].args["expressions"]
        ]
    return (
        [
            _this_deep_parse(i) + ":" + j
            for i, j in zip_longest(insert_cols, incoming_cols, fillvalue="*")
        ],
        None,
    )


def _parse_update(op: Update):
    """Обрабатывает UPDATE-операцию.

    Returns:
        Tuple:
            - List[str]: Колонки для обновления
            - List[str]: Колонки из WHERE-условия
    """
    update_cols = op.args.get("expressions", [])
    where = _where_column_names(op) if "where" in op.args and op.args["where"] else []
    if len(update_cols) != 0:
        return (
            [
                _this_deep_parse(i) + ":" + _this_deep_parse(i.args["expression"])
                for i in update_cols
            ],
            where,
        )
    raise Exception("No update columns")


def _parse_delete(op: Delete):
    """Обрабатывает DELETE-операцию.

    Returns:
        Tuple:
            - None (нет изменяемых колонок)
            - List[str]: Колонки из WHERE-условия
    """
    if op.args["where"] is None:
        return []
    return (None, _where_column_names(op))


def _parse_merge(op: Merge):
    """Обрабатывает MERGE-операцию.

    Returns:
        Tuple:
            - List[str]: Колонки для слияния
            - None
    """
    if "on" in op.args and op.args["on"]:
        on = op.args["on"]
        return (
            [f"{_this_deep_parse(on)}:{_this_deep_parse(on, prior='expression')}"],
            None,
        )
    return ([], None)


def _select_columns(op):
    """Извлекает имена колонок из SELECT-выражения.

    Обрабатывает различные варианты выражений:
    - Прямые ссылки на колонки (Column)
    - Алиасы (Alias)
    - Сложные выражения (например, функции агрегации)

    Args:
        op (Expression): Выражение из SELECT-клаузы

    Returns:
        str: Название колонки или строковое представление выражения

    Example:
        >>> expr = sqlglot.parse_one("SELECT COUNT(id) AS total FROM users")
        >>> _select_columns(expr.args["expressions"][0])
        'COUNT(id)'
    """
    if hasattr(op, "args") and "this" in op.args:
        if (
            hasattr(op.args["this"], "args")
            and "this" in op.args["this"].args
            and isinstance(op.args["this"].args["this"], str)
        ):
            return op.args["this"].args["this"]
        else:
            return str(op.args["this"])
    if isinstance(op, Alias):
        return str(op.args["this"])
    return str(op)


def _parse_select(op: Select):
    """Обрабатывает SELECT-операцию.

    Returns:
        Tuple:
            - List[str]: Выбираемые колонки
            - List[str]: Колонки из WHERE-условия
    """
    where = []
    where = _where_column_names(op) if "where" in op.args else []
    select_cols = op.args["expressions"]
    if select_cols[0].is_star:
        return (["*"], where)
    return ([_select_columns(i) for i in select_cols], where)
