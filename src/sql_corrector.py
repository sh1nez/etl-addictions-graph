import re
import sqlparse
from typing import  Tuple,List
from sqlglot import transpile
HAS_SQLGLOT=True

class SQLSyntaxCorrector:
    """
    A class to detect and correct various SQL syntax errors
    """
    def __init__(self):
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

        self.sql_keywords.sort(key=len, reverse=True)

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

        self.string_patterns = [
            (r'(\s*=\s*)([^\'"\d][a-zA-Z0-9_]+)(\s+|;|$)', r'\1\'\2\'\3'),
            (r'(\s+LIKE\s+)([^\'"][a-zA-Z0-9_]+)(\s+|;|$)', r'\1\'\2\'\3'),
            (r'(\bVALUES\s*\()([^\'",\d][a-zA-Z0-9_]+)(,|\))', r'\1\'\2\'\3'),
        ]

        self.join_patterns = [
            (r'(\bJOIN\s+[a-zA-Z0-9_]+\s+)(?!ON\b|USING\b)', r'\1ON '),
            (r'(\bLEFT\s+JOIN\s+[a-zA-Z0-9_]+\s+)(?!ON\b|USING\b)', r'\1ON '),
            (r'(\bRIGHT\s+JOIN\s+[a-zA-Z0-9_]+\s+)(?!ON\b|USING\b)', r'\1ON '),
            (r'(\bINNER\s+JOIN\s+[a-zA-Z0-9_]+\s+)(?!ON\b|USING\b)', r'\1ON '),
            (r'(\bFULL\s+JOIN\s+[a-zA-Z0-9_]+\s+)(?!ON\b|USING\b)', r'\1ON '),
        ]

        self.double_op_patterns = [
            (r'\bAND\s+AND\b', r'AND'),
            (r'\bOR\s+OR\b', r'OR'),
            (r'\bIN\s+IN\b', r'IN'),
            (r'\bIS\s+IS\b', r'IS'),
            (r'\bNOT\s+NOT\b', r'NOT'),
            (r'\bLIKE\s+LIKE\b', r'LIKE'),
        ]

        self.comparison_patterns = [
            (r'\s=\s*=\s', r' = '),
            (r'\s<\s*<\s', r' < '),
            (r'\s>\s*>\s', r' > '),
            (r'\s!\s*=\s', r' != '),
            (r'\s<\s*>\s', r' <> '),
        ]

    def correct_query(self, sql_query: str) -> Tuple[str, List[str]]:
        corrections = []
        if not sql_query or not sql_query.strip():
            return "", ["Empty query provided"]
        sql_query = sql_query.strip()
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
        if not corrections:
            corrections.append("No syntax errors detected")
        try:
            sql_query = sqlparse.format(sql_query, reindent=True, keyword_case='upper')
        except Exception as e:
            corrections.append(f"Warning: Formatting failed - {str(e)}")
        return sql_query, corrections

    def _fix_keyword_typos(self, sql_query):
        corrections = []
        for typo, correction in self.keyword_typos.items():
            if re.search(typo, sql_query, re.IGNORECASE):
                original_text = re.search(typo, sql_query, re.IGNORECASE).group()
                sql_query = re.sub(typo, correction, sql_query, flags=re.IGNORECASE)
                corrections.append(f"Corrected typo: '{original_text}' to '{correction}'")
        return sql_query, corrections

    def _standardize_keywords(self, sql_query):
        corrections = []
        for keyword in self.sql_keywords:
            keyword_pattern = r'\b' + re.escape(keyword.replace(' ', r'\s+')) + r'\b'
            matches = re.finditer(keyword_pattern, sql_query, re.IGNORECASE)
            for match in matches:
                if match.group().upper() != keyword:
                    matched_text = match.group()
                    old_query = sql_query
                    sql_query = sql_query[:match.start()] + keyword + sql_query[match.end():]
                    if old_query != sql_query:
                        corrections.append(f"Standardized keyword: '{matched_text}' to '{keyword}'")
        return sql_query, corrections

    def _fix_semicolons(self, sql_query):
        corrections = []
        if sql_query.count(';') > 1:
            original_count = sql_query.count(';')
            sql_query = sql_query.replace(';', ' ', original_count - 1).replace('  ', ' ')
            sql_query = sql_query.rstrip('; ') + ';'
            corrections.append(f"Removed {original_count - 1} extra semicolons")
        if not sql_query.strip().endswith(';'):
            sql_query = sql_query.strip() + ';'
            corrections.append("Added missing semicolon at the end")
        return sql_query, corrections

    def _fix_parentheses(self, sql_query):
        corrections = []
        open_parens = sql_query.count('(')
        close_parens = sql_query.count(')')
        if open_parens > close_parens:
            sql_query = sql_query.rstrip(';') + ')' * (open_parens - close_parens) + ';'
            corrections.append(f"Added {open_parens - close_parens} missing closing parentheses")
        elif close_parens > open_parens:
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
        corrections = []
        if re.search(r',\S', sql_query):
            old_query = sql_query
            sql_query = re.sub(r',(\S)', r', \1', sql_query)
            if old_query != sql_query:
                corrections.append("Added missing spaces after commas")
        return sql_query, corrections

    def _fix_functions(self, sql_query):
        corrections = []
        for pattern, replacement in self.function_patterns.items():
            if re.search(pattern, sql_query, re.IGNORECASE):
                old_query = sql_query
                sql_query = re.sub(pattern, replacement, sql_query, flags=re.IGNORECASE)
                if old_query != sql_query:
                    corrections.append("Fixed function syntax by adding missing parentheses")
        return sql_query, corrections

    def _fix_string_literals(self, sql_query):
        corrections = []
        for pattern, replacement in self.string_patterns:
            if re.search(pattern, sql_query, re.IGNORECASE):
                old_query = sql_query
                sql_query = re.sub(pattern, replacement, sql_query, flags=re.IGNORECASE)
                if old_query != sql_query:
                    corrections.append("Added missing quotes around string literals")
        return sql_query, corrections

    def _fix_alias_syntax(self, sql_query):
        corrections = []
        # Для FROM: если после имени таблицы идет токен, не являющийся зарезервированным словом
        from_alias_pattern = r'(\bFROM\s+[a-zA-Z0-9_]+\s+)(?!AS\b|JOIN\b|WHERE\b|GROUP\b|ORDER\b|HAVING\b|LIMIT\b)([a-zA-Z0-9_]+)(\b)'
        new_sql_query, count = re.subn(from_alias_pattern, r'\1AS \2', sql_query, flags=re.IGNORECASE)
        if count > 0:
            sql_query = new_sql_query
            corrections.append("Added missing AS in table alias")
        # Для JOIN: аналогично, проверяем, что следующий токен не является зарезервированным
        join_alias_pattern = r'(\bJOIN\s+[a-zA-Z0-9_]+\s+ON\s+[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+\s*=\s*[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+\s+)(?!AS\b|WHERE\b|GROUP\b|ORDER\b|HAVING\b|LIMIT\b|ON\b)([a-zA-Z0-9_]+)(\b)'
        new_sql_query, count = re.subn(join_alias_pattern, r'\1AS \2', sql_query, flags=re.IGNORECASE)
        if count > 0:
            sql_query = new_sql_query
            corrections.append("Added missing AS in JOIN alias")
        return sql_query, corrections

    def _fix_join_syntax(self, sql_query):
        corrections = []
        for pattern, replacement in self.join_patterns:
            if re.search(pattern, sql_query, re.IGNORECASE):
                old_query = sql_query
                sql_query = re.sub(pattern, replacement, sql_query, flags=re.IGNORECASE)
                if old_query != sql_query:
                    corrections.append("Added missing ON clause after JOIN")
        return sql_query, corrections

    def _fix_incomplete_clauses(self, sql_query):
        corrections = []
        gb_pattern = r'\bGROUP\s+BY\s*$'
        if re.search(gb_pattern, sql_query, re.IGNORECASE):
            old_query = sql_query
            sql_query = re.sub(gb_pattern, '', sql_query, flags=re.IGNORECASE)
            if old_query != sql_query:
                corrections.append("Removed incomplete GROUP BY clause")
        ob_pattern = r'\bORDER\s+BY\s*$'
        if re.search(ob_pattern, sql_query, re.IGNORECASE):
            old_query = sql_query
            sql_query = re.sub(ob_pattern, '', sql_query, flags=re.IGNORECASE)
            if old_query != sql_query:
                corrections.append("Removed incomplete ORDER BY clause")
        where_pattern = r'\bWHERE\s*(?:;|$)'
        if re.search(where_pattern, sql_query, re.IGNORECASE):
            old_query = sql_query
            sql_query = re.sub(where_pattern, ';', sql_query, flags=re.IGNORECASE)
            if old_query != sql_query:
                corrections.append("Removed WHERE clause without condition")
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
        corrections = []
        for pattern, replacement in self.double_op_patterns:
            if re.search(pattern, sql_query, re.IGNORECASE):
                old_query = sql_query
                sql_query = re.sub(pattern, replacement, sql_query, flags=re.IGNORECASE)
                if old_query != sql_query:
                    corrections.append("Removed duplicate operators")
        for pattern, replacement in self.comparison_patterns:
            if re.search(pattern, sql_query):
                old_query = sql_query
                sql_query = re.sub(pattern, replacement, sql_query)
                if old_query != sql_query:
                    corrections.append("Fixed duplicate comparison operators")
        return sql_query, corrections

    def _fix_quote_balance(self, sql_query):
        corrections = []
        single_quotes = sql_query.count("'")
        if single_quotes % 2 != 0:
            sql_query = sql_query.rstrip(';') + "'" + ";"
            corrections.append("Added missing closing single quote")
        double_quotes = sql_query.count('"')
        if double_quotes % 2 != 0:
            sql_query = sql_query.rstrip(';') + '"' + ";"
            corrections.append("Added missing closing double quote")
        return sql_query, corrections

class EnhancedSQLCorrector:
    """Enhanced SQL corrector class that combines syntax correction with SQL transpilation."""
    def __init__(self):
        self.syntax_corrector = SQLSyntaxCorrector()
    def correct(self, sql_code: str) -> Tuple[str, List[str]]:
        if not sql_code or not isinstance(sql_code, str):
            return "", ["Invalid input: Not a valid SQL string"]
        corrected_sql, corrections = self.syntax_corrector.correct_query(sql_code)
        if HAS_SQLGLOT:
            try:
                transpiled_sql = transpile(corrected_sql, dialect='mysql')[0]
                if transpiled_sql != corrected_sql:
                    corrections.append("Standardized SQL dialect to MySQL")
                return transpiled_sql, corrections
            except Exception as e:
                corrections.append(f"Transpilation failed: {str(e)}")
                return corrected_sql, corrections
        else:
            corrections.append("sqlglot not installed - transpilation skipped")
            return corrected_sql, corrections