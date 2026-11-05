import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError


class SQLParseException(Exception):
    pass


def parse_sql(sql: str, dialect: str = "postgres") -> exp.Expression:
    """Parsea una única sentencia SQL; nunca descarta sentencias posteriores."""
    try:
        statements = [
            statement
            for statement in sqlglot.parse(sql, read=dialect)
            if statement is not None
        ]
    except ParseError as e:
        raise SQLParseException(f"Error de sintaxis SQL ({dialect}): {e}") from e

    if not statements:
        raise SQLParseException("No se encontró ninguna sentencia SQL.")
    if len(statements) > 1:
        raise SQLParseException(
            f"Se encontraron {len(statements)} sentencias. "
            "Actualmente se admite una sentencia por archivo."
        )
    return statements[0]


def format_sql(ast: exp.Expression, dialect: str = "postgres") -> str:
    """Convierte un árbol AST de vuelta a SQL formateado."""
    return ast.sql(dialect=dialect, pretty=True)
