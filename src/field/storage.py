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
from logger_config import logger


class ColumnStorage(GraphStorage):
    def add_dependencies(self, dependencies: defaultdict):
        for to_table, edges in dependencies.items():
            self.nodes.add(to_table)
            for edge in edges:
                self.nodes.add(edge.source)
                op = edge.op
                op_name = type(op).__name__
                op_color = self.COLORS.get(type(op), "gray")

                # Создаем словарь с метаданными для ребра
                edge_data = {"operation": op_name, "color": op_color}
                if edge.is_internal_update:
                    edge_data["operation"] = "InternalUpdate"
                    edge_data["style"] = (
                        "dashed"  # Use dashed line style for self-updates
                    )
                # Упрощаем отображение для JOIN - всегда "Join"
                elif isinstance(op, Join):
                    edge_data["operation"] = "Join"

                # Упрощаем отображение для прямых ссылок на таблицы
                elif isinstance(op, Table):
                    edge_data["operation"] = "Reference"

                if edge.is_recursive:
                    edge_data["style"] = (
                        "dotted"  # Use dotted line for recursive relationships
                    )
                    edge_data["operation"] = "Recursive"

                if isinstance(op, Expression) and not isinstance(op, Table):
                    edge_data["columns"] = parse_columns(op)
                    if edge_data["columns"] is None:
                        logger.warning(f"Type of invalid input: {type(op)}")

                self.edges.append((edge.source, to_table, edge_data))
