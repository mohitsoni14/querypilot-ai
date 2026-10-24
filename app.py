from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from data.generate_demo_db import build_database
from src.agent.orchestrator import QueryPilotOrchestrator
from src.analytics.profiling import quality_summary
from src.database.connection import ConnectionConfig, engine_from_config, mask_connection_url, test_connection
from src.database.introspection import inspect_database
from src.models.base import AnalysisRecord
from src.models.open_weight_adapter import ModelConfig, OpenWeightAdapter
from src.ui.components import load_history, render_analysis, render_brand, render_empty_state, render_metric_cards, render_page_header, render_status, save_history
from src.ui.theme import inject_theme


st.set_page_config(page_title="QueryPilot AI", page_icon="◈", layout="wide", initial_sidebar_state="expanded")
inject_theme()


def ensure_demo():
    path = Path("data/demo.db")
    if not path.exists(): build_database(path)
    return path


def connect(url: str):
    engine = engine_from_config(ConnectionConfig(url=url, label="Connected database"))
    ok, message = test_connection(engine)
    if not ok: raise RuntimeError(message)
    profiles = inspect_database(engine)
    st.session_state.engine = engine
    st.session_state.profiles = profiles
    st.session_state.connection_url = url
    st.session_state.connected_at = __import__('datetime').datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")


def connected() -> bool:
    return "engine" in st.session_state and "profiles" in st.session_state


def ensure_connection():
    if not connected():
        try: connect(f"sqlite:///{ensure_demo()}")
        except Exception as exc: st.error(str(exc))


def render_connection():
    render_page_header("Workspace setup", "Connect your database", "Use a read-only SQLAlchemy connection string. QueryPilot masks credentials and inspects the schema before analysis.")
    st.markdown('<div class="qp-callout qp-callout--success"><strong>Privacy by design</strong><br><span class="qp-muted">Passwords are never shown in the interface, sent to the model, or saved in query history.</span></div>', unsafe_allow_html=True)
    st.markdown("### Connection details")
    with st.form("connection_form"):
        default = st.session_state.get("connection_url", f"sqlite:///{ensure_demo()}")
        url = st.text_input("SQLAlchemy connection string", value=default, type="password" if "://" in default and "@" in default else "default", help="Examples: sqlite:///data/demo.db or postgresql+psycopg2://user:password@host:5432/database")
        submitted = st.form_submit_button("Validate and connect", type="primary", use_container_width=True)
    if submitted:
        try:
            connect(url or ""); st.success(f"Connected and inspected {len(st.session_state.profiles)} tables/views.")
        except Exception as exc: st.error(str(exc))
    if connected():
        s=quality_summary(st.session_state.profiles)
        st.markdown("### Connection status")
        render_status("connected", "Connected and inspected")
        st.caption(f"{mask_connection_url(st.session_state.connection_url)} · last verified {st.session_state.connected_at}")
        render_metric_cards([("Tables and views", str(s["tables"]), "Accessible objects"), ("Rows inspected", f'{s["rows"]:,}', "Across connected tables"), ("Quality issues", str(s["issues"]), "Profiler findings")])


def render_dashboard():
    ensure_connection()
    st.markdown('<div class="qp-hero"><div class="qp-eyebrow">QueryPilot AI</div><h1>Ask your data better questions.</h1><div class="qp-muted">Explore your schema, generate read-only SQL, validate the evidence, and know when the database cannot answer.</div></div>', unsafe_allow_html=True)
    if not connected(): return
    summary=quality_summary(st.session_state.profiles)
    render_metric_cards([("Accessible tables", str(summary["tables"]), "Tables and views ready to explore"), ("Rows inspected", f'{summary["rows"]:,}', "Profiled from the connected database"), ("Quality issues", str(summary["issues"]), "Missing, placeholder, or duplicate signals")])
    st.markdown('<div class="qp-section-title"><div><div class="qp-kicker">Start here</div><h2>Choose a question</h2></div><span class="qp-muted">Each example uses live demo data</span></div>', unsafe_allow_html=True)
    examples=["Which schools had falling enrolment between the last two complete academic years, and which districts had the largest percentage decline?", "Which fields contain missing values in customers?", "Find duplicate customer records.", "Can this database answer a question about student attendance if no attendance data exists?"]
    example_cols = st.columns(2, gap="medium")
    for i, example in enumerate(examples):
        with example_cols[i % 2]:
            if st.button(example, key=f"example_{i}", use_container_width=True): st.session_state.pending_question=example; st.session_state.view="Analyst"; st.rerun()
    st.markdown('<div class="qp-section-title"><div><div class="qp-kicker">Workspace activity</div><h2>Recent analyses</h2></div></div>', unsafe_allow_html=True)
    history=load_history()
    if history:
        for row in history[:5]:
            st.markdown(f'<div class="qp-card"><strong>{row.get("original_question")}</strong><br><span class="qp-muted">{row.get("created_at", "")}</span><br><span class="qp-pill">{row.get("validation",{}).get("status", "unknown")}</span><span class="qp-pill">{row.get("returned_rows", 0)} rows</span></div><br>', unsafe_allow_html=True)
    else: st.info("No saved analyses yet. Run the sample question to create your first evidence-backed analysis.")


