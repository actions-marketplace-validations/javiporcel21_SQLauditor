# Contributing

Thanks for helping improve SQLGuard. Keep changes small, explain behavior changes, and include tests for bug fixes or new behavior.

## Development setup

SQLGuard supports Python 3.10 and later. From the repository root:

```bash
python -m venv .venv
# Activate the environment, then:
python -m pip install -e ".[dev]"
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`; on macOS or Linux, use `source .venv/bin/activate`.

## Before opening a change

Run the project checks and package build:

```bash
pytest -q
ruff check .
python -m build
```

Add or update tests when changing parsing, rule detection, autofixes, CLI exit codes, JSON output, or GitHub Action behavior. Keep SQL examples to one statement per file. Autofixes must work on a copy of the AST and should be covered by tests that assert the resulting SQL and relevant safety boundaries.

## Pull requests

- Describe the user-visible change and any behavior that may affect existing SQL.
- State the checks you ran and their results.
- Update the README or changelog when behavior, CLI options, supported dialects, or Action inputs change.
- Do not describe heuristic findings as measured savings or guaranteed query-plan improvements.

## Contribuir

SQLGuard admite Python 3.10 o posterior. Sigue los pasos de instalación anteriores y ejecuta `pytest -q`, `ruff check .` y `python -m build` antes de enviar cambios. Incluye pruebas para cambios en el parser, las reglas, los autofixes, los códigos de salida o la GitHub Action. Documenta cualquier cambio visible y evita presentar heurísticas como ahorros medidos o mejoras garantizadas del plan de ejecución.
