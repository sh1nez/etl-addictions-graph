from collections import defaultdict
from sqlglot.expressions import Update, Insert, Table, Delete, Merge, Select, Join


class GraphStorage:
    """Class for storing dependency graph data."""

    COLORS = {
        Insert: "red",
        Update: "green",
        Delete: "blue",
        Merge: "yellow",
        Select: "purple",
        Join: "orange",
        Table: "cyan",  # Для прямых ссылок на таблицы
    }

    def __init__(self):
        self.nodes = set()
        self.edges = []

    def add_dependencies(self, dependencies: defaultdict):
        for to_table, edges in dependencies.items():
            self.nodes.add(to_table)
            for edge in edges:
                self.nodes.add(edge.from_table)
                op = edge.op
                op_name = type(op).__name__
                op_color = self.COLORS.get(type(op), "gray")

                # Создаем словарь с метаданными для ребра
                edge_data = {"operation": op_name, "color": op_color}

                # Упрощаем отображение для JOIN - всегда "Join"
                if isinstance(op, Join):
                    edge_data["operation"] = "Join"

                # Упрощаем отображение для прямых ссылок на таблицы
                elif isinstance(op, Table):
                    edge_data["operation"] = "Reference"

                self.edges.append((edge.from_table, to_table, edge_data))

    def clear(self):
        self.nodes.clear()
        self.edges.clear()
