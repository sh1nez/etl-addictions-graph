import os
import networkx as nx
from collections import defaultdict
from typing import Optional, Tuple, List
from matplotlib import pyplot as plt
from sqlglot import parse, transpile
from sqlglot.expressions import Update, Insert, Table, Delete, Merge, Select

HAS_SQLGLOT = True  # TODO remove it


class GraphStorage:
    """Class for storing dependency graph data."""

    def __init__(self):
        self.nodes = set()
        self.edges = []

    def add_dependencies(self, dependencies: defaultdict):
        for to_table, from_tables in dependencies.items():
            self.nodes.add(to_table)
            for from_table in from_tables:
                self.nodes.add(from_table)
                self.edges.append((from_table, to_table))

    def clear(self):
        self.nodes.clear()
        self.edges.clear()


class GraphVisualizer:
    """Class for visualizing dependency graphs."""

    def render(self, storage: GraphStorage, title: Optional[str] = None):
        if not storage.nodes:
            print("Graph is empty, no dependencies to display.")
            return
        G = nx.DiGraph()
        G.add_nodes_from(storage.nodes)
        G.add_edges_from(storage.edges)
        plt.figure(figsize=(10, 6))
        try:
            pos = nx.spring_layout(G)
            nx.draw(
                G,
                pos,
                with_labels=True,
                node_color="lightblue",
                edge_color="gray",
                font_size=10,
                node_size=2000,
            )
            if title:
                plt.title(title)
            plt.show()
        except Exception as e:
            print(f"Error visualizing graph: {e}")
            print(
                "You may need to run this in an environment that supports matplotlib display."
            )


class SqlAst:
    """Class for building AST of SQL queries."""

    def __init__(self, sql_code: str):
        # self.corrector = EnhancedSQLCorrector()
        if not sql_code or not isinstance(sql_code, str):
            self.corrected_sql = ""
            self.corrections = ["Invalid input: Not a valid SQL string"]
            self.sql_code = ""
            self.parsed = None
            self.dependencies = defaultdict(set)
            return
        self.corrections = []
        self.sql_code = sql_code
        self.corrected_sql = self.sql_code
        self.dependencies = defaultdict(set)
        # self.corrected_sql, self.corrections = self.corrector.correct(sql_code)
        # self.sql_code = self.corrected_sql
        if not HAS_SQLGLOT:
            self.parsed = None
            self.dependencies = defaultdict(set)
            self.corrections.append(
                "sqlglot not installed - dependency extraction skipped"
            )
            return
        try:
            self.parsed = parse(self.corrected_sql)
            self.dependencies = self._extract_dependencies()
        except Exception as e:
            print(f"Error parsing SQL: {e}")
            self.parsed = None
            self.dependencies = defaultdict(set)
            self.corrections.append(f"Error parsing SQL: {str(e)}")

    def _extract_dependencies(self) -> defaultdict:
        """Extracts dependencies between tables and operations including ETL and SELECT queries."""
        dependencies = defaultdict(set)
        if not self.parsed or not HAS_SQLGLOT:
            return dependencies
        etl_types = (Insert, Update, Delete, Merge)
        try:
            for statement in self.parsed:
                for sub_statement in statement.walk():
                    if isinstance(sub_statement, etl_types):
                        if "this" not in sub_statement.args:
                            continue
                        try:
                            to_table = self.get_table_name(sub_statement)
                            from_table = self.get_first_from(sub_statement) or "input"
                            dependencies[to_table].add(from_table)
                        except Exception as e:
                            print(f"Error extracting dependencies: {e}")
                    elif isinstance(sub_statement, Select):
                        # Если есть конструкция INTO, обрабатываем как SELECT INTO
                        if (
                            hasattr(sub_statement, "into")
                            and sub_statement.into is not None
                        ):
                            try:
                                to_table = self.get_table_name(sub_statement.into)
                                from_table = (
                                    self.get_first_from(sub_statement) or "input"
                                )
                                dependencies[to_table].add(from_table)
                            except Exception as e:
                                print(f"Error extracting SELECT INTO dependencies: {e}")
                        else:
                            # Для обычного SELECT, считаем целевым псевдо-таблицу "result"
                            try:
                                from_table = (
                                    self.get_first_from(sub_statement) or "input"
                                )
                                dependencies["result"].add(from_table)
                            except Exception as e:
                                print(f"Error extracting SELECT dependency: {e}")
        except Exception as e:
            print(f"Error in dependency extraction: {e}")
        return dependencies

    def get_dependencies(self) -> defaultdict:
        return self.dependencies

    def get_corrections(self) -> List[str]:
        return self.corrections

    def get_first_from(self, stmt) -> Optional[str]:
        if not HAS_SQLGLOT:
            return None
        try:
            if "from" in stmt.args:
                return self.get_table_name(stmt.args["from"])
            if "expression" in stmt.args:
                return self.get_first_from(stmt.args["expression"])
        except Exception as e:
            print(f"Error in get_first_from: {e}")
        return None

    def get_table_name(self, parsed) -> str:
        if not HAS_SQLGLOT:
            return "unknown"
        try:
            counter = 0
            while "this" in parsed.args and counter < 100:
                counter += 1
                if isinstance(parsed, Table):
                    return parsed.args["this"].args["this"]
                parsed = parsed.args["this"]
            raise Exception("No table found")
        except Exception as e:
            print(f"Error in get_table_name: {e}")
            return "unknown"


