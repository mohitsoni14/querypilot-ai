from src.agent.orchestrator import QueryPilotOrchestrator


def test_unsupported_question_abstains_without_sql(demo_context):
    engine, profiles = demo_context
    record = QueryPilotOrchestrator(engine, profiles, offline_demo=True).analyze("Can you tell me about student attendance?")
    assert record.sql is None
    assert "cannot answer" in record.final_answer.lower()
