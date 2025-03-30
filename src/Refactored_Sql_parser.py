import re
import os

import networkx as nx
import sqlparse
from collections import defaultdict
from typing import Optional, Tuple, List

from matplotlib import pyplot as plt

# Try to import sqlglot, but provide fallback if not installed
try:
    from sqlglot import parse, transpile
    from sqlglot.expressions import Update, Insert, Table

    HAS_SQLGLOT = True
except ImportError:
    HAS_SQLGLOT = False
    print("WARNING: sqlglot not installed. Some advanced features will be disabled.")

    # Define placeholder classes to prevent errors
    class DummyExpression:
        def __init__(self):
            self.args = {}
            self.this = None

        def walk(self):
            return []

    class Update(DummyExpression):
        pass

    class Insert(DummyExpression):
        pass

    class Table(DummyExpression):
        pass

    def parse(sql):
        print("sqlglot not installed - parsing disabled")
        return [DummyExpression()]

    def transpile(sql, dialect=None):
        return [sql]

class SQLSyntaxCorrector:
    """
    A class to detect and correct various SQL syntax errors
    """

    def __init__(self):
        """Initialize the SQL Syntax Corrector with keyword dictionaries and patterns"""

        # Common SQL keyword typos and their corrections
        self.keyword_typos = {
            r'\bselct\b': 'SELECT',
            r'\bselecy\b': 'SELECT',
            r'\bselet\b': 'SELECT',
            r'\bform\b': 'FROM',
            r'\bfrmo\b': 'FROM',
            r'\bwhere\b': 'WHERE',
            r'\bwher\b': 'WHERE',
            r'\bwhre\b': 'WHERE',
            r'\bwehere\b': 'WHERE',
            r'\bgropu\b': 'GROUP',
            r'\bgroup bu\b': 'GROUP BY',
            r'\border bu\b': 'ORDER BY',
            r'\bordr by\b': 'ORDER BY',
            r'\border\s+buy\b': 'ORDER BY',
            r'\bhvaing\b': 'HAVING',
            r'\bhaving\b': 'HAVING',
            r'\bjion\b': 'JOIN',
            r'\bjoi\b': 'JOIN',
            r'\bupdat\b': 'UPDATE',
            r'\bdelet\b': 'DELETE',
            r'\bdeleet\b': 'DELETE',
            r'\binsrt\b': 'INSERT',
            r'\binsert\s+in\b': 'INSERT INTO',
            r'\binsert\s+it\b': 'INSERT INTO',
            r'\bcreate\s+tbl\b': 'CREATE TABLE',
            r'\bcreate\s+tble\b': 'CREATE TABLE',
            r'\balter\s+tbl\b': 'ALTER TABLE',
            r'\bdrop\s+tbl\b': 'DROP TABLE',
            r'\binot\b': 'NOT',
            r'\bnto\b': 'NOT',
            r'\bisnull\b': 'IS NULL',
            r'\bis\s+nul\b': 'IS NULL',
            r'\bis\s+not\s+nul\b': 'IS NOT NULL',
            r'\blik\b': 'LIKE',
            r'\bunoin\b': 'UNION',
            r'\bunon\b': 'UNION',
            r'\ball\b': 'ALL',
            r'\bdescing\b': 'DESC',
            r'\bascneding\b': 'ASC',
            r'\bwere\b': 'WHERE',
        }

        # Standard SQL keywords for capitalization
        self.sql_keywords = [
            'SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING',
            'JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN', 'OUTER JOIN', 'FULL JOIN',
            'UPDATE', 'DELETE', 'INSERT INTO', 'CREATE TABLE', 'ALTER TABLE',
            'DROP TABLE', 'AS', 'ON', 'AND', 'OR', 'NOT', 'NULL', 'IS NULL',
            'IS NOT NULL', 'LIKE', 'IN', 'BETWEEN', 'DISTINCT', 'UNION', 'ALL',
            'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'EXISTS', 'WITH', 'VALUES',
            'SET', 'ADD', 'COLUMN', 'INDEX', 'PRIMARY KEY', 'FOREIGN KEY', 'REFERENCES',
            'DEFAULT', 'CASCADE', 'RESTRICT', 'CHECK', 'CONSTRAINT', 'UNIQUE',
            'TEMPORARY', 'IF EXISTS', 'IF NOT EXISTS', 'DESC', 'ASC', 'LIMIT', 'OFFSET'
        ]

        # Sort keywords by length in descending order to prevent partial replacements
        self.sql_keywords.sort(key=len, reverse=True)

        # Function patterns to check for missing parentheses
        self.function_patterns = {
            r'COUNT\s+([^(])': r'COUNT(\1',
            r'SUM\s+([^(])': r'SUM(\1',
            r'AVG\s+([^(])': r'AVG(\1',
            r'MIN\s+([^(])': r'MIN(\1',
            r'MAX\s+([^(])': r'MAX(\1',
            r'COALESCE\s+([^(])': r'COALESCE(\1',
            r'CONCAT\s+([^(])': r'CONCAT(\1',
            r'SUBSTRING\s+([^(])': r'SUBSTRING(\1',
            r'UPPER\s+([^(])': r'UPPER(\1',
            r'LOWER\s+([^(])': r'LOWER(\1',
            r'TRIM\s+([^(])': r'TRIM(\1',
            r'FIRST\s+([^(])': r'FIRST(\1',
            r'LAST\s+([^(])': r'LAST(\1',
            r'LEN\s+([^(])': r'LEN(\1',
            r'LENGTH\s+([^(])': r'LENGTH(\1',
            r'ROUND\s+([^(])': r'ROUND(\1',
            r'DATE\s+([^(])': r'DATE(\1',
            r'NOW\s+([^(])': r'NOW(\1',
            r'DATEDIFF\s+([^(])': r'DATEDIFF(\1',
        }

        # Patterns for string literals that might be missing quotes
        self.string_patterns = [
            (r'(\s*=\s*)([^\'"\d][a-zA-Z0-9_]+)(\s+|;|$)', r'\1\'\2\'\3'),
            (r'(\s+LIKE\s+)([^\'"][a-zA-Z0-9_]+)(\s+|;|$)', r'\1\'\2\'\3'),
            (r'(\bVALUES\s*\()([^\'",\d][a-zA-Z0-9_]+)(,|\))', r'\1\'\2\'\3'),
        ]

        # JOIN syntax patterns
        self.join_patterns = [
            (r'(\bJOIN\b\s+[a-zA-Z0-9_]+\s+)(?!ON\b|USING\b)', r'\1ON '),
            (r'(\bLEFT\s+JOIN\b\s+[a-zA-Z0-9_]+\s+)(?!ON\b|USING\b)', r'\1ON '),
            (r'(\bRIGHT\s+JOIN\b\s+[a-zA-Z0-9_]+\s+)(?!ON\b|USING\b)', r'\1ON '),
            (r'(\bINNER\s+JOIN\b\s+[a-zA-Z0-9_]+\s+)(?!ON\b|USING\b)', r'\1ON '),
            (r'(\bFULL\s+JOIN\b\s+[a-zA-Z0-9_]+\s+)(?!ON\b|USING\b)', r'\1ON '),
        ]

        # Double operator patterns
        self.double_op_patterns = [
            (r'\bAND\s+AND\b', r'AND'),
            (r'\bOR\s+OR\b', r'OR'),
            (r'\bIN\s+IN\b', r'IN'),
            (r'\bIS\s+IS\b', r'IS'),
            (r'\bNOT\s+NOT\b', r'NOT'),
            (r'\bLIKE\s+LIKE\b', r'LIKE'),
        ]

        # Comparison operator patterns
        self.comparison_patterns = [
            (r'\s=\s*=\s', r' = '),
            (r'\s<\s*<\s', r' < '),
            (r'\s>\s*>\s', r' > '),
            (r'\s!\s*=\s', r' != '),
            (r'\s<\s*>\s', r' <> '),
        ]

    def correct_query(self, sql_query: str) -> Tuple[str, List[str]]:
        """
        Main method to correct SQL syntax errors

        Args:
            sql_query (str): The potentially invalid SQL query

        Returns:
            str: Corrected SQL query
            list: List of corrections made
        """
        corrections = []

        # Check if input is empty or None
        if not sql_query or not sql_query.strip():
            return "", ["Empty query provided"]

        # Preprocessing to normalize whitespace and clean up the query
        sql_query = sql_query.strip()

        # Apply all correction methods
        sql_query, typo_corrections = self._fix_keyword_typos(sql_query)
        corrections.extend(typo_corrections)

        sql_query, keyword_corrections = self._standardize_keywords(sql_query)
        corrections.extend(keyword_corrections)

        sql_query, semicolon_corrections = self._fix_semicolons(sql_query)
        corrections.extend(semicolon_corrections)

        sql_query, paren_corrections = self._fix_parentheses(sql_query)
        corrections.extend(paren_corrections)

        sql_query, spacing_corrections = self._fix_spacing(sql_query)
        corrections.extend(spacing_corrections)

        sql_query, function_corrections = self._fix_functions(sql_query)
        corrections.extend(function_corrections)

        sql_query, quotes_corrections = self._fix_string_literals(sql_query)
        corrections.extend(quotes_corrections)

        sql_query, alias_corrections = self._fix_alias_syntax(sql_query)
        corrections.extend(alias_corrections)

        sql_query, join_corrections = self._fix_join_syntax(sql_query)
        corrections.extend(join_corrections)

        sql_query, clause_corrections = self._fix_incomplete_clauses(sql_query)
        corrections.extend(clause_corrections)

        sql_query, operator_corrections = self._fix_operators(sql_query)
        corrections.extend(operator_corrections)

        sql_query, quote_balance_corrections = self._fix_quote_balance(sql_query)
        corrections.extend(quote_balance_corrections)

        # If no corrections were made, note that
        if not corrections:
            corrections.append("No syntax errors detected")

        # Apply final formatting
        try:
            sql_query = sqlparse.format(sql_query, reindent=True, keyword_case='upper')
        except Exception as e:
            # If formatting fails, keep the current query
            corrections.append(f"Warning: Formatting failed - {str(e)}")

        return sql_query, corrections

    def _fix_keyword_typos(self, sql_query):
        """Fix common typos in SQL keywords"""
        corrections = []

        for typo, correction in self.keyword_typos.items():
            if re.search(typo, sql_query, re.IGNORECASE):
                original_text = re.search(typo, sql_query, re.IGNORECASE).group()
                sql_query = re.sub(typo, correction, sql_query, flags=re.IGNORECASE)
                corrections.append(f"Corrected typo: '{original_text}' to '{correction}'")

        return sql_query, corrections

    def _standardize_keywords(self, sql_query):
        """Standardize SQL keyword casing to uppercase"""
        corrections = []

        for keyword in self.sql_keywords:
            # Create a regex pattern that matches the keyword case-insensitively and as whole words
            keyword_pattern = r'\b' + re.escape(keyword.replace(' ', r'\s+')) + r'\b'
            matches = re.finditer(keyword_pattern, sql_query, re.IGNORECASE)

            for match in matches:
                if match.group().upper() != keyword:
                    matched_text = match.group()
                    # Fix the index calculation for replacement
                    old_query = sql_query
                    sql_query = sql_query[:match.start()] + keyword + sql_query[match.end():]
                    if old_query != sql_query:  # Only add correction if something changed
                        corrections.append(f"Standardized keyword: '{matched_text}' to '{keyword}'")

        return sql_query, corrections

    def _fix_semicolons(self, sql_query):
        """Fix issues with semicolons"""
        corrections = []

        if sql_query.count(';') > 1:
            # Multiple semicolons - keep only the last one assuming it's a single statement
            original_count = sql_query.count(';')
            sql_query = sql_query.replace(';', ' ', original_count - 1).replace('  ', ' ')
            # Only add the last semicolon at the end
            sql_query = sql_query.rstrip('; ') + ';'
            corrections.append(f"Removed {original_count - 1} extra semicolons")

        if not sql_query.strip().endswith(';'):
            sql_query = sql_query.strip() + ';'
            corrections.append("Added missing semicolon at the end")

        return sql_query, corrections

    def _fix_parentheses(self, sql_query):
        """Balance parentheses in the query"""
        corrections = []

        open_parens = sql_query.count('(')
        close_parens = sql_query.count(')')

        if open_parens > close_parens:
            sql_query = sql_query.rstrip(';') + ')' * (open_parens - close_parens) + ';'
            corrections.append(f"Added {open_parens - close_parens} missing closing parentheses")
        elif close_parens > open_parens:
            # Try to find and remove extra closing parentheses
            excess = close_parens - open_parens
            pattern = r'\)(\s*\))'
            found = 0
            for _ in range(excess):
                if re.search(pattern, sql_query):
                    sql_query = re.sub(pattern, ')', sql_query, count=1)
                    found += 1
            corrections.append(f"Removed {found} extra closing parentheses")

        return sql_query, corrections

    def _fix_spacing(self, sql_query):
        """Fix spacing issues, especially after commas"""
        corrections = []

        if re.search(r',\S', sql_query):
            old_query = sql_query
            sql_query = re.sub(r',(\S)', r', \1', sql_query)
            if old_query != sql_query:
                corrections.append("Added missing spaces after commas")

        return sql_query, corrections

    def _fix_functions(self, sql_query):
        """Fix function syntax issues (missing parentheses)"""
        corrections = []

        for pattern, replacement in self.function_patterns.items():
            if re.search(pattern, sql_query, re.IGNORECASE):
                old_query = sql_query
                sql_query = re.sub(pattern, replacement, sql_query, flags=re.IGNORECASE)
                if old_query != sql_query:
                    corrections.append("Fixed function syntax by adding missing parentheses")

        return sql_query, corrections

    def _fix_string_literals(self, sql_query):
        """Add missing quotes around string literals"""
        corrections = []

        for pattern, replacement in self.string_patterns:
            if re.search(pattern, sql_query, re.IGNORECASE):
                old_query = sql_query
                sql_query = re.sub(pattern, replacement, sql_query, flags=re.IGNORECASE)
                if old_query != sql_query:
                    corrections.append("Added missing quotes around string literals")

        return sql_query, corrections

    def _fix_alias_syntax(self, sql_query):
        """Fix incorrect table alias syntax"""
        corrections = []

        alias_pattern = r'(\s+FROM\s+[a-zA-Z0-9_]+)(\s+)([a-zA-Z][a-zA-Z0-9_]*)(\s+)'
        if re.search(alias_pattern, sql_query, re.IGNORECASE):
            old_query = sql_query
            sql_query = re.sub(alias_pattern, r'\1 AS \3\4', sql_query, flags=re.IGNORECASE)
            if old_query != sql_query:
                corrections.append("Added missing AS in table alias")

        return sql_query, corrections

    def _fix_join_syntax(self, sql_query):
        """Fix issues with JOIN syntax"""
        corrections = []

        for pattern, replacement in self.join_patterns:
            if re.search(pattern, sql_query, re.IGNORECASE):
                old_query = sql_query
                sql_query = re.sub(pattern, replacement, sql_query, flags=re.IGNORECASE)
                if old_query != sql_query:
                    corrections.append("Added missing ON clause after JOIN")

        return sql_query, corrections

    def _fix_incomplete_clauses(self, sql_query):
        """Fix incomplete clauses like GROUP BY, ORDER BY, WHERE without condition"""
        corrections = []

        # Fix GROUP BY without column specification
        gb_pattern = r'\bGROUP\s+BY\s*$'
        if re.search(gb_pattern, sql_query, re.IGNORECASE):
            old_query = sql_query
            sql_query = re.sub(gb_pattern, '', sql_query, flags=re.IGNORECASE)
            if old_query != sql_query:
                corrections.append("Removed incomplete GROUP BY clause")

        # Fix ORDER BY without column specification
        ob_pattern = r'\bORDER\s+BY\s*$'
        if re.search(ob_pattern, sql_query, re.IGNORECASE):
            old_query = sql_query
            sql_query = re.sub(ob_pattern, '', sql_query, flags=re.IGNORECASE)
            if old_query != sql_query:
                corrections.append("Removed incomplete ORDER BY clause")

        # Fix WHERE without condition
        where_pattern = r'\bWHERE\s*(?:;|$)'
        if re.search(where_pattern, sql_query, re.IGNORECASE):
            old_query = sql_query
            sql_query = re.sub(where_pattern, ';', sql_query, flags=re.IGNORECASE)
            if old_query != sql_query:
                corrections.append("Removed WHERE clause without condition")

        # Fix missing FROM in SELECT
        # Check first if there's a SELECT statement but no FROM clause
        if 'SELECT' in sql_query.upper() and 'FROM' not in sql_query.upper():
            select_pattern = r'\bSELECT\b.+(?!\bFROM\b).+\b(?:GROUP BY|ORDER BY|HAVING|LIMIT|;)'
            if re.search(select_pattern, sql_query, re.IGNORECASE):
                old_query = sql_query
                try:
                    sql_query = re.sub(r'(\bSELECT\b.+?)(\b(?:GROUP BY|ORDER BY|HAVING|LIMIT|;))',
                                       r'\1 FROM dual \2', sql_query, flags=re.IGNORECASE)
                    if old_query != sql_query:
                        corrections.append("Added missing FROM clause to SELECT statement")
                except Exception as e:
                    corrections.append(f"Error fixing FROM clause: {str(e)}")

        return sql_query, corrections

    def _fix_operators(self, sql_query):
        """Fix issues with operators (double operators, comparison operators)"""
        corrections = []

        # Fix double operators (e.g., AND AND, OR OR)
        for pattern, replacement in self.double_op_patterns:
            if re.search(pattern, sql_query, re.IGNORECASE):
                old_query = sql_query
                sql_query = re.sub(pattern, replacement, sql_query, flags=re.IGNORECASE)
                if old_query != sql_query:
                    corrections.append("Removed duplicate operators")

        # Fix comparison operator issues
        for pattern, replacement in self.comparison_patterns:
            if re.search(pattern, sql_query):
                old_query = sql_query
                sql_query = re.sub(pattern, replacement, sql_query)
                if old_query != sql_query:
                    corrections.append("Fixed duplicate comparison operators")

        return sql_query, corrections

    def _fix_quote_balance(self, sql_query):
        """Balance quotes in the query"""
        corrections = []

        # Fix single quote issues
        single_quotes = sql_query.count("'")
        if single_quotes % 2 != 0:
            # Add a closing quote at the end of the query before the semicolon
            sql_query = sql_query.rstrip(';') + "'" + ";"
            corrections.append("Added missing closing single quote")

        # Fix double quote issues for identifiers
        double_quotes = sql_query.count('"')
        if double_quotes % 2 != 0:
            # Add a closing double quote at an appropriate place
            sql_query = sql_query.rstrip(';') + '"' + ";"
            corrections.append("Added missing closing double quote")

        return sql_query, corrections

