from src.agent.orchestrator import QueryPilotOrchestrator


def test_demo_question_returns_validated_evidence(demo_context):
    engine, profiles = demo_context
    record = QueryPilotOrchestrator(engine, profiles, offline_demo=True).analyze("Which schools had falling enrolment between the last two complete academic years, and which districts had the largest percentage decline?")
    assert record.sql
    assert record.returned_rows > 0
    assert record.validation.execution_succeeded
    assert any(c["name"] == "arithmetic_consistency" for c in record.validation.checks)
