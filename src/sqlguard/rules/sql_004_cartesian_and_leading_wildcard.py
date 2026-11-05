from sqlglot import exp

from sqlguard.models import Issue, Severity
from sqlguard.rules.base import BaseRule


class CartesianAndWildcardRule(BaseRule):
    rule_id = "SQL_004"
    title = "Producto cartesiano o LIKE con comodín inicial"
    severity = Severity.HIGH
    impact = "high"
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
                        "Se detectó un JOIN sin cláusula ON ni USING, que puede producir un "
                        "producto cartesiano. Puede ser intencional; confirma que la cardinalidad "
                        "resultante es la esperada."
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
                            "Un patrón con comodín inicial suele impedir una búsqueda por prefijo "
                            "con un índice B-Tree estándar. El plan depende del motor y de los "
                            "índices disponibles; revisa EXPLAIN si necesitas confirmar el coste."
                        )
                    )

        return issues
