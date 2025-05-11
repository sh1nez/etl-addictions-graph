# src.util package

## Submodules

## cli module

### util.cli.parse_arguments()

Парсит и валидирует аргументы командной строки для инструмента анализа SQL.

Конфигурирует парсер аргументов с:
: - Обязательным выбором режима работы
: - Взаимоисключающими источниками данных (директория или сырой SQL-код)
: - Опциями настройки вывода

Возвращает:
: argparse.Namespace: Объект с аргументами командной строки.

  > Ожидаемые атрибуты:
  >   - mode (str): Выбранный режим работы
  >   - directory_path (str|None): Путь к директории с SQL-файлами
  >   - sql_code (str|None): Строка с SQL-кодом
  >   - separate_graph (str): Режим отображения графиков
  >   - operators (str|None): Фильтр SQL-операторов

Примеры использования:
: ```pycon
  >>> python cli.py --mode functional --directory_path ./sql --separate_graph true
  >>> python cli.py --mode field --sql_code "SELECT * FROM table" --operators "SELECT,JOIN"
  ```

Примечания:
  - Режимы работы:
     * table: Анализ на уровне таблиц
     * field: Анализ связей между колонками
     * functional: Полное построение зависимостей
 - Требования к директории:
     * Должна содержать .sql файлы
     * Минимум 1 валидный SQL-файл
 - SQL-код должен быть синтаксически корректным

## dialect module

### util.dialect.safe_parse(sql)

Пытается распарсить SQL-код, автоматически определяя диалект (PostgreSQL/Oracle).

Последовательно проверяет поддержку диалектов. Если парсинг для диалекта завершается успешно,
возвращает результат и название диалекта. В противном случае пробует следующий диалект.

* **Parameters:**
  **sql** (*str*) – SQL-код для анализа. Должен быть синтаксически корректным для одного из поддерживаемых диалектов.
* **Returns:**
  Кортеж из двух элементов:
    - Список AST-узлов (sqlglot.expressions.Expression) | None: Результат парсинга.
    - str: Название диалекта (“postgres”, “oracle”) или “Unknown” при неудаче.
* **Return type:**
  tuple

### Examples

```pycon
>>> ast, dialect = safe_parse("SELECT * FROM users")
>>> print(dialect)  # "postgres" (если парсинг успешен)
```

```pycon
>>> ast, dialect = safe_parse("INVALID SQL")
>>> print(ast, dialect)  # None, "Unknown"
```
