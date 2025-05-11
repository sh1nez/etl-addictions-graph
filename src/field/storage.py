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
    """Хранилище для зависимостей между колонками таблиц.

    Наследует функциональность GraphStorage и добавляет:
        - Анализ зависимостей на уровне колонок
        - Расширенную обработку метаданных для операций

    Attributes:
        nodes (set): Множество таблиц/сущностей
        edges (list): Рёбра зависимостей в формате (источник, цель, метаданные)
        COLORS (dict): Цвета для визуализации операций (наследуется от GraphStorage)
    """

    def add_dependencies(self, dependencies: defaultdict):
        """Добавляет зависимости в хранилище с анализом колонок.

        Args:
            dependencies (defaultdict): Зависимости в формате:
                {"target_table": [Edge(source, target, op),...]}

        Raises:
            TypeError: Если передан неверный тип зависимостей

        Example:
            >>> storage = ColumnStorage()
            >>> deps = defaultdict(set)
            >>> deps["users"].add(Edge("orders", "users", Insert()))
            >>> storage.add_dependencies(deps)
        """

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
