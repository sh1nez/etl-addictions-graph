import src.main
from src.settings import BASE_DIR
from unittest.mock import ANY


class TestSqlInput:
    def test_process_sql_insert_select(self):
        """INSERT INTO orders SELECT * FROM temp_orders"""
        manager = src.main.GraphManager()
        sql = "INSERT INTO orders SELECT * FROM temp_orders;"
        corrections = manager.process_sql(sql)
        
        assert corrections == []
        assert manager.storage.nodes == {"orders", "temp_orders"}
        assert manager.storage.edges == [
            ("temp_orders", "orders", {"operation": "Insert", "color": ANY})
        ]

    def test_process_sql_update_with_from(self):
        """UPDATE users FROM logs"""
        manager = src.main.GraphManager()
        sql = "UPDATE users SET name = 'test' FROM logs WHERE users.id = logs.user_id;"
        corrections = manager.process_sql(sql)
        
        assert corrections == []
        assert manager.storage.nodes == {"users", "logs"}
        assert manager.storage.edges == [
            ("logs", "users", {"operation": "Update", "color": ANY})
        ]

    def test_process_sql_select_into(self):
        """SELECT INTO backup FROM active_users"""
        manager = src.main.GraphManager()
        sql = "SELECT * INTO backup FROM active_users;"
        corrections = manager.process_sql(sql)
        
        assert corrections == []
        assert manager.storage.nodes == {"backup", "active_users"}
        assert manager.storage.edges == [
            ("active_users", "backup", {"operation": "SelectInto", "color": ANY})
        ]

    def test_process_sql_simple_select(self):
        """SELECT FROM products"""
        manager = src.main.GraphManager()
        sql = "SELECT * FROM products;"
        corrections = manager.process_sql(sql)
        
        assert corrections == []
        assert manager.storage.nodes == {"products", "result"}
        assert manager.storage.edges == [
            ("products", "result", {"operation": "Select", "color": ANY})
        ]

    def test_process_sql_nested_subquery(self):
        """Nested SELECT FROM employees"""
        manager = src.main.GraphManager()
        sql = "SELECT * FROM (SELECT id FROM employees);"
        corrections = manager.process_sql(sql)
        
        assert corrections == []
        assert manager.storage.nodes == {"employees", "result"}
        assert manager.storage.edges == [
            ("employees", "result", {"operation": "Select", "color": ANY})
        ]


    # ... остальные оригинальные тесты
