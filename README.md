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
```
