# Utility for parsing DDL and generating an ETL ~~dependencies~~ addictions graph.

* ./src - source code
* ./ddl - sql code (pg/mysql/oracle dialects)
* ./test - unit test via pytest


# Install
```python4
python -m venv venv
source venv/bin/activate
pip install -r ./requirements.txt
```
## Nix
For pure MacOS users and other paupers in terrible life situation u can use nix:
```bash
nix develop
```
## UV - Python Package Manager

[Документация UV](https://docs.astral.sh/uv/)

### Установка
- **macOS/Linux**:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Windows**:
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

### Основные команды

#### Запуск программы
```bash
uv run src/main.py
```

#### Управление пакетами
- **Добавление пакета**:
  ```bash
  uv add package_name
  ```
- **Добавление пакета необязательного для запуска программы (инструменты для разработки)**:
  ```bash
  uv add --dev package_name
  ```
- **Удаление пакета**:
  ```bash
  uv remove package_name
  ```

#### Тестирование и форматирование
- **Запуск тестов**:
  ```bash
  uv run pytest
  ```
- **Форматирование кода**:
  ```bash
  uv run black file_path
  ```

#### Генерация requirements.txt

Нужно запустить, если хотите получить requirements.txt с актуальными библиотеками из файла pyproject.toml

```bash
uv pip compile pyproject.toml -o requirements.txt && uv pip compile --group dev >> requirements.txt
=======
# Usage
The program runs from the command line with the following flags:

```bash
# General format
uv run src/main.py --mode <mode> --directory_path <path> --separate_graph <true|false>

# or for running with SQL code directly
uv run src/main.py --mode <mode> --sql_code "SQL-code" --separate_graph <true|false>
```

## Required parameters

- `--mode` - program operation mode:
  - `table` - analysis of tables and their dependencies
  - `field` - work with table fields (in development)
  - `functional` - analysis of functional dependencies

- One of the two parameters (mutually exclusive):
  - `--directory_path` - path to directory with SQL files
  - `--sql_code` - SQL code for analysis, passed directly

## Additional parameters

- `--separate_graph` - graph visualization format:
  - `true` - separate graph for each file
  - `false` - common graph for all files (default)

## Usage examples

```bash
# Running in table mode with directory processing
uv run src/main.py --mode table --directory_path ./ddl --separate_graph false

# Running in functional mode with direct SQL code input
uv run src/main.py --mode functional --sql_code "CREATE TABLE test (id int);" --separate_graph false

# Running in field mode with directory processing and separate graphs
uv run src/main.py --mode field --directory_path ./ddl --separate_graph true
```�
