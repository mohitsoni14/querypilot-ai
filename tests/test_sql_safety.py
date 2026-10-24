import pytest

from src.security.sql_policy import SQLPolicyError, validate_read_only_sql


def test_select_and_cte_are_allowed():
    assert validate_read_only_sql("WITH x AS (SELECT 1 AS n) SELECT n FROM x")


@pytest.mark.parametrize("sql", ["DROP TABLE schools", "DELETE FROM schools", "SELECT 1; SELECT 2", "PRAGMA database_list"])
def test_mutating_or_multi_statement_sql_is_rejected(sql):
    with pytest.raises(SQLPolicyError): validate_read_only_sql(sql)
