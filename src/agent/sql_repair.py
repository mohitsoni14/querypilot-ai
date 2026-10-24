from __future__ import annotations

from src.models.base import AnalystPlan


def repair_plan(plan: AnalystPlan, error: str, attempt: int) -> AnalystPlan:
    """Conservative repair hook. It only removes trailing semicolons and reports the error."""
    if plan.sql:
        plan.sql = plan.sql.strip().rstrip(";")
    plan.assumptions.append(f"Repair attempt {attempt}: database rejected the first query ({error[:160]}).")
    return plan
