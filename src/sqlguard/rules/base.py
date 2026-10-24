from abc import ABC, abstractmethod

from sqlglot import exp

from sqlguard.models import Issue, Severity


class BaseRule(ABC):
    rule_id: str = "SQL_000"
    title: str = "Base Rule"
    severity: Severity = Severity.MEDIUM
    estimated_scan_reduction_pct: int = 10
    supports_autofix: bool = False

    @abstractmethod
    def check(self, ast: exp.Expression, dialect: str = "postgres") -> list[Issue]:
        """Inspecciona el AST sin mutarlo y devuelve la lista de problemas encontrados."""
        raise NotImplementedError

    def autofix(self, ast: exp.Expression, dialect: str = "postgres") -> exp.Expression:
        """Devuelve una copia del AST con la optimización aplicada (si aplica)."""
        return ast.copy()

    def build_issue(self, custom_desc: str) -> Issue:
        return Issue(
            rule_id=self.rule_id,
            title=self.title,
            severity=self.severity,
            description=custom_desc,
            estimated_scan_reduction_pct=self.estimated_scan_reduction_pct,
            can_autofix=self.supports_autofix,
        )
