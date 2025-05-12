# src.field package

## Submodules

## columns module

### field.columns.parse_columns(op: Expression) → Tuple[List[str] | None, List[str] | None]

Анализирует SQL-операцию и возвращает информацию о колонках.

* **Parameters:**
  **op** (*Expression*) – SQL-выражение для анализа.
* **Returns:**
  - List[str]: Колонки в формате [“источник:цель”]
  - List[str]: Колонки из WHERE-условия (если есть)
* **Return type:**
  Tuple

### Example

```pycon
>>> expr = sqlglot.parse_one("INSERT INTO table (a, b) VALUES (1, 2)")
>>> parse_columns(expr)
(['a:input', 'b:input'], None)
```

### field.columns.print_ifnt_str(func)

Декоратор для логирования входных и выходных данных функций (только для отладки).

* **Parameters:**
  **func** – Оборачиваемая функция
* **Returns:**
  Обёрнутая функция с логированием.

## run module

### field.run.process_args(args)

Обрабатывает аргументы командной строки для анализа зависимостей между колонками.

**Основные сценарии:**
  - Обработка SQL-кода из командной строки
  - Обработка SQL-файлов в директории:
      - Создание отдельных графов для каждого файла
      - Построение единого графа для всех файлов

* **Parameters:**
  **args** – Объект с аргументами командной строки.

  Ожидаемые атрибуты:
    - sql_code (str): SQL-запрос для анализа
    - directory_path (str): Путь к директории с SQL-файлами
    - operators (List[str]): Фильтр операторов (например, [“INSERT”, “SELECT”])
    - separate_graph (str): “True”/”False” - раздельная визуализация файлов
* **Returns:**
  None
* **Raises:**
  * **FileNotFoundError** – Если директория не существует
  * **ValueError** – Если не указаны sql_code или directory_path

### Example

```pycon
>>> # Анализ SQL-кода
>>> args.sql_code = "INSERT INTO users (id) VALUES (1)"
>>> process_args(args)
```

```pycon
>>> # Анализ директории с раздельными графами
>>> args.directory_path = "./sql_scripts"
>>> args.separate_graph = "True"
>>> process_args(args)
```

### Notes

- Логирует корректировки SQL-кода через logger.info
- Использует ColumnStorage для хранения зависимостей колонок

## storage module

### *class* field.storage.ColumnStorage

Bases: [`GraphStorage`](src.base.md#class-basestoragegraphstorage)

Хранилище для зависимостей между колонками таблиц.

Наследует функциональность GraphStorage и добавляет:
  - Анализ зависимостей на уровне колонок
  - Расширенную обработку метаданных для операций

#### nodes

Множество таблиц/сущностей

* **Type:**
  set

#### edges

Рёбра зависимостей в формате (источник, цель, метаданные)

* **Type:**
  list

#### COLORS

Цвета для визуализации операций (наследуется от GraphStorage)

* **Type:**
  dict

#### add_dependencies(dependencies: defaultdict)

Добавляет зависимости в хранилище с анализом колонок.

* **Parameters:**
  **dependencies** (*defaultdict*) – Зависимости в формате:
  {“target_table”: [Edge(source, target, op),…]}
* **Raises:**
  **TypeError** – Если передан неверный тип зависимостей

### Example

```pycon
>>> storage = ColumnStorage()
>>> deps = defaultdict(set)
>>> deps["users"].add(Edge("orders", "users", Insert()))
>>> storage.add_dependencies(deps)
```

## visualize module

### *class* field.visualize.ColumnVisualizer

Bases: [`GraphVisualizer`](src.base.md#class-basevisualizegraphvisualizer)

Визуализатор графов зависимостей между колонками таблиц.

Наследует функциональность GraphVisualizer и добавляет:
  - Интерактивное отображение информации о колонках при клике
  - Расширенную стилизацию для операций с колонками
  - Автоматическое определение стилей соединений для мультиграфов

### Наследует все атрибуты GraphVisualizer

#### render(storage: [GraphStorage](src.base.md#class-basestoragegraphstorage), title: str | None = None, output_path=None)

Визуализирует граф зависимостей с возможностью интерактивного взаимодействия.

* **Parameters:**
  * **storage** ([*GraphStorage*](src.base.md#class-basestoragegraphstorage)) – Хранилище с данными графа
  * **title** (*str* *,* *optional*) – Заголовок графа. По умолчанию None
  * **output_path** (*str* *,* *optional*) – Путь для сохранения изображения. Пример: “output/graph.png”
* **Raises:**
  * **RuntimeError** – Если визуализация невозможна в текущем окружении
  * **ValueError** – При передаче некорректных данных

### Example

```pycon
>>> storage = ColumnStorage()
>>> visualizer = ColumnVisualizer()
>>> visualizer.render(storage, title="User Columns", output_path="graph.png")
```

Особенности реализации:
  - Использует spring_layout с параметрами k=0.5 и iterations=50
  - Поддерживает до 10 соединений между узлами с автоматическим смещением
  - Реализует интерактивные подсказки с информацией о колонках:
    * ЛКМ по ребру -> отображение связанных колонок
    * Повторный клик -> скрытие подсказки