class GraphStorage:
    """Class for storing dependency graph data."""

    def __init__(self):
        self.nodes = set()
        self.edges = []

    def add_dependencies(self, dependencies: defaultdict):
        """Adds dependencies to the storage."""
        for to_table, from_tables in dependencies.items():
            self.nodes.add(to_table)
            for from_table in from_tables:
                self.nodes.add(from_table)
                self.edges.append((from_table, to_table))

    def clear(self):
        """Clears the graph storage."""
        self.nodes.clear()
        self.edges.clear()

class GraphVisualizer:
    """Class for visualizing dependency graphs."""

    def render(self, storage: GraphStorage, title: Optional[str] = None):
        """Visualizes the dependency graph."""
        if not storage.nodes:
            print("Graph is empty, no dependencies to display.")
            return

        G = nx.DiGraph()
        G.add_nodes_from(storage.nodes)
        G.add_edges_from(storage.edges)

        plt.figure(figsize=(10, 6))
        try:
            pos = nx.spring_layout(G)
            nx.draw(G, pos, with_labels=True, node_color='lightblue',
                    edge_color='gray', font_size=10, node_size=2000)

            if title:
                plt.title(title)

            plt.show()
        except Exception as e:
            print(f"Error visualizing graph: {e}")
            print("You may need to run this in an environment that supports matplotlib display.")

