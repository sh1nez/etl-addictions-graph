<!-- Утилита для анализа DDL и построения графа ETL-зависимостей -->

Утилита для автоматического анализа SQL-кода, определения зависимостей между объектами и визуализации результатов.

# Структура проекта

```default
.
├── src/       # Исходный код приложения
├── ddl/       # Примеры SQL-скриптов (поддержка PG/MySQL/Oracle)
└── test/      # Юнит-тесты (pytest)
```

# Установка

## Вариант 1: Стандартная установка

```bash
python -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Вариант 2: Использование UV (рекомендуется)

1. Установите [UV](https://docs.astral.sh/uv/):

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
irm https://astral.sh/uv/install.ps1 | iex
```

1. Установите зависимости:

```bash
uv pip install -r requirements.txt
```

# Запуск

## Базовые команды

```bash
# Анализ директории с SQL-файлами
uv run src/main.py --mode <режим> --directory_path <путь> --separate_graph <true|false>

# Прямой ввод SQL-кода
uv run src/main.py --mode <режим> --sql_code "SQL-запрос" --separate_graph <true|false>
```

## Параметры запуска

| Параметр           | Обязательный   | Описание                                                 |
|--------------------|----------------|----------------------------------------------------------|
| `--mode`           | Да             | Режим работы: `table`, `field`, `functional`             |
| `--directory_path` | Да\*           | Путь к директории с SQL-файлами                          |
| `--sql_code`       | Да\*           | SQL-код для анализа                                      |
| `--separate_graph` | Нет            | `true` — отдельные графы, `false` — общий (по умолчанию) |

## Примеры использования

```bash
# Анализ табличных зависимостей
uv run src/main.py --mode table --directory_path ./ddl --separate_graph false

# Функциональный анализ SQL-кода
uv run src/main.py --mode functional --sql_code "CREATE TABLE users (id INT);"

# Полевой анализ с раздельными графами
uv run src/main.py --mode field --directory_path ./ddl --separate_graph true
```

# Дополнительные команды

| Действие                   | Команда                                             |
|----------------------------|-----------------------------------------------------|
| Запуск тестов              | `uv run pytest`                                     |
| Форматирование кода        | `uv run black src/`                                 |
| Генерация requirements.txt | `uv pip compile pyproject.toml -o requirements.txt` |

## Общее описание

Проект предназначен для анализа SQL-зависимостей и визуализации графов ETL.
Основные компоненты разделены по функциональному назначению:

- **Базовый функционал**: Общие утилиты, парсинг аргументов, логирование
- **Режим-специфичный функционал**: Модули для работы в режимах `table`, `field`, `functional`

### Базовый функционал

| Директория/Файл     | Описание                                                    |
|---------------------|-------------------------------------------------------------|
| `/src/main.py`      | Точка входа. Управление режимами, инициализация компонентов |
| `/src/util/cli.py`  | Парсинг аргументов командной строки (режимы, пути, SQL-код) |
| `/logger_config.py` | Конфигурация логгера с ротацией файлов и режимами вывода    |
| `/dialect.py`       | Автодетекция SQL-диалекта (PostgreSQL, Oracle)              |
| `/src/base/run.py`  | Базовый функционал                                          |

### Режим-специфичный функционал

| Директория          | Режимы и назначение                                       |
|---------------------|-----------------------------------------------------------|
| `/src/table/run.py` | Режим `table`: Анализ табличных зависимостей              |
| `/src/field/run.py` | Режим `field`: Анализ связей между полями таблиц          |
| `/src/func/run.py`  | Режим `functional`: Построение полного графа зависимостей |

### Contents:

* [src package](src.md)
  * [Subpackages](src.md#subpackages)
    * [src.base package](src.base.md)
      * [Submodules](src.base.md#submodules)
      * [manager module](src.base.md#manager-module)
      * [parse module](src.base.md#parse-module)
      * [run module](src.base.md#run-module)
      * [storage module](src.base.md#storage-module)
      * [visualize module](src.base.md#visualize-module)
    * [src.field package](src.field.md)
      * [Submodules](src.field.md#submodules)
      * [columns module](src.field.md#columns-module)
      * [run module](src.field.md#run-module)
      * [storage module](src.field.md#storage-module)
      * [visualize module](src.field.md#visualize-module)
    * [src.func package](src.func.md)
      * [Submodules](src.func.md#submodules)
      * [buff_tables module](src.func.md#buff_tables-module)
      * [run module](src.func.md#run-module)
    * [src.table package](src.table.md)
      * [Submodules](src.table.md#submodules)
      * [run module](src.table.md#run-module)
    * [src.util package](src.util.md)
      * [Submodules](src.util.md#submodules)
      * [cli module](src.util.md#cli-module)
      * [dialect module](src.util.md#dialect-module)
  * [Submodules](src.md#submodules)
  * [logger_config module](src.md#logger_config-module)
    * [`setup_logger()`](src.md#logger_configsetup_loggermode-str--normal)
  * [main module](src.md#main-module)
    * [`configure_logging()`](src.md#mainconfigure_loggingmode-str-log_file-str--none)
    * [`main()`](src.md#mainmain)
