from unittest.mock import ANY
from dataclasses import dataclass
from typing import Set, Tuple

import pytest

from src.base.manager import GraphManager
from src.settings import BASE_DIR


__all__ = []


class TestSqlInput:

    @pytest.fixture(autouse=True)
    def setup_manager(self):
        self.graph_manager = GraphManager()

    def test_graph_manager_process_sql_incorrect_sql_query_corrections(
        self,
    ):
        corrections = self.graph_manager.process_sql(
            "INSERT INTO invalid_table VALUES ('unclosed_quote);"
        )
        error_message = "Error parsing SQL:"

        assert len(corrections) == 1

        assert error_message in corrections[0]

    def test_graph_manager_process_sql_incorrect_sql_query_storage_empty(
        self,
    ):
        self.graph_manager.process_sql(
            "INSERT ONTO invalid_table VALUES ('unclosed_quote');"
        )
        graph_storage = (
            self.graph_manager.storage.nodes,
            self.graph_manager.storage.edges,
        )

        assert graph_storage[0] == set()

        assert graph_storage[1] == []

    def test_graph_manager_process_sql_correct_sql_query_insert_operation(
        self,
    ):
        table_name = "valid_table"

        corrections = self.graph_manager.process_sql(
            f"INSERT INTO {table_name} VALUES ('unclosed_quote');"
        )

        assert corrections == []

        graph_storage = (
            self.graph_manager.storage.nodes,
            self.graph_manager.storage.edges,
        )

        assert graph_storage[0] == {"input 0", table_name}

        # Проверка ребер (убираем дубликаты)
        unique_edges = list(
            {
                (src, dst, frozenset(attrs.items()))
                for src, dst, attrs in graph_storage[1]
            }
        )

        assert (
            len(unique_edges) == 1
        ), f"Found duplicate edges: {graph_storage[1]}"

        edge = unique_edges[0]
        assert edge[0] == "input 0"  # source
        assert edge[1] == table_name  # target
        assert dict(edge[2]) == {"operation": "Insert", "color": "red"}

    def test_graph_manager_process_sql_merge_statement(self):
        target_table = "target_table"
        source_table = "source_table"

        corrections = self.graph_manager.process_sql(
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

        graph_storage = (
            self.graph_manager.storage.nodes,
            self.graph_manager.storage.edges,
        )

        assert graph_storage[0] == set([target_table, source_table])

        assert graph_storage[1] == [
            (source_table, target_table, {"operation": "Merge", "color": ANY})
        ]

    def test_graph_manager_process_sql_correct_sql_query_update_operation(
        self,
    ):
        table_name_1 = "valid_table"
        table_name_2 = "valid_table_2"

        corrections = self.graph_manager.process_sql(
            f"UPDATE {table_name_1} SET a = {table_name_2}.a FROM "
            f"{table_name_2} WHERE {table_name_1}.b = {table_name_2}.b;"
        )

        assert corrections == []

        graph_storage = (
            self.graph_manager.storage.nodes,
            self.graph_manager.storage.edges,
        )

        assert graph_storage[0] == set([table_name_2, table_name_1])

        assert graph_storage[1] == [
            (table_name_2, table_name_1, {"operation": "Update", "color": ANY})
        ]

        def test_graph_manager_process_sql_correct_sql_query_different_sources(
            self,
        ):
            table_name_1 = "employees"

            corrections = self.graph_manager.process_sql(
                f"""INSERT INTO {table_name_1} (name, department, salary)
                    VALUES ('Иван Иванов', 'IT', 75000.00);


                    INSERT INTO {table_name_1} (name, department, salary, hire_date)
                    VALUES ('Мария Петрова', 'HR', 65000.00, DEFAULT);
                """
            )

            assert corrections == []

            graph_storage = (
                self.graph_manager.storage.nodes,
                self.graph_manager.storage.edges,
            )

            assert graph_storage[0] == set(
                ["input 0", "input 1", table_name_1]
            )

            assert sorted(graph_storage[1]) == sorted(
                [
                    (
                        "input 0",
                        table_name_1,
                        {"operation": "Insert", "color": ANY},
                    ),
                    (
                        "input 1",
                        table_name_1,
                        {"operation": "Insert", "color": ANY},
                    ),
                ]
            )

    def test_graph_manager_process_directory_dir_path_not_exists(
        self,
        capsys,
    ):
        dir_path = "/hfjalsf"

        results = self.graph_manager.process_directory(dir_path)

        assert results == []

        error_message = f"Error: Directory {dir_path} does not exist"

        captured = capsys.readouterr()

        assert error_message in captured.out

    def test_graph_manager_process_directory_dir_path_not_a_dir_path(
        self,
        capsys,
    ):
        dir_path = BASE_DIR / "ddl/Employee.ddl"

        results = self.graph_manager.process_directory(dir_path)

        assert results == []

        error_message = f"Error: {dir_path} is not a directory"

        captured = capsys.readouterr()

        assert error_message in captured.out

    def test_graph_manager_process_directory_correct_dir_path(
        self,
        capsys,
    ):
        dir_path = BASE_DIR / "ddl/"

        results = self.graph_manager.process_directory(dir_path)

        assert len(results) > 0

        message = f"Processing files in directory: {dir_path}"

        captured = capsys.readouterr()

        assert message in captured.out

    def test_graph_manager_process_sql_emtpy_string(self):
        sql_code = ""

        corrections = self.graph_manager.process_sql(sql_code)

        assert len(corrections) == 1

        correction_message = "Invalid input: Not a valid SQL string"

        assert correction_message in corrections[0]

    def test_graph_manager_process_sql_not_a_string(self):
        sql_code = GraphManager()

        corrections = self.graph_manager.process_sql(sql_code)

        assert len(corrections) == 1

        correction_message = "Invalid input: Not a valid SQL string"

        assert correction_message in corrections[0]


@dataclass
class SqlTestCase:
    sql: str
    expected_nodes: Set[str]
    expected_edges: Set[Tuple[str, str]]
    name: str


class TestJoinInput:

    @pytest.fixture(autouse=True)
    def setup_manager(self):
        self.graph_manager = GraphManager()

    test_cases = [
        SqlTestCase(
            sql="SELECT * FROM orders, customers WHERE orders.customer_id = customers.id;",
            expected_nodes={"orders", "customers"},
            expected_edges={("customers", "join"), ("orders", "select")},
            name="implicit_join_orders_customers",
        ),
        SqlTestCase(
            sql="SELECT * FROM orders, customers WHERE orders.customer_id = customers.id;",
            expected_nodes={"orders", "customers"},
            expected_edges={("orders", "select"), ("customers", "join")},
            name="implicit_join_orders_customers",
        ),
        SqlTestCase(
            sql="""SELECT * FROM A
                   JOIN B ON A.id = B.a_id
                   JOIN C ON B.id = C.b_id;""",
            expected_nodes={"a", "b", "c"},
            expected_edges={("b", "join"), ("c", "join"), ("a", "select")},
            name="chain_join_a_b_c",
        ),
        SqlTestCase(
            sql="""SELECT * FROM (
                    SELECT t1.id, t2.name FROM table1 t1
                    JOIN table2 t2 ON t1.id = t2.t1_id
                  ) AS subquery
                  JOIN table3 ON subquery.id = table3.sub_id;""",
            expected_nodes={"table3", "unknown 2"},
            expected_edges={("table3", "join"), ("unknown 2", "select")},
            name="nested_join_table1_table2_table3",
        ),
        SqlTestCase(
            sql="SELECT * FROM users AS u LEFT JOIN payments p ON u.id = p.user_id;",
            expected_nodes={"users (u)", "payments (p)"},
            expected_edges={("users (u)", "select"), ("payments (p)", "join")},
            name="alias_join_users_payments",
        ),
        SqlTestCase(
            sql="SELECT * FROM 'Users' JOIN 'Payments' ON 'Users'.id = 'Payments'.user_id;",
            expected_nodes={"users", "payments"},
            expected_edges={("users", "select"), ("payments", "join")},
            name="quoted_join_users_payments",
        ),
    ]

    @pytest.mark.parametrize(
        "case", test_cases, ids=[case.name for case in test_cases]
    )
    def test_valid_joins(self, case: SqlTestCase):
        self.graph_manager.storage = GraphManager().storage
        corrections = self.graph_manager.process_sql(case.sql)

        assert corrections == []

        nodes = {
            node.lower()
            for node in self.graph_manager.storage.nodes
            if "result " not in node
        }
        assert nodes == case.expected_nodes

        edges = {
            (src.lower(), data["operation"].lower())
            for src, dst, data in self.graph_manager.storage.edges
        }

        assert edges == case.expected_edges

    def test_invalid_join(self):
        sql_query = (
            "SELECT * FROM users JON orders ON users.id = orders.user_id;"
        )

        corrections = self.graph_manager.process_sql(sql_query)

        assert corrections
        assert self.graph_manager.storage.nodes == set()
        assert self.graph_manager.storage.edges == []
