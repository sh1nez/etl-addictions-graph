import re
import os
from collections import defaultdict
from typing import Optional, List, Tuple, Set, Dict
from base.storage import BuffRead, BuffWrite, Edge, GraphStorage
from base.parse import DirectoryParser, SqlAst
from base.visualize import GraphVisualizer
from base.manager import GraphManager


class Procedure:  # TODO mode it to different files.
    """Представляет SQL-процедуру/функцию и её связи с буферными таблицами.

    Attributes:
        name (str): Название процедуры
        code (str): Тело процедуры (код между BEGIN и END)

    Example:
        >>> sql = "CREATE FUNCTION test() RETURNS void AS $$ BEGIN ... END $$"
        >>> procs = Procedure.extract_procedures(sql)
        >>> procs[0].name
        'test'
    """

    def __init__(self, name: str, code: str) -> None:
        """Инициализирует объект процедуры.

        Args:
            name: Название процедуры (должно быть уникальным)
            code: SQL-код между BEGIN и END (без внешних блоков)
        """
        self.name = name
        self.code = code

    def get_graph_name(self) -> str:
        """Генерирует специальное имя для визуализации в графе.

        Returns:
            Строка в формате: \$procedure_name\$

        Example:
            >>> proc = Procedure("calculate_stats", "BEGIN ... END")
            >>> proc.get_graph_name()
            '\\$calculate_stats\\$'
        """

        return f"\\${self.name}\\$"

    @staticmethod
    def __extract_procedure_code(sql: str) -> str:

        if not ("BEGIN" in sql and "END" in sql):
            return sql

        sql = sql.split("BEGIN", 1)[1]
        sql = sql.rsplit("END", 1)[0]
        sql = sql.strip()

        return sql

    @staticmethod
    def extract_procedures(sql_code: str) -> List["Procedure"]:
        """Извлекает все процедуры из SQL-кода.

        Args:
            sql_code: Полный текст SQL-запроса

        Returns:
            Список объектов Procedure (пустой, если процедур нет)

        Raises:
            ValueError: При некорректном формате SQL

        Example:
            >>> sql = "CREATE FUNCTION test() AS $$ BEGIN ... END $$"
            >>> procedures = Procedure.extract_procedures(sql)
            >>> len(procedures)
            1
        """

        found = re.findall(
            r"[?:PROCEDURE|FUNCTION]\s+[\"\'?]?(\w+)[\"\'?]?\s*\(.*?\)\s*[^$]+?\$\$(.*?)\$\$",
            sql_code,
            re.DOTALL,
        )

        if not found:
            return []

        procedures = []

        for i in found:
            if len(i) == 2:
                procedures.append(
                    Procedure(i[0], Procedure.__extract_procedure_code(i[1]))
                )
            else:
                print(f"Error parsing procedure: {i}")

        return procedures

    def __repr__(self) -> str:
        return f"{self.name}: '{self.code}'"