def render_analyst():
    ensure_connection()
    render_page_header("Analysis workspace", "AI Analyst", "Every answer stays linked to the source schema, read-only SQL, returned rows, and validation checks.")
    if not connected(): return
    with st.container(border=True):
        offline=st.toggle("Use reproducible offline planner", value=True, help="Uses deterministic rules for the bundled demo database. Turn off to use the configured Ollama model.")
        st.caption("Recommended for the demo. The model adapter never receives database credentials.")
    question=st.session_state.pop("pending_question", "")
    question = question or ""
    st.markdown("### Ask a business question")
    question=st.text_area("Question", value=question, height=120, placeholder="Which schools had falling enrolment last year?", label_visibility="collapsed")
    if st.button("Run analysis", type="primary", use_container_width=True) and question.strip():
        with st.spinner("Inspecting schema, executing read-only SQL, and validating evidence…"):
            orch=QueryPilotOrchestrator(st.session_state.engine, st.session_state.profiles, model=OpenWeightAdapter(ModelConfig()), offline_demo=offline)
            record=orch.analyze(question.strip())
            st.session_state.last_record=record
            save_history(record)
            if record.sql:
                from src.database.safe_executor import execute_read_only
                try: st.session_state.last_df=execute_read_only(st.session_state.engine, record.sql).dataframe
                except Exception: st.session_state.last_df=None
            else: st.session_state.last_df=None
    if "last_record" in st.session_state:
        render_analysis(st.session_state.last_record, st.session_state.get("last_df"))
    else:
        render_empty_state("Ready when you are", "Ask a natural-language question above to inspect the schema and produce a validated answer.")


def render_explorer():
    ensure_connection(); render_page_header("Data model", "Schema explorer", "Browse tables, column semantics, relationship hints, samples, and quality signals from the connected database.")
    if not connected(): return
    for profile in st.session_state.profiles:
        with st.expander(f"{profile.name} · {profile.row_count:,} rows · {len(profile.quality_issues)} issue(s)"):
            st.write({"kind":profile.kind,"primary_key":profile.primary_key,"foreign_keys":profile.foreign_keys})
            st.dataframe([c.__dict__ for c in profile.columns], use_container_width=True, hide_index=True)
            if profile.quality_issues:
                for issue in profile.quality_issues: st.warning(issue)


def render_quality():
    ensure_connection(); render_page_header("Trust center", "Data quality", "Review the issues QueryPilot found before trusting an answer.")
    if not connected(): return
    for p in st.session_state.profiles:
        issues = p.quality_issues or ["No issues detected by the lightweight profiler."]
        st.markdown(f"**{p.name}** — {p.row_count:,} rows")
        for issue in issues: st.write("⚠️ " + issue)


def render_history():
    render_page_header("Workspace activity", "Query history", "Reopen the evidence trail behind previous analyses. Credentials are never stored here.")
    history=load_history()
    if not history: render_empty_state("No analyses saved yet", "Run an analysis from the Analyst page to create your first history item.")
    for row in history:
        with st.expander(row.get("original_question", "Untitled")):
            st.write({"created_at":row.get("created_at"),"status":row.get("validation",{}).get("status"),"rows":row.get("returned_rows"),"duration_ms":row.get("execution_duration_ms")})
            if row.get("sql"): st.code(row["sql"], language="sql")
            st.write(row.get("final_answer"))


def render_benchmarks():
    render_page_header("Evaluation", "Benchmarks", "Run the reproducible local evaluation suite. QueryPilot does not claim an official BIRD score without running the benchmark.")
    st.markdown('<div class="qp-callout"><strong>What is covered</strong><br><span class="qp-muted">SQL safety, schema linking, dirty-data detection, validation, abstention, and the end-to-end demo workflow.</span></div>', unsafe_allow_html=True)
    st.code("pytest -q", language="bash")


ensure_connection()
with st.sidebar:
    render_brand()
    if connected(): render_status("connected", "Connected · demo.db" if "demo.db" in st.session_state.connection_url else "Connected")
    else: render_status("error", "Not connected")
    view=st.radio("Navigate", ["Home", "Analyst", "Database explorer", "Data quality", "Query history", "Benchmarks", "Connection"], index=["Home","Analyst","Database explorer","Data quality","Query history","Benchmarks","Connection"].index(st.session_state.get("view", "Home")))
    st.session_state.view=view
    st.caption("QueryPilot AI · local-first · evidence before confidence")

if st.session_state.view == "Home": render_dashboard()
elif st.session_state.view == "Analyst": render_analyst()
elif st.session_state.view == "Database explorer": render_explorer()
elif st.session_state.view == "Data quality": render_quality()
elif st.session_state.view == "Query history": render_history()
elif st.session_state.view == "Benchmarks": render_benchmarks()
else: render_connection()
