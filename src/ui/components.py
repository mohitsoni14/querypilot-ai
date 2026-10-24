from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.analytics.visualizations import choose_chart
from src.models.base import AnalysisRecord


def render_brand():
    st.markdown('<div class="qp-brand"><div class="qp-mark" aria-hidden="true"></div><div><div class="qp-brand-name">QueryPilot</div><div class="qp-brand-subtitle">Self-validating data analyst</div></div></div>', unsafe_allow_html=True)


def render_page_header(eyebrow: str, title: str, description: str) -> None:
    st.markdown(f'<div class="qp-eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<div class="qp-muted">{description}</div>', unsafe_allow_html=True)


def render_status(status: str, label: str | None = None) -> None:
    normalized = status.lower().strip()
    tone = "success" if normalized in {"validated", "connected", "ready", "success"} else "danger" if normalized in {"failed", "error", "abstained"} else "warning" if normalized in {"warning", "degraded"} else "neutral"
    text = label or status.replace("_", " ").title()
    st.markdown(f'<span class="qp-status qp-status--{tone}" role="status">{text}</span>', unsafe_allow_html=True)


def render_metric_cards(metrics: list[tuple[str, str, str | None]]) -> None:
    columns = st.columns(len(metrics))
    for column, (label, value, helper) in zip(columns, metrics):
        with column:
            helper_html = f'<div class="qp-muted">{helper}</div>' if helper else ''
            st.markdown(f'<div class="qp-card qp-card-compact"><div class="qp-kicker">{label}</div><div class="qp-value">{value}</div>{helper_html}</div>', unsafe_allow_html=True)


def render_empty_state(title: str, detail: str) -> None:
    st.markdown(f'<div class="qp-empty"><strong>{title}</strong><br><span>{detail}</span></div>', unsafe_allow_html=True)


def render_analysis(record: AnalysisRecord, dataframe: pd.DataFrame | None = None):
    st.markdown('<div class="qp-section-title"><div><div class="qp-kicker">Analysis result</div><h2>Evidence-backed answer</h2></div></div>', unsafe_allow_html=True)
    st.success(record.final_answer)
    render_status(record.validation.status)
    for value in (record.intent.replace("_", " ").title(), f"{record.returned_rows} returned rows", record.dialect.upper()):
        st.markdown(f'<span class="qp-pill">{value}</span>', unsafe_allow_html=True)

    overview, evidence, validation = st.tabs(["Overview", "Evidence", "Validation"])
    with overview:
        left, right = st.columns([1.2, .8], gap="large")
        with left:
            st.markdown("#### Interpreted question")
            st.write(record.original_question)
            st.markdown("#### Relevant schema")
            if record.relevant_tables:
                st.write("Tables: " + ", ".join(record.relevant_tables))
            if record.relevant_columns:
                st.write("Columns: " + ", ".join(record.relevant_columns))
        with right:
            st.markdown("#### Execution timeline")
            st.markdown('<div class="qp-timeline"><div><span class="qp-dot"></span><span class="qp-step-label">Question parsed</span><div class="qp-step-detail">Intent and business terms identified.</div></div><div><span class="qp-dot"></span><span class="qp-step-label">Schema discovered</span><div class="qp-step-detail">Relevant tables and columns selected.</div></div><div><span class="qp-dot"></span><span class="qp-step-label">Read-only SQL executed</span><div class="qp-step-detail">No database mutations permitted.</div></div><div><span class="qp-dot"></span><span class="qp-step-label">Evidence validated</span><div class="qp-step-detail">Rows, nulls, and arithmetic checked.</div></div></div>', unsafe_allow_html=True)
            if record.execution_duration_ms is not None:
                st.caption(f"Execution time: {record.execution_duration_ms:.0f} ms")
    with evidence:
        if record.sql:
            st.markdown("#### SQL used")
            st.code(record.sql, language="sql")
            sql_col, csv_col = st.columns(2)
            with sql_col:
                st.download_button("Download SQL", record.sql, file_name=f"{record.question_id}.sql", mime="text/plain", use_container_width=True)
            with csv_col:
                if dataframe is not None and not dataframe.empty:
                    st.download_button("Download result CSV", dataframe.to_csv(index=False), file_name=f"{record.question_id}.csv", mime="text/csv", use_container_width=True)
        if dataframe is not None and not dataframe.empty:
            st.markdown("#### Returned rows")
            st.dataframe(dataframe, use_container_width=True, hide_index=True)
            chart = choose_chart(dataframe, record.original_question)
            if chart is not None:
                st.markdown("#### Visual summary")
                st.plotly_chart(chart, use_container_width=True)
        elif record.validation.execution_succeeded:
            render_empty_state("No matching rows", "The database returned an empty result. QueryPilot did not infer or fabricate a value.")
        elif record.error:
            st.error(record.error)
    with validation:
        st.markdown("#### Validation checks")
        for check in record.validation.checks:
            if check["passed"]:
                st.success(f"{check['name'].replace('_', ' ').title()}: {check['detail']}")
            else:
                st.warning(f"{check['name'].replace('_', ' ').title()}: {check['detail']}")
        for warning in record.validation.warnings + record.data_quality_warnings:
            st.warning(warning)
        if record.assumptions:
            st.markdown("#### Assumptions")
            for assumption in record.assumptions:
                st.write("• " + assumption)


def history_path() -> Path:
    path = Path("data/query_history.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def save_history(record: AnalysisRecord):
    path = history_path()
    existing = []
    if path.exists():
        try: existing = json.loads(path.read_text(encoding="utf-8"))
        except Exception: existing = []
    existing = [record.model_dump(mode="json")] + [x for x in existing if x.get("question_id") != record.question_id]
    path.write_text(json.dumps(existing[:50], indent=2), encoding="utf-8")


def load_history() -> list[dict]:
    path = history_path()
    if not path.exists(): return []
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception: return []
