.. Утилита для анализа DDL и построения графа ETL-зависимостей

Утилита для автоматического анализа SQL-кода, определения зависимостей между объектами и визуализации результатов.

Структура проекта
=================
::

    .
    ├── src/       # Исходный код приложения
    ├── ddl/       # Примеры SQL-скриптов (поддержка PG/MySQL/Oracle)
    └── test/      # Юнит-тесты (pytest)

Установка
=========

Вариант 1: Стандартная установка
--------------------------------
.. code-block:: bash

    python -m venv venv
    source venv/bin/activate  # Для Windows: venv\Scripts\activate
    pip install -r requirements.txt

Вариант 2: Использование UV (рекомендуется)
-------------------------------------------
1. Установите `UV <https://docs.astral.sh/uv/>`_:

.. code-block:: bash

    # Linux/macOS
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Windows
    irm https://astral.sh/uv/install.ps1 | iex

2. Установите зависимости:

.. code-block:: bash

    uv pip install -r requirements.txt

Запуск
======

Базовые команды
---------------
.. code-block:: bash

    # Анализ директории с SQL-файлами
    uv run src/main.py --mode <режим> --directory_path <путь> --separate_graph <true|false>

    # Прямой ввод SQL-кода
    uv run src/main.py --mode <режим> --sql_code "SQL-запрос" --separate_graph <true|false>

Параметры запуска
-----------------
+---------------------+--------------+--------------------------------------------------------------+
| Параметр            | Обязательный | Описание                                                     |
+=====================+==============+==============================================================+
| ``--mode``          | Да           | Режим работы: ``table``, ``field``, ``functional``           |
+---------------------+--------------+--------------------------------------------------------------+
| ``--directory_path``| Да*          | Путь к директории с SQL-файлами                              |
+---------------------+--------------+--------------------------------------------------------------+
| ``--sql_code``      | Да*          | SQL-код для анализа                                          |
+---------------------+--------------+--------------------------------------------------------------+
| ``--separate_graph``| Нет          | ``true`` — отдельные графы, ``false`` — общий (по умолчанию) |
+---------------------+--------------+--------------------------------------------------------------+

Примеры использования
---------------------
.. code-block:: bash

    # Анализ табличных зависимостей
    uv run src/main.py --mode table --directory_path ./ddl --separate_graph false

    # Функциональный анализ SQL-кода
    uv run src/main.py --mode functional --sql_code "CREATE TABLE users (id INT);"

    # Полевой анализ с раздельными графами
    uv run src/main.py --mode field --directory_path ./ddl --separate_graph true

Дополнительные команды
======================
+------------------------------+-------------------------------------------------------+
| Действие                     | Команда                                               |
+==============================+=======================================================+
| Запуск тестов                | ``uv run pytest``                                     |
+------------------------------+-------------------------------------------------------+
| Форматирование кода          | ``uv run black src/``                                 |
+------------------------------+-------------------------------------------------------+
| Генерация requirements.txt   | ``uv pip compile pyproject.toml -o requirements.txt`` |
+------------------------------+-------------------------------------------------------+


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   files
   sheme
