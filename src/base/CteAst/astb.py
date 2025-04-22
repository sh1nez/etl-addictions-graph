from typing import List, Union


class ASTNode:
    pass


class CTE(ASTNode):
    def __init__(
        self,
        name: str,
        subquery: "Subquery",
        dependencies: List[str],
        is_recursive: bool,
    ):
        self.name = name
        self.subquery = subquery
        self.dependencies = dependencies
        self.is_recursive = is_recursive

    def __repr__(self):
        return f"CTE(name={self.name!r}, deps={self.dependencies}, recursive={self.is_recursive})"


class CTEBlock(ASTNode):
    def __init__(self, recursive: bool, expressions: List[CTE]):
        self.recursive = recursive
        self.expressions = expressions

    def __repr__(self):
        exprs = ", ".join(repr(e) for e in self.expressions)
        return f"CTEBlock(recursive={self.recursive}, expressions=[{exprs}])"


class Subquery(ASTNode):
    def __init__(self, query: "MainQuery"):
        self.query = query

    def __repr__(self):
        return f"Subquery({self.query!r})"


class MainQuery(ASTNode):
    def __init__(self, **kwargs):
        # Здесь можно хранить селект-поля, таблицы, условия и т.д.
        self.params = kwargs

    def __repr__(self):
        return f"MainQuery({self.params})"


class SqlAstRoot(ASTNode):
    def __init__(self, statements: List[Union[CTEBlock, MainQuery]]):
        self.statements = statements

    def __repr__(self):
        stmts = "\n".join(repr(s) for s in self.statements)
        return f"SqlAstRoot:\n{stmts}"
