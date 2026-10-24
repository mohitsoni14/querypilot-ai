from __future__ import annotations

import os
import time
import uuid
from datetime import datetime, timezone

from src.agent.answer_generator import answer_from_result
from src.agent.question_parser import plan_from_question
from src.agent.result_validator import validate_result
from src.agent.sql_generator import generate_demo_sql
from src.agent.sql_repair import repair_plan
from src.database.introspection import TableProfile, schema_context
from src.database.safe_executor import execute_read_only
from src.models.base import AnalysisRecord, AnalystPlan
from src.models.open_weight_adapter import ModelUnavailable, OpenWeightAdapter


class QueryPilotOrchestrator:
    def __init__(self, engine, profiles: list[TableProfile], model: OpenWeightAdapter | None = None, offline_demo: bool = True):
        self.engine = engine
        self.profiles = profiles
        self.model = model or OpenWeightAdapter()
        self.offline_demo = offline_demo
        self.max_attempts = int(os.getenv("QUERYPILOT_MAX_REPAIR_ATTEMPTS", "3"))
        self.row_limit = int(os.getenv("QUERYPILOT_ROW_LIMIT", "1000"))

    def analyze(self, question: str) -> AnalysisRecord:
        started = time.perf_counter()
        plan: AnalystPlan
        model_note = None
        if self.offline_demo:
            plan = plan_from_question(question, self.profiles)
            plan = generate_demo_sql(plan, self.profiles)
            plan.assumptions.append("Offline deterministic planner selected; switch to Ollama for open-weight model inference.")
        else:
            try:
                plan = self.model.plan(question, schema_context(self.profiles))
            except ModelUnavailable as exc:
                model_note = str(exc)
                plan = plan_from_question(question, self.profiles)
                plan.clarification_needed = model_note
        if not plan.sql:
            report = validate_result(__import__('pandas').DataFrame(), False, plan.clarification_needed)
            answer = answer_from_result(question, plan, __import__('pandas').DataFrame(), report)
            return AnalysisRecord(question_id=str(uuid.uuid4()), original_question=question, created_at=datetime.now(timezone.utc).isoformat(), intent=plan.intent, relevant_tables=plan.relevant_tables, relevant_columns=plan.relevant_columns, dialect=self.engine.dialect.name, validation=report, final_answer=answer, assumptions=plan.assumptions, data_quality_warnings=[model_note] if model_note else [])
        repair_attempts = 0
        result = None
        report = None
        for attempt in range(self.max_attempts):
            repair_attempts = attempt
            try:
                result = execute_read_only(self.engine, plan.sql, self.row_limit)
            except Exception as exc:
                result = type("Result", (), {"dataframe": __import__('pandas').DataFrame(), "duration_ms": 0.0, "sql": plan.sql, "error": str(exc)})()
            report = validate_result(result.dataframe, result.error is None, result.error)
            if report.execution_succeeded:
                break
            if attempt + 1 < self.max_attempts:
                plan = repair_plan(plan, result.error or "unknown error", attempt + 1)
        assert result is not None and report is not None
        answer = answer_from_result(question, plan, result.dataframe, report)
        warnings = list(report.warnings)
        if model_note:
            warnings.append(model_note)
        return AnalysisRecord(question_id=str(uuid.uuid4()), original_question=question, created_at=datetime.now(timezone.utc).isoformat(), intent=plan.intent, relevant_tables=plan.relevant_tables, relevant_columns=plan.relevant_columns, sql=result.sql, dialect=self.engine.dialect.name, execution_duration_ms=result.duration_ms, returned_rows=len(result.dataframe), validation=report, repair_attempts=repair_attempts, final_answer=answer, assumptions=plan.assumptions, data_quality_warnings=warnings, error=result.error)
