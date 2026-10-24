from sqlglot import exp

from sqlguard.models import Issue, Severity
from sqlguard.rules.base import BaseRule


class SelectStarRule(BaseRule):
    rule_id = "SQL_001"
    title = "Evitar SELECT * en consultas de producción"
    severity = Severity.HIGH
    estimated_scan_reduction_pct = 60
    supports_autofix = False

    def check(self, ast: exp.Expression, dialect: str = "postgres") -> list[Issue]:
        issues: list[Issue] = []

        for star in ast.find_all(exp.Star):
            # Ignorar COUNT(*) porque no lee columnas innecesarias
            if isinstance(star.parent, exp.Count):
                continue

            issues.append(
                self.build_issue(
                    "Se detectó 'SELECT *'. En motores columnares (BigQuery, Snowflake, Parquet) "
                    "e índices cubrientes de Postgres, leer todas las columnas multiplica el I/O "
                    "y el coste por TB escaneado. Especifica explícitamente las columnas necesarias."
                )
            )
            break

        return issues
