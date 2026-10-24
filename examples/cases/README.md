# SQLGuard test cases

Each `.sql` file is an independent case. Run the GitHub Actions workflow **Audit SQL test cases** to see the findings and autofixed SQL in the Actions log. The workflow copies the examples to a temporary directory before enabling autofix, so the source cases in this folder remain unchanged. It does not fail on HIGH findings.

| File | Expected result | Autofix |
|---|---|---|
| `SQL_001_select_star.sql` | SQL_001, HIGH | No |
| `SQL_002_order_by_in_cte.sql` | SQL_002, MEDIUM | Removes `ORDER BY` inside the CTE |
| `SQL_003_year_function.sql` | SQL_003, HIGH | Rewrites the year predicate to a date range |
| `SQL_004_cartesian_join.sql` | SQL_004, HIGH | No |
| `SQL_004_leading_wildcard.sql` | SQL_004, HIGH | No |
| `SQL_005_or_to_in.sql` | SQL_005, LOW | Rewrites the `OR` chain to `IN` |
| `no_issue.sql` | No findings | Not needed |

To try the autofixes locally without changing these examples:

```bash
sqlguard examples/cases/SQL_002_order_by_in_cte.sql --fix
sqlguard examples/cases/SQL_003_year_function.sql --fix
sqlguard examples/cases/SQL_005_or_to_in.sql --fix
```