class EnhancedSQLCorrector:
    """Enhanced SQL corrector class that combines syntax correction with SQL transpilation."""

    def __init__(self):
        self.syntax_corrector = SQLSyntaxCorrector()

    def correct(self, sql_code: str) -> Tuple[str, List[str]]:
        """
        Correct SQL code using both syntax correction and SQL transpilation.

        Args:
            sql_code (str): SQL code to correct

        Returns:
            Tuple[str, List[str]]: Corrected SQL code and list of corrections made
        """
        # Check if input is valid
        if not sql_code or not isinstance(sql_code, str):
            return "", ["Invalid input: Not a valid SQL string"]

        # First apply syntax corrections
        corrected_sql, corrections = self.syntax_corrector.correct_query(sql_code)

        # Then try to apply sqlglot transpilation for dialect standardization if available
        if HAS_SQLGLOT:
            try:
                transpiled_sql = transpile(corrected_sql, dialect='mysql')[0]
                if transpiled_sql != corrected_sql:
                    corrections.append("Standardized SQL dialect to MySQL")
                return transpiled_sql, corrections
            except Exception as e:
                # If transpilation fails, return the syntax-corrected version
                corrections.append(f"Transpilation failed: {str(e)}")
                return corrected_sql, corrections
        else:
            corrections.append("sqlglot not installed - transpilation skipped")
            return corrected_sql, corrections

