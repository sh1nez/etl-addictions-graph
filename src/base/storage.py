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
from util.request_counter import get_analiz
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
        self.edge_widths = {}
        logger.debug("GraphStorage initialized")

    def add_dependencies(self, dependencies: defaultdict):
        for to_table, edges in dependencies.items():
            self.nodes.add(to_table)
            for edge in edges:
                self.nodes.add(edge.from_table)
                op = edge.op
                op_name = type(op).__name__
                op_color = self.COLORS.get(type(op), "gray")

                edge_data = {
                    "operation": op_name,
                    "color": op_color,
                    "width": self.edge_widths.get(op_name, 1.0),  # Add width
                }

                if isinstance(op, Join):
                    edge_data["operation"] = "Join"
                elif isinstance(op, Table):
                    edge_data["operation"] = "Reference"

                if op_name in self.edge_widths:
                    edge_data["width"] = self.edge_widths[op_name]
                else:
                    edge_data["width"] = 1.0

                self.edges.append((edge.from_table, to_table, edge_data))
        logger.info(f"Added {len(dependencies)} dependencies")

    def set_edge_widths(self, file_path: str):
        _, edge_widths = get_analiz(file_path)
        self.edge_widths = edge_widths

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
