from typing import List, Tuple

# AST-классы из base/sqlast
from astb import (
    SqlAstRoot,
    CTEBlock as AstCTEBlock,
    CTE as AstCTE,
    Subquery as AstSubquery,
    MainQuery as AstMainQuery,
)
from lexer import tokenize, Token, TokenType


class CTEparser:
    def __init__(self):
        # состояние парсера, счётчик позиций и т.п.
        pass

    def parse(self, tokens: List[Token]) -> SqlAstRoot:
        """
        Основной метод: строит список statements, включая CTE-блок
        """
        pos = 0
        statements = []

        # 1) Обработка CTE-блока, если встречается WITH
        if self._match_keyword(tokens, pos, "WITH"):
            cte_block, pos = self._parse_cte_block(tokens, pos)
            statements.append(cte_block)

        # 2) Разбор основного запроса
        main_query, pos = self._parse_main_query(tokens, pos)
        statements.append(main_query)

        # 3) Дополнительные запросы через ';'
        while pos < len(tokens) and self._match_symbol(tokens, pos, ";"):
            pos += 1
            next_query, pos = self._parse_main_query(tokens, pos)
            statements.append(next_query)

        return SqlAstRoot(statements=statements)

    def _parse_cte_block(
        self, tokens: List[Token], pos: int
    ) -> Tuple[AstCTEBlock, int]:
        """
        Разбирает:
            WITH [RECURSIVE]
              name1 AS (subquery1),
              name2 AS (subquery2), ...
        Возвращает AstCTEBlock и новую позицию в tokens
        """
        # Съедаем 'WITH'
        pos += 1
        recursive = False
        if self._match_keyword(tokens, pos, "RECURSIVE"):
            recursive = True
            pos += 1

        expressions: List[AstCTE] = []
        seen_names: List[str] = []

        # Парсим список CTE separated by commas
        while True:
            # Ожидаем идентификатор — имя CTE
            tok = tokens[pos]
            if tok.type != TokenType.IDENTIFIER:
                raise SyntaxError(f"Expected CTE name at position {pos}, got {tok}")
            name = tok.value
            seen_names.append(name)
            pos += 1

            # Ключевое слово AS
            if not self._match_keyword(tokens, pos, "AS"):
                raise SyntaxError(f"Expected AS after CTE name '{name}'")
            pos += 1

            # Открывающая скобка перед подзапросом
            if not self._match_symbol(tokens, pos, "("):
                raise SyntaxError(f"Expected '(' before subquery of CTE '{name}'")
            subq_node, pos = self._parse_subquery(tokens, pos)

            # Определение зависимостей: ищем в подзапросе встречающиеся ранее объявленные CTE
            deps = [n for n in seen_names[:-1] if self._subquery_uses(subq_node, n)]

            expressions.append(
                AstCTE(
                    name=name,
                    subquery=subq_node,
                    dependencies=deps,
                    is_recursive=recursive,
                )
            )

            # Если следующая запятая -> новый CTE
            if self._match_symbol(tokens, pos, ","):
                pos += 1
                continue
            break

        return AstCTEBlock(recursive=recursive, expressions=expressions), pos

    def _parse_subquery(self, tokens_or_node, pos: int = 0) -> Tuple[AstSubquery, int]:
        """
        Парсит подзапрос, балансирует скобки и строит узел Subquery.
        При manual-парсинге tokens_or_node = tokens list.
        """
        # Для простоты здесь предполагаем, что парсинг subquery делегируется
        # основному parse(), либо вызывается специфический метод.
        # Например:
        inner_tokens, new_pos = self._extract_parenthesized(tokens_or_node, pos)
        inner_query, _ = self._parse_main_query(inner_tokens, 0)
        return AstSubquery(inner_query), new_pos

    def _subquery_uses(self, subq_node: AstSubquery, name: str) -> bool:
        """
        Проверяем, использует ли подзапрос CTE с именем name.
        Можно либо сканировать токены, либо обходить AST subq_node.query.
        """
        # Пример: рекурсивный обход AST для поиска идентификаторов
        for node in subq_node.query.walk():
            if getattr(node, "name", None) == name:
                return True
        return False

    # --- Утилиты для сравнения токенов ---
    def _match_keyword(self, tokens: List[Token], pos: int, kw: str) -> bool:
        return (
            pos < len(tokens)
            and tokens[pos].type == TokenType.KEYWORD
            and tokens[pos].value.upper() == kw
        )

    def _match_symbol(self, tokens: List[Token], pos: int, sym: str) -> bool:
        return (
            pos < len(tokens)
            and tokens[pos].type == TokenType.SYMBOL
            and tokens[pos].value == sym
        )

    def _extract_parenthesized(
        self, tokens: List[Token], pos: int
    ) -> Tuple[List[Token], int]:
        """
        Выделяет подсписок токенов между скобками (pos указывает на '(')
        Возвращает (inner_tokens, new_pos после ')').
        """
        depth = 0
        start = pos
        for i in range(pos, len(tokens)):
            if tokens[i].value == "(":
                depth += 1
            elif tokens[i].value == ")":
                depth -= 1
                if depth == 0:
                    return tokens[start + 1 : i], i + 1
        raise SyntaxError("Unbalanced parentheses in subquery")
