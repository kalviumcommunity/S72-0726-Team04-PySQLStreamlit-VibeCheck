"""Root-cause investigation for delayed onboarding.

For every candidate factor, hires *with* the factor are compared to hires without it:

    lift             delay rate (with factor) / delay rate (without)
    risk_difference  delay rate (with) - delay rate (without), in percentage points
    coverage         share of all delayed hires that have the factor

This measures association, not causation - low training, for example, is partly a
*symptom* of being delayed. Factors seen on fewer than ``min_support`` hires are
kept in the table but marked unreliable.

    python -m pipeline.analysis.root_cause
"""
from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import markdown_table


@dataclass(frozen=True)
class Factor:
    name: str
    description: str
    predicate: Callable[[pd.DataFrame], pd.Series]
    symptom: bool = False  # likely a consequence of delay; ranked after genuine candidates


CANDIDATE_FACTORS: tuple[Factor, ...] = (
    Factor("missed_first_week_checkin", "No manager check-in in week one",
           lambda d: d["first_week_checkin"].eq(False)),
    Factor("orientation_skipped", "Orientation not completed", lambda d: d["orientation_completed"].eq(False)),
    Factor("no_buddy", "No onboarding buddy assigned", lambda d: d["buddy_assigned"].eq(False)),
    Factor("no_manager", "No reporting manager assigned", lambda d: d["manager_assigned"].eq(False)),
    Factor("low_tool_engagement", "Bottom quartile of active tool minutes",
           lambda d: d["total_active_minutes"] <= d["total_active_minutes"].quantile(0.25)),
    Factor("narrow_tool_adoption", "Two or fewer distinct tools used", lambda d: d["distinct_tools"] <= 2),
    Factor("entry_level_role", "Job level 1", lambda d: d["JobLevel"].eq(1)),
    Factor("low_training", "Training below 60%",
           lambda d: d["training_completion_percent"] < 60, symptom=True),
)


def _mask(values: pd.Series) -> np.ndarray:
    return pd.Series(values).to_numpy(dtype=bool, na_value=False)


def _population(features: pd.DataFrame, new_hires_only: bool) -> tuple[pd.DataFrame, np.ndarray]:
    pool = features[features["is_new_hire"]] if new_hires_only else features
    return pool, _mask(pool["onboarding_status"].eq("Delayed"))


def rank_root_causes(features: pd.DataFrame, factors: Sequence[Factor] = CANDIDATE_FACTORS,
                     new_hires_only: bool = True, min_support: int = 5) -> pd.DataFrame:
    pool, delayed = _population(features, new_hires_only)
    total_delayed = int(delayed.sum())
    rows = []
    for factor in factors:
        exposed = _mask(factor.predicate(pool))
        n_with, n_without = int(exposed.sum()), int((~exposed).sum())
        delayed_with, delayed_without = int((exposed & delayed).sum()), int((~exposed & delayed).sum())
        rate_with = delayed_with / n_with if n_with else np.nan
        rate_without = delayed_without / n_without if n_without else np.nan
        if rate_without > 0:
            lift = rate_with / rate_without
        else:
            lift = np.inf if rate_with > 0 else np.nan
        rows.append({
            "factor": factor.name,
            "description": factor.description,
            "hires_with_factor": n_with,
            "delayed_with_factor": delayed_with,
            "delay_rate_with_pct": rate_with * 100,
            "delay_rate_without_pct": rate_without * 100,
            "lift": lift,
            "risk_difference_pts": (rate_with - rate_without) * 100,
            "coverage_pct": delayed_with / total_delayed * 100 if total_delayed else np.nan,
            "reliable": n_with >= min_support,
            "symptom": factor.symptom,
        })
    table = pd.DataFrame(rows).sort_values(["reliable", "symptom", "lift"], ascending=[False, True, False],
                                           na_position="last")
    return table.round(2).reset_index(drop=True)


def delay_rate_by(features: pd.DataFrame, column: str, new_hires_only: bool = True) -> pd.DataFrame:
    pool, delayed = _population(features, new_hires_only)
    grouped = pd.DataFrame({column: pool[column].to_numpy(), "delayed": delayed}).groupby(column, observed=True)
    table = grouped["delayed"].agg(hires="size", delayed="sum").reset_index()
    table["delay_rate_pct"] = (table["delayed"] / table["hires"] * 100).round(2)
    return table.sort_values("delay_rate_pct", ascending=False).reset_index(drop=True)


def root_cause_findings(table: pd.DataFrame, min_lift: float = 1.5) -> list[str]:
    strong = table[table["reliable"] & (table["lift"] >= min_lift)]
    findings = []
    for row in strong.itertuples(index=False):
        lift = "no delays without it" if np.isinf(row.lift) else f"{row.lift:.1f}x"
        findings.append(
            f"{row.description}: {row.delay_rate_with_pct:.0f}% delayed vs {row.delay_rate_without_pct:.0f}% "
            f"without ({lift}), covering {row.coverage_pct:.0f}% of delayed hires"
            + (" - likely a symptom, not a cause" if row.symptom else "")
        )
    return findings or [f"No reliable factor raises the delay rate by {min_lift}x or more."]


def main(argv: list[str] | None = None) -> int:
    from ..features import build_feature_table

    features = build_feature_table()
    table = rank_root_causes(features)
    print("# Why do new-hire onboardings get delayed?\n")
    print("\n".join(f"- {f}" for f in root_cause_findings(table)), end="\n\n")
    print(markdown_table(table.drop(columns="description")), end="\n\n")
    for column in ("Department", "JobLevel"):
        print(f"## Delay rate by {column}\n\n{markdown_table(delay_rate_by(features, column))}\n")
    print("_Association, not causation: validate the top factors with the onboarding team._")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
