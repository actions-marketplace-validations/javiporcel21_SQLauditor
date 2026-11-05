from sqlglot import exp

from sqlguard.models import Issue, Severity
from sqlguard.rules.base import BaseRule


class NonSargableYearRule(BaseRule):
    rule_id = "SQL_003"
    title = "Función YEAR() no sargable en WHERE"
    severity = Severity.HIGH
    impact = "high"
    # The analyzer has no schema or session-timezone information to prove that
    # replacing YEAR(column) with calendar boundaries preserves semantics.
    supports_autofix = False

    def _find_year_eq_pairs(self, ast: exp.Expression) -> list[exp.EQ]:
        """Encuentra nodos EQ donde un lado es YEAR(col) y el otro un literal de 4 dígitos."""
        matches: list[exp.EQ] = []

        for eq_node in ast.find_all(exp.EQ):
            if not self._is_inside_where(eq_node):
                continue
            left, right = eq_node.this, eq_node.expression
            year_func = None
            literal_node = None

            # Determinar cuál lado es YEAR(col) y cuál es el literal
            if self._is_year_func(left) and self._is_year_literal(right):
                year_func = left
                literal_node = right
            elif self._is_year_func(right) and self._is_year_literal(left):
                year_func = right
                literal_node = left

            if (
                year_func is not None
                and literal_node is not None
                and self._extract_column_and_year(eq_node)
            ):
                matches.append(eq_node)

        return matches

    def _is_inside_where(self, node: exp.Expression) -> bool:
        parent = node.parent
        while parent is not None:
            if isinstance(parent, exp.Where):
                return True
            parent = parent.parent
        return False

    def _is_year_func(self, node: exp.Expression) -> bool:
        """Comprueba si el nodo es una función YEAR()."""
        if isinstance(node, exp.Year):
            return True
        return isinstance(node, exp.Anonymous) and node.this.upper() == "YEAR"

    def _is_year_literal(self, node: exp.Expression) -> bool:
        """Comprueba si el nodo es un literal entero de 4 dígitos (año)."""
        if isinstance(node, exp.Literal) and node.is_int:
            val = node.this
            return len(str(val)) == 4
        return False

    def _extract_column_and_year(
        self, eq_node: exp.EQ
    ) -> tuple[exp.Expression, int] | None:
        """Extrae la columna y el valor del año de un nodo EQ con YEAR(col) = YYYY."""
        left, right = eq_node.this, eq_node.expression

        year_func = None
        literal_node = None

        if self._is_year_func(left) and self._is_year_literal(right):
            year_func = left
            literal_node = right
        elif self._is_year_func(right) and self._is_year_literal(left):
            year_func = right
            literal_node = left

        if year_func is None or literal_node is None:
            return None

        # Extraer la columna del interior de YEAR()
        if isinstance(year_func, exp.Year):
            column = year_func.this
        else:  # exp.Anonymous
            column = year_func.expressions[0] if year_func.expressions else None

        if not isinstance(column, exp.Column):
            return None

        year_val = int(literal_node.this)
        if not 1 <= year_val <= 9998:
            return None
        return (column, year_val)

    def check(self, ast: exp.Expression, dialect: str = "postgres") -> list[Issue]:
        issues: list[Issue] = []

        matches = self._find_year_eq_pairs(ast)
        for _ in matches:
            issues.append(
                self.build_issue(
                    "Se detectó YEAR(columna) = YYYY en la cláusula WHERE. "
                    "Aplicar una función a la columna puede limitar el uso de algunos índices "
                    "o la poda de particiones. Un rango de fechas puede ser más adecuado, pero "
                    "la equivalencia depende del tipo de dato, la zona horaria y el motor. "
                    "SQLGuard no aplica una reescritura automática en este caso."
                )
            )

        return issues
