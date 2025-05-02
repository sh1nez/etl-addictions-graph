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
from logger_config import logger


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
        Table: "cyan",
        BuffWrite: "green",
        BuffRead: "blue",
    }

    def __init__(self):
        self.nodes = set()
        self.edges = []
        logger.debug("GraphStorage initialized")

    def add_dependencies(self, dependencies: defaultdict):
        for to_table, edges in dependencies.items():
            self.nodes.add(to_table)
            for edge in edges:
                self.nodes.add(edge.from_table)
                op = edge.op
                op_name = type(op).__name__
                op_color = self.COLORS.get(type(op), "gray")

                edge_data = {"operation": op_name, "color": op_color}

                if isinstance(op, Join):
                    edge_data["operation"] = "Join"
                elif isinstance(op, Table):
                    edge_data["operation"] = "Reference"

                self.edges.append((edge.from_table, to_table, edge_data))
        logger.info(f"Added {len(dependencies)} dependencies")

    def clear(self):
        self.nodes.clear()
        self.edges.clear()
        logger.debug("GraphStorage cleared")


class Edge:
    def __init__(self, from_table: str, to_table: str, op: Union[DML, Select]):
        self.from_table = from_table
        self.to_table = to_table
        self.op = op
        logger.debug(f"Edge created: {from_table} -> {to_table}")