class SQLAST:
    """Class for building AST of SQL queries."""

    def __init__(self, sql_code: str):
        self.corrector = EnhancedSQLCorrector()

        # Validate input
        if not sql_code or not isinstance(sql_code, str):
            self.corrected_sql = ""
            self.corrections = ["Invalid input: Not a valid SQL string"]
            self.sql_code = ""
            self.parsed = None
            self.dependencies = defaultdict(set)
            return

        self.corrected_sql, self.corrections = self.corrector.correct(sql_code)
        self.sql_code = self.corrected_sql

        if not HAS_SQLGLOT:
            self.parsed = None
            self.dependencies = defaultdict(set)
            self.corrections.append("sqlglot not installed - dependency extraction skipped")
            return

        try:
            self.parsed = parse(self.corrected_sql)
            self.dependencies = self._extract_dependencies()
        except Exception as e:
            print(f"Error parsing SQL: {e}")
            # Create empty dependencies if parsing fails
            self.parsed = None
            self.dependencies = defaultdict(set)
            self.corrections.append(f"Error parsing SQL: {str(e)}")

    def _extract_dependencies(self) -> defaultdict:
        """Extracts dependencies between tables and operations."""
        dependencies = defaultdict(set)
        if not self.parsed or not HAS_SQLGLOT:
            return dependencies

        try:
            for statement in self.parsed:
                for sub_statement in statement.walk():
                    if not isinstance(sub_statement, (Insert, Update)):
                        continue
                    if 'this' not in sub_statement.args:
                        continue  # Skip unsupported structures without raising exception
                    try:
                        to_table = self.get_table_name(sub_statement)
                        from_table = self.get_first_from(sub_statement) or 'input'
                        dependencies[to_table].add(from_table)
                    except Exception as e:
                        print(f"Error extracting dependencies: {e}")
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
            if 'from' in stmt.args:
                return self.get_table_name(stmt.args['from'])
            if 'expression' in stmt.args:
                return self.get_first_from(stmt.args['expression'])
        except Exception as e:
            print(f"Error in get_first_from: {e}")
        return None

    def get_table_name(self, parsed) -> str:
        if not HAS_SQLGLOT:
            return "unknown"

        try:
            counter = 0  # Prevent infinite loops
            while 'this' in parsed.args and counter < 100:
                counter += 1
                if isinstance(parsed, Table):
                    return parsed.args['this'].args['this']
                parsed = parsed.args['this']
            raise Exception('No table found')
        except Exception as e:
            print(f"Error in get_table_name: {e}")
            return "unknown"

