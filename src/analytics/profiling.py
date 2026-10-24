from __future__ import annotations

from typing import Any

from src.database.introspection import TableProfile


def quality_summary(profiles: list[TableProfile]) -> dict[str, Any]:
    return {"tables": len(profiles), "rows": sum(p.row_count for p in profiles), "issues": sum(len(p.quality_issues) for p in profiles), "duplicates": sum(p.duplicate_like_rows for p in profiles)}
