from sqlglot import exp

from sqlguard.models import Issue, Severity
from sqlguard.rules.base import BaseRule


def _collect_eq_from_or(node: exp.Expression) -> list[exp.EQ] | None:
    """Recursivamente recolecta nodos EQ de una cadena de OR.
    Retorna None si algún nodo hoja no es EQ (cadena mixta)."""
    if isinstance(node, exp.EQ):
        return [node]
    if isinstance(node, exp.Or):
        left = _collect_eq_from_or(node.this)
        right = _collect_eq_from_or(node.expression)
        if left is not None and right is not None:
            return left + right
    return None


def _get_column_and_literal(eq_node: exp.EQ) -> tuple[str, exp.Expression, exp.Expression] | None:
    """Extrae (column_sql, column_node, literal_node) de un nodo EQ
    donde un lado es Column y el otro es Literal."""
    left, right = eq_node.this, eq_node.expression

    if isinstance(left, exp.Column) and isinstance(right, exp.Literal):
        return (left.sql(), left, right)
    if isinstance(right, exp.Column) and isinstance(left, exp.Literal):
        return (right.sql(), right, left)
    return None


class OrToInRewriteRule(BaseRule):
    rule_id = "SQL_005"
    title = "Cadena de OR reescribible como IN"
    severity = Severity.LOW
    estimated_scan_reduction_pct = 15
    supports_autofix = True

    def _find_or_chains(self, ast: exp.Expression) -> list[exp.Or]:
        """Encuentra nodos Or de nivel superior (no hijos de otro Or)
        que forman cadenas de EQ sobre la misma columna."""
        chains: list[exp.Or] = []

        for or_node in ast.find_all(exp.Or):
            # Saltar nodos Or que son hijos de otro Or (evitar duplicados)
            if isinstance(or_node.parent, exp.Or):
                continue

            eq_nodes = _collect_eq_from_or(or_node)
            if eq_nodes is None or len(eq_nodes) < 2:
                continue

            # Verificar que todos comparan la misma columna contra literales
            column_sql = None
            all_same = True
            for eq in eq_nodes:
                result = _get_column_and_literal(eq)
                if result is None:
                    all_same = False
                    break
                col_sql, _, _ = result
                if column_sql is None:
                    column_sql = col_sql
                elif col_sql != column_sql:
                    all_same = False
                    break

            if all_same and column_sql is not None:
                chains.append(or_node)

        return chains

    def check(self, ast: exp.Expression, dialect: str = "postgres") -> list[Issue]:
        issues: list[Issue] = []

        chains = self._find_or_chains(ast)
        for _ in chains:
            issues.append(
                self.build_issue(
                    "Se detectó una cadena de condiciones OR comparando la misma columna "
                    "contra distintos literales (ej. col = 'A' OR col = 'B'). "
                    "Reescribir como col IN ('A', 'B') simplifica el plan de ejecución "
                    "del optimizador y mejora la legibilidad de la consulta."
                )
            )

        return issues

    def autofix(self, ast: exp.Expression, dialect: str = "postgres") -> exp.Expression:
        new_ast = ast.copy()

        for or_node in list(self._find_or_chains(new_ast)):
            eq_nodes = _collect_eq_from_or(or_node)
            if eq_nodes is None:
                continue

            # Extraer columna y literales
            column_node = None
            literals: list[exp.Expression] = []

            for eq in eq_nodes:
                result = _get_column_and_literal(eq)
                if result is None:
                    continue
                _, col, lit = result
                if column_node is None:
                    column_node = col
                literals.append(lit)

            if column_node is None or len(literals) < 2:
                continue

            # Construir expresión IN
            in_node = exp.In(
                this=column_node.copy(),
                expressions=[lit.copy() for lit in literals],
            )

            or_node.replace(in_node)

        return new_ast
