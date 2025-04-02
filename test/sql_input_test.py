import src.main
from src.settings import BASE_DIR


__all__ = []


class TestSqlInput:

    def test_graph_manager_process_sql_incorrect_sql_query_corrections(self):
        manager = src.main.GraphManager()
        corrections = manager.process_sql(
            "INSERT INTO invalid_table VALUES ('unclosed_quote);"
        )
        error_message = "Error parsing SQL:"

        assert len(corrections) == 1

        assert error_message in corrections[0]

    def test_graph_manager_process_sql_incorrect_sql_query_storage_empty(self):
        manager = src.main.GraphManager()
        manager.process_sql(
            "INSERT ONTO invalid_table VALUES ('unclosed_quote');"
        )
        graph_storage = (manager.storage.nodes, manager.storage.edges)

        assert graph_storage[0] == set()

        assert graph_storage[1] == []

    def test_graph_manager_process_sql_correct_sql_query(self):
        table_name = "valid_table"
        manager = src.main.GraphManager()
        corrections = manager.process_sql(
            f"INSERT INTO {table_name} VALUES ('unclosed_quote');"
        )

        assert corrections == []

        graph_storage = (manager.storage.nodes, manager.storage.edges)

        assert graph_storage[0] == set(["input", table_name])

        assert graph_storage[1] == [("input", table_name)]

    def test_graph_manager_process_directory_dir_path_not_exists(self, capsys):
        dir_path = "/hfjalsf"
        manager = src.main.GraphManager()
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
        manager = src.main.GraphManager()
        results = manager.process_directory(dir_path)

        assert results == []

        error_message = f"Error: {dir_path} is not a directory"

        captured = capsys.readouterr()

        assert error_message in captured.out

    def test_graph_manager_process_directory_correct_dir_path(self, capsys):
        dir_path = BASE_DIR / "ddl/"

        manager = src.main.GraphManager()
        results = manager.process_directory(dir_path)

        assert len(results) > 0

        message = f"Processing files in directory: {dir_path}"

        captured = capsys.readouterr()

        assert message in captured.out

    def test_graph_manager_process_sql_emtpy_string(self):
        sql_code = ""

        manager = src.main.GraphManager()
        corrections = manager.process_sql(sql_code)

        assert len(corrections) == 1

        correction_message = "Invalid input: Not a valid SQL string"

        assert correction_message in corrections[0]

    def test_graph_manager_process_sql_not_a_string(self):
        sql_code = src.main.GraphManager()

        manager = src.main.GraphManager()
        corrections = manager.process_sql(sql_code)

        assert len(corrections) == 1

        correction_message = "Invalid input: Not a valid SQL string"

        assert correction_message in corrections[0]
