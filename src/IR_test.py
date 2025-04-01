import os
import networkx as nx
import matplotlib.pyplot as plt
from sqlglot import parse
from collections import defaultdict
from sqlglot.expressions import Update, Insert, Table
from typing import Optional


class SQLAST:
    """Класс для построения AST SQL-запросов."""

    def __init__(self, sql_code: str):
        self.sql_code = sql_code
        self.parsed = parse(sql_code)
        self.dependencies = self._extract_dependencies()

    def _extract_dependencies(self) -> defaultdict[set[Table, Table]]:
        """Извлекает зависимости между таблицами и операциями."""
        dependencies = defaultdict(set)
        for statement in self.parsed:
            for sub_statement in statement.walk():
                if not isinstance(sub_statement, (Insert, Update)):
                    continue
                if 'this' not in sub_statement.args:
                    raise Exception('Unsupported structure')
                to_table = self.get_table_name(sub_statement)
                from_table = self.get_first_from(sub_statement)
                if from_table is None:
                    from_table = 'input'
                else:
                    from_table = self.get_table_name(from_table)

                dependencies[to_table].add(from_table)

        return dependencies

    def get_dependencies(self)  -> defaultdict[set[Table, Table]]:
        return self.dependencies

    def get_first_from(self, stmt) -> Table:
        if 'from' in stmt.args:
            return stmt.args['from']

        if 'expression' in stmt.args:
            return self.get_first_from(stmt.expression)

        return None

    def get_table_name(self, parsed) -> Table:
        while 'this' in parsed.args:
            if isinstance(parsed, Table):
                return parsed.this.this
            parsed = parsed.this

        raise Exception('No table found')


class DirectoryParser:
    """Класс для обработки SQL-файлов в директории."""

    def __init__(self, sql_ast: SQLAST, graph):
        self.sql_ast = sql_ast
        self.graph = graph

    def parse_directory(self, directory: str):
        """Парсит все SQL-файлы в указанной директории."""
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".sql"):
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        sql_code = f.read()
                        ast = self.sql_ast(sql_code)
                        self.graph.add_dependencies(ast.get_dependencies())
    
    def separate_parse(self, directory: str):
        """Парсит поочерёдно все SQL-файлы в указанной директории в отдельные графы и отображает их.(для тестирования)"""
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".sql"):
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        one_graph = DependencyGraph()
                        sql_code = f.read()
                        ast = self.sql_ast(sql_code)
                        one_graph.add_dependencies(ast.get_dependencies())
                        one_graph.visualize(file)


class DependencyGraph:
    """Класс графа зависимостей."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_dependencies(self, dependencies: defaultdict[set[Table, Table]]):
        """Добавляет зависимости в граф."""
        for k, v in dependencies.items():
            for i in v:
                self.graph.add_edge(i, k)

    def visualize(self, title:Optional[str] = None):
        """Визуализирует граф зависимостей."""
        if not self.graph.nodes:
            print("Граф пуст, нет зависимостей для отображения.")
            return

        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_color='lightblue', edge_color='gray', font_size=10,
                node_size=2000)
        if title is not None:
            plt.gcf().canvas.manager.set_window_title(f'DML FILE {title}')
        plt.show()

class GraphManager:
    """Class for managing graph building and visualization components."""
    def __init__(self):
        self.storage = GraphStorage()
        self.visualizer = GraphVisualizer()
        self.parser = DirectoryParser(SQLAST)
    def process_sql(self, sql_code: str) -> List[str]:
        ast = SQLAST(sql_code)
        self.storage.add_dependencies(ast.get_dependencies())
        return ast.get_corrections()
    def process_directory(self, directory_path: str) -> List[Tuple[str, List[str]]]:
        results = []
        parse_results = self.parser.parse_directory(directory_path)
        for dependencies, corrections, file_path in parse_results:
            self.storage.add_dependencies(dependencies)
            results.append((file_path, corrections))
        return results
    def visualize(self, title: Optional[str] = None):
        self.visualizer.render(self.storage, title)

def load_sql_code():
    """Позволяет пользователю ввести SQL-код вручную."""
    print("Введите SQL-код (для завершения введите пустую строку):")
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    return "\n".join(lines)


# Пример использования
graph = DependencyGraph()
choice = input("Хотите ввести SQL-код вручную? (y/n): ")
if choice.lower() == 'y':
    sql_code = load_sql_code()
    ast = SQLAST(sql_code)
    graph.add_dependencies(ast.get_dependencies())
else:
    parser = DirectoryParser(SQLAST, graph)
    choice = input("Вывести графы зависимости отдельно для каждого файла? (y/n): ")
    if choice.lower() == 'y':
        parser.separate_parse("./dml")
    else:
        parser.parse_directory("./dml")

graph.visualize()

