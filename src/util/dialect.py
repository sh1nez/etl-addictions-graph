from sqlglot import parse


def safe_parse(sql):
    """Пытается распарсить SQL-код, автоматически определяя диалект (PostgreSQL/Oracle).

    Последовательно проверяет поддержку диалектов. Если парсинг для диалекта завершается успешно,
    возвращает результат и название диалекта. В противном случае пробует следующий диалект.

    Args:
        sql (str): SQL-код для анализа. Должен быть синтаксически корректным для одного из поддерживаемых диалектов.

    Returns:
        tuple: Кортеж из двух элементов:
            - Список AST-узлов (sqlglot.expressions.Expression) | None: Результат парсинга.
            - str: Название диалекта ("postgres", "oracle") или "Unknown" при неудаче.

    Examples:
        >>> ast, dialect = safe_parse("SELECT * FROM users")
        >>> print(dialect)  # "postgres" (если парсинг успешен)

        >>> ast, dialect = safe_parse("INVALID SQL")
        >>> print(ast, dialect)  # None, "Unknown"
    """

    try:
        return parse(sql, dialect="postgres"), "postgres"
    except:  # catch error
        pass

    try:
        return parse(sql, dialect="oracle"), "oracle"
    except:
        pass

    return None, "Unknown"
