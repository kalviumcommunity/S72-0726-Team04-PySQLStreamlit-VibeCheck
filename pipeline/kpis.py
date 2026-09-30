"""Onboarding KPIs computed in pandas - the Python twin of pipeline/sql/kpis/.

Works on any slice of the feature table, so the dashboard can recompute KPIs for
a filtered cohort without a database round trip. Key names match the SQL aliases.
"""
from __future__ import annotations

import pandas as pd

KPI_KEYS = (
    "total_hires",
    "completed_count",
    "in_progress_count",
    "delayed_count",
    "completion_rate_pct",
    "avg_days_to_complete",
    "avg_training_pct",
    "buddy_coverage_pct",
    "first_week_checkin_pct",
)


def _pct(part: int, whole: int) -> float | None:
    return round(100 * part / whole, 2) if whole else None


def _mean(values: pd.Series) -> float | None:
    values = values.dropna().astype("float64")
    return round(float(values.mean()), 2) if len(values) else None


def compute_onboarding_kpis(df: pd.DataFrame) -> dict[str, float | None]:
    status = df["onboarding_status"]
    completed = status.eq("Completed")
    total = len(df)
    return {
        "total_hires": total,
        "completed_count": int(completed.sum()),
        "in_progress_count": int(status.eq("In Progress").sum()),
        "delayed_count": int(status.eq("Delayed").sum()),
        "completion_rate_pct": _pct(int(completed.sum()), total),
        "avg_days_to_complete": _mean(df.loc[completed, "onboarding_days"]),
        "avg_training_pct": _mean(df["training_completion_percent"]),
        "buddy_coverage_pct": _pct(int(df["buddy_assigned"].eq(True).sum()), total),
        "first_week_checkin_pct": _pct(int(df["first_week_checkin"].eq(True).sum()), total),
    }


def compute_department_kpis(features: pd.DataFrame) -> pd.DataFrame:
    """Same columns as pipeline/sql/kpis/by_department.sql."""
    rows = []
    for department, group in features.groupby("Department", observed=True):
        kpis = compute_onboarding_kpis(group)
        rows.append({
            "department": department,
            "hires": kpis["total_hires"],
            "completion_rate_pct": kpis["completion_rate_pct"],
            "delayed_count": kpis["delayed_count"],
            "avg_days_to_complete": kpis["avg_days_to_complete"],
            "avg_training_pct": kpis["avg_training_pct"],
        })
    return pd.DataFrame(rows).sort_values("department").reset_index(drop=True)
