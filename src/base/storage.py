from collections import defaultdict
from sqlglot.expressions import Update, Insert, Table, Delete, Merge, Select, Join
from typing import Union
from sqlglot.expressions import Select, DML
from logger_config import logger


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
    logger.debug("Начало добавления зависимостей")
    for to_table, edges in dependencies.items():
        logger.debug(f"Обрабатывается таблица-приёмник: {to_table}")
        self.nodes.add(to_table)
        logger.debug(f"Добавлен узел: {to_table}")

        for edge in edges:
            self.nodes.add(edge.from_table)
            logger.debug(f"Добавлен узел-источник: {edge.from_table}")

            op = edge.op
            op_name = type(op).__name__
            op_color = self.COLORS.get(type(op), "gray")

            edge_data = {"operation": op_name, "color": op_color}

            if isinstance(op, Join):
                edge_data["operation"] = "Join"
                logger.debug(f"Операция Join между {edge.from_table} -> {to_table}")
            elif isinstance(op, Table):
                edge_data["operation"] = "Reference"
                logger.debug(f"Прямая ссылка между {edge.from_table} -> {to_table}")
            else:
                logger.debug(
                    f"Операция {op_name} ({op_color}) между {edge.from_table} -> {to_table}"
                )

            self.edges.append((edge.from_table, to_table, edge_data))
            logger.debug(
                f"Добавлено ребро: {edge.from_table} -> {to_table} с данными {edge_data}"
            )
    logger.debug("Завершено добавление зависимостей")


def clear(self):
    logger.debug("Очистка графа...")
    self.nodes.clear()
    self.edges.clear()
    logger.debug("Граф очищен")


class Edge:
    def __init__(self, from_table: str, to_table: str, op: Union[DML, Select]):
        self.from_table = from_table
        self.to_table = to_table
        self.op = op  # operation
