from pathlib import Path

from typer.testing import CliRunner

from sqlguard.cli import app

runner = CliRunner()


def test_low_and_medium_issues_are_autofixed(tmp_path: Path) -> None:
    sql_file = tmp_path / "query.sql"
    sql_file.write_text(
        """
        WITH recent_orders AS (
            SELECT id, status FROM orders
            WHERE status = 'PENDING' OR status = 'PROCESSING'
            ORDER BY id
        )
        SELECT id, status FROM recent_orders
        """,
        encoding="utf-8",
    )

    result = runner.invoke(app, [str(sql_file), "--fix", "--fail-on-high"])

    assert result.exit_code == 0, result.output
    optimized_sql = sql_file.read_text(encoding="utf-8")
    assert "status IN ('PENDING', 'PROCESSING')" in optimized_sql
    assert "ORDER BY" not in optimized_sql.upper()


def test_high_issue_fails_without_writing_any_autofixes(tmp_path: Path) -> None:
    sql_file = tmp_path / "query.sql"
    original_sql = "SELECT * FROM orders WHERE status = 'PENDING' OR status = 'PROCESSING';"
    sql_file.write_text(original_sql, encoding="utf-8")

    result = runner.invoke(app, [str(sql_file), "--fix", "--fail-on-high"])

    assert result.exit_code == 1
    assert sql_file.read_text(encoding="utf-8") == original_sql


def test_optimized_sql_succeeds_without_changing_file(tmp_path: Path) -> None:
    sql_file = tmp_path / "query.sql"
    original_sql = "SELECT id FROM orders WHERE status IN ('PENDING', 'PROCESSING');"
    sql_file.write_text(original_sql, encoding="utf-8")

    result = runner.invoke(app, [str(sql_file), "--fix", "--fail-on-high"])

    assert result.exit_code == 0, result.output
    assert "Consulta óptima" in result.output
    assert sql_file.read_text(encoding="utf-8") == original_sql


def test_missing_path_returns_clear_error(tmp_path: Path) -> None:
    result = runner.invoke(app, [str(tmp_path / "missing.sql")])
    assert result.exit_code == 2
    assert "La ruta no existe" in result.output


def test_unsupported_dialect_returns_clear_error(tmp_path: Path) -> None:
    sql_file = tmp_path / "query.sql"
    sql_file.write_text("SELECT 1", encoding="utf-8")
    result = runner.invoke(app, [str(sql_file), "--dialect", "oracle"])
    assert result.exit_code == 2
    assert "Dialecto no admitido" in result.output


def test_multiple_statements_fail_without_applying_fixes(tmp_path: Path) -> None:
    sql_file = tmp_path / "query.sql"
    original = "SELECT * FROM orders; SELECT id FROM users;"
    sql_file.write_text(original, encoding="utf-8")
    result = runner.invoke(app, [str(sql_file), "--fix"])
    assert result.exit_code == 2
    assert "una sentencia por archivo" in result.output
    assert sql_file.read_text(encoding="utf-8") == original
