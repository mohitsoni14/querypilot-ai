from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import pandas as pd
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


@dataclass
class ColumnProfile:
    name: str
    data_type: str
    nullable: bool = True
    sample_values: list[Any] = field(default_factory=list)
    null_count: int = 0
    unique_count: int = 0
    semantic_type: str = "unknown"
    suspicious_values: list[str] = field(default_factory=list)


@dataclass
class TableProfile:
    name: str
    kind: str
    row_count: int
    columns: list[ColumnProfile]
    primary_key: list[str] = field(default_factory=list)
    foreign_keys: list[dict[str, Any]] = field(default_factory=list)
    duplicate_like_rows: int = 0
    quality_issues: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _semantic_type(name: str, dtype: str, values: list[Any]) -> str:
    n = name.lower()
    d = dtype.lower()
    if any(x in n for x in ("date", "time", "year")) or "date" in d:
        return "date"
    if any(x in n for x in ("amount", "price", "revenue", "cost", "salary", "rate", "percent", "pct")):
        return "currency" if any(x in n for x in ("amount", "price", "revenue", "cost", "salary")) else "percentage"
    if any(x in n for x in ("id", "code", "key")):
        return "identifier"
    if "int" in d or "float" in d or "decimal" in d or "numeric" in d:
        return "numeric"
    distinct = {str(v).strip().lower() for v in values if v is not None}
    return "categorical" if 0 < len(distinct) <= 30 else "text"


def _safe_rows(engine: Engine, table: str, limit: int = 5) -> pd.DataFrame:
    return pd.read_sql_query(text(f'SELECT * FROM "{table.replace(chr(34), chr(34)*2)}" LIMIT {int(limit)}'), engine)


def inspect_database(engine: Engine, sample_rows: int = 5) -> list[TableProfile]:
    inspector = inspect(engine)
    names: list[tuple[str, str]] = [(t, "table") for t in inspector.get_table_names()]
    names += [(v, "view") for v in inspector.get_view_names() if v not in {x[0] for x in names}]
    profiles: list[TableProfile] = []
    for table, kind in names:
        columns_info = inspector.get_columns(table)
        pk = inspector.get_pk_constraint(table).get("constrained_columns") or []
        fks = inspector.get_foreign_keys(table)
        try:
            df = _safe_rows(engine, table, sample_rows)
            row_count = int(pd.read_sql_query(text(f'SELECT COUNT(*) AS n FROM "{table.replace(chr(34), chr(34)*2)}"'), engine).iloc[0, 0])
        except Exception:
            df = pd.DataFrame(columns=[c["name"] for c in columns_info])
            row_count = 0
        columns: list[ColumnProfile] = []
        quality: list[str] = []
        for c in columns_info:
            name = c["name"]
            values = df[name].dropna().head(5).tolist() if name in df else []
            try:
                null_count = int(pd.read_sql_query(text(f'SELECT COUNT(*) AS n FROM "{table}" WHERE "{name}" IS NULL'), engine).iloc[0, 0])
                unique_count = int(pd.read_sql_query(text(f'SELECT COUNT(DISTINCT "{name}") AS n FROM "{table}"'), engine).iloc[0, 0])
            except Exception:
                null_count, unique_count = 0, 0
            suspicious = []
            for value in values:
                if isinstance(value, str) and (not value.strip() or value.strip().upper() in {"N/A", "NA", "NULL", "UNKNOWN", "-"}):
                    suspicious.append(str(value))
            semantic = _semantic_type(name, str(c.get("type", "")), values)
            if suspicious:
                quality.append(f"{name} contains placeholder values: {', '.join(sorted(set(suspicious)))}")
            columns.append(ColumnProfile(name, str(c.get("type", "")), bool(c.get("nullable", True)), values, null_count, unique_count, semantic, suspicious))
        try:
            all_rows = pd.read_sql_query(text(f'SELECT * FROM "{table.replace(chr(34), chr(34)*2)}"'), engine)
            identity_cols = [c["name"] for c in columns_info if c["name"] not in pk and c["name"].lower() not in {"id", "created_at"}]
            if identity_cols and not all_rows.empty:
                duplicate_like = int(all_rows.duplicated(subset=identity_cols, keep=False).sum())
            else:
                duplicate_like = max(0, row_count - int(pd.read_sql_query(text(f'SELECT COUNT(*) AS n FROM (SELECT DISTINCT * FROM "{table}")'), engine).iloc[0, 0]))
        except Exception:
            duplicate_like = 0
        if duplicate_like:
            quality.append(f"{duplicate_like} duplicate-like row(s) detected")
        profiles.append(TableProfile(table, kind, row_count, columns, list(pk), fks, duplicate_like, quality))
    return profiles


def schema_context(profiles: list[TableProfile], max_samples: int = 3) -> str:
    chunks = []
    for table in profiles:
        cols = ", ".join(f"{c.name} ({c.data_type}, {c.semantic_type})" for c in table.columns)
        chunks.append(f"{table.kind.upper()} {table.name}: {cols}; rows={table.row_count}; PK={table.primary_key}; FKs={table.foreign_keys}; samples=" + str({c.name: c.sample_values[:max_samples] for c in table.columns if c.sample_values}))
    return "\n".join(chunks)
