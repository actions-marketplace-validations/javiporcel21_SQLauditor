# SQLGuard ⚡

### Static SQL Optimizer & FinOps Rewriter via AST

> Catch expensive SQL antipatterns **before they hit production**. Zero database connections required.

---

## 🌍 English

### The Problem

A single `SELECT *` on BigQuery can scan **terabytes** of data you don't need. A `YEAR(col) = 2026` in your WHERE clause **kills every index** on that column. These mistakes cost real money — and most teams only discover them after the bill arrives.

### The Solution

**SQLGuard** analyzes your SQL files statically via AST (Abstract Syntax Tree) using [sqlglot](https://github.com/tobymao/sqlglot). No database connection needed. It detects antipatterns, estimates the scan/CPU reduction, and **automatically rewrites** your queries to be optimal.

### Before & After

**Before** (your original query):
```sql
WITH recent_orders AS (
    SELECT id, customer_id, order_date, status, total_amount
    FROM sales.orders
    WHERE YEAR(order_date) = 2026
      AND (status = 'PAID' OR status = 'SHIPPED')
    ORDER BY order_date DESC
)
SELECT *
FROM recent_orders
WHERE customer_name LIKE '%garcia';
```

**After** (automatically rewritten by SQLGuard):
```sql
WITH recent_orders AS (
  SELECT
    id,
    customer_id,
    order_date,
    status,
    total_amount
  FROM sales.orders
  WHERE
    order_date >= '2026-01-01'
    AND order_date < '2027-01-01'
    AND status IN ('PAID', 'SHIPPED')
)
SELECT
  *
FROM recent_orders
WHERE
  customer_name LIKE '%garcia'
```

**What changed:**
- `YEAR(order_date) = 2026` → sargable range `order_date >= '2026-01-01' AND order_date < '2027-01-01'` (index & partition friendly)
- `status = 'PAID' OR status = 'SHIPPED'` → `status IN ('PAID', 'SHIPPED')` (simpler execution plan)
- `ORDER BY order_date DESC` removed from CTE (useless without LIMIT)

### Quick Start

```bash
# Install
pip install .

# Analyze a single file
sqlguard examples/bad_query.sql --dialect postgres

# Analyze an entire folder
sqlguard ./sql/ --dialect bigquery

# Auto-fix files in place
sqlguard ./sql/ --fix

# JSON output for CI/CD
sqlguard ./sql/ --json

# Fail CI if HIGH severity issues found
sqlguard ./sql/ --fail-on-high
```

### GitHub Action Integration

Add SQLGuard to any repository in **5 lines of YAML**:

```yaml
# .github/workflows/sql-audit.yml
name: SQL Audit
on: [pull_request]
jobs:
  sqlguard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: javiporcel21/SQLauditor@v1.0.2
        with:
          path: "."
          dialect: "postgres"
          fail_on_high: "true"
          fix: "true"
```

With `fix: "true"`, SQLGuard overwrites files in the runner's checkout when a supported autofix applies. The action itself does not commit or push the changes; a workflow can add a separate commit-and-push step if you want the optimized SQL saved to the branch. This repository's `Test SQLGuard Action` workflow demonstrates that flow for `examples/autofix_smoke.sql`. If the query has no supported optimizations, the workflow succeeds without creating a commit.

### Rules (Community Edition)

| ID | Rule | Severity | Estimated Savings | Autofix |
|---|---|---|---|---|
| SQL_001 | `SELECT *` in production queries | HIGH | ~60% scan reduction | Manual |
| SQL_002 | `ORDER BY` in CTE/subquery without `LIMIT` | MEDIUM | ~25% CPU savings | ✔ Auto |
| SQL_003 | `YEAR(col) = YYYY` non-sargable predicate | HIGH | ~75% scan reduction | ✔ Auto |
| SQL_004 | Cartesian product (JOIN without ON) / Leading wildcard LIKE | HIGH | ~80% scan reduction | Manual |
| SQL_005 | `col = 'A' OR col = 'B'` chains → `IN` | LOW | ~15% plan simplification | ✔ Auto |

### Supported Dialects

PostgreSQL, BigQuery, Snowflake, MySQL — powered by [sqlglot](https://github.com/tobymao/sqlglot).

---

## 🌍 Español

### El Problema

Un solo `SELECT *` en BigQuery puede escanear **terabytes** de datos innecesarios. Un `YEAR(col) = 2026` en tu WHERE **anula todos los índices** de esa columna. Estos errores cuestan dinero real — y la mayoría de equipos solo los descubren cuando llega la factura.

### La Solución

**SQLGuard** analiza tus archivos SQL de forma estática mediante AST (Árbol de Sintaxis Abstracta) usando [sqlglot](https://github.com/tobymao/sqlglot). Sin conexión a base de datos. Detecta antipatrones, estima la reducción de escaneo/CPU, y **reescribe automáticamente** tus consultas para que sean óptimas.

### Inicio Rápido

```bash
# Instalar
pip install .

# Analizar un archivo
sqlguard examples/bad_query.sql --dialect postgres

# Analizar una carpeta entera
sqlguard ./sql/ --dialect bigquery

# Auto-corregir archivos
sqlguard ./sql/ --fix

# Salida JSON para CI/CD
sqlguard ./sql/ --json

# Fallar CI si hay problemas HIGH
sqlguard ./sql/ --fail-on-high
```

### Integración como GitHub Action

Añade SQLGuard a cualquier repositorio en **5 líneas de YAML**:

```yaml
# .github/workflows/sql-audit.yml
name: SQL Audit
on: [pull_request]
jobs:
  sqlguard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: javiporcel21/SQLauditor@v1.0.2
        with:
          path: "."
          dialect: "postgres"
          fail_on_high: "true"
          fix: "true"
```

Con `fix: "true"`, SQLGuard sobrescribe los archivos en la copia de trabajo del runner cuando aplica una regla de autofix compatible. La acción por sí sola no crea ningún commit ni sube esos cambios; un workflow puede añadir un paso separado para guardar el resultado en la rama. El workflow `Test SQLGuard Action` de este repositorio muestra ese flujo con `examples/autofix_smoke.sql`. Si la consulta no tiene optimizaciones compatibles, el workflow termina correctamente sin crear un commit.

### Casos de prueba SQL

La carpeta [`examples/cases`](./examples/cases/README.md) contiene consultas independientes para las reglas SQL_001 a SQL_005, incluidos los dos patrones de SQL_004 y un caso sin hallazgos. El workflow `Audit SQL test cases` las analiza en modo informativo: muestra los resultados, no falla por hallazgos HIGH y no modifica los archivos.

### Reglas Incluidas (Edición Community)

| ID | Regla | Severidad | Ahorro Estimado | Autofix |
|---|---|---|---|---|
| SQL_001 | `SELECT *` en consultas de producción | HIGH | ~60% reducción de escaneo | Manual |
| SQL_002 | `ORDER BY` en CTE/subconsulta sin `LIMIT` | MEDIUM | ~25% ahorro de CPU | ✔ Auto |
| SQL_003 | `YEAR(col) = YYYY` predicado no sargable | HIGH | ~75% reducción de escaneo | ✔ Auto |
| SQL_004 | Producto cartesiano (JOIN sin ON) / LIKE con comodín inicial | HIGH | ~80% reducción de escaneo | Manual |
| SQL_005 | Cadenas `col = 'A' OR col = 'B'` → `IN` | LOW | ~15% simplificación de plan | ✔ Auto |

---

## 🚀 Pro Roadmap

| Feature | Description | Status |
|---|---|---|
| **Metadata Catalog Integration** | Connect to dbt, Alation, or DataHub catalogs to calculate actual cost in EUR/USD per query | Planned |
| **Auto-commit in Pull Requests** | Automatically push optimized SQL as a commit suggestion in PRs | Planned |
| **Cost Estimation Engine** | Estimate BigQuery/Snowflake cost savings in real currency based on table metadata | Planned |
| **Custom Rule SDK** | Define your own rules with a simple Python API | Planned |
| **VS Code Extension** | Real-time SQL optimization feedback in the editor | Planned |
| **Slack/Teams Notifications** | Alert channels when expensive queries are detected in PRs | Planned |

---

## Development

```bash
# Setup
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/Mac

pip install -e .
pip install pytest ruff

# Run tests
pytest -q

# Lint
ruff check .
```

## License

MIT
