from __future__ import annotations

import pandas as pd

from src.models.base import AnalystPlan, ValidationReport


def answer_from_result(question: str, plan: AnalystPlan, df: pd.DataFrame, report: ValidationReport) -> str:
    if plan.clarification_needed and not plan.sql:
        return f"I cannot answer this from the connected database. {plan.clarification_needed}"
    if not report.execution_succeeded:
        return f"I could not answer this because the read-only SQL failed: {report.warnings[0] if report.warnings else 'unknown database error'}"
    if df.empty:
        return "The database returned no matching records for this question. I did not infer or fabricate a result."
    if plan.intent == "enrolment_decline" and "school" in df.columns:
        top = df.iloc[0]
        district_count = int(df["district"].nunique()) if "district" in df else 0
        return f"{len(df)} school(s) had falling enrolment across the two most recent complete academic years, spanning {district_count} district(s). The largest percentage decline was {top['school']} ({top['pct_change']:.2f}%), from {int(top['previous_enrolment'])} to {int(top['latest_enrolment'])} students."
    if plan.intent == "missing_values":
        total = int(df.iloc[0].get("total_rows", 0))
        nonzero = [(col, int(df.iloc[0][col])) for col in df.columns if col != "total_rows" and pd.notna(df.iloc[0][col]) and int(df.iloc[0][col]) > 0]
        detail = ", ".join(f"{col}: {count}" for col, count in nonzero[:6]) or "no missing values detected"
        return f"Profiled {total} row(s). Missing or placeholder values were found as follows: {detail}."
    if plan.intent == "duplicates":
        return f"Found {len(df)} duplicate group(s). The result table shows the repeated values and their duplicate counts."
    if len(df) == 1 and len(df.columns) == 1:
        return f"The answer is {df.iloc[0, 0]}."
    return f"The query returned {len(df)} evidence row(s). Review the result table and validation report for the complete answer."
