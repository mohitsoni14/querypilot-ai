from __future__ import annotations

import time
from dataclasses import dataclass

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.database.connection import sanitize_db_error
from src.security.sql_policy import validate_read_only_sql


@dataclass
class ExecutionResult:
    dataframe: pd.DataFrame
    duration_ms: float
    sql: str
    error: str | None = None


def execute_read_only(engine: Engine, sql: str, row_limit: int = 1000) -> ExecutionResult:
    safe_sql = validate_read_only_sql(sql)
    started = time.perf_counter()
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(text(safe_sql), conn)
        if len(df) > row_limit:
            df = df.head(row_limit)
        return ExecutionResult(df, (time.perf_counter() - started) * 1000, safe_sql)
    except Exception as exc:
        return ExecutionResult(pd.DataFrame(), (time.perf_counter() - started) * 1000, safe_sql, sanitize_db_error(exc))