class DirectoryParser:
    """Class for processing SQL files in a directory."""

    def __init__(self, sql_ast_cls):
        self.sql_ast_cls = sql_ast_cls

    def parse_directory(self, directory: str) -> List[Tuple[defaultdict, List[str], str]]:
        """
        Parses all SQL files in the specified directory and returns dependencies and corrections.

        Returns:
            List[Tuple[defaultdict, List[str], str]]: List of tuples containing (dependencies, corrections, file_path)
        """
        results = []
        # Check if directory exists
        if not os.path.exists(directory):
            print(f"Error: Directory {directory} does not exist!")
            return results
        # Check if it's readable
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
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            sql_code = f.read()
                            ast = self.sql_ast_cls(sql_code)
                            results.append((ast.get_dependencies(), ast.get_corrections(), file_path))
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")
                        # Add empty results to maintain consistency
                        results.append((defaultdict(set), [f"Error: {str(e)}"], file_path))
        return results

class GraphManager:
    """Class for managing graph building and visualization components."""

    def __init__(self):
        self.storage = GraphStorage()
        self.visualizer = GraphVisualizer()
        self.parser = DirectoryParser(SQLAST)

    def process_sql(self, sql_code: str) -> List[str]:
        """
        Processes SQL code and adds dependencies to storage.

        Returns:
            List[str]: List of corrections made
        """
        ast = SQLAST(sql_code)
        self.storage.add_dependencies(ast.get_dependencies())
        return ast.get_corrections()

    def process_directory(self, directory_path: str) -> List[Tuple[str, List[str]]]:
        """
        Processes SQL files in a directory and adds dependencies to storage.

        Returns:
            List[Tuple[str, List[str]]]: List of (file_path, corrections) tuples
        """
        results = []
        parse_results = self.parser.parse_directory(directory_path)
        for dependencies, corrections, file_path in parse_results:
            self.storage.add_dependencies(dependencies)
            results.append((file_path, corrections))
        return results

    def visualize(self, title: Optional[str] = None):
        """Visualizes the dependency graph."""
        self.visualizer.render(self.storage, title)

