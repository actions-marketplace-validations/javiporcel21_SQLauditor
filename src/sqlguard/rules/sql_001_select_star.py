from sqlglot import exp

from sqlguard.models import Issue, Severity
from sqlguard.rules.base import BaseRule


class SelectStarRule(BaseRule):
    rule_id = "SQL_001"
    title = "Evitar SELECT * en consultas de producción"
    severity = Severity.HIGH
    impact = "high"
    supports_autofix = False

    def check(self, ast: exp.Expression, dialect: str = "postgres") -> list[Issue]:
        issues: list[Issue] = []

        for star in ast.find_all(exp.Star):
            # Ignorar COUNT(*) porque no lee columnas innecesarias
            if isinstance(star.parent, exp.Count):
                continue

            issues.append(
                self.build_issue(
                    "Se detectó 'SELECT *'. Puede procesar columnas que la consulta no necesita, "
                    "especialmente en almacenes columnares. El efecto depende del motor "
                    "y del plan; "
                    "especifica las columnas necesarias cuando sea posible."
                )
            )
            break

        return issues
