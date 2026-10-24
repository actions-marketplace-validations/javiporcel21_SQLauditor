import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError


class SQLParseException(Exception):
    pass


def parse_sql(sql: str, dialect: str = "postgres") -> exp.Expression:
    """Convierte texto SQL en un árbol AST de sqlglot."""
    try:
        ast = sqlglot.parse_one(sql, read=dialect)
        return ast
    except ParseError as e:
        raise SQLParseException(f"Error de sintaxis SQL ({dialect}): {e}") from e


def format_sql(ast: exp.Expression, dialect: str = "postgres") -> str:
    """Convierte un árbol AST de vuelta a SQL formateado."""
    return ast.sql(dialect=dialect, pretty=True)
