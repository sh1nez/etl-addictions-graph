# src.base package

## Submodules

## manager module

### *class* base.manager.GraphManager(column_mode=False, operators=None)

Bases: `object`

Управляет процессом парсинга SQL, хранением зависимостей и визуализацией графов.

Поддерживает два режима работы:
  - Режим таблиц (по умолчанию): использует GraphStorage и GraphVisualizer.
  - Режим колонок (column_mode=True): использует ColumnStorage и ColumnVisualizer.

#### storage

Хранилище зависимостей.

* **Type:**
  Union[[GraphStorage](#class-basestoragegraphstorage), [ColumnStorage](src.field.md#field.storage.ColumnStorage)]

#### visualizer

Генератор графов.

* **Type:**
  Union[[GraphVisualizer](#class-basevisualizegraphvisualizer), [ColumnVisualizer](src.field.md#field.visualize.ColumnVisualizer)]

#### parser

Парсер для обработки директорий с SQL-файлами.

* **Type:**
  [DirectoryParser](#class-baseparsedirectoryparsersql_ast_clsclass-baseparsesqlast)

#### \_\_init_\_(column_mode=False, operators=None)

Инициализирует компоненты на основе выбранного режима.

* **Parameters:**
  * **column_mode** (*bool*) – Если True, активирует режим работы с колонками. По умолчанию False.
  * **operators** (*Optional* *[**List* *[**str* *]* *]*) – Фильтр для операторов (например, [‘JOIN’, ‘WHERE’]).

#### process_directory(directory_path: str) → List[Tuple[str, List[str]]]

Обрабатывает все SQL-файлы в указанной директории.

* **Parameters:**
  **directory_path** (*str*) – Путь к директории с SQL-файлами.
* **Returns:**
  Список кортежей вида (путь_к_файлу, корректировки_для_файла).
* **Return type:**
  List[Tuple[str, List[str]]]

### Example

```pycon
>>> manager.process_directory("/data/sql")
[("/data/sql/query1.sql", ['WARNING: Ambiguous column "id"'])]
```

#### process_sql(sql_code: str) → List[str]

Парсит SQL-код, извлекает зависимости и возвращает корректировки.

* **Parameters:**
  **sql_code** (*str*) – SQL-запрос для анализа.
* **Returns:**
  Список предупреждений или предложений по исправлению.
* **Return type:**
  List[str]

### Example

```pycon
>>> manager.process_sql("SELECT * FROM users")
['WARNING: Missing schema prefix in table "users"']
```

#### visualize(title: str | None = None)

Генерирует графическое представление зависимостей.

* **Parameters:**
  **title** (*Optional* *[**str* *]*) – Заголовок графа. Если не указан, используется значение по умолчанию.

### Example

```pycon
>>> manager.visualize(title="Data Pipeline")
```

## parse module

### *class* base.parse.DirectoryParser(sql_ast_cls=<class 'base.parse.SqlAst'>)

Bases: `object`

Обрабатывает SQL-файлы в директории и возвращает результаты анализа.

#### sql_ast_cls

Класс для анализа SQL (можно заменить на кастомный).

* **Type:**
  Type[[SqlAst](#class-baseparsesqlastsql_code-str-sep_parse-bool--false)]

### Example

```pycon
>>> parser = DirectoryParser()
>>> results = parser.parse_directory("/data/sql")
>>> results[0]  # (dependencies, corrections, "/data/sql/query.sql")
```

#### \_\_init_\_(sql_ast_cls=<class 'base.parse.SqlAst'>)

Инициализирует парсер директорий.

* **Parameters:**
  **sql_ast_cls** (*type*) – Класс для анализа SQL. Можно заменить на кастомную реализацию.

#### parse_directory(directory: str, sep_parse: bool = False) → List[Tuple[defaultdict, List[str], str]]

Парсит все SQL-файлы в указанной директории.

* **Parameters:**
  * **directory** (*str*) – Путь к директории (например, “/data/sql”).
  * **sep_parse** (*bool*) – Передается в SqlAst._\_init_\_().
* **Returns:**
  Список кортежей: (зависимости, корректировки, путь_к_файлу).
* **Return type:**
  List[Tuple[defaultdict, List[str], str]
* **Raises:**
  **FileNotFoundError** – Если директория не существует.

### Example

```pycon
>>> parser = DirectoryParser()
>>> results = parser.parse_directory("./data/sql")
>>> file_path = results[0][2]
>>> isinstance(file_path, str)
True
>>> len(results[0][1])  # Количество корректировок
0
```

### *class* base.parse.SqlAst(sql_code: str, sep_parse: bool = False)

Bases: `object`

Парсит SQL-код, строит AST и извлекает зависимости между таблицами/CTE.

#### corrections

Корректировки и предупреждения (например, [“Error: syntax error”]).

* **Type:**
  List[str]

#### dependencies

Граф зависимостей вида {target: {Edge(source, target, node)}}.

* **Type:**
  defaultdict

#### table_schema

Схемы таблиц из CREATE-запросов (например, {“users”: {“id”: “INT”}}).

* **Type:**
  Dict[str, Dict]

#### recursive_ctes

Множество рекурсивных CTE (например, {“cte1”}).

* **Type:**
  Set[str]

### Example

```pycon
>>> ast = SqlAst("SELECT * FROM users")
>>> ast.get_dependencies()
defaultdict(<class 'set'>, {'result_0': {Edge('users', 'result_0', ...)}})
```

#### \_\_init_\_(sql_code: str, sep_parse: bool = False)

Инициализирует парсер SQL и запускает анализ кода.

* **Parameters:**
  * **sql_code** (*str*) – SQL-код для анализа.
  * **sep_parse** (*bool*) – Если True, использует отдельные счетчики для каждого экземпляра.
* **Raises:**
  **Exception** – Если возникает ошибка при парсинге SQL.

#### find_all(expr_type, obj=None)

Ищет все узлы указанного типа в AST.

* **Parameters:**
  * **expr_type** – Тип узла (например, Join)
  * **obj** – Корневой узел для поиска
* **Returns:**
  Найденные узлы
* **Return type:**
  List[Expression]

### Example

```pycon
>>> sql = "SELECT * FROM a JOIN b WHERE c IN (SELECT d FROM e)"
>>> ast = SqlAst(sql)
>>> joins = ast.find_all(Join)
>>> len(joins)
1
```

#### get_corrections() → List[str]

Возвращает список предупреждений и исправлений.

* **Returns:**
  Список сообщений о проблемах.
* **Return type:**
  List[str]

#### get_cyclic_dependencies() → List[List[str]]

Возвращает циклы в графе зависимостей.

* **Returns:**
  Список циклов
* **Return type:**
  List[List[str]]

### Example

```pycon
>>> sql = "CREATE TABLE a AS SELECT * FROM b; CREATE TABLE b AS SELECT * FROM a"
>>> ast = SqlAst(sql)
>>> ast.get_cyclic_dependencies()
[['a', 'b', 'a']]
```

#### get_dependencies() → defaultdict

Возвращает граф зависимостей между таблицами.

* **Returns:**
  Граф в формате {целевая_таблица: {рёбра}}
* **Return type:**
  defaultdict[set]

### Example

```pycon
>>> ast.get_dependencies()["orders"]
{Edge(source='customers', target='orders', expression=<Merge>)}
```

#### get_first_from(stmt) → str | None

Возвращает первую таблицу в FROM-клаузе.

* **Parameters:**
  **stmt** – Узел запроса (например, Select)
* **Returns:**
  Имя таблицы или None
* **Return type:**
  Optional[str]

### Example

```pycon
>>> sql = "SELECT * FROM orders JOIN customers"
>>> ast = SqlAst(sql)
>>> select_node = ast.parsed[0]
>>> ast.get_first_from(select_node)
'orders'
```

#### get_recursive_ctes() → Set[str]

Возвращает имена рекурсивных CTE.

* **Returns:**
  Множество имен. Пусто, если рекурсии нет.
* **Return type:**
  Set[str]

### Example

```pycon
>>> sql = "WITH RECURSIVE cte AS (SELECT * FROM cte)"
>>> ast = SqlAst(sql)
>>> ast.get_recursive_ctes()
{'cte'}
```

#### get_table_name(parsed) → str

Извлекает имя таблицы из узла AST.

* **Parameters:**
  **parsed** (*Expression*) – Узел AST, например, объект Table.
* **Returns:**
  Имя таблицы или “unknown_{id}”. Пример: “users” или “unknown_1”.
* **Return type:**
  str

### Example

```pycon
>>> table_node = sqlglot.parse_one("SELECT * FROM users").find(Table)
>>> ast.get_table_name(table_node)
'users'
```

#### get_table_schema() → Dict[str, Dict[str, Dict]]

Возвращает схему таблиц из CREATE-запросов.

* **Returns:**
  Структура вида {‘table’: {‘column’: {‘type’: ‘INT’}}}
* **Return type:**
  Dict

### Example

```pycon
>>> sql = "CREATE TABLE users (id INT, name VARCHAR(255))"
>>> ast = SqlAst(sql)
>>> ast.get_table_schema()
{'users': {'id': {'data_type': 'INT', ...}, 'name': {...}}}
```

## run module

### base.run.process_args(args)

Обрабатывает аргументы командной строки и запускает анализ SQL-зависимостей.

Основные сценарии:
1. Обработка SQL-кода из командной строки
2. Обработка SQL-файлов в директории (единый граф или раздельные)

* **Parameters:**
  **args** – Объект с аргументами командной строки.

   Ожидаемые атрибуты:
    - sql_code (str): SQL-запрос для анализа
    - directory_path (str): Путь к директории с SQL-файлами
    - operators (List[str]): Фильтр операторов для зависимостей
    - separate_graph (str): “True”/”False” - раздельная визуализация файлов
* **Returns:**
  None

### Example

```pycon
>>> #Обработка SQL-запроса
>>> args.sql_code = "SELECT * FROM table"
>>> process_args(args)
```

```pycon
>>> #Обработка директории с объединенным графом
>>> args.directory_path = "./sql_scripts"
>>> args.separate_graph = "False"
>>> process_args(args)
```

* **Raises:**
  * **FileNotFoundError** – Если передан несуществующий путь к директории
  * **ValueError** – Если не указаны sql_code или directory_path

Логирование:
  - INFO: Выводит список корректировок SQL
  - DEBUG: Детали обработки файлов

## storage module
### *class* base.storage.BuffRead

Bases: `object`

### *class* base.storage.BuffWrite

Bases: `object`

### *class* base.storage.Edge(from_table: str, to_table: str, op: DML | Select, is_internal_update=False)

Bases: `object`

Представляет ребро графа зависимостей между двумя сущностями.

#### source

Источник зависимости (таблица/сущность).

* **Type:**
  str

#### target

Цель зависимости.

* **Type:**
  str

#### op

Операция, вызывающая зависимость.

* **Type:**
  Union[DML, Select]

#### is_internal_update

Флаг внутреннего обновления.

* **Type:**
  bool

#### is_recursive

Флаг рекурсивной зависимости.

* **Type:**
  bool

### Example

```pycon
>>> edge = Edge("users", "orders", Insert())
>>> edge.is_recursive = True
```

#### \_\_init_\_(from_table: str, to_table: str, op: DML | Select, is_internal_update=False)

Инициализирует ребро зависимости.

* **Parameters:**
  * **from_table** (*str*) – Источник зависимости.
  * **to_table** (*str*) – Цель зависимости.
  * **op** (*Union* *[**DML* *,* *Select* *]*) – Операция (например, Insert, Select).
  * **is_internal_update** (*bool* *,* *optional*) – Внутреннее обновление. По умолчанию False.

### *class* base.storage.GraphStorage

Bases: `object`

Хранилище данных графа зависимостей между SQL-сущностями.

#### nodes

Множество узлов графа (имена таблиц/сущностей).

* **Type:**
  set

#### edges

Список рёбер графа в формате (источник, цель, метаданные).

* **Type:**
  list

#### operator_filter

Фильтр типов операторов для отображения.

* **Type:**
  set

#### COLORS

Сопоставление типов операторов с цветами для визуализации.
Пример: {Insert: “red”, Select: “purple”}

**Важные ключи**:
  - Insert: Красный
  - Select: Фиолетовый
  - Join: Оранжевый

* **Type:**
  dict

#### OPERATOR_MAP

Соответствие строковых имен операторов их классам.
Пример: {“INSERT”: Insert, “SELECT”: Select}

**Поддерживаемые операторы**:
  - “INSERT”, “UPDATE”, “DELETE”,
  - “SELECT”, “CREATE”, “ALTER”,
  - “DROP”, “MERGE”, “JOIN”, “TABLE”

* **Type:**
  dict

### Example

```pycon
>>> storage = GraphStorage()
>>> storage.set_operator_filter("SELECT,INSERT")
>>> storage.add_dependencies(dependencies)
```

#### \_\_init_\_()

Инициализирует хранилище с пустыми данными.

#### add_dependencies(dependencies: defaultdict)

Добавляет зависимости в хранилище.

* **Parameters:**
  **dependencies** (*defaultdict*) – Зависимости в формате:
  {цель: [Edge(source, target, op), …]}

### Example

```pycon
>>> dependencies = defaultdict(set)
>>> dependencies["table1"].add(Edge("table2", "table1", Insert()))
>>> storage.add_dependencies(dependencies)
```

#### clear()

Очищает все данные хранилища.

### Example

```pycon
>>> storage.clear()
```

#### get_filtered_nodes_edges()

Возвращает отфильтрованные узлы и рёбра.

* **Returns:**
  (узлы, рёбра) после применения фильтра.
* **Return type:**
  Tuple[set, list]

### Example

```pycon
>>> nodes, edges = storage.get_filtered_nodes_edges()
```

#### set_operator_filter(operators: str | None = None)

Устанавливает фильтр отображаемых операторов.

* **Parameters:**
  **operators** (*str* *,* *optional*) – Строка с операторами через запятую.
  Пример: “SELECT,INSERT”. Если None, фильтр отключается.

### Example

```pycon
>>> storage.set_operator_filter("UPDATE,DELETE")
```

## visualize module

### *class* base.visualize.GraphVisualizer

Bases: `object`

Визуализирует графы зависимостей на основе данных из GraphStorage.

### Нет публичных атрибутов. Все параметры передаются в метод render.

### Example

```pycon
>>> storage = GraphStorage()
>>> visualizer = GraphVisualizer()
>>> visualizer.render(storage, title="Пример графа", save_path="graph.png")
```

#### render(storage: [GraphStorage](#class-basestoragegraphstorage), title: str | None = None, save_path: str | None = None, figsize: tuple = (20, 16), seed: int | None = 42, central_spread: float = 2.0, peripheral_spread: float = 1.5)

Визуализирует граф зависимостей и отображает/сохраняет результат.

* **Parameters:**
  * **storage** ([*GraphStorage*](#class-basestoragegraphstorage)) – Хранилище с данными графа.
  * **title** (*str* *,* *optional*) – Заголовок графа. По умолчанию None.
  * **save_path** (*str* *,* *optional*) – Путь для сохранения изображения. Пример: “output/graph.png”.
  * **figsize** (*tuple*) – Размер холста в дюймах. По умолчанию (20, 16).
  * **seed** (*int* *,* *optional*) – Seed для воспроизводимости расположения узлов.
  * **central_spread** (*float*) – Коэффициент расстояния между центральными узлами.
  * **peripheral_spread** (*float*) – Коэффициент расстояния для периферийных узлов.
* **Returns:**
  None
* **Raises:**
  **ValueError** – Если передан пустой storage.

### Example

```pycon
>>> # Базовая визуализация
>>> visualizer.render(storage)
```

```pycon
>>> # Кастомизация параметров
>>> visualizer.render(storage, title="Data Pipeline", save_path="pipeline.png", figsize=(15, 10), seed=123, central_spread=3.0)
```

## Module contents
