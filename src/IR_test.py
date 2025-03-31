import os
from collections import defaultdict
from typing import List, Optional

import matplotlib.pyplot as plt
import networkx as nx
from sqlglot import parse
from sqlglot.expressions import Insert, Table, Update


class SQLAST:
    """Класс для построения AST SQL-запросов."""

    def __init__(self, sql_code: str):
        self.sql_code = sql_code
        self.parsed = parse(sql_code)
        self.dependencies = self._extract_dependencies()

    def _extract_dependencies(self) -> defaultdict[set[Table, Table]]:
        """Извлекает зависимости между таблицами и операциями."""
        dependencies = defaultdict(set)
        for statement in self.parsed:

            if statement is None:
                continue

            for sub_statement in statement.walk():
                if not isinstance(sub_statement, (Insert, Update)):
                    continue
                if 'this' not in sub_statement.args:
                    raise Exception('Unsupported structure')
                to_table = self.get_table_name(sub_statement)
                from_table = self.get_first_from(sub_statement)
                if from_table is None:
                    from_table = 'input'
                else:
                    from_table = self.get_table_name(from_table)

                dependencies[to_table].add(from_table)

        return dependencies

    def get_dependencies(self)  -> defaultdict[set[Table, Table]]:
        return self.dependencies

    def get_first_from(self, stmt) -> Table:
        if 'from' in stmt.args:
            return stmt.args['from']

        if 'expression' in stmt.args:
            return self.get_first_from(stmt.expression)

        return None

    def get_table_name(self, parsed) -> Table:
        while 'this' in parsed.args:
            if isinstance(parsed, Table):
                return parsed.this.this
            parsed = parsed.this

        raise Exception('No table found')


class SQLTransactionParser:
    """Класс для разбиения SQL-кода на транзакции."""

    def __init__(self, sql_code: str):
        """
        Инициализирует парсер транзакций.

        Args:
            sql_code (str): SQL-код для разбиения на транзакции
        """
        self.sql_code = sql_code.strip() if sql_code else ""
        self.transactions = self._split_transactions()

    def _split_transactions(self) -> List[str]:
        """
        Разбивает SQL-код на транзакции.

        Returns:
            List[str]: Список строк, каждая из которых представляет отдельную транзакцию
        """
        # Проверка на пустой код
        if not self.sql_code:
            return []

        # Если код содержит явные транзакции (BEGIN...COMMIT)
        if "BEGIN" in self.sql_code.upper() and "COMMIT" in self.sql_code.upper():
            # Разделяем по BEGIN...COMMIT
            transactions = []
            code = self.sql_code
            last_position = 0

            # Проверяем, есть ли код до первого BEGIN
            first_begin = code.upper().find("BEGIN")
            if first_begin > 0:
                pre_code = code[:first_begin].strip()
                if pre_code:
                    # Разбиваем код до первого BEGIN по точке с запятой
                    for stmt in [s.strip() for s in pre_code.split(';') if s.strip()]:
                        transactions.append(stmt + ';')

            while "BEGIN" in code.upper():
                begin_index = code.upper().find("BEGIN")
                # Найти соответствующий COMMIT
                commit_index = code.upper().find("COMMIT", begin_index)

                if commit_index == -1:
                    # Если COMMIT не найден, берем весь оставшийся код
                    transactions.append(code[begin_index:])
                    break

                # Добавляем транзакцию (включая COMMIT)
                transaction = code[begin_index:commit_index + len("COMMIT")]
                if transaction.strip():  # Проверка, что транзакция не пустая
                    transactions.append(transaction)

                # Переходим к следующей части кода
                last_position = commit_index + len("COMMIT")
                code = code[last_position:]

            # Проверяем, есть ли код после последнего COMMIT
            if last_position < len(self.sql_code) and code.strip():
                # Разбиваем код после последнего COMMIT по точке с запятой
                for stmt in [s.strip() for s in code.split(';') if s.strip()]:
                    transactions.append(stmt + ';')

            if transactions:
                return transactions

        # Если явных транзакций нет или не удалось разбить по BEGIN...COMMIT, разбиваем по точке с запятой
        statements = [stmt.strip() for stmt in self.sql_code.split(';') if stmt.strip()]
        return [stmt + ';' for stmt in statements]

    def get_transactions(self) -> List[str]:
        """
        Возвращает список транзакций.

        Returns:
            List[str]: Список транзакций
        """
        return self.transactions


class DirectoryParser:
    """Класс для обработки SQL-файлов в директории."""

    def __init__(self, sql_ast, graph):
        self.sql_ast = sql_ast
        self.graph = graph

    def parse_directory(self, directory: str):
        """Парсит все SQL-файлы в указанной директории."""
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".sql"):
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        sql_code = f.read()
                        transaction_parser = SQLTransactionParser(sql_code)
                        transactions = transaction_parser.get_transactions()

                        for transaction in transactions:
                            ast = self.sql_ast(transaction)
                            self.graph.add_dependencies(ast.get_dependencies())

    def separate_parse(self, directory: str):
        """Парсит поочерёдно все SQL-файлы в указанной директории в отдельные графы и отображает их.(для тестирования)"""
        if not os.path.exists(directory):
            print(f"Директория {directory} не существует.")
            return

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".sql"):
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        one_graph = DependencyGraph()
                        sql_code = f.read()
                        transaction_parser = SQLTransactionParser(sql_code)
                        transactions = transaction_parser.get_transactions()

                        for transaction in transactions:
                            ast = self.sql_ast(transaction)
                            one_graph.add_dependencies(ast.get_dependencies())

                        one_graph.visualize(file)


class DependencyGraph:
    """Класс графа зависимостей."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_dependencies(self, dependencies: defaultdict[set[Table, Table]]):
        """Добавляет зависимости в граф."""
        for k, v in dependencies.items():
            for i in v:
                self.graph.add_edge(i, k)

    def visualize(self, title:Optional[str] = None):
        """Визуализирует граф зависимостей."""
        if not self.graph.nodes:
            print("Граф пуст, нет зависимостей для отображения.")
            return

        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_color='lightblue', edge_color='gray', font_size=10,
                node_size=2000)
        if title is not None:
            plt.gcf().canvas.manager.set_window_title(f'DML FILE {title}')
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
    choice = input("Вывести графы зависимости отдельно для каждого файла? (y/n): ")
    if choice.lower() == 'y':
        parser.separate_parse("./dml")
    else:
        parser.parse_directory("./dml")

graph.visualize()
