class SqlAst:
    """Класс для построения AST SQL-запросов."""

    _input_id = 0
    _output_id = 0
    _unknown_id = 0
    _join_id = 0
    _transfer_id = 0

    def __init__(self, sql_code: str, sep_parse: bool = False):
        if not sql_code or not isinstance(sql_code, str):
            self.corrected_sql = ""
            self.corrections = ["Invalid input: Not a valid SQL string"]
            self.sql_code = ""
            self.parsed = None
            self.dependencies = defaultdict(set)
            return
        self.corrections = []
        self.sql_code = sql_code
        self.corrected_sql = self.sql_code
        self.dependencies = defaultdict(set)
        self.input_id = SqlAst._input_id
        self.output_id = SqlAst._output_id
        self.unknown_id = SqlAst._unknown_id
        self.sep_parse = sep_parse

        try:
            self.parsed, self.dialect = safe_parse(self.corrected_sql)
            assert self.parsed is not None
            self.dependencies = self._extract_dependencies()
        except Exception as e:
            print(f"Error parsing SQL: {e}")
            self.parsed = None
            self.dependencies = defaultdict(set)
            self.corrections.append(f"Error parsing SQL: {str(e)}")

    def _extract_dependencies(self) -> defaultdict:
        """Извлекает зависимости между таблицами и операциями, включая ETL, SELECT и JOIN запросы."""
        dependencies = defaultdict(set)
        etl_types = (Insert, Update, Delete, Merge)
        try:
            for statement in self.parsed:
                # Определяем целевую таблицу (для операций модификации данных)
                to_table = None
                if isinstance(statement, etl_types):
                    if "this" in statement.args:
                        to_table = self.get_table_name(statement)
                elif (
                        isinstance(statement, Select)
                        and hasattr(statement, "into")
                        and statement.into is not None
                ):
                    to_table = self.get_table_name(statement.into)
                else:
                    to_table = f"result {self._get_output_id()}"

                # Добавляем входные узлы для каждой исходной таблицы
                if isinstance(statement, (Insert, Update, Delete, Merge, Select)):
                    self._add_input_nodes(statement, dependencies)

                # Обрабатываем основной запрос и все подзапросы
                self._process_statement_tree(statement, to_table, dependencies)

        except Exception as e:
            print(f"Error in dependency extraction: {e}")

        return dependencies

    def _add_input_nodes(self, statement, dependencies):
        """Добавляет входные узлы для каждой исходной таблицы в запросе."""
        source_tables = set()

        # Собираем все исходные таблицы из FROM и JOIN
        if "from" in statement.args and statement.args["from"] is not None:
            from_table = self.get_table_name(statement.args["from"])
            if from_table and not from_table.startswith(("unknown", "result")):
                source_tables.add(from_table)

        if "joins" in statement.args and statement.args["joins"]:
            for join_node in statement.args["joins"]:
                if "this" in join_node.args:
                    join_table = self.get_table_name(join_node.args["this"])
                    if join_table and not join_table.startswith(("unknown", "result")):
                        source_tables.add(join_table)

        # Добавляем входные узлы для каждой исходной таблицы
        for source_table in source_tables:
            input_node = f"input_{source_table}"
            dependencies[source_table].add(Edge(input_node, source_table, "input"))
