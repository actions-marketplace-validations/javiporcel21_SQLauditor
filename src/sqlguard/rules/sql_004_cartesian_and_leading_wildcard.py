from sqlglot import exp

from sqlguard.models import Issue, Severity
from sqlguard.rules.base import BaseRule


class CartesianAndWildcardRule(BaseRule):
    rule_id = "SQL_004"
    title = "Producto cartesiano o LIKE con comodín inicial"
    severity = Severity.HIGH
    estimated_scan_reduction_pct = 80
    supports_autofix = False

    def check(self, ast: exp.Expression, dialect: str = "postgres") -> list[Issue]:
        issues: list[Issue] = []

        # 1. Detectar JOINs sin condición ON ni USING (producto cartesiano accidental)
        for join_node in ast.find_all(exp.Join):
            has_on = join_node.args.get("on")
            has_using = join_node.args.get("using")
            join_kind = (join_node.args.get("kind") or "").upper()

            # CROSS JOIN es intencional, no lo reportamos
            if join_kind == "CROSS":
                continue

            if not has_on and not has_using:
                issues.append(
                    self.build_issue(
                        "Se detectó un JOIN sin cláusula ON ni USING, lo que produce un "
                        "producto cartesiano accidental (M × N filas). Esto genera una "
                        "explosión combinatoria que puede saturar la memoria y el CPU del "
                        "motor SQL. Añade siempre una condición de join explícita."
                    )
                )

        # 2. Detectar LIKE / ILIKE con comodín al inicio ('%...')
        for like_node in ast.find_all(exp.Like, exp.ILike):
            pattern = like_node.expression
            if isinstance(pattern, exp.Literal) and pattern.is_string:
                # El valor del literal de texto en sqlglot
                pattern_val = pattern.this
                if pattern_val.startswith("%"):
                    issues.append(
                        self.build_issue(
                            f"Se detectó LIKE/ILIKE con comodín inicial ('{pattern_val}'). "
                            "Un patrón que empieza con '%' impide el uso de cualquier índice "
                            "B-Tree estándar, forzando un escaneo secuencial completo de la "
                            "tabla. Considera usar índices GIN/trigram, búsqueda full-text "
                            "o reestructurar la consulta."
                        )
                    )

        return issues
