__all__ = []

import pytest
from sqlglot.expressions import (
    Insert,
    Join,
    Update,
)

import src.base.parse
import src.base.storage


class TestVisual:
    @pytest.fixture(autouse=True)
    def setup_storage(self):
        self.storage = src.base.storage.GraphStorage()

    def test_edge_colors(self):
        sql_code = "INSERT INTO orders SELECT * FROM customers; "
        "UPDATE users SET name = 'Alice' WHERE id = 1; "
        ast = src.base.parse.SqlAst(sql_code)
        self.storage.add_dependencies(ast.get_dependencies())

        insert_edges = [
            e for e in self.storage.edges if e[2].get("operation") == "Insert"
        ]
        update_edges = [
            e for e in self.storage.edges if e[2].get("operation") == "Update"
        ]

        for edge in insert_edges:
            assert edge[2]["color"] == self.storage.COLORS[Insert]
        for edge in update_edges:
            assert edge[2]["color"] == self.storage.COLORS[Update]

    def test_node_names(self):
        sql_code = (
            "MERGE INTO target USING source ON target.id = source.id "
            "WHEN MATCHED THEN UPDATE SET target.name = source.name "
            "WHEN NOT MATCHED THEN INSERT (id, name) VALUES (source.id, source.name);"
        )
        ast = src.base.parse.SqlAst(sql_code)
        print(ast.get_corrections())
        self.storage.add_dependencies(ast.get_dependencies())

        expected_nodes = {"target", "source"}
        assert self.storage.nodes == expected_nodes

    def test_visualization_params(self):
        sql_code = "SELECT * FROM a JOIN b ON a.id = b.id;"
        ast = src.base.parse.SqlAst(sql_code)
        self.storage.add_dependencies(ast.get_dependencies())

        for u, v, data in self.storage.edges:
            operation = data.get("operation")
            assert operation is not None
            if operation == "Insert":
                assert data.get("color") == self.storage.COLORS[Insert]
            elif operation == "Join":
                assert data.get("color") == self.storage.COLORS[Join]

    def test_edge_labels(self):
        sql_code = (
            "CREATE TABLE employees (id INT, name VARCHAR(255));"
            "ALTER TABLE employees ADD COLUMN salary DECIMAL;"
        )
        ast = src.base.parse.SqlAst(sql_code)
        self.storage.add_dependencies(ast.get_dependencies())

        created_edges = [
            e for e in self.storage.edges if e[2].get("operation") == "Create"
        ]
        altered_edges = [
            e for e in self.storage.edges if e[2].get("operation") == "Alter"
        ]

        for edge in created_edges:
            assert edge[2]["operation"] == "Create"
        for edge in altered_edges:
            assert edge[2]["operation"] == "Alter"
