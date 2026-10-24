import pandas as pd

from src.agent.result_validator import validate_result


def test_enrolment_arithmetic_is_checked():
    df = pd.DataFrame([{ "previous_enrolment": 100, "latest_enrolment": 90, "change": -10 }])
    report = validate_result(df, True)
    assert any(c["name"] == "arithmetic_consistency" and c["passed"] for c in report.checks)
    assert report.status == "validated"
