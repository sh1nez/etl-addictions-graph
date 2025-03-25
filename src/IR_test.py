import os
import sqlparse
import networkx as nx
import matplotlib.pyplot as plt
from typing import List


class SQLAST:
    """Класс для построения AST SQL-запросов."""

    def __init__(self, sql_code: str):
        self.sql_code = sql_code
        self.parsed = sqlparse.parse(sql_code)
        self.dependencies = self._extract_dependencies()

    def _extract_dependencies(self):
        """Извлекает зависимости между таблицами и операциями."""
        dependencies = []
        for statement in self.parsed:
            tables = set()
            current_table = False
            for token in statement.tokens:
                if token.ttype and token.value.upper() in ('FROM', 'JOIN', 'INNER JOIN',):
                    current_table = True
                elif current_table:
                    if isinstance(token, sqlparse.sql.Identifier):
                        tables.add(token.get_name())
                        current_table = False
                    elif isinstance(token, sqlparse.sql.IdentifierList):
                        for identifier in token.get_identifiers():
                            tables.add(identifier.get_name())
                        current_table = False

            if len(tables) > 1:
                dependencies.append(list(tables))
        return dependencies

    def get_dependencies(self):
        return self.dependencies


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


class DependencyGraph:
    """Класс графа зависимостей."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_dependencies(self, dependencies: List[List[str]]):
        """Добавляет зависимости в граф."""
        for dep in dependencies:
            if len(dep) > 1:
                for i in range(len(dep) - 1):
                    self.graph.add_edge(dep[i], dep[i + 1])

    def visualize(self):
        """Визуализирует граф зависимостей."""
        if not self.graph.nodes:
            print("Граф пуст, нет зависимостей для отображения.")
            return

        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_color='lightblue', edge_color='gray', font_size=10,
                node_size=2000)
        plt.show()


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
    parser.parse_directory("./sql_files")

graph.visualize()