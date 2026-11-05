# Changelog

Notable user-facing changes are recorded here. GitHub Action releases use semantic `v1.x` tags; the Python distribution version is maintained separately in `pyproject.toml`.

## Unreleased

## v1.0.5 — 2026-11-05 (GitHub Action)

### Changed

- Stage autofixes before replacing files and restore already-replaced files if a later write fails.
- Keep SQL_003 diagnostic-only because equivalence depends on column type, timezone, and engine.
- Clarify that no detected findings do not mean the query plan was evaluated.
- Pin GitHub Actions to full commit SHAs and check the declared minimum dependency versions in CI.
- Set the Typer and build lower bounds to releases compatible with modern Click and Python 3.10.

## v1.0.4 — 2026-11-05 (GitHub Action)

### Added

- CI across Python 3.10–3.14, package lint/build checks, and an installed-wheel CLI smoke test.
- Contributor documentation and an MIT license.

### Changed

- Reject SQL files containing multiple statements rather than silently analyzing only one.
- Preserve `ORDER BY` autofixes when a subquery has `LIMIT`, `OFFSET`, `FETCH`, or `TOP`.
- Describe rule impact qualitatively without promising measured savings or guaranteed query plans.
- Run action workflows against the local checkout with read-only permissions.

### Fixed

- Correct SQL_003's `WHERE` ancestry check using the SQLGlot parent chain.
- Improve CLI validation, diagnostics, and file read/write error handling.