class BufferTable:
    """Отражает буферную таблицу и её связи с процедурами.

    Attributes:
        name (str): Имя таблицы
        write_procedures (Set[Procedure]): Процедуры, записывающие в таблицу
        read_procedures (Set[Procedure]): Процедуры, читающие из таблицы

    Example:
        >>> table = BufferTable("temp_data")
        >>> table.write_procedures.add(proc)
    """

    def __init__(self, name) -> None:
        """Инициализирует объект буферной таблицы.

        Args:
            name: Уникальное имя таблицы в БД
        """

        self.name = name
        self.write_procedures = set()  # procedures that write into the table
        self.read_procedures = set()  # procedures that read from the table

    @staticmethod
    def build_dependencies(
        buff_tables: List["BufferTable"], edges: List[Edge]
    ) -> Dict[str, Set[Edge]]:
        """Строит граф зависимостей между таблицами и процедурами.

        Args:
            buff_tables: Список анализируемых таблиц

        Returns:
            Словарь в формате: {target_node: set_of_edges}

        Example:
            >>> tables = [BufferTable("temp1"), BufferTable("temp2")]
            >>> deps = BufferTable.build_dependencies(tables)
            >>> "temp1" in deps
            True
        """

        dependencies = defaultdict(set)
        for buff_table in buff_tables:
            for proc in buff_table.read_procedures:
                edge = Edge(buff_table.name, proc.get_graph_name(), BuffRead())
                dependencies[proc.get_graph_name()].add(edge)

            for proc in buff_table.write_procedures:
                edge = Edge(proc.get_graph_name(), buff_table.name, BuffWrite())
                dependencies[buff_table.name].add(edge)

        for edge in edges:
            if edge.target not in dependencies:
                dependencies[edge.target] = set()

            dependencies[edge.target].add(edge)

        return dependencies

    @staticmethod
    def find_buffer_tables(
        procedures: List[Procedure],
        known_buff_tables: List["BufferTable"] | Set["BufferTable"],
    ) -> Tuple[List["BufferTable"], List[Edge]]:
        """Идентифицирует буферные таблицы по их использованию.

        Args:
            procedures: Список процедур для анализа
            known_buff_tables: Ранее обнаруженные таблицы

        Returns:
            Отфильтрованный список реальных буферных таблиц

        Raises:
            SyntaxError: При обнаружении некорректного SQL
        """

        buff_tables = dict()
        for table in known_buff_tables:
            buff_tables[table.name] = table

        all_edges = []

        for proc in procedures:
            ast = SqlAst(proc.code)

            for to_table, edges in ast.get_dependencies().items():
                all_edges.extend(edges)
                if to_table not in buff_tables:
                    buff_tables[to_table] = BufferTable(to_table)

                for edge in edges:
                    if edge.source not in buff_tables:
                        buff_tables[edge.source] = BufferTable(edge.source)

                    buff_tables[to_table].write_procedures.add(proc)
                    buff_tables[edge.source].read_procedures.add(proc)

        real_buff_tables = set()
        other_tables = set()
        for _, table in buff_tables.items():
            if len(table.write_procedures) > 0 and len(table.read_procedures) > 0:
                real_buff_tables.add(table)

        return real_buff_tables, all_edges

    def __repr__(self) -> str:
        return f"{self.name}:\nreaders: {(self.read_procedures)}\nwriters: {self.write_procedures}"


class BufferTableGraphStorage(GraphStorage):
    """Специализированное хранилище для графа зависимостей буферных таблиц.

    Наследует:
        - Все возможности GraphStorage
        - Автоматическую генерацию узлов и рёбер
        - Специальные типы операций (BuffRead/BuffWrite)
    """

    def __init__(self):
        """Инициализирует хранилище с пустыми данными."""

        self.buff_tables = []
        self.nodes = set()
        self.edges = []

    def set_buff_tables(self, buff_tables):
        """Инициализирует данные из списка BufferTable.

        Args:
            buff_tables: Список объектов буферных таблиц
        """

        self.buff_tables = buff_tables
        self.nodes = self.get_buf_nodes()
        self.edges = self.get_buf_edges()

    def get_buf_nodes(self):
        """Генерирует уникальные узлы графа.

        Returns:
            Set[str]: Имена таблиц и процедур в специальном формате

        Example:
            >>> nodes = storage.get_buf_nodes()
            >>> "\\$proc1\\$" in nodes
            True
        """

        nodes = set()

        for table in self.buff_tables:
            nodes.add(table.name)
            for proc in table.write_procedures:
                nodes.add(proc.get_graph_name())

            for proc in table.read_procedures:
                nodes.add(proc.get_graph_name())
        return nodes

    def get_buf_edges(self):
        """Формирует список соединений между узлами.

        Returns:
            List[Tuple[str, str]]: Пары (источник, цель)

        Example:
            >>> edges = storage.get_buf_edges()
            >>> ("\\$proc1\\$", "temp_data") in edges
            True
        """

        edges = []

        for table in self.buff_tables:
            for proc in table.write_procedures:
                edges.append((proc.get_graph_name(), table.name))

            for proc in table.read_procedures:
                edges.append((table.name, proc.get_graph_name()))

        return edges

    def clear(self):
        self.nodes.clear()
        self.edges.clear()


