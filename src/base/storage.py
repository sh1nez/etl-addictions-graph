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
    Create,
    Alter,
    Drop,
)
from typing import Union, Optional, Type
from sqlglot.expressions import Select, DML
from logger_config import logger


class BuffRead:
    pass


class BuffWrite:
    pass


class GraphStorage:
    """Хранилище данных графа зависимостей между SQL-сущностями.

    Attributes:

        nodes (set): Множество узлов графа (имена таблиц/сущностей).
        edges (list): Список рёбер графа в формате (источник, цель, метаданные).
        operator_filter (set): Фильтр типов операторов для отображения.

        COLORS (dict): Сопоставление типов операторов с цветами для визуализации.
            Пример: `{Insert: "red", Select: "purple"}`

            **Важные ключи**:
                - `Insert`: Красный
                - `Select`: Фиолетовый
                - `Join`: Оранжевый

        OPERATOR_MAP (dict): Соответствие строковых имен операторов их классам.
            Пример: `{"INSERT": Insert, "SELECT": Select}`

            **Поддерживаемые операторы**:
                - "INSERT", "UPDATE", "DELETE",
                - "SELECT", "CREATE", "ALTER",
                - "DROP", "MERGE", "JOIN", "TABLE"

    Example:
        >>> storage = GraphStorage()
        >>> storage.set_operator_filter("SELECT,INSERT")
        >>> storage.add_dependencies(dependencies)
    """

    COLORS = {  #: :no-index:
        Insert: "red",
        Update: "green",
        Delete: "blue",
        Merge: "yellow",
        Select: "purple",
        Join: "orange",
        Table: "cyan",
        BuffWrite: "green",
        BuffRead: "blue",
    }  #: :meta private:

    OPERATOR_MAP = {  #: :no-index:
        "INSERT": Insert,
        "UPDATE": Update,
        "DELETE": Delete,
        "SELECT": Select,
        "CREATE": Create,
        "ALTER": Alter,
        "DROP": Drop,
        "MERGE": Merge,
        "JOIN": Join,
        "TABLE": Table,
    }  #: :meta private:

    def __init__(self, ignore_io=False):
        """Инициализирует хранилище с пустыми данными."""
        self.nodes = set()
        self.edges = []
        self.operator_filter = None
        self.ignore_io = ignore_io
        logger.debug("GraphStorage initialized")

    def set_operator_filter(self, operators: Optional[str] = None):
        """Устанавливает фильтр отображаемых операторов.

        Args:
            operators (str, optional): Строка с операторами через запятую.
                Пример: "SELECT,INSERT". Если None, фильтр отключается.

        Example:
            >>> storage.set_operator_filter("UPDATE,DELETE")
        """
        if not operators:
            self.operator_filter = None
            logger.debug("Operator filter cleared - showing all operators")
            return

        operator_names = [op.strip().upper() for op in operators.split(",")]
        self.operator_filter = set()

        for op_name in operator_names:
            if op_name in self.OPERATOR_MAP:
                self.operator_filter.add(self.OPERATOR_MAP[op_name])
                logger.debug(f"Added {op_name} to operator filter")
            else:
                logger.warning(f"Unknown operator '{op_name}' - ignoring")

        logger.info(f"Operator filter set to: {', '.join(operator_names)}")

    def add_dependencies(self, dependencies: defaultdict):
        """Добавляет зависимости в хранилище.

        Args:
            dependencies (defaultdict): Зависимости в формате:
                {цель: [Edge(source, target, op), ...]}

        Example:
            >>> dependencies = defaultdict(set)
            >>> dependencies["table1"].add(Edge("table2", "table1", Insert()))
            >>> storage.add_dependencies(dependencies)
        """
        for to_table, edges in dependencies.items():
            if self.ignore_io and "unknown" in to_table:
                continue
            self.nodes.add(to_table)
            for edge in edges:
                if self.ignore_io and "unknown" in edge.source:
                    continue
                if (
                    hasattr(self, "operator_filter")  # Check if attribute exists
                    and self.operator_filter is not None
                    and type(edge.op) not in self.operator_filter
                ):
                    logger.debug(f"Skipping edge {edge} due to operator filter")
                    continue
                self.nodes.add(edge.source)
                op = edge.op
                op_name = type(op).__name__
                op_color = self.COLORS.get(type(op), "gray")

                edge_data = {"operation": op_name, "color": op_color}

                if edge.is_internal_update:
                    edge_data["operation"] = "InternalUpdate"
                    edge_data["style"] = (
                        "dashed"  # Use dashed line style for self-updates
                    )

                elif isinstance(op, Join):
                    edge_data["operation"] = "Join"
                elif isinstance(op, Table):
                    edge_data["operation"] = "Reference"

                if edge.is_recursive:
                    edge_data["style"] = (
                        "dotted"  # Use dotted line for recursive relationships
                    )
                    edge_data["operation"] = "Recursive"

                self.edges.append((edge.source, to_table, edge_data))
        logger.info(f"Added {len(dependencies)} dependencies")

    def clear(self):
        """Очищает все данные хранилища.

        Example:
            >>> storage.clear()
        """
        self.nodes.clear()
        self.edges.clear()
        logger.debug("GraphStorage cleared")

    def get_filtered_nodes_edges(self):
        """Возвращает отфильтрованные узлы и рёбра.

        Returns:
            Tuple[set, list]: (узлы, рёбра) после применения фильтра.

        Example:
            >>> nodes, edges = storage.get_filtered_nodes_edges()
        """
        if not self.operator_filter:
            return self.nodes, self.edges

        # If we have a filter, we need to recalculate the nodes that should be visible
        filtered_edges = []
        for source, target, data in self.edges:
            # Check if this edge's operation type is in our filter
            # The operation name is stored in the data dict
            op_name = data.get("operation", "")
            for op_class in self.operator_filter:
                if op_class.__name__ == op_name:
                    filtered_edges.append((source, target, data))
                    break

        # Only include nodes that are connected by at least one visible edge
        visible_nodes = set()
        for source, target, _ in filtered_edges:
            visible_nodes.add(source)
            visible_nodes.add(target)

        return visible_nodes, filtered_edges


