from __future__ import annotations

import pandas as pd
import plotly.express as px


def choose_chart(df: pd.DataFrame, question: str):
    if df.empty or len(df.columns) < 2:
        return None
    lower = question.lower()
    date_cols = [c for c in df.columns if "date" in c.lower() or "year" in c.lower()]
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    category_cols = [c for c in df.columns if c not in numeric_cols]
    if date_cols and numeric_cols:
        return px.line(df, x=date_cols[0], y=numeric_cols[:2], markers=True, title="Evidence over time")
    if category_cols and numeric_cols:
        return px.bar(df, x=category_cols[0], y=numeric_cols[0], title="Comparison from query results")
    return None
