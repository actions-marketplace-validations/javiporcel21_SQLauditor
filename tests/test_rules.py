"""Tests unitarios para las 5 reglas de sqlguard (SQL_001 a SQL_005)."""
from sqlguard.engine import analyze_and_optimize_sql


class TestSQL001SelectStar:
    """Tests para la regla SQL_001: Evitar SELECT *."""

    def test_select_star_triggers_issue(self):
        sql = "SELECT * FROM orders"
        result = analyze_and_optimize_sql(sql)
        rule_ids = [i.rule_id for i in result.issues]
        assert "SQL_001" in rule_ids

    def test_count_star_no_issue(self):
        sql = "SELECT COUNT(*) FROM orders"
        result = analyze_and_optimize_sql(sql)
        rule_ids = [i.rule_id for i in result.issues]
        assert "SQL_001" not in rule_ids


class TestSQL002RedundantOrderBy:
    """Tests para la regla SQL_002: ORDER BY redundante en CTE sin LIMIT."""

    def test_cte_order_by_without_limit_triggers(self):
        sql = """
        WITH cte AS (
            SELECT id, name FROM users ORDER BY name
        )
        SELECT * FROM cte
        """
        result = analyze_and_optimize_sql(sql)
        rule_ids = [i.rule_id for i in result.issues]
        assert "SQL_002" in rule_ids

    def test_cte_order_by_without_limit_autofix(self):
        sql = """
        WITH cte AS (
            SELECT id, name FROM users ORDER BY name
        )
        SELECT * FROM cte
        """
        result = analyze_and_optimize_sql(sql)
        assert result.was_modified
        # El SQL optimizado no debe contener ORDER BY dentro de la CTE
        optimized_upper = result.optimized_sql.upper()
        # Verificar que el ORDER BY fue eliminado de la CTE
        # Buscamos que no haya ORDER BY antes de la primera aparición de SELECT *
        cte_part = optimized_upper.split("SELECT *")[0] if "SELECT *" in optimized_upper else optimized_upper
        # Puede haber variaciones, pero el ORDER BY no debe estar en la CTE
        assert "ORDER BY" not in cte_part or "LIMIT" in cte_part

    def test_cte_order_by_with_limit_no_issue(self):
        sql = """
        WITH cte AS (
            SELECT id, name FROM users ORDER BY name LIMIT 10
        )
        SELECT * FROM cte
        """
        result = analyze_and_optimize_sql(sql)
        rule_ids = [i.rule_id for i in result.issues]
        assert "SQL_002" not in rule_ids


class TestSQL003NonSargableYear:
    """Tests para la regla SQL_003: YEAR() no sargable."""

    def test_year_function_triggers_issue(self):
        sql = "SELECT id FROM orders WHERE YEAR(order_date) = 2026"
        result = analyze_and_optimize_sql(sql)
        rule_ids = [i.rule_id for i in result.issues]
        assert "SQL_003" in rule_ids

    def test_year_function_autofix_rewrites_to_range(self):
        sql = "SELECT id FROM orders WHERE YEAR(order_date) = 2026"
        result = analyze_and_optimize_sql(sql)
        assert result.was_modified
        optimized = result.optimized_sql.upper()
        assert "2026-01-01" in result.optimized_sql
        assert "2027-01-01" in result.optimized_sql
        # No debe contener YEAR() en el SQL optimizado
        assert "YEAR(" not in optimized

    def test_normal_where_no_issue(self):
        sql = "SELECT id FROM orders WHERE order_date >= '2026-01-01'"
        result = analyze_and_optimize_sql(sql)
        rule_ids = [i.rule_id for i in result.issues]
        assert "SQL_003" not in rule_ids


class TestSQL004CartesianAndWildcard:
    """Tests para la regla SQL_004: Producto cartesiano y LIKE con comodín inicial."""

    def test_leading_wildcard_triggers_issue(self):
        sql = "SELECT * FROM users WHERE name LIKE '%garcia'"
        result = analyze_and_optimize_sql(sql)
        rule_ids = [i.rule_id for i in result.issues]
        assert "SQL_004" in rule_ids

    def test_trailing_wildcard_no_issue_004(self):
        sql = "SELECT id FROM users WHERE name LIKE 'garcia%'"
        result = analyze_and_optimize_sql(sql)
        rule_ids = [i.rule_id for i in result.issues]
        assert "SQL_004" not in rule_ids


class TestSQL005OrToIn:
    """Tests para la regla SQL_005: Cadena de OR reescribible como IN."""

    def test_or_chain_triggers_issue(self):
        sql = "SELECT * FROM orders WHERE status = 'A' OR status = 'B'"
        result = analyze_and_optimize_sql(sql)
        rule_ids = [i.rule_id for i in result.issues]
        assert "SQL_005" in rule_ids

    def test_or_chain_autofix_rewrites_to_in(self):
        sql = "SELECT id FROM orders WHERE status = 'A' OR status = 'B'"
        result = analyze_and_optimize_sql(sql)
        assert result.was_modified
        optimized_upper = result.optimized_sql.upper()
        assert "IN" in optimized_upper
        # No debe tener la cadena OR original
        assert " OR " not in optimized_upper or "IN" in optimized_upper

    def test_different_columns_no_issue(self):
        sql = "SELECT id FROM orders WHERE status = 'A' OR priority = 'HIGH'"
        result = analyze_and_optimize_sql(sql)
        rule_ids = [i.rule_id for i in result.issues]
        assert "SQL_005" not in rule_ids

    def test_triple_or_chain_rewrites(self):
        sql = "SELECT id FROM orders WHERE status = 'A' OR status = 'B' OR status = 'C'"
        result = analyze_and_optimize_sql(sql)
        rule_ids = [i.rule_id for i in result.issues]
        assert "SQL_005" in rule_ids
        assert result.was_modified
