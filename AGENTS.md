# Reglas Estrictas del Proyecto sqlguard (MVP)

## 1. Alcance y Stack
- Proyecto exclusivamente en Python 3.10+ para analizar y reescribir consultas SQL mediante `sqlglot`.
- PROHIBIDO usar expresiones regulares (`re`) para analizar o modificar SQL. Todo debe hacerse mediante `sqlglot.parse_one` y manipulación de nodos `sqlglot.expressions` (`exp`).
- Modelos de datos estrictamente en Pydantic v2 (`BaseModel`, `Field`).

## 2. Arquitectura de Reglas
- Cada regla vive en `src/sqlguard/rules/sql_XXX_<nombre>.py` y hereda de `BaseRule` (`src/sqlguard/rules/base.py`).
- El método `check(self, ast: exp.Expression, dialect: str) -> list[Issue]` NUNCA muta el AST recibido.
- El método `autofix(self, ast: exp.Expression, dialect: str) -> exp.Expression` trabaja siempre sobre `ast.copy()` y devuelve el nuevo AST optimizado.

## 3. Verificación Obligatoria
- Después de crear o editar cualquier archivo, ejecuta SIEMPRE en terminal: `pytest -q` y `ruff check .`
- Ninguna tarea está terminada si `pytest` falla.
