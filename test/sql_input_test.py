from src.base.manager import GraphManager
from src.settings import BASE_DIR
from unittest.mock import ANY


__all__ = []


class TestSqlInput:
    def test_graph_manager_process_sql_incorrect_sql_query_corrections(self):
        manager = GraphManager()
        corrections = manager.process_sql(
            "INSERT INTO invalid_table VALUES ('unclosed_quote);"
        )
        error_message = "Error parsing SQL:"

        assert len(corrections) == 1

        assert error_message in corrections[0]

    def test_graph_manager_process_sql_incorrect_sql_query_storage_empty(self):
        manager = GraphManager()
        manager.process_sql("INSERT ONTO invalid_table VALUES ('unclosed_quote');")
        graph_storage = (manager.storage.nodes, manager.storage.edges)

        assert graph_storage[0] == set()

        assert graph_storage[1] == []

    def test_graph_manager_process_sql_correct_sql_query_insert_operation(self):
        table_name = "valid_table"
        manager = GraphManager()
        corrections = manager.process_sql(
            f"INSERT INTO {table_name} VALUES ('unclosed_quote');"
        )

        assert corrections == []

        graph_storage = (manager.storage.nodes, manager.storage.edges)

        assert graph_storage[0] == {"input 0", table_name}

        # Проверка ребер (убираем дубликаты)
<<<<<<< HEAD
        unique_edges = list({(src, dst, frozenset(attrs.items()))
                             for src, dst, attrs in graph_storage[1]})
=======
        unique_edges = list(
            {
                (src, dst, frozenset(attrs.items()))
                for src, dst, attrs in graph_storage[1]
            }
        )
>>>>>>> 4ce56f0 (fixx test input (#51))

        assert len(unique_edges) == 1, f"Found duplicate edges: {graph_storage[1]}"

        edge = unique_edges[0]
        assert edge[0] == "input 0"  # source
        assert edge[1] == table_name  # target
        assert dict(edge[2]) == {"operation": "Insert", "color": "red"}

    def test_graph_manager_process_sql_merge_statement(self):
        target_table = "target_table"
        source_table = "source_table"
        manager = GraphManager()

        corrections = manager.process_sql(
            f"""
            MERGE INTO {target_table}
            USING {source_table}
            ON {source_table}.id = {target_table}.id
            WHEN MATCHED THEN
                UPDATE SET {target_table}.name = {source_table}.name
            WHEN NOT MATCHED THEN
                INSERT (id, name) VALUES ({source_table}.id, {source_table}.name);
            """
        )

        assert corrections == []

        graph_storage = (manager.storage.nodes, manager.storage.edges)

        assert graph_storage[0] == set([target_table, source_table])

        assert graph_storage[1] == [
            (source_table, target_table, {"operation": "Merge", "color": ANY})
        ]

    def test_graph_manager_process_sql_correct_sql_query_update_operation(self):
        table_name_1 = "valid_table"
        table_name_2 = "valid_table_2"
        manager = GraphManager()
        corrections = manager.process_sql(
            f"UPDATE {table_name_1} SET a = {table_name_2}.a FROM {table_name_2} WHERE {table_name_1}.b = {table_name_2}.b;"
        )

        assert corrections == []

        graph_storage = (manager.storage.nodes, manager.storage.edges)

        assert graph_storage[0] == set([table_name_2, table_name_1])

        assert graph_storage[1] == [
            (table_name_2, table_name_1, {"operation": "Update", "color": ANY})
        ]

        def test_graph_manager_process_sql_correct_sql_query_different_sources(self):
            table_name_1 = "employees"
            manager = GraphManager()
            corrections = manager.process_sql(
                f"""INSERT INTO {table_name_1} (name, department, salary)
    VALUES ('Иван Иванов', 'IT', 75000.00);


    INSERT INTO {table_name_1} (name, department, salary, hire_date)
    VALUES ('Мария Петрова', 'HR', 65000.00, DEFAULT);"""
            )

            assert corrections == []

            graph_storage = (manager.storage.nodes, manager.storage.edges)

            assert graph_storage[0] == set(["input 0", "input 1", table_name_1])

            assert sorted(graph_storage[1]) == sorted(
                [
                    ("input 0", table_name_1, {"operation": "Insert", "color": ANY}),
                    ("input 1", table_name_1, {"operation": "Insert", "color": ANY}),
                ]
            )

    def test_graph_manager_process_directory_dir_path_not_exists(self, capsys):
        dir_path = "/hfjalsf"
        manager = GraphManager()
        results = manager.process_directory(dir_path)

        assert results == []

        error_message = f"Error: Directory {dir_path} does not exist"

        captured = capsys.readouterr()

        assert error_message in captured.out

    def test_graph_manager_process_directory_dir_path_not_a_dir_path(
        self,
        capsys,
    ):
        dir_path = BASE_DIR / "ddl/Employee.ddl"
        manager = GraphManager()
        results = manager.process_directory(dir_path)

        assert results == []

        error_message = f"Error: {dir_path} is not a directory"

        captured = capsys.readouterr()

        assert error_message in captured.out

    # def test_graph_manager_process_directory_correct_dir_path(self, capsys):
    #     dir_path = BASE_DIR / "ddl/"
    #
    #     manager = GraphManager()
    #     results = manager.process_directory(dir_path)
    #
    #     assert len(results) > 0
    #
    #     message = f"Processing files in directory: {dir_path}"
    #
    #     captured = capsys.readouterr()
    #
    #     assert message in captured.out

    def test_graph_manager_process_sql_emtpy_string(self):
        sql_code = ""

        manager = GraphManager()
        corrections = manager.process_sql(sql_code)

        assert len(corrections) == 1

        correction_message = "Invalid input: Not a valid SQL string"

        assert correction_message in corrections[0]

    def test_graph_manager_process_sql_not_a_string(self):
        sql_code = GraphManager()

        manager = GraphManager()
        corrections = manager.process_sql(sql_code)

        assert len(corrections) == 1

        correction_message = "Invalid input: Not a valid SQL string"

        assert correction_message in corrections[0]
