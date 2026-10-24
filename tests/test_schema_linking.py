from src.agent.question_parser import parse_question


def test_enrolment_question_links_related_tables(demo_context):
    _, profiles = demo_context
    parsed = parse_question("Which schools had falling enrolment last year?", profiles)
    assert parsed.intent == "enrolment_decline"
    assert {"schools", "enrolment", "districts", "academic_years"}.issubset(parsed.tables)
