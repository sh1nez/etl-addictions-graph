from base.storage import GraphStorage
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
from field.columns import parse_columns


class ColumnStorage(GraphStorage):
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

                if isinstance(op, Expression) and not isinstance(op, Table):
                    edge_data["columns"] = parse_columns(op)
                    if edge_data["columns"] is None:
                        print("Type of invalid input:", type(op))

                self.edges.append((edge.from_table, to_table, edge_data))
