"""Behavioural analysis of new hires: how fast and slow onboarders differ.

Compares new hires in the ``fast`` and ``slow`` onboarding_speed buckets on
training, setup and tool engagement. Cohen's d is reported next to the raw
means so a large-looking gap on a small group is not over-read.

    python -m pipeline.analysis.behaviour
"""
from __future__ import annotations

import math
from collections.abc import Sequence

import pandas as pd

from . import markdown_table

BEHAVIOUR_METRICS = (
    "training_completion_percent",
    "setup_completeness",
    "total_logins",
    "total_active_minutes",
    "distinct_tools",
    "active_days",
    "logins_per_active_day",
    "minutes_per_session",
)


def cohens_d(fast: pd.Series, slow: pd.Series) -> float:
    """Standardised mean difference, slow minus fast (positive = slow hires score higher)."""
    a, b = fast.dropna().astype("float64"), slow.dropna().astype("float64")
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    pooled = math.sqrt(((len(a) - 1) * a.var() + (len(b) - 1) * b.var()) / (len(a) + len(b) - 2))
    return float((b.mean() - a.mean()) / pooled) if pooled else float("nan")


def effect_label(d: float) -> str:
    if math.isnan(d):
        return "n/a"
    size = abs(d)
    return "large" if size >= 0.8 else "medium" if size >= 0.5 else "small" if size >= 0.2 else "negligible"


def _speed_groups(features: pd.DataFrame, new_hires_only: bool) -> tuple[pd.DataFrame, pd.DataFrame]:
    if new_hires_only:
        if "is_new_hire" not in features.columns:
            raise KeyError("is_new_hire missing: build features with the employees table joined")
        features = features[features["is_new_hire"]]
    speed = features["onboarding_speed"]
    return features[speed.eq("fast")], features[speed.eq("slow")]


def compare_fast_vs_slow(features: pd.DataFrame, metrics: Sequence[str] = BEHAVIOUR_METRICS,
                         new_hires_only: bool = True, min_group_size: int = 10) -> pd.DataFrame:
    fast, slow = _speed_groups(features, new_hires_only)
    rows = []
    for metric in metrics:
        fast_mean, slow_mean = fast[metric].mean(), slow[metric].mean()
        d = cohens_d(fast[metric], slow[metric])
        rows.append({
            "metric": metric,
            "fast_mean": fast_mean,
            "slow_mean": slow_mean,
            "difference": slow_mean - fast_mean,
            "pct_difference": (slow_mean - fast_mean) / fast_mean * 100 if fast_mean else float("nan"),
            "cohens_d": d,
            "effect": effect_label(d),
            "fast_n": len(fast),
            "slow_n": len(slow),
            "reliable": min(len(fast), len(slow)) >= min_group_size,
        })
    table = pd.DataFrame(rows)
    order = table["cohens_d"].abs().sort_values(ascending=False, na_position="last").index
    return table.loc[order].round(3).reset_index(drop=True)


def tool_minutes_by_speed(features: pd.DataFrame, tool_usage: pd.DataFrame,
                          new_hires_only: bool = True) -> pd.DataFrame:
    """Average active minutes per hire on each tool, fast vs slow (non-users count as 0)."""
    groups = dict(zip(("fast", "slow"), _speed_groups(features, new_hires_only)))
    columns = {}
    for label, group in groups.items():
        usage = tool_usage[tool_usage["employee_id"].isin(group["employee_id"])]
        minutes = pd.to_numeric(usage["active_minutes"], errors="coerce").groupby(usage["tool_name"]).sum()
        columns[label] = minutes / max(len(group), 1)
    table = pd.DataFrame(columns).fillna(0.0).round(1)
    table["gap"] = table["slow"] - table["fast"]
    return table.sort_values("gap").rename_axis("tool_name").reset_index()


def behaviour_findings(comparison: pd.DataFrame, top: int = 3) -> list[str]:
    findings = []
    for row in comparison.head(top).itertuples(index=False):
        direction = "lower" if row.difference < 0 else "higher"
        findings.append(
            f"Slow onboarders show {direction} {row.metric.replace('_', ' ')} "
            f"({row.slow_mean:.3g} vs {row.fast_mean:.3g}; {row.effect} effect, d={row.cohens_d:+.2f})"
            + ("" if row.reliable else " - small groups, treat as indicative")
        )
    return findings


def main(argv: list[str] | None = None) -> int:
    from ..features import build_feature_table
    from ..ingest import load_dataset

    features = build_feature_table()
    comparison = compare_fast_vs_slow(features)
    tools = tool_minutes_by_speed(features, load_dataset("tool_usage")[0])
    print("# Fast vs slow onboarding - new hires\n")
    print("\n".join(f"- {f}" for f in behaviour_findings(comparison)), end="\n\n")
    print(markdown_table(comparison), end="\n\n")
    print("## Average active minutes per hire, by tool\n")
    print(markdown_table(tools))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
