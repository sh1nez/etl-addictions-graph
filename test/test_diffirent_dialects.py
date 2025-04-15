__all__ = []

import src.base.parse


class TestDialectsInput:
    def test_safe_parse_postgres(self):
        ast = src.base.parse.SqlAst(
            "SELECT * FROM employees WHERE " "position ILIKE '%newbee%';"
        )

        assert ast.dialect == "postgres"

    def test_safe_parse_oracle(self):
        ast = src.base.parse.SqlAst("SELECT TOP 10 * FROM employees;")

        assert ast.dialect == "oracle"

    def test_safe_parse_unknown(self):
        ast = src.base.parse.SqlAst("SELECT TOP IFNULL(name, 'N/A') FROM users;")

        assert ast.dialect == "Unknown"