class SQLTransactionParser:
    """Class for splitting SQL code into transactions."""

    def __init__(self, sql_code: str):
        """
        Initialize the transaction parser.

        Args:
            sql_code (str): SQL code to split into transactions
        """
        self.sql_code = sql_code.strip() if sql_code else ""
        self.transactions = self._split_transactions()

    def _split_transactions(self) -> List[str]:
        """
        Split SQL code into transactions.

        Returns:
            List[str]: List of strings, each representing a separate transaction
        """
        # Check for empty code
        if not self.sql_code:
            return []

        # If the code contains explicit transactions (BEGIN...COMMIT)
        if "BEGIN" in self.sql_code.upper() and "COMMIT" in self.sql_code.upper():
            # Split by BEGIN...COMMIT
            transactions = []
            code = self.sql_code
            last_position = 0

            # Check if there's any code before the first BEGIN
            first_begin = code.upper().find("BEGIN")
            if first_begin > 0:
                pre_code = code[:first_begin].strip()
                if pre_code:
                    # Split the code before the first BEGIN by semicolon
                    for stmt in [s.strip() for s in pre_code.split(';') if s.strip()]:
                        transactions.append(stmt + ';')

            while "BEGIN" in code.upper():
                begin_index = code.upper().find("BEGIN")
                # Find the corresponding COMMIT
                commit_index = code.upper().find("COMMIT", begin_index)

                if commit_index == -1:
                    # If COMMIT isn't found, take all the remaining code
                    transactions.append(code[begin_index:])
                    break

                # Add the transaction (including COMMIT)
                transaction = code[begin_index:commit_index + len("COMMIT")]
                if transaction.strip():  # Check if the transaction isn't empty
                    transactions.append(transaction)

                # Move to the next part of the code
                last_position = commit_index + len("COMMIT")
                code = code[last_position:]

            # Check if there's any code after the last COMMIT
            if last_position < len(self.sql_code) and code.strip():
                # Split the code after the last COMMIT by semicolon
                for stmt in [s.strip() for s in code.split(';') if s.strip()]:
                    transactions.append(stmt + ';')

            if transactions:
                return transactions

        # If there are no explicit transactions or couldn't split by BEGIN...COMMIT, split by semicolon
        statements = [stmt.strip() for stmt in self.sql_code.split(';') if stmt.strip()]
        return [stmt + ';' for stmt in statements]

    def get_transactions(self) -> List[str]:
        """
        Return the list of transactions.

        Returns:
            List[str]: List of transactions
        """
        return self.transactions


