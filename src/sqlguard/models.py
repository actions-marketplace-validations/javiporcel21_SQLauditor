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
    description: str = Field(..., description="Descripción del hallazgo y de su posible efecto")
    impact: str = Field(default="moderate", description="Impacto cualitativo; no estima ahorros")
    can_autofix: bool = Field(default=False)


class OptimizationResult(BaseModel):
    file_path: str
    dialect: str
    original_sql: str
    optimized_sql: str
    was_modified: bool
    issues: list[Issue] = Field(default_factory=list)
