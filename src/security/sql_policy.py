from __future__ import annotations

import re


class SQLPolicyError(ValueError):
    pass


FORBIDDEN = re.compile(
    r"\b(drop|delete|update|insert|alter|truncate|create|grant|revoke|attach|detach|replace|vacuum|pragma|reindex)\b",
    re.IGNORECASE,
)


def validate_read_only_sql(sql: str) -> str:
    if not sql or not sql.strip():
        raise SQLPolicyError("The generated SQL is empty.")
    clean = re.sub(r"--.*?$|/\*.*?\*/", "", sql, flags=re.MULTILINE | re.DOTALL).strip()
    if clean.count(";") > 1 or (";" in clean and not clean.rstrip().endswith(";")):
        raise SQLPolicyError("Only one SQL statement is permitted.")
    statement = clean.rstrip(";").strip()
    if not re.match(r"^(select|with)\b", statement, re.IGNORECASE):
        raise SQLPolicyError("Only SELECT statements and read-only CTEs are permitted.")
    if FORBIDDEN.search(statement):
        raise SQLPolicyError("The query contains a prohibited mutating or administrative operation.")
    if re.search(r"\b(load_extension|xp_cmdshell|into\s+outfile)\b", statement, re.IGNORECASE):
        raise SQLPolicyError("The query contains a prohibited external operation.")
    return statement
