from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field, ConfigDict


class AnalystPlan(BaseModel):
    """Validated structure accepted from a model or the offline planner."""

    model_config = ConfigDict(extra="ignore")
    intent: str = "unknown"
    relevant_tables: list[str] = Field(default_factory=list)
    relevant_columns: list[str] = Field(default_factory=list)
    clarification_needed: str | None = None
    sql: str | None = None
    assumptions: list[str] = Field(default_factory=list)
    validation_plan: list[str] = Field(default_factory=list)
    answer_summary: str | None = None


class ValidationReport(BaseModel):
    execution_succeeded: bool
    returned_rows: int = 0
    checks: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    status: Literal["validated", "warning", "failed", "abstained"] = "warning"


class AnalysisRecord(BaseModel):
    question_id: str
    original_question: str
    created_at: str
    intent: str
    relevant_tables: list[str]
    relevant_columns: list[str]
    sql: str | None = None
    dialect: str
    execution_duration_ms: float | None = None
    returned_rows: int = 0
    validation: ValidationReport
    repair_attempts: int = 0
    final_answer: str
    assumptions: list[str] = Field(default_factory=list)
    data_quality_warnings: list[str] = Field(default_factory=list)
    error: str | None = None
