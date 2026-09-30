"""Outlier detection for onboarding completion times.

Two methods, both robust to the long right tail that delayed onboardings create:

* ``iqr`` - Tukey fences: outside [Q1 - k*IQR, Q3 + k*IQR]
* ``mad`` - modified z-score (Iglewicz & Hoaglin): |0.6745 * (x - median) / MAD| > threshold

Bounds can be computed per group (e.g. department). Groups too small to have a
stable distribution fall back to company-wide bounds rather than flagging noise.
"""
from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

METHODS = ("iqr", "mad")
_MEAN_AD_SCALE = 1.253314  # MeanAD -> sigma for normal data; used when MAD collapses to 0


def iqr_bounds(values: pd.Series, k: float = 1.5) -> tuple[float, float]:
    q1, q3 = values.quantile([0.25, 0.75])
    spread = k * (q3 - q1)
    return float(q1 - spread), float(q3 + spread)


def mad_bounds(values: pd.Series, threshold: float = 3.5) -> tuple[float, float]:
    median = values.median()
    deviations = (values - median).abs()
    mad = deviations.median()
    if mad > 0:
        spread = threshold * mad / 0.6745
    else:  # more than half the values are identical; fall back to the mean absolute deviation
        spread = threshold * _MEAN_AD_SCALE * deviations.mean()
    return float(median - spread), float(median + spread)


def _bounds(values: pd.Series, method: str, k: float, threshold: float) -> tuple[float, float]:
    return iqr_bounds(values, k) if method == "iqr" else mad_bounds(values, threshold)


def detect_completion_outliers(
    df: pd.DataFrame,
    column: str = "onboarding_days",
    method: str = "iqr",
    group_by: str | None = None,
    k: float = 1.5,
    threshold: float = 3.5,
    min_group_size: int = 20,
    context_columns: Sequence[str] = ("onboarding_status",),
) -> pd.DataFrame:
    """Return one row per employee with the bounds applied and an outlier flag."""
    if method not in METHODS:
        raise ValueError(f"method must be one of {METHODS}, got {method!r}")
    data = df.loc[df[column].notna()]
    values = data[column].astype("float64")
    overall_low, overall_high = _bounds(values, method, k, threshold)
    lower = pd.Series(overall_low, index=data.index)
    upper = pd.Series(overall_high, index=data.index)
    scope = pd.Series("all", index=data.index, dtype="object")

    if group_by:
        for group, index in data.groupby(group_by, observed=True).groups.items():
            if len(index) >= min_group_size:
                lower.loc[index], upper.loc[index] = _bounds(values.loc[index], method, k, threshold)
                scope.loc[index] = str(group)

    direction = pd.Series(None, index=data.index, dtype="object")
    direction = direction.mask(values > upper, "high").mask(values < lower, "low")
    context = [c for c in (group_by, *context_columns) if c and c in data.columns]
    result = data[["employee_id", *context]].assign(
        **{column: values},
        lower_bound=lower.round(2),
        upper_bound=upper.round(2),
        bounds_scope=scope,
        direction=direction,
        is_outlier=direction.notna(),
        method=method,
    )
    return result.reset_index(drop=True)


def summarize_outliers(result: pd.DataFrame) -> pd.DataFrame:
    """Outlier counts and fences per bounds scope (company-wide or group)."""
    return (result.groupby("bounds_scope")
                  .agg(employees=("employee_id", "size"),
                       outliers_high=("direction", lambda d: int((d == "high").sum())),
                       outliers_low=("direction", lambda d: int((d == "low").sum())),
                       lower_bound=("lower_bound", "first"),
                       upper_bound=("upper_bound", "first"))
                  .reset_index())
