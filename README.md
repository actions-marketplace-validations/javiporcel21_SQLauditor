# SQLGuard

[![Quality](https://github.com/javiporcel21/SQLauditor/actions/workflows/quality.yml/badge.svg)](https://github.com/javiporcel21/SQLauditor/actions/workflows/quality.yml)

**Static SQL checks with cautious AST-based autofixes.** SQLGuard analyzes SQL locally with [SQLGlot](https://github.com/tobymao/sqlglot). It does not connect to a database or execute queries.

> SQLGuard reports heuristics. It does not inspect schemas, query plans, table statistics, or cloud billing, so it cannot promise a performance improvement or cost saving. Review rewritten SQL and validate it against your database before deployment.

## Requirements and installation

SQLGuard requires Python 3.10 or later. Install it from a local checkout:

```bash
python -m pip install .
```

## Use

```bash
# Check one SQL file
sqlguard examples/bad_query.sql --dialect postgres

# Recursively check SQL files in a directory
sqlguard ./sql/ --dialect bigquery

# Emit JSON for CI
sqlguard ./sql/ --json

# Apply supported autofixes in place
sqlguard ./sql/ --fix

# Return exit code 1 when HIGH findings exist
sqlguard ./sql/ --fail-on-high
```

Supported dialects are `postgres`, `bigquery`, `snowflake`, and `mysql`. Each file must contain exactly one SQL statement; files with multiple statements are rejected instead of silently skipping later statements. Parse, path, encoding, and write errors exit with status 2. `--fail-on-high` exits with status 1. When combined with `--fix`, no files are written if any HIGH finding is present. `--json` writes results to standard output and diagnostics to standard error.

## Rules

| ID | Finding | Severity | Autofix |
|---|---|---:|---|
| SQL_001 | `SELECT *` outside `COUNT(*)` | HIGH | No |
| SQL_002 | `ORDER BY` in a CTE or subquery without a row limit | MEDIUM | Removes inner ordering |
| SQL_003 | `YEAR(column) = YYYY` in a `WHERE` predicate | HIGH | Rewrites a simple column reference to a half-open date range |
| SQL_004 | Join without `ON`/`USING`, or `LIKE`/`ILIKE` pattern starting with `%` | HIGH | No |
| SQL_005 | Equality `OR` chain on the same column and literals | LOW | Rewrites to `IN` |

Severity and impact are qualitative labels, not measured estimates. SQL_003 assumes a date-like column whose value and timezone semantics make the generated calendar-year range equivalent. SQL_002 removes ordering that does not define the outer query's result order. These checks cannot prove equivalence for every engine or application; inspect and test autofixes before merging them.

## GitHub Action

```yaml
name: SQL audit
on: [pull_request]
jobs:
  sqlguard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: javiporcel21/SQLauditor@85272da3d4b9f4c9174d030bb07bec98ba6b0f40 # v1.0.3
        with:
          path: ./sql
          dialect: postgres
          fail_on_high: "true"
          fix: "false"
```

With `fix: "true"`, the Action writes supported autofixes into the runner's checkout. The Action does not commit or push changes. Pin the Action to a reviewed immutable commit SHA in production workflows.

## Development

```bash
python -m venv .venv
# Activate the environment, then:
python -m pip install -e ".[dev]"
pytest -q
ruff check .
python -m build
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [CHANGELOG.md](CHANGELOG.md), and the SQL examples in [`examples/cases`](examples/cases/README.md).

## License

SQLGuard is distributed under the MIT License. See [LICENSE](LICENSE).

---

## Español

**Análisis estático de SQL con autofixes prudentes basados en AST.** SQLGuard analiza SQL localmente con [SQLGlot](https://github.com/tobymao/sqlglot). No se conecta a bases de datos ni ejecuta consultas.

> SQLGuard ofrece heurísticas. No inspecciona esquemas, planes de ejecución, estadísticas de tablas ni facturación cloud, por lo que no puede prometer mejoras concretas de rendimiento o coste. Revisa el SQL reescrito y valídalo en tu base de datos antes de desplegarlo.

### Requisitos, instalación y uso

Requiere Python 3.10 o posterior. Desde una copia local del repositorio:

```bash
python -m pip install .
sqlguard examples/bad_query.sql --dialect postgres
sqlguard ./sql/ --dialect bigquery
sqlguard ./sql/ --json
sqlguard ./sql/ --fix
sqlguard ./sql/ --fail-on-high
```

Los dialectos admitidos son `postgres`, `bigquery`, `snowflake` y `mysql`. Cada archivo debe contener exactamente una sentencia SQL; los archivos con varias sentencias se rechazan para evitar ignorar consultas. Los errores de sintaxis, ruta, codificación y escritura terminan con código 2. `--fail-on-high` termina con código 1. Si se combina con `--fix`, no se escriben cambios cuando hay algún hallazgo HIGH. `--json` escribe resultados en la salida estándar y diagnósticos en la salida de error.

### Reglas

| ID | Hallazgo | Severidad | Autofix |
|---|---|---:|---|
| SQL_001 | `SELECT *` salvo `COUNT(*)` | HIGH | No |
| SQL_002 | `ORDER BY` en CTE/subconsulta sin límite de filas | MEDIUM | Elimina el orden interno |
| SQL_003 | `YEAR(columna) = YYYY` en `WHERE` | HIGH | Rango semiabierto para una referencia simple a columna |
| SQL_004 | JOIN sin `ON`/`USING`, o `LIKE`/`ILIKE` que empieza por `%` | HIGH | No |
| SQL_005 | Cadena de `OR` con igualdades de la misma columna | LOW | Reescribe como `IN` |

La severidad y el impacto son etiquetas cualitativas, no estimaciones medidas. SQL_003 presupone que el tipo de dato y las reglas de zona horaria permiten expresar el mismo año con el rango generado. SQL_002 elimina un orden que no define el resultado exterior. Ninguna regla demuestra equivalencia para todos los motores y aplicaciones: revisa y prueba los autofixes antes de integrarlos.

### GitHub Action

La configuración en inglés anterior también funciona en repositorios en español. Con `fix: "true"`, la Action modifica archivos en el checkout del runner, pero no crea commits ni los sube al repositorio. En producción, fija la Action a un SHA revisado.

### Desarrollo y licencia

Consulta [CONTRIBUTING.md](CONTRIBUTING.md), el [historial de cambios](CHANGELOG.md) y los casos de [`examples/cases`](examples/cases/README.md). SQLGuard se distribuye bajo licencia MIT; consulta [LICENSE](LICENSE).
