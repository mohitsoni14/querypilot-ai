from src.database.introspection import inspect_database


def test_profiler_detects_placeholder_and_duplicate_like_data(demo_context):
    _, profiles = demo_context
    customers = next(p for p in profiles if p.name == "customers")
    assert any("placeholder" in issue for issue in customers.quality_issues)
    assert customers.duplicate_like_rows >= 1
