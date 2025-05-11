# src package

## Subpackages

* [src.base package](src.base.md)
  * [Submodules](src.base.md#submodules)
  * [manager module](src.base.md#manager-module)
    * [`GraphManager`](src.base.md#class-basemanagergraphmanagercolumn_modefalse-operatorsnone)
      * [`GraphManager.storage`](src.base.md#storage)
      * [`GraphManager.visualizer`](src.base.md#visualizer)
      * [`GraphManager.parser`](src.base.md#parser)
      * [`GraphManager.__init__()`](src.base.md#__init__column_modefalse-operatorsnone)
      * [`GraphManager.process_directory()`](src.base.md#process_directorydirectory_path-str--listtuplestr-liststr)
      * [`GraphManager.process_sql()`](src.base.md#process_sqlsql_code-str--liststr)
      * [`GraphManager.visualize()`](src.base.md#visualizetitle-str--none--none)
  * [parse module](src.base.md#parse-module)
    * [`DirectoryParser`](src.base.md#class-baseparsedirectoryparsersql_ast_clsclass-baseparsesqlast)
      * [`DirectoryParser.sql_ast_cls`](src.base.md#sql_ast_cls)
      * [`DirectoryParser.__init__()`](src.base.md#__init__sql_ast_clsclass-baseparsesqlast)
      * [`DirectoryParser.parse_directory()`](src.base.md#parse_directorydirectory-str-sep_parse-bool--false--listtupledefaultdict-liststr-str)
    * [`SqlAst`](src.base.md#class-baseparsesqlastsql_code-str-sep_parse-bool--false)
      * [`SqlAst.corrections`](src.base.md#corrections)
      * [`SqlAst.dependencies`](src.base.md#dependencies)
      * [`SqlAst.table_schema`](src.base.md#table_schema)
      * [`SqlAst.recursive_ctes`](src.base.md#recursive_ctes)
      * [`SqlAst.__init__()`](src.base.md#__init__sql_code-str-sep_parse-bool--false)
      * [`SqlAst.find_all()`](src.base.md#find_allexpr_type-objnone)
      * [`SqlAst.get_corrections()`](src.base.md#get_corrections--liststr)
      * [`SqlAst.get_cyclic_dependencies()`](src.base.md#get_cyclic_dependencies--listliststr)
      * [`SqlAst.get_dependencies()`](src.base.md#get_dependencies--defaultdict)
      * [`SqlAst.get_first_from()`](src.base.md#get_first_fromstmt--str--none)
      * [`SqlAst.get_recursive_ctes()`](src.base.md#get_recursive_ctes--setstr)
      * [`SqlAst.get_table_name()`](src.base.md#get_table_nameparsed--str)
      * [`SqlAst.get_table_schema()`](src.base.md#get_table_schema--dictstr-dictstr-dict)
  * [run module](src.base.md#run-module)
    * [`process_args()`](src.base.md#baserunprocess_argsargs)
  * [storage module](src.base.md#storage-module)
    * [`BuffRead`](src.base.md#class-basestoragebuffread)
    * [`BuffWrite`](src.base.md#class-basestoragebuffwrite)
    * [`Edge`](src.base.md#class-basestorageedgefrom_table-str-to_table-str-op-dml--select-is_internal_updatefalse)
      * [`Edge.source`](src.base.md#source)
      * [`Edge.target`](src.base.md#target)
      * [`Edge.op`](src.base.md#op)
      * [`Edge.is_internal_update`](src.base.md#is_internal_update)
      * [`Edge.is_recursive`](src.base.md#is_recursive)
      * [`Edge.__init__()`](src.base.md#__init__from_table-str-to_table-str-op-dml--select-is_internal_updatefalse)
    * [`GraphStorage`](src.base.md#class-basestoragegraphstorage)
      * [`GraphStorage.nodes`](src.base.md#nodes)
      * [`GraphStorage.edges`](src.base.md#edges)
      * [`GraphStorage.operator_filter`](src.base.md#operator_filter)
      * [`GraphStorage.COLORS`](src.base.md#COLORS)
      * [`GraphStorage.OPERATOR_MAP`](src.base.md#OPERATOR_MAP)
      * [`GraphStorage.__init__()`](src.base.md#__init__)
      * [`GraphStorage.add_dependencies()`](src.base.md#add_dependenciesdependencies-defaultdict)
      * [`GraphStorage.clear()`](src.base.md#clear)
      * [`GraphStorage.get_filtered_nodes_edges()`](src.base.md#get_filtered_nodes_edges)
      * [`GraphStorage.set_operator_filter()`](src.base.md#set_operator_filteroperators-str--none--none)
  * [visualize module](src.base.md#visualize-module)
    * [`GraphVisualizer`](src.base.md#class-basevisualizegraphvisualizer)
      * [`GraphVisualizer.render()`](src.base.md#renderstorage-graphstorage-title-str--none--none-save_path-str--none--none-figsize-tuple--20-16-seed-int--none--42-central_spread-float--20-peripheral_spread-float--15)
* [src.field package](src.field.md)
  * [Submodules](src.field.md#submodules)
  * [columns module](src.field.md#columns-module)
    * [`parse_columns()`](src.field.md#fieldcolumnsparse_columnsop-expression--tupleliststr--none-liststr--none)
    * [`print_ifnt_str()`](src.field.md#fieldcolumnsprint_ifnt_strfunc)
  * [run module](src.field.md#run-module)
    * [`process_args()`](src.field.md#fieldrunprocess_argsargs)
  * [storage module](src.field.md#storage-module)
    * [`ColumnStorage`](src.field.md#class-fieldstoragecolumnstorage)
      * [`ColumnStorage.nodes`](src.field.md#nodes)
      * [`ColumnStorage.edges`](src.field.md#edges)
      * [`ColumnStorage.COLORS`](src.field.md#COLORS)
      * [`ColumnStorage.add_dependencies()`](src.field.md#add_dependenciesdependencies-defaultdict)
  * [visualize module](src.field.md#visualize-module)
    * [`ColumnVisualizer`](src.field.md#class-fieldvisualizecolumnvisualizer)
      * [`ColumnVisualizer.render()`](src.field.md#renderstorage-graphstorage-title-str--none--none-output_pathnone)
* [src.func package](src.func.md)
  * [Submodules](src.func.md#submodules)
  * [buff_tables module](src.func.md#buff_tables-module)
    * [`BufferTable`](src.func.md#class-funcbuff_tablesbuffertablename)
      * [`BufferTable.name`](src.func.md#name)
      * [`BufferTable.write_procedures`](src.func.md#write_procedures)
      * [`BufferTable.read_procedures`](src.func.md#read_procedures)
      * [`BufferTable.__init__()`](src.func.md#__init__name--none)
      * [`BufferTable.build_dependencies()`](src.func.md#static-build_dependenciesbuff_tables-listbuffertablefuncbuff_tablesbuffertable--dictstr-setedgesrcbasemdbasestorageedge)
      * [`BufferTable.find_buffer_tables()`](src.func.md#static-find_buffer_tablesprocedures-listprocedurefuncbuff_tablesprocedure-known_buff_tables-listbuffertablefuncbuff_tablesbuffertable--setbuffertablefuncbuff_tablesbuffertable--listbuffertablefuncbuff_tablesbuffertable)
    * [`BufferTableDirectoryParser`](src.func.md#class-funcbuff_tablesbuffertabledirectoryparsersql_ast_cls)
      * [`BufferTableDirectoryParser.__init__()`](src.func.md#__init__sql_ast_cls)
      * [`BufferTableDirectoryParser.parse_directory()`](src.func.md#parse_directorydirectory-str--listbuffertablefuncbuff_tablesbuffertable)
    * [`BufferTableGraphStorage`](src.func.md#class-funcbuff_tablesbuffertablegraphstorage)
      * [`BufferTableGraphStorage.__init__()`](src.func.md#__init__)
      * [`BufferTableGraphStorage.clear()`](src.func.md#clear)
      * [`BufferTableGraphStorage.get_buf_edges()`](src.func.md#get_buf_edges)
      * [`BufferTableGraphStorage.get_buf_nodes()`](src.func.md#get_buf_nodes)
      * [`BufferTableGraphStorage.set_buff_tables()`](src.func.md#set_buff_tablesbuff_tables)
    * [`NewBuffGraphManager`](src.func.md#class-funcbuff_tablesnewbuffgraphmanager)
      * [`NewBuffGraphManager.__init__()`](src.func.md#__init__-1)
      * [`NewBuffGraphManager.process_sql()`](src.func.md#process_sqlsql_code-str--liststr)
    * [`Procedure`](src.func.md#class-funcbuff_tablesprocedurename-str-code-str)
      * [`Procedure.name`](src.func.md#name-1)
      * [`Procedure.code`](src.func.md#code)
      * [`Procedure.__init__()`](src.func.md#__init__name-str-code-str--none)
      * [`Procedure.extract_procedures()`](src.func.md#static-extract_proceduressql_code-str--listprocedurefuncbuff_tablesprocedure)
      * [`Procedure.get_graph_name()`](src.func.md#get_graph_name--str)
    * [`run()`](src.func.md#funcbuff_tablesrun)
  * [run module](src.func.md#run-module)
    * [`main()`](src.func.md#funcrunmain)
    * [`process_args()`](src.func.md#funcrunprocess_argsargs)
* [src.table package](src.table.md)
  * [Submodules](src.table.md#submodules)
  * [run module](src.table.md#run-module)
    * [`process_args()`](src.table.md#tablerunprocess_argsargs)
* [src.util package](src.util.md)
  * [Submodules](src.util.md#submodules)
  * [cli module](src.util.md#cli-module)
    * [`parse_arguments()`](src.util.md#utilcliparse_arguments)
  * [dialect module](src.util.md#dialect-module)
    * [`safe_parse()`](src.util.md#utildialectsafe_parsesql)

## Submodules

## logger_config module

### logger_config.setup_logger(mode: str = 'normal')

Настраивает обработчики логирования в зависимости от выбранного режима.

Полностью переконфигурирует логгер:
  - Удаляет существующие обработчики
  - Создает новые обработчики для файла и консоли
  - Настраивает уровни логирования и форматы вывода

* **Parameters:**
  **mode** (*str*) –

  Режим логирования.
  Допустимые значения:
  > - ”normal”:      Консоль (INFO+), файл (DEBUG+)
  > - ”quiet”:       Только файл (DEBUG+)
  > - ”errors_only”: Консоль (ERROR+), файл (DEBUG+)
  > - ”debug”:       Консоль (DEBUG+), файл (DEBUG+)
* **Returns:**
  None
* **Raises:**
  * **PermissionError** – Если нет прав на запись в лог-директорию
  * **OSError** – При проблемах с созданием файлового обработчика

### Examples

```pycon
>>> setup_logger(mode="normal")  # Стандартный режим
>>> setup_logger(mode="debug")   # Подробное логирование
```

### Notes

- Формат логов: [LEVEL] YYYY-MM-DD HH:MM:SS - NAME - MESSAGE
- Файловый обработчик:
    * Ротация при достижении 5 МБ
    * Хранится до 3 резервных копий
    * Кодировка UTF-8
- Консольный вывод направляется в sys.stdout
- Лог-файл сохраняется в {LOG_DIR}/{LOG_FILE}

## main module

### main.configure_logging(mode: str, log_file: str = None)

Настраивает глобальный логгер в соответствии с выбранным режимом.

**Управляет обработчиками вывода**:
  - Добавляет/удаляет консольные и файловые обработчики
  - Устанавливает уровни логирования для каждого обработчика
  - Форматирует сообщения

* **Parameters:**
  * **mode** (*str*) – Режим логирования.
    - “normal”: Консоль (INFO+), файл (DEBUG+)
    - “quiet”: Только файл (DEBUG+)
    - “error”: Консоль (ERROR+), файл (DEBUG+)
  * **log_file** (*str* *,* *optional*) – Путь к файлу для логирования. Если не указан, используется “app.log”.
* **Returns:**
  None
* **Raises:**
  * **PermissionError** – При отсутствии прав на запись в файл
  * **OSError** – При проблемах с созданием файла

### Examples

```pycon
>>> configure_logging("normal", "application.log")
>>> configure_logging("quiet")
```

### Notes

- Формат сообщений: “%Y-%m-%d %H:%M:%S [LEVEL] NAME: MESSAGE”
- Файловый обработчик создается только при необходимости
- Существующие обработчики перезаписываются

### main.main()

Основная точка входа в приложение.

Выполняет последовательность:
  1. Инициализация логгера
  2. Парсинг аргументов командной строки
  3. Запуск соответствующего модуля обработки
  4. Обработка ошибок режима выполнения

* **Returns:**
  None
* **Raises:**
  **SystemExit** – При указании неверного режима работы

### Examples

Запуск из командной строки:
> python main.py –mode functional –sql_code “SELECT \* FROM table”

### Notes

- Зависит от модулей table.run, field.run, func.run
- Использует глобальный логгер “dependency_graph”
- Коды завершения:
    * 0: Успешное выполнение
    * 1: Ошибка в режиме работы
