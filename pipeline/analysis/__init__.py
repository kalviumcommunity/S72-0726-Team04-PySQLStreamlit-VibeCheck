"""Analyses built on the pipeline's feature table (pipeline.features.build_feature_table)."""
from __future__ import annotations

import pandas as pd


def markdown_table(df: pd.DataFrame, floatfmt: str = ".2f") -> str:
    """Render a DataFrame as a GitHub Markdown table (no tabulate dependency)."""
    def fmt(value: object) -> str:
        if isinstance(value, float):
            return "" if pd.isna(value) else format(value, floatfmt)
        return "" if value is None or value is pd.NA else str(value).replace("|", "\\|")

    header = "| " + " | ".join(str(c) for c in df.columns) + " |"
    rule = "| " + " | ".join("---:" if pd.api.types.is_numeric_dtype(df[c]) else ":---" for c in df.columns) + " |"
    rows = ["| " + " | ".join(fmt(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join([header, rule, *rows])