class Edge:
    """Представляет ребро графа зависимостей между двумя сущностями.

    Attributes:
        source (str): Источник зависимости (таблица/сущность).
        target (str): Цель зависимости.
        op (Union[DML, Select]): Операция, вызывающая зависимость.
        is_internal_update (bool): Флаг внутреннего обновления.
        is_recursive (bool): Флаг рекурсивной зависимости.

    Example:
        >>> edge = Edge("users", "orders", Insert())
        >>> edge.is_recursive = True
    """

    def __init__(
        self,
        from_table: str,
        to_table: str,
        op: Union[DML, Select],
        is_internal_update=False,
    ):
        """Инициализирует ребро зависимости.

        Args:
            from_table (str): Источник зависимости.
            to_table (str): Цель зависимости.
            op (Union[DML, Select]): Операция (например, Insert, Select).
            is_internal_update (bool, optional): Внутреннее обновление. По умолчанию False.
        """
        self.source = from_table  # Изменяем имя атрибута для согласованности
        self.target = to_table  # Изменяем имя атрибута для согласованности
        self.op = op
        self.is_internal_update = is_internal_update
        self.is_recursive = False
        logger.debug(f"Edge created: {from_table} -> {to_table}")

    def __repr__(self):
        """Возвращает строковое представление ребра.

        Returns:
            str: Описание ребра в формате:
                'Edge(source -> target, операция, статус)'

        Example:
            >>> print(Edge("a", "b", Insert()))
            Edge(a -> b, Insert, normal)
        """
        op_type = type(self.op).__name__
        status = "internal" if self.is_internal_update else "normal"
        recursive_status = " (recursive)" if self.is_recursive else ""
        return f"Edge({self.source} -> {self.target}, {op_type}, {status}{recursive_status})"