class DirectoryParser:
    """Class for processing SQL files in a directory."""

    def __init__(self, sql_ast_cls):
        self.sql_ast_cls = sql_ast_cls

    def parse_directory(
        self, directory: str
    ) -> List[Tuple[defaultdict, List[str], str]]:
        results = []  # maybe hashmap better??
        if not os.path.exists(directory):
            print(f"Error: Directory {directory} does not exist!")
            return results
        if not os.path.isdir(directory):
            print(f"Error: {directory} is not a directory!")
            return results
        print(f"Processing files in directory: {directory}")
        for root, _, files in os.walk(directory):
            print(f"Processing directory: {root}")
            for file in files:
                if file.endswith(".sql"):
                    file_path = os.path.join(root, file)
                    print(f"Reading file: {file_path}")
                    try:  # TODO with заменяет трай кетч блок, насколько я знаю, заменить
                        with open(file_path, "r", encoding="utf-8") as f:
                            sql_code = f.read()
                            # Use SQLTransactionParser to split the file into transactions
                            transaction_parser = SQLTransactionParser(sql_code)
                            transactions = transaction_parser.get_transactions()

                            # Process each transaction and combine dependencies
                            combined_dependencies = defaultdict(set)
                            all_corrections = []

                            for i, transaction in enumerate(transactions, 1):
                                ast = self.sql_ast_cls(transaction)
                                trans_dependencies = ast.get_dependencies()
                                trans_corrections = ast.get_corrections()

                                # Add transaction number to correction messages
                                if trans_corrections:
                                    all_corrections.extend([f"Transaction {i}: {corr}" for corr in trans_corrections])

                                # Combine dependencies from all transactions
                                for to_table, from_tables in trans_dependencies.items():
                                    combined_dependencies[to_table].update(from_tables)

                            results.append(
                                (
                                    combined_dependencies,
                                    all_corrections,
                                    file_path,
                                )
                            )
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")
                        results.append(
                            (defaultdict(set), [f"Error: {str(e)}"], file_path)
                        )
        return results


class GraphManager:
    """Class for managing graph building and visualization components."""

    def __init__(self):
        self.storage = GraphStorage()
        self.visualizer = GraphVisualizer()
        self.parser = DirectoryParser(SqlAst)

    def process_sql(self, sql_code: str) -> List[str]:
        """
        Process SQL code by splitting it into transactions and analyzing each one.

        Args:
            sql_code (str): SQL code to process

        Returns:
            List[str]: List of corrections from all transactions
        """
        # Use SQLTransactionParser to split code into transactions
        transaction_parser = SQLTransactionParser(sql_code)
        transactions = transaction_parser.get_transactions()

        all_corrections = []

        # Process each transaction
        for i, transaction in enumerate(transactions, 1):
            ast = SqlAst(transaction)
            self.storage.add_dependencies(ast.get_dependencies())

            # Add transaction number to correction messages
            corrections = ast.get_corrections()
            if corrections:
                all_corrections.extend([f"Transaction {i}: {corr}" for corr in corrections])

        return all_corrections

    def process_directory(self, directory_path: str) -> List[Tuple[str, List[str]]]:
        results = []  # maybe hashmap better??
        parse_results = self.parser.parse_directory(directory_path)
        for dependencies, corrections, file_path in parse_results:
            self.storage.add_dependencies(dependencies)
            results.append((file_path, corrections))
        return results

    def visualize(self, title: Optional[str] = None):
        self.visualizer.render(self.storage, title)


def main():
    manager = GraphManager()
    print("SQL Syntax Corrector and Dependency Analyzer")
    print("-------------------------------------------")
    choice = input("Would you like to enter SQL code manually? (y/n): ")
    if choice.lower() == "y":
        print("Enter your SQL code (type 'END' on a new line to finish):")
        sql_lines = []
        while True:
            line = input()
            if line.upper() == "END":
                break
            sql_lines.append(line)
        sql_code = "\n".join(sql_lines)
        corrections = manager.process_sql(sql_code)
        if corrections:
            print("\nCorrections made:")
            for i, correction in enumerate(corrections, 1):
                print(f"{i}. {correction}")
        manager.visualize("Dependencies Graph")
    else:
        directory = input("Enter the directory path containing SQL files: ")
        choice = input("Display graphs separately for each file? (y/n): ")
        if choice.lower() == "y":
            parse_results = manager.parser.parse_directory(directory)
            for dependencies, corrections, file_path in parse_results:
                print(f"\nFile: {file_path}")
                if corrections:
                    print("Corrections made:")
                    for i, correction in enumerate(corrections, 1):
                        print(f"{i}. {correction}")
                temp_storage = GraphStorage()
                temp_storage.add_dependencies(dependencies)
                manager.visualizer.render(
                    temp_storage, f"Dependencies for {os.path.basename(file_path)}"
                )
        else:
            results = manager.process_directory(directory)
            for file_path, corrections in results:
                print(f"\nFile: {file_path}")
                if corrections:
                    print("Corrections made:")
                    for i, correction in enumerate(corrections, 1):
                        print(f"{i}. {correction}")
            manager.visualize("Full Dependencies Graph")


if __name__ == "__main__":
    main()
