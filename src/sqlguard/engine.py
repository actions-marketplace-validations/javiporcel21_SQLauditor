from sqlguard.models import Issue, OptimizationResult
from sqlguard.parser import format_sql, parse_sql
from sqlguard.rules.base import BaseRule
from sqlguard.rules.sql_001_select_star import SelectStarRule
from sqlguard.rules.sql_002_redundant_subquery_orderby import (
    RedundantSubqueryOrderByRule,
)
from sqlguard.rules.sql_003_non_sargable_year import NonSargableYearRule
from sqlguard.rules.sql_004_cartesian_and_leading_wildcard import (
    CartesianAndWildcardRule,
)
from sqlguard.rules.sql_005_or_to_in_rewrite import OrToInRewriteRule

DEFAULT_RULES: list[BaseRule] = [
    SelectStarRule(),
    RedundantSubqueryOrderByRule(),
    NonSargableYearRule(),
    CartesianAndWildcardRule(),
    OrToInRewriteRule(),
]


def analyze_and_optimize_sql(
    sql: str,
    dialect: str = "postgres",
    file_path: str = "inline.sql",
    rules: list[BaseRule] | None = None,
) -> OptimizationResult:
    active_rules = rules if rules is not None else DEFAULT_RULES
    ast = parse_sql(sql, dialect=dialect)
    current_ast = ast.copy()

    all_issues: list[Issue] = []

    for rule in active_rules:
        detected = rule.check(current_ast, dialect=dialect)
        if detected:
            all_issues.extend(detected)
            if rule.supports_autofix:
                current_ast = rule.autofix(current_ast, dialect=dialect)

    original_formatted = format_sql(ast, dialect=dialect)
    optimized_formatted = format_sql(current_ast, dialect=dialect)

    return OptimizationResult(
        file_path=file_path,
        dialect=dialect,
        original_sql=original_formatted,
        optimized_sql=optimized_formatted,
        was_modified=(original_formatted != optimized_formatted),
        issues=all_issues,
    )
