import io
import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from sqlguard.engine import analyze_and_optimize_sql

# Force UTF-8 output on Windows to avoid cp1252 encoding errors with Rich
if sys.platform == "win32" and not isinstance(sys.stdout, io.TextIOWrapper):
    pass  # non-standard stdout, leave as is
elif sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]

app = typer.Typer(help="sqlguard: Optimizador estatico y reescritor AST de consultas SQL.")
console = Console()


@app.command()
def check(
    path: Path = typer.Argument(..., help="Archivo .sql o carpeta con archivos .sql"),  # noqa: B008
    dialect: str = typer.Option("postgres", "--dialect", "-d", help="Dialecto: postgres, bigquery, snowflake, mysql"),
    fix: bool = typer.Option(False, "--fix", help="Sobrescribe el archivo SQL con la versión optimizada"),
    json_output: bool = typer.Option(False, "--json", help="Devuelve el resultado en formato JSON para CI/CD"),
    fail_on_high: bool = typer.Option(False, "--fail-on-high", help="Devuelve exit code 1 si hay alertas HIGH"),
) -> None:
    sql_files = [path] if path.is_file() else list(path.rglob("*.sql"))
    if not sql_files:
        console.print("[red]No se encontraron archivos .sql en la ruta indicada.[/red]")
        raise typer.Exit(code=1)

    results = []
    has_high_severity = False

    for file_path in sql_files:
        raw_sql = file_path.read_text(encoding="utf-8")
        res = analyze_and_optimize_sql(raw_sql, dialect=dialect, file_path=str(file_path))
        results.append(res)

        if any(i.severity.value == "HIGH" for i in res.issues):
            has_high_severity = True

    if fix and not (fail_on_high and has_high_severity):
        for file_path, res in zip(sql_files, results, strict=True):
            if res.was_modified:
                file_path.write_text(res.optimized_sql + "\n", encoding="utf-8")

    if json_output:
        print(json.dumps([r.model_dump() for r in results], indent=2, ensure_ascii=False))
        if fail_on_high and has_high_severity:
            raise typer.Exit(code=1)
        return

    for res in results:
        console.rule(f"[bold cyan]Archivo: {res.file_path} ({res.dialect})[/bold cyan]")
        if not res.issues:
            console.print("[bold green]✔ Consulta óptima. Sin antipatrones detectados.[/bold green]\n")
            continue

        table = Table(title=f"Problemas Detectados (Ahorro estimado de lectura/CPU: ~{res.total_estimated_savings_pct}%)")
        table.add_column("ID", style="bold")
        table.add_column("Severidad")
        table.add_column("Impacto")
        table.add_column("Autofix")
        table.add_column("Explicación Técnica")

        for issue in res.issues:
            sev_color = "red" if issue.severity.value == "HIGH" else "yellow"
            table.add_row(
                issue.rule_id,
                f"[{sev_color}]{issue.severity.value}[/{sev_color}]",
                f"-{issue.estimated_scan_reduction_pct}% scan",
                "✔ Sí" if issue.can_autofix else "Manual",
                issue.description,
            )
        console.print(table)

        if res.was_modified:
            console.print(
                Panel(
                    Syntax(res.optimized_sql, "sql", theme="monokai", line_numbers=True),
                    title="[bold green]✨ SQL Optimizado Automáticamente por sqlguard[/bold green]",
                    border_style="green",
                )
            )

    if fail_on_high and has_high_severity:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