def main():
    manager = GraphManager()
    print("SQL Syntax Corrector and Dependency Analyzer")
    print("-------------------------------------------")

    choice = input("Would you like to enter SQL code manually? (y/n): ")
    if choice.lower() == 'y':
        sql_code = input("Enter your SQL code: ")
        corrections = manager.process_sql(sql_code)

        print("\nCorrections made:")
        for i, correction in enumerate(corrections, 1):
            print(f"{i}. {correction}")

        manager.visualize("Dependencies Graph")
    else:
        directory = input("Enter the directory path containing SQL files: ")
        choice = input("Display graphs separately for each file? (y/n): ")

        if choice.lower() == 'y':
            parse_results = manager.parser.parse_directory(directory)
            for dependencies, corrections, file_path in parse_results:
                print(f"\nFile: {file_path}")
                print("Corrections made:")
                for i, correction in enumerate(corrections, 1):
                    print(f"{i}. {correction}")

                temp_storage = GraphStorage()
                temp_storage.add_dependencies(dependencies)
                manager.visualizer.render(temp_storage, f"Dependencies for {os.path.basename(file_path)}")
        else:
            results = manager.process_directory(directory)

            for file_path, corrections in results:
                print(f"\nFile: {file_path}")
                print("Corrections made:")
                for i, correction in enumerate(corrections, 1):
                    print(f"{i}. {correction}")

            manager.visualize("Full Dependencies Graph")

if __name__ == "__main__":
    main()
