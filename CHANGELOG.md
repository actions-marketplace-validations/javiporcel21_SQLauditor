# Changelog

Notable user-facing changes are recorded here. This project has not published a release from this changelog yet.

## Unreleased

### Added

- CI checks for tests across supported Python versions, Ruff, and source distribution/wheel builds.
- Local composite Action smoke checks for autofixes, HIGH-severity blocking, and already-clean SQL.
- Contributor instructions and an MIT license file.

### Changed

- Reject SQL files containing multiple statements instead of silently analyzing only one.
- Return clear CLI errors for unsupported dialects, missing paths, read failures, and write failures.
- Treat rule impact as qualitative and describe findings without promising measured savings or guaranteed execution plans.
- Preserve `ORDER BY` autofixes when a subquery uses `LIMIT`, `OFFSET`, `FETCH`, or `TOP`.
- Clarify that SQLGuard is a static heuristic tool and that autofixes must be reviewed and validated.
- Replace the unsupported `estimated_scan_reduction_pct` issue field and aggregate with qualitative `impact` metadata; clients reading JSON results should update accordingly.