class BufferTableDirectoryParser:
    """Парсер DDL-файлов для анализа временных таблиц."""

    def __init__(self, sql_ast_cls):
        self.sql_ast_cls = sql_ast_cls

    def parse_directory(
        self, directory: str, sep_parse: bool = False
    ) -> List[BufferTable]:
        """Обрабатывает все .ddl файлы в директории.

        Args:
            directory (str): Путь к анализируемой директории

        Returns:
            List[Tuple]:
                - defaultdict: Зависимости
                - list: Ошибки
                - str: Путь к файлу

        Raises:
            FileNotFoundError: При несуществующей директории

        Example:
            >>> parser = BufferTableDirectoryParser(SqlAst)
            >>> results = parser.parse_directory("./ddl_files")
        """

        results = []  # maybe hashmap better??
        known_buff_tables = []
        if not os.path.exists(directory):
            print(f"Error: Directory {directory} does not exist!")
            return results
        if not os.path.isdir(directory):
            print(f"Error: {directory} is not a directory!")
            return results
        print(f"Processing files in directory: {directory}")
        for root, _, files in os.walk(directory):
            print(f"Processing directory: {root}")

            for file in files:
                known_buff_tables = []
                if file.endswith(".ddl"):
                    file_path = os.path.join(root, file)
                    print(f"Reading file: {file_path}")
                    try:  # TODO with заменяет трай кетч блок, насколько я знаю, заменить
                        with open(file_path, "r", encoding="utf-8") as f:
                            sql_code = f.read()
                            procs = Procedure.extract_procedures(sql_code)
                            tables, edges = BufferTable.find_buffer_tables(
                                procs, known_buff_tables
                            )
                            if not sep_parse:
                                known_buff_tables = tables
                            dependencies = BufferTable.build_dependencies(tables, edges)
                            results.append(
                                (
                                    dependencies,
                                    [],
                                    file_path,
                                )
                            )
                    except Exception as e:
                        results.append(
                            (defaultdict(set), [f"Error: {str(e)}"], file_path)
                        )
        return results


class NewBuffGraphManager(GraphManager):
    """Менеджер процессов для работы с буферными таблицами."""

    def __init__(self):
        self.storage = GraphStorage()
        self.visualizer = GraphVisualizer()
        self.parser = BufferTableDirectoryParser(SqlAst)

    def process_sql(self, sql_code: str) -> List[str]:
        """Анализирует SQL-код и возвращает предупреждения.

        Args:
            sql_code (str): SQL DDL-код с процедурами

        Returns:
            List[str]: Сообщения о найденных таблицах и проблемах

        Example:
            >>> warnings = manager.process_sql("CREATE FUNCTION ...")
            >>> len(warnings)
            2
        """

        procs = Procedure.extract_procedures(sql_code)
        tables = BufferTable.find_buffer_tables(procs, [])
        self.storage.add_dependencies(BufferTable.build_dependencies(tables))
        return []


def run(directory, sql_code, separate_graph):
    """Интерактивная консольная утилита для анализа зависимостей.

    Пример workflow:
        1. Выбор режима ввода (ручной/файлы)
        2. Парсинг зависимостей
        3. Визуализация результатов

    Example:
        >>> run()
        SQL Syntax Corrector and Dependency Analyzer
        -------------------------------------------
        Would you like to enter SQL code manually? (y/n):
    """

    manager = NewBuffGraphManager()
    if sql_code:
        corrections = manager.process_sql(sql_code)
        if corrections:
            print("\nCorrections made:")
            for i, correction in enumerate(corrections, 1):
                print(f"{i}. {correction}")
        manager.visualize("Dependencies Graph")
    else:
        if separate_graph:
            parse_results = manager.parser.parse_directory(directory, sep_parse=True)
            for dependencies, corrections, file_path in parse_results:
                print(f"\nFile: {file_path}")
                if corrections:
                    print("Corrections made:")
                    for i, correction in enumerate(corrections, 1):
                        print(f"{i}. {correction}")
                temp_storage = GraphStorage()
                temp_storage.add_dependencies(dependencies)
                manager.visualizer.render(
                    temp_storage, f"Dependencies for { os.path.basename(file_path)}"
                )
        else:
            results = manager.process_directory(directory)
            for file_path, corrections in results:
                print(f"\nFile: {file_path}")
                if corrections:
                    print("Corrections made:")
                    for i, correction in enumerate(corrections, 1):
                        print(f"{i}. {correction}")
            manager.visualize("Full Dependencies Graph")
