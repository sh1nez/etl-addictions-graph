from collections import defaultdict
from sqlglot.expressions import (
    Update,
    Insert,
    Table,
    Delete,
    Merge,
    Select,
    Join,
    Expression,
)
from typing import Union
from sqlglot.expressions import Select, DML
from field.columns import parse_columns


class BuffRead:
    pass


class BuffWrite:
    pass


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
        BuffWrite: "green",  # Для прямых ссылок на таблицы
        BuffRead: "blue",  # Для прямых ссылок на таблицы
    }

    def __init__(self, column_mode=False):
        self.nodes = set()
        self.edges = []
        self.column_mode = column_mode

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

                if (
                    self.column_mode
                    and isinstance(op, Expression)
                    and not isinstance(op, Table)
                ):
                    edge_data["columns"] = parse_columns(op)
                    if edge_data["columns"] is None:
                        print("Type of invalid input:", type(op))

                self.edges.append((edge.from_table, to_table, edge_data))

    def clear(self):
        self.nodes.clear()
        self.edges.clear()


class Edge:
    def __init__(self, from_table: str, to_table: str, op: Union[DML, Select]):
        self.from_table = from_table
        self.to_table = to_table
        self.op = op  # operation
