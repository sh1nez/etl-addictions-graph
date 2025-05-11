# src.func package

## Submodules

## buff_tables module

### *class* func.buff_tables.BufferTable(name)

Bases: `object`

Отражает буферную таблицу и её связи с процедурами.

#### name

Имя таблицы

* **Type:**
  str

#### write_procedures

Процедуры, записывающие в таблицу

* **Type:**
  Set[[Procedure](#class-funcbuff_tablesprocedurename-str-code-str)]

#### read_procedures

Процедуры, читающие из таблицы

* **Type:**
  Set[[Procedure](#class-funcbuff_tablesprocedurename-str-code-str)]

### Example

```pycon
>>> table = BufferTable("temp_data")
>>> table.write_procedures.add(proc)
```

#### \_\_init_\_(name) → None

Инициализирует объект буферной таблицы.

* **Parameters:**
  **name** – Уникальное имя таблицы в БД

#### *static* build_dependencies(buff_tables: List[[BufferTable](#class-funcbuff_tablesbuffertablename)]) → Dict[str, Set[[Edge](src.base.md#class-basestorageedgefrom_table-str-to_table-str-op-dml--select-is_internal_updatefalse)]]

Строит граф зависимостей между таблицами и процедурами.

* **Parameters:**
  **buff_tables** – Список анализируемых таблиц
* **Returns:**
  {target_node: set_of_edges}
* **Return type:**
  Словарь в формате

### Example

```pycon
>>> tables = [BufferTable("temp1"), BufferTable("temp2")]
>>> deps = BufferTable.build_dependencies(tables)
>>> "temp1" in deps
True
```

#### *static* find_buffer_tables(procedures: List[[Procedure](#class-funcbuff_tablesprocedurename-str-code-str)], known_buff_tables: List[[BufferTable](#class-funcbuff_tablesbuffertablename)] | Set[[BufferTable](#class-funcbuff_tablesbuffertablename)]) → List[[BufferTable](#class-funcbuff_tablesbuffertablename)]

Идентифицирует буферные таблицы по их использованию.

* **Parameters:**
  * **procedures** – Список процедур для анализа
  * **known_buff_tables** – Ранее обнаруженные таблицы
* **Returns:**
  Отфильтрованный список реальных буферных таблиц
* **Raises:**
  **SyntaxError** – При обнаружении некорректного SQL

### *class* func.buff_tables.BufferTableDirectoryParser(sql_ast_cls)

Bases: `object`

Парсер DDL-файлов для анализа временных таблиц.

#### \_\_init_\_(sql_ast_cls)

#### parse_directory(directory: str) → List[[BufferTable](#class-funcbuff_tablesbuffertablename)]

Обрабатывает все .ddl файлы в директории.

* **Parameters:**
  **directory** (*str*) – Путь к анализируемой директории
* **Returns:**
  - defaultdict: Зависимости
  - list: Ошибки
  - str: Путь к файлу
* **Return type:**
  List[Tuple]
* **Raises:**
  **FileNotFoundError** – При несуществующей директории

### Example

```pycon
>>> parser = BufferTableDirectoryParser(SqlAst)
>>> results = parser.parse_directory("./ddl_files")
```

### *class* func.buff_tables.BufferTableGraphStorage

Bases: [`GraphStorage`](src.base.md#class-basestoragegraphstorage)

Специализированное хранилище для графа зависимостей буферных таблиц.

Наследует:
: - Все возможности GraphStorage
: - Автоматическую генерацию узлов и рёбер
: - Специальные типы операций (BuffRead/BuffWrite)

#### \_\_init_\_()

Инициализирует хранилище с пустыми данными.

#### clear()

Очищает все данные хранилища.

### Example

```pycon
>>> storage.clear()
```

#### get_buf_edges()

Формирует список соединений между узлами.

* **Returns:**
  Пары (источник, цель)
* **Return type:**
  List[Tuple[str, str]]

### Example

```pycon
>>> edges = storage.get_buf_edges()
>>> ("\$proc1\$", "temp_data") in edges
True
```

#### get_buf_nodes()

Генерирует уникальные узлы графа.

* **Returns:**
  Имена таблиц и процедур в специальном формате
* **Return type:**
  Set[str]

### Example

```pycon
>>> nodes = storage.get_buf_nodes()
>>> "\$proc1\$" in nodes
True
```

#### set_buff_tables(buff_tables)

Инициализирует данные из списка BufferTable.

* **Parameters:**
  **buff_tables** – Список объектов буферных таблиц

### *class* func.buff_tables.NewBuffGraphManager

Bases: [`GraphManager`](src.base.md#class-basemanagergraphmanagercolumn_modefalse-operatorsnone)

Менеджер процессов для работы с буферными таблицами.

#### \_\_init_\_()

Инициализирует компоненты на основе выбранного режима.

* **Parameters:**
  * **column_mode** (*bool*) – Если True, активирует режим работы с колонками. По умолчанию False.
  * **operators** (*Optional* *[**List* *[**str* *]* *]*) – Фильтр для операторов (например, [‘JOIN’, ‘WHERE’]).

#### process_sql(sql_code: str) → List[str]

Анализирует SQL-код и возвращает предупреждения.

* **Parameters:**
  **sql_code** (*str*) – SQL DDL-код с процедурами
* **Returns:**
  Сообщения о найденных таблицах и проблемах
* **Return type:**
  List[str]

### Example

```pycon
>>> warnings = manager.process_sql("CREATE FUNCTION ...")
>>> len(warnings)
2
```

### *class* func.buff_tables.Procedure(name: str, code: str)

Bases: `object`

Представляет SQL-процедуру/функцию и её связи с буферными таблицами.

#### name

Название процедуры

* **Type:**
  str

#### code

Тело процедуры (код между BEGIN и END)

* **Type:**
  str

### Example

```pycon
>>> sql = "CREATE FUNCTION test() RETURNS void AS $$ BEGIN ... END $$"
>>> procs = Procedure.extract_procedures(sql)
>>> procs[0].name
'test'
```

#### \_\_init_\_(name: str, code: str) → None

Инициализирует объект процедуры.

* **Parameters:**
  * **name** – Название процедуры (должно быть уникальным)
  * **code** – SQL-код между BEGIN и END (без внешних блоков)

#### *static* extract_procedures(sql_code: str) → List[[Procedure](#class-funcbuff_tablesprocedurename-str-code-str)]

Извлекает все процедуры из SQL-кода.

* **Parameters:**
  **sql_code** – Полный текст SQL-запроса
* **Returns:**
  Список объектов Procedure (пустой, если процедур нет)
* **Raises:**
  **ValueError** – При некорректном формате SQL

### Example

```pycon
>>> sql = "CREATE FUNCTION test() AS $$ BEGIN ... END $$"
>>> procedures = Procedure.extract_procedures(sql)
>>> len(procedures)
1
```

#### get_graph_name() → str

Генерирует специальное имя для визуализации в графе.

* **Returns:**
  $procedure_name$
* **Return type:**
  Строка в формате

### Example

```pycon
>>> proc = Procedure("calculate_stats", "BEGIN ... END")
>>> proc.get_graph_name()
'\$calculate_stats\$'
```

### func.buff_tables.run()

Интерактивная консольная утилита для анализа зависимостей.

Пример workflow:
  1. Выбор режима ввода (ручной/файлы)
  2. Парсинг зависимостей
  3. Визуализация результатов

### Example

```pycon
>>> run()
SQL Syntax Corrector and Dependency Analyzer
-------------------------------------------
Would you like to enter SQL code manually? (y/n):
```

## run module

### func.run.main()

Main entry point for script execution.

Designed to be invoked when running the module directly.
Executes the core application logic by calling the buff_tables module’s run() function.

### Example

```pycon
>>> python -m run
```

### func.run.process_args(args)

Обрабатывает аргументы командной строки и инициализирует выполнение функционального режима.

Парсит переданные аргументы командной строки, отображает конфигурационные параметры
и запускает основную логику обработки из модуля buff_tables.

* **Parameters:**
  **args** (*argparse.Namespace*) – Объект с аргументами командной строки.

  Ожидаемые атрибуты:
    - directory_path (str|None): Путь к входной директории (взаимоисключающий с sql_code)
    - sql_code (str|None): Сырой SQL-код для обработки (взаимоисключающий с directory_path)
    - separate_graph (bool): Флаг разделения графиков в выводе

Выводит:
: Сообщение инициализации с конфигурацией переданных аргументов.

Вызывает:
: func.buff_tables.run() для выполнения основной логики.

## Module contents
