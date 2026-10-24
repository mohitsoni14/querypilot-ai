from __future__ import annotations

import pandas as pd

from src.models.base import ValidationReport


def validate_result(df: pd.DataFrame, execution_succeeded: bool, sql_error: str | None = None) -> ValidationReport:
    if not execution_succeeded:
        return ValidationReport(execution_succeeded=False, status="failed", warnings=[sql_error or "SQL execution failed."])
    checks = [{"name": "sql_execution", "passed": True, "detail": "Read-only SQL executed successfully."}, {"name": "row_count", "passed": True, "detail": f"Returned {len(df)} row(s)."}]
    warnings: list[str] = []
    if df.empty:
        warnings.append("The query returned no rows; the answer is an evidence-backed empty result, not a fabricated value.")
    null_cells = int(df.isna().sum().sum()) if not df.empty else 0
    checks.append({"name": "null_scan", "passed": null_cells == 0, "detail": f"{null_cells} null cell(s) in the returned result."})
    if {"change", "previous_enrolment", "latest_enrolment"}.issubset(df.columns):
        arithmetic_ok = ((df["latest_enrolment"] - df["previous_enrolment"]) == df["change"]).all()
        checks.append({"name": "arithmetic_consistency", "passed": bool(arithmetic_ok), "detail": "Latest minus previous equals reported change."})
        if not arithmetic_ok:
            warnings.append("At least one reported change did not reconcile with the source values.")
    status = "validated" if not warnings and all(c["passed"] for c in checks) else "warning"
    return ValidationReport(execution_succeeded=True, returned_rows=len(df), checks=checks, warnings=warnings, status=status)
