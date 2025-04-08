import pytest
import os
from unittest.mock import ANY
from src.graph import GraphManager, GraphStorage
from src.parser.sql_ast import SQLAST

class TestSQLProcessing:
    def test_insert_select(self):
        """INSERT INTO target SELECT FROM source"""
        manager = GraphManager()
        sql = "INSERT INTO orders SELECT * FROM temp_orders;"
        
        corrections = manager.process_sql(sql)
        storage = manager.storage
        
        assert corrections == []
        assert "orders" in storage.nodes
        assert "temp_orders" in storage.nodes
        assert ("temp_orders", "orders", {"operation": "Insert", "color": ANY}) in storage.edges

    def test_update_with_from(self):
        """UPDATE target FROM source"""
        manager = GraphManager()
        sql = """
        UPDATE users 
        SET name = 'test' 
        FROM logs 
        WHERE users.id = logs.user_id;
        """
        
        manager.process_sql(sql)
        storage = manager.storage
        
        assert "users" in storage.nodes
        assert "logs" in storage.nodes
        assert ("logs", "users", {"operation": "Update", "color": ANY}) in storage.edges

    def test_select_into(self):
        """SELECT INTO new_table FROM source"""
        manager = GraphManager()
        sql = "SELECT * INTO backup FROM active_users;"
        
        manager.process_sql(sql)
        storage = manager.storage
        
        assert "backup" in storage.nodes
        assert "active_users" in storage.nodes
        assert ("active_users", "backup", {"operation": "Select", "color": ANY}) in storage.edges

    def test_simple_select(self):
        """SELECT FROM source without target"""
        manager = GraphManager()
        sql = "SELECT * FROM products;"
        
        manager.process_sql(sql)
        storage = manager.storage
        
        assert "products" in storage.nodes
        assert "result" in storage.nodes
        assert ("products", "result", {"operation": "Select", "color": ANY}) in storage.edges

    def test_nested_subquery(self):
        """SELECT with nested subquery"""
        manager = GraphManager()
        sql = "SELECT * FROM (SELECT id FROM employees);"
        
        manager.process_sql(sql)
        storage = manager.storage
        
        assert "employees" in storage.nodes
        assert "result" in storage.nodes
        assert ("employees", "result", {"operation": "Select", "color": ANY}) in storage.edges

class TestDirectoryProcessing:
    def test_process_directory(self, tmp_path):
        sql_dir = tmp_path / "sql"
        sql_dir.mkdir()
        
        (sql_dir / "create.sql").write_text("""
        CREATE TABLE users (id INT PRIMARY KEY);
        CREATE TABLE logs (user_id INT, action TEXT);
        """)
        
        (sql_dir / "insert.sql").write_text("""
        INSERT INTO users VALUES (1);
        INSERT INTO logs SELECT 1, 'login';
        """)
        
        (sql_dir / "update.sql").write_text("""
        UPDATE users 
        SET name = 'test' 
        FROM logs 
        WHERE users.id = logs.user_id;
        """)

        manager = GraphManager()
        results = manager.process_directory(sql_dir)
        storage = manager.storage
        
        assert len(results) == 0
        assert {"users", "logs", "result"} <= storage.nodes
        assert ("logs", "users", {"operation": "Update", "color": ANY}) in storage.edges

class TestSQLASTParsing:
    def test_ast_insert_parsing(self):
        sql = "INSERT INTO orders SELECT * FROM temp_orders;"
        ast = SQLAST(sql)
        
        assert ast.target_tables == ["orders"]
        assert ast.source_tables == {"temp_orders"}

    def test_ast_update_parsing(self):
        sql = """
        UPDATE users 
        SET name = 'test' 
        FROM logs 
        WHERE users.id = logs.user_id;
        """
        ast = SQLAST(sql)
        
        assert ast.target_tables == ["users"]
        assert ast.source_tables == {"logs"}

    def test_ast_select_into_parsing(self):
        sql = "SELECT * INTO backup FROM active_users;"
        ast = SQLAST(sql)
        
        assert ast.target_tables == ["backup"]
        assert ast.source_tables == {"active_users"}

    def test_ast_simple_select_parsing(self):
        sql = "SELECT * FROM products;"
        ast = SQLAST(sql)
        
        assert ast.target_tables == ["result"]
        assert ast.source_tables == {"products"}

    def test_ast_nested_query_parsing(self):
        sql = "SELECT * FROM (SELECT id FROM employees);"
        ast = SQLAST(sql)
        
        assert ast.target_tables == ["result"]
        assert ast.source_tables == {"employees"}

    def test_ast_complex_query_parsing(self):
        sql = """
        WITH cte AS (SELECT id FROM departments)
        UPDATE employees
        SET dept_id = cte.id
        FROM cte
        WHERE employees.name = cte.dept_name;
        """
        ast = SQLAST(sql)
        
        assert ast.target_tables == ["employees"]
        assert ast.source_tables == {"departments"}
