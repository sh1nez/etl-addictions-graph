import pytest
import time
from src.graph import GraphManager, GraphStorage
from src.parser.sql_ast import SQLAST

@pytest.fixture
def empty_storage():
    return GraphStorage()

@pytest.fixture
def large_storage():
    storage = GraphStorage()
    for i in range(100):
        storage.add_node(f"table_{i}")
        storage.add_node(f"source_{i}")
        storage.add_edge(f"source_{i}", f"table_{i}", "Insert")
    return storage

class TestVisualization:
    def test_empty_graph_visualization(self, empty_storage, capsys):
        empty_storage.visualize()
        captured = capsys.readouterr()
        assert "Graph is empty, no dependencies to display" in captured.out

    def test_single_node_graph(self):
        manager = GraphManager()
        sql = "CREATE TABLE audit_logs (id INT);"
        manager.process_sql(sql)
        
        start_time = time.time()
        manager.storage.visualize()
        render_time = time.time() - start_time
        
        assert "audit_logs" in manager.storage.nodes
        assert len(manager.storage.edges) == 0
        assert render_time < 1.0  

    def test_large_graph_performance(self, large_storage):
        start_time = time.time()
        large_storage.visualize()
        render_time = time.time() - start_time
        
        assert len(large_storage.nodes) == 200
        assert len(large_storage.edges) == 100
        assert render_time < 5.0  
        print(f"\nLarge graph render time: {render_time:.2f}s")

class TestFailingCases:
    def test_missing_table_reference(self):
        """Тест должен упасть: ссылка на несуществующую таблицу"""
        manager = GraphManager()
        sql = "INSERT INTO new_orders SELECT * FROM non_existing_table;"
        
        result = manager.process_sql(sql)
        
        assert "Missing table: non_existing_table" in result[0], "Нет валидации ссылок на таблицы"

    def test_circular_dependency(self):
        """Тест должен упасть: циклическая зависимость"""
        manager = GraphManager()
        sqls = [
            "INSERT INTO A SELECT * FROM B;",
            "INSERT INTO B SELECT * FROM A;"
        ]
        
        for sql in sqls:
            manager.process_sql(sql)
        
        assert manager.storage.has_cycles() is True, "Циклические зависимости не обнаружены"

class TestGeneratedQueries:
    def test_large_scale_operations(self, benchmark):
        """Генерация 100 INSERT-SELECT операций"""
        manager = GraphManager()
        
        def setup():
            return ["INSERT INTO table_{i} SELECT * FROM source_{i};" for i in range(100)]
        
        queries = setup()
        
        result = benchmark(manager.process_sql_batch, queries)
        
        assert len(result) == 0
        assert len(manager.storage.nodes) == 200
        assert len(manager.storage.edges) == 100
