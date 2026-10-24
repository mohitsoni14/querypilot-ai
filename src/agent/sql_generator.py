from __future__ import annotations

from src.database.introspection import TableProfile
from src.models.base import AnalystPlan


def _has(profiles: list[TableProfile], name: str) -> bool:
    return any(p.name == name for p in profiles)


def generate_demo_sql(plan: AnalystPlan, profiles: list[TableProfile]) -> AnalystPlan:
    if plan.sql or plan.clarification_needed:
        return plan
    if plan.intent == "enrolment_decline" and all(_has(profiles, x) for x in ("schools", "enrolment", "districts", "academic_years")):
        plan.sql = """WITH complete_years AS (
    SELECT id, label, end_date,
           ROW_NUMBER() OVER (ORDER BY end_date DESC) AS year_rank
    FROM academic_years
    WHERE is_complete = 1
), paired AS (
    SELECT s.name AS school, d.name AS district,
           prev.label AS previous_year, latest.label AS latest_year,
           prev_e.enrolled_count AS previous_enrolment,
           latest_e.enrolled_count AS latest_enrolment,
           latest_e.enrolled_count - prev_e.enrolled_count AS change,
           ROUND(100.0 * (latest_e.enrolled_count - prev_e.enrolled_count) / NULLIF(prev_e.enrolled_count, 0), 2) AS pct_change
    FROM enrolment prev_e
    JOIN complete_years prev ON prev.id = prev_e.academic_year_id AND prev.year_rank = 2
    JOIN enrolment latest_e ON latest_e.school_id = prev_e.school_id
    JOIN complete_years latest ON latest.id = latest_e.academic_year_id AND latest.year_rank = 1
    JOIN schools s ON s.id = latest_e.school_id
    JOIN districts d ON d.id = s.district_id
)
SELECT * FROM paired
WHERE change < 0
ORDER BY pct_change ASC, school"""
        plan.answer_summary = "Schools with declining enrolment between the two most recent complete academic years, ranked by percentage decline."
        return plan
    if plan.intent == "missing_values":
        table = plan.relevant_tables[0] if plan.relevant_tables else None
        if table:
            cols = next((p.columns for p in profiles if p.name == table), [])
            expressions = ", ".join(f'SUM(CASE WHEN "{c.name}" IS NULL OR TRIM(CAST("{c.name}" AS TEXT)) IN ("", "N/A", "NA", "NULL") THEN 1 ELSE 0 END) AS "{c.name}"' for c in cols)
            plan.sql = f'SELECT COUNT(*) AS total_rows, {expressions} FROM "{table}"'
            plan.answer_summary = f"Missing-value counts for {table}."
            return plan
    if plan.intent == "duplicates":
        table = plan.relevant_tables[0] if plan.relevant_tables else None
        if table:
            plan.sql = f'SELECT *, COUNT(*) AS duplicate_count FROM "{table}" GROUP BY ' + ', '.join(f'"{c.name}"' for c in next(p for p in profiles if p.name == table).columns) + ' HAVING COUNT(*) > 1 ORDER BY duplicate_count DESC'
            plan.answer_summary = f"Exact duplicate-like records in {table}."
            return plan
    if plan.intent == "count" and plan.relevant_tables:
        plan.sql = f'SELECT COUNT(*) AS row_count FROM "{plan.relevant_tables[0]}"'
        plan.answer_summary = f"Count of rows in {plan.relevant_tables[0]}."
        return plan
    plan.clarification_needed = plan.clarification_needed or "The available schema does not support a safe, evidence-backed query for this request."
    return plan
