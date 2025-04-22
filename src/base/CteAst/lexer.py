import ply.lex as lex
import ply.yacc as yacc
from typing import List

# AST-классы
from astb import (
    CTEBlock as AstCTEBlock,
    CTE as AstCTE,
    Subquery as AstSubquery,
    MainQuery as AstMainQuery,
    SqlAstRoot,
)

# ------- ЛЕКСЕР -------

# Список токенов
tokens = (
    "WITH",
    "RECURSIVE",
    "AS",
    "IDENTIFIER",
    "LPAREN",
    "RPAREN",
    "COMMA",
    "SEMI",
    # другие токены для SELECT/WHERE и т.д.
)

# Регулярные выражения для простых токенов
t_WITH = r"(?i)WITH"
t_RECURSIVE = r"(?i)RECURSIVE"
t_AS = r"(?i)AS"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_COMMA = r","
t_SEMI = r";"


# Идентификаторы (имена таблиц, CTE и т.п.)
def t_IDENTIFIER(t):
    r"[A-Za-z_][A-Za-z0-9_]*"
    val = t.value.upper()
    if val == "WITH":
        t.type = "WITH"
    elif val == "RECURSIVE":
        t.type = "RECURSIVE"
    elif val == "AS":
        t.type = "AS"
    return t


# Пропускаем пробелы и табуляцию
t_ignore = " \t\n"


def t_error(t):
    raise SyntaxError(f"Непонятный символ '{t.value[0]}' в позиции {t.lexpos}")


lexer = lex.lex()

# ------- ПАРСЕР -------

# Определяем приоритеты (если нужно для UNION и т.д.)
precedence = ()

# Сборка списка выражений


def p_sql_root(p):
    "sql_root : statements"
    p[0] = SqlAstRoot(statements=p[1])


def p_statements_multi(p):
    "statements : statements SEMI statement"
    p[0] = p[1] + [p[3]]


def p_statements_single(p):
    "statements : statement"
    p[0] = [p[1]]


# Одиночное выражение: либо CTE-блок + основной запрос, либо просто запрос


def p_statement(p):
    """statement : cte_block main_query
    | main_query"""
    if len(p) == 3:
        block, main = p[1], p[2]
        p[0] = ["CTE_BLOCK", block, main]
    else:
        p[0] = p[1]


# CTE-блок


def p_cte_block(p):
    "cte_block : WITH opt_recursive cte_list"
    recursive, exprs = p[2], p[3]
    p[0] = AstCTEBlock(recursive=recursive, expressions=exprs)


# Опциональный RECURSIVE


def p_opt_recursive_recursive(p):
    "opt_recursive : RECURSIVE"
    p[0] = True


def p_opt_recursive_empty(p):
    "opt_recursive :"
    p[0] = False


# Список CTE-записей


def p_cte_list_single(p):
    "cte_list : cte_item"
    p[0] = [p[1]]


def p_cte_list_many(p):
    "cte_list : cte_list COMMA cte_item"
    p[0] = p[1] + [p[3]]


# Одна CTE-запись


def p_cte_item(p):
    "cte_item : IDENTIFIER AS LPAREN main_query RPAREN"
    name = p[1]
    subq = p[4]
    # зависимости можно вычислить после того, как все CTE распарсены
    p[0] = AstCTE(
        name=name, subquery=AstSubquery(subq), dependencies=[], is_recursive=False
    )


# Заглушка для основного запроса (использовать существующие правила)


def p_main_query(p):
    "main_query : IDENTIFIER"
    # Временная реализация. Подключите парсинг SELECT и т.д.
    p[0] = AstMainQuery(content=p[1])


# Обработка синтаксических ошибок


def p_error(p):
    if p:
        raise SyntaxError(f"Ошибка синтаксиса около '{p.value}'")
    else:
        raise SyntaxError("Неверный конец ввода")


import re
from enum import Enum, auto
from typing import List


class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    SYMBOL = auto()
    NUMBER = auto()
    STRING = auto()
    EOF = auto()


class Token:
    def __init__(self, type: TokenType, value: str, position: int):
        self.type = type
        self.value = value
        self.position = position

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', pos={self.position})"


KEYWORDS = {"WITH", "RECURSIVE", "AS", "SELECT", "FROM", "WHERE", "JOIN", "ON"}
SYMBOLS = {"(", ")", ",", ";", "*", "=", "."}

_token_spec = [
    ("WHITESPACE", r"[ \t\n]+"),
    ("STRING", r"'(?:''|[^'])*'"),
    ("NUMBER", r"\d+(\.\d*)?"),
    ("IDENTIFIER", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("SYMBOL", r"[(),;*=\.]"),
]

_token_re = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in _token_spec)
)


def tokenize(sql: str) -> List[Token]:
    tokens: List[Token] = []
    pos = 0
    for mo in _token_re.finditer(sql):
        kind = mo.lastgroup
        value = mo.group()
        start = mo.start()

        if kind == "WHITESPACE":
            continue
        elif kind == "STRING":
            tokens.append(Token(TokenType.STRING, value, start))
        elif kind == "NUMBER":
            tokens.append(Token(TokenType.NUMBER, value, start))
        elif kind == "IDENTIFIER":
            upper_val = value.upper()
            if upper_val in KEYWORDS:
                tokens.append(Token(TokenType.KEYWORD, upper_val, start))
            else:
                tokens.append(Token(TokenType.IDENTIFIER, value, start))
        elif kind == "SYMBOL":
            tokens.append(Token(TokenType.SYMBOL, value, start))
        else:
            raise SyntaxError(f"Unknown token {value} at position {start}")

    tokens.append(Token(TokenType.EOF, "", len(sql)))
    return tokens
