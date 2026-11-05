import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from sqlguard.engine import analyze_and_optimize_sql
from sqlguard.parser import SQLParseException

app = typer.Typer(help="sqlguard: análisis estático de consultas SQL con autofixes prudentes.")
console = Console()
error_console = Console(stderr=True)


@app.command()
def check(
    path: Path = typer.Argument(..., help="Archivo .sql o carpeta con archivos .sql"),  # noqa: B008
    dialect: str = typer.Option(
        "postgres", "--dialect", "-d", help="Dialecto: postgres, bigquery, snowflake, mysql"
    ),
    fix: bool = typer.Option(
        False, "--fix", help="Sobrescribe el archivo SQL con la versión optimizada"
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Devuelve el resultado en formato JSON para CI/CD"
    ),
    fail_on_high: bool = typer.Option(
        False, "--fail-on-high", help="Devuelve exit code 1 si hay alertas HIGH"
    ),
) -> None:
    supported_dialects = {"postgres", "bigquery", "snowflake", "mysql"}
    if dialect.lower() not in supported_dialects:
        options = ", ".join(sorted(supported_dialects))
        error_console.print(
            f"[red]Dialecto no admitido: {dialect}. Opciones: {options}.[/red]"
        )
        raise typer.Exit(code=2)
    if not path.exists():
        error_console.print(f"[red]La ruta no existe: {path}[/red]")
        raise typer.Exit(code=2)
    if not path.is_file() and not path.is_dir():
        error_console.print(f"[red]La ruta no es un archivo ni una carpeta: {path}[/red]")
        raise typer.Exit(code=2)

    sql_files = [path] if path.is_file() else sorted(path.rglob("*.sql"))
    if not sql_files:
        error_console.print("[red]No se encontraron archivos .sql en la ruta indicada.[/red]")
        raise typer.Exit(code=1)

    results = []
    has_high_severity = False

    try:
        for file_path in sql_files:
            raw_sql = file_path.read_text(encoding="utf-8")
            res = analyze_and_optimize_sql(
                raw_sql,
                dialect=dialect.lower(),
                file_path=str(file_path),
            )
            results.append(res)

            if any(i.severity.value == "HIGH" for i in res.issues):
                has_high_severity = True
    except (OSError, UnicodeError, SQLParseException) as exc:
        error_console.print(f"[red]No se pudo completar la auditoría: {exc}[/red]")
        raise typer.Exit(code=2) from exc

    if fix and not (fail_on_high and has_high_severity):
        try:
            for file_path, res in zip(sql_files, results, strict=True):
                if res.was_modified:
                    file_path.write_text(res.optimized_sql + "\n", encoding="utf-8")
        except OSError as exc:
            error_console.print(f"[red]No se pudieron escribir los cambios: {exc}[/red]")
            raise typer.Exit(code=2) from exc

    if json_output:
        print(json.dumps([r.model_dump() for r in results], indent=2, ensure_ascii=False))
        if fail_on_high and has_high_severity:
            raise typer.Exit(code=1)
        return

    for res in results:
        console.rule(f"[bold cyan]Archivo: {res.file_path} ({res.dialect})[/bold cyan]")
        if not res.issues:
            console.print(
                "[bold green]✔ Consulta óptima. Sin antipatrones detectados.[/bold green]\n"
            )
            continue

        table = Table(title="Hallazgos (impacto cualitativo; no es una estimación de ahorro)")
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
                issue.impact.capitalize(),
                "✔ Sí" if issue.can_autofix else "Manual",
                issue.description,
            )
        console.print(table)

        if res.was_modified:
            console.print(
                Panel(
                    Syntax(res.optimized_sql, "sql", theme="monokai", line_numbers=True),
                    title=(
                        "[bold green]SQL reescrito por SQLGuard; revisa el resultado "
                        "antes de aplicarlo[/bold green]"
                    ),
                    border_style="green",
                )
            )

    if fail_on_high and has_high_severity:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
