from __future__ import annotations

import re
from dataclasses import dataclass

from src.database.introspection import TableProfile
from src.models.base import AnalystPlan


@dataclass
class ParsedQuestion:
    intent: str
    tables: list[str]
    columns: list[str]
    assumptions: list[str]
    clarification_needed: str | None = None


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", text.lower()))


def parse_question(question: str, profiles: list[TableProfile]) -> ParsedQuestion:
    tokens = _tokens(question)
    tables: list[str] = []
    columns: list[str] = []
    for profile in profiles:
        table_tokens = _tokens(profile.name.replace("_", " "))
        score = len(tokens & table_tokens)
        if score:
            tables.append(profile.name)
        for column in profile.columns:
            if tokens & _tokens(column.name.replace("_", " ")):
                columns.append(f"{profile.name}.{column.name}")
    q = question.lower()
    if any(x in q for x in ("falling enrolment", "declining enrolment", "enrollment decline", "enrolment decline")):
        intent = "enrolment_decline"
        for name in ("schools", "enrolment", "districts", "academic_years"):
            if any(p.name == name for p in profiles) and name not in tables:
                tables.append(name)
        assumptions = ["Compare the two most recent academic years marked complete.", "Percentage decline is (latest - previous) / previous * 100."]
    elif any(x in q for x in ("missing", "null", "blank")):
        intent = "missing_values"
        assumptions = ["Missing values include SQL NULLs and common placeholder strings when profiled."]
    elif any(x in q for x in ("duplicate", "duplicates")):
        intent = "duplicates"
        assumptions = ["Duplicate-like rows are exact duplicates across all accessible columns."]
    elif any(x in q for x in ("sales", "revenue", "orders")):
        intent = "sales_analysis"
        assumptions = ["Revenue is interpreted from available revenue/amount columns; no unavailable business definition is inferred."]
    elif any(x in q for x in ("how many", "count", "number of")):
        intent = "count"
        assumptions = []
    else:
        intent = "schema_question"
        assumptions = []
    clarification = None
    if not tables and intent != "schema_question":
        clarification = "I could not map the question to accessible tables or columns."
    return ParsedQuestion(intent, tables, sorted(set(columns)), assumptions, clarification)


def plan_from_question(question: str, profiles: list[TableProfile]) -> AnalystPlan:
    parsed = parse_question(question, profiles)
    return AnalystPlan(intent=parsed.intent, relevant_tables=parsed.tables, relevant_columns=parsed.columns, clarification_needed=parsed.clarification_needed, assumptions=parsed.assumptions, validation_plan=["Confirm execution succeeds", "Check returned row count", "Check arithmetic and nulls where applicable"])
