from sqlglot import exp

from sqlguard.models import Issue, Severity
from sqlguard.rules.base import BaseRule


class NonSargableYearRule(BaseRule):
    rule_id = "SQL_003"
    title = "Función YEAR() no sargable en WHERE"
    severity = Severity.HIGH
    estimated_scan_reduction_pct = 75
    supports_autofix = True

    def _find_year_eq_pairs(self, ast: exp.Expression) -> list[exp.EQ]:
        """Encuentra nodos EQ donde un lado es YEAR(col) y el otro un literal de 4 dígitos."""
        matches: list[exp.EQ] = []

        for eq_node in ast.find_all(exp.EQ):
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

            if year_func is not None and literal_node is not None:
                matches.append(eq_node)

        return matches

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

        if column is None:
            return None

        year_val = int(literal_node.this)
        return (column, year_val)

    def check(self, ast: exp.Expression, dialect: str = "postgres") -> list[Issue]:
        issues: list[Issue] = []

        matches = self._find_year_eq_pairs(ast)
        for _ in matches:
            issues.append(
                self.build_issue(
                    "Se detectó YEAR(columna) = YYYY en la cláusula WHERE. "
                    "Envolver una columna de fecha en la función YEAR() impide que el "
                    "optimizador utilice índices B-Tree o la poda de particiones, "
                    "forzando un Full Table Scan. Reescribe como un predicado de rango: "
                    "columna >= 'YYYY-01-01' AND columna < '{YYYY+1}-01-01'."
                )
            )

        return issues

    def autofix(self, ast: exp.Expression, dialect: str = "postgres") -> exp.Expression:
        new_ast = ast.copy()

        for eq_node in list(new_ast.find_all(exp.EQ)):
            result = self._extract_column_and_year(eq_node)
            if result is None:
                continue

            column, year_val = result
            next_year = year_val + 1

            # Construir predicado sargable: col >= 'YYYY-01-01' AND col < '{YYYY+1}-01-01'
            start_date = f"{year_val}-01-01"
            end_date = f"{next_year}-01-01"

            range_predicate = exp.And(
                this=exp.GTE(
                    this=column.copy(),
                    expression=exp.Literal.string(start_date),
                ),
                expression=exp.LT(
                    this=column.copy(),
                    expression=exp.Literal.string(end_date),
                ),
            )

            eq_node.replace(range_predicate)

        return new_ast
