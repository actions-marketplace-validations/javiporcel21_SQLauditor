from sqlglot import exp

from sqlguard.models import Issue, Severity
from sqlguard.rules.base import BaseRule


class RedundantSubqueryOrderByRule(BaseRule):
    rule_id = "SQL_002"
    title = "ORDER BY redundante en CTE/subconsulta sin LIMIT"
    severity = Severity.MEDIUM
    impact = "moderate"
    supports_autofix = True

    def _has_limit_or_offset(self, select_node: exp.Select) -> bool:
        """Comprueba si el Select limita o pagina filas con alguna sintaxis admitida."""
        return bool(
            select_node.args.get("limit")
            or select_node.args.get("offset")
            or select_node.args.get("fetch")
            or select_node.args.get("top")
        )

    def check(self, ast: exp.Expression, dialect: str = "postgres") -> list[Issue]:
        issues: list[Issue] = []

        for node in ast.find_all(exp.CTE, exp.Subquery):
            inner = node.this
            if not isinstance(inner, exp.Select):
                continue

            if inner.args.get("order") and not self._has_limit_or_offset(inner):
                issues.append(
                    self.build_issue(
                        "Se detectó ORDER BY dentro de una CTE o subconsulta sin "
                        "LIMIT/OFFSET/FETCH. "
                        "El orden interno no garantiza el orden del resultado exterior y puede "
                        "añadir trabajo innecesario. Revisa las dependencias del motor y de la "
                        "aplicación antes de eliminarlo."
                    )
                )

        return issues

    def autofix(self, ast: exp.Expression, dialect: str = "postgres") -> exp.Expression:
        new_ast = ast.copy()

        for node in new_ast.find_all(exp.CTE, exp.Subquery):
            inner = node.this
            if not isinstance(inner, exp.Select):
                continue

            if inner.args.get("order") and not self._has_limit_or_offset(inner):
                inner.set("order", None)

        return new_ast
