from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Issue(BaseModel):
    rule_id: str = Field(..., description="ID único de la regla, ej. SQL_001")
    title: str = Field(..., description="Título corto del problema detectado")
    severity: Severity
    description: str = Field(..., description="Explicación técnica del impacto en rendimiento/coste")
    estimated_scan_reduction_pct: int = Field(
        default=0, ge=0, le=100, description="Porcentaje estimado de ahorro de lectura/CPU"
    )
    can_autofix: bool = Field(default=False)


class OptimizationResult(BaseModel):
    file_path: str
    dialect: str
    original_sql: str
    optimized_sql: str
    was_modified: bool
    issues: list[Issue] = Field(default_factory=list)

    @property
    def total_estimated_savings_pct(self) -> int:
        if not self.issues:
            return 0
        # Combinación conservadora de ahorros acumulados (tope 95%)
        combined = sum(i.estimated_scan_reduction_pct for i in self.issues)
        return min(combined, 95)
