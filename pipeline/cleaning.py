"""Reusable cleaning functions for the onboarding dataset.

Cleaning fixes the *shape* of the data: column names, whitespace, duplicate rows
and impossible values. Turning Yes/No, dates and statuses into real types is a
separate step (pipeline.standardize) so each stage can be tested on its own.
"""
from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, field

import pandas as pd

ONBOARDING_COLUMNS = (
    "employee_id",
    "orientation_completed",
    "training_completion_percent",
    "onboarding_days",
    "onboarding_status",
    "manager_assigned",
    "buddy_assigned",
    "first_week_checkin",
    "onboarding_completion_date",
)

# Values outside these ranges are data-entry errors: they are nulled, never clipped,
# so a typo like 950% cannot masquerade as a fully trained hire.
VALID_RANGES = {
    "training_completion_percent": (0.0, 100.0),
    "onboarding_days": (0, 365),
}


@dataclass
class CleaningReport:
    rows_in: int = 0
    rows_out: int = 0
    blank_strings: int = 0
    invalid_ids: int = 0
    exact_duplicates: int = 0
    duplicate_ids: int = 0
    invalid_values: dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return asdict(self)


def to_snake_case(name: object) -> str:
    """'Training Completion Percent', 'onboardingDays', 'EmployeeID' -> snake_case."""
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", str(name).strip())
    return re.sub(r"[^0-9a-zA-Z]+", "_", text).strip("_").lower()


def snake_case_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = df.rename(columns=to_snake_case)
    clashes = renamed.columns[renamed.columns.duplicated()].tolist()
    if clashes:
        raise ValueError(f"Columns collide after normalising names: {clashes}")
    return renamed


def require_columns(df: pd.DataFrame, required: Iterable[str]) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")


def strip_strings(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Trim whitespace in text columns and turn blank strings into nulls."""
    out = df.copy()
    blanks = 0
    for col in out.select_dtypes(include=["object", "string"]).columns:
        stripped = out[col].map(lambda v: v.strip() if isinstance(v, str) else v)
        is_blank = stripped.map(lambda v: v == "" if isinstance(v, str) else False).astype(bool)
        blanks += int(is_blank.sum())
        out[col] = stripped.mask(is_blank)
    return out, blanks


def null_invalid_numbers(df: pd.DataFrame,
                         ranges: Mapping[str, tuple[float, float]]) -> tuple[pd.DataFrame, dict[str, int]]:
    """Coerce columns to numbers; unparseable or out-of-range values become null."""
    out = df.copy()
    counts: dict[str, int] = {}
    for col, (low, high) in ranges.items():
        values = pd.to_numeric(out[col], errors="coerce")
        invalid = (out[col].notna() & values.isna()) | (values.notna() & ~values.between(low, high))
        counts[col] = int(invalid.sum())
        out[col] = values.mask(invalid)
    return out, counts


def deduplicate_by_key(df: pd.DataFrame, key: str) -> tuple[pd.DataFrame, int, int]:
    """Drop exact duplicates, then keep the most complete row per key (later rows win ties).

    Returns (frame, exact_duplicates_removed, duplicate_keys_removed).
    """
    exact = int(df.duplicated().sum())
    unique_rows = df.drop_duplicates()
    ranked = unique_rows.assign(_filled=unique_rows.notna().sum(axis=1), _order=range(len(unique_rows)))
    kept = (ranked.sort_values(["_filled", "_order"], ascending=False)
                  .drop_duplicates(subset=key, keep="first")
                  .sort_values("_order")
                  .drop(columns=["_filled", "_order"])
                  .reset_index(drop=True))
    return kept, exact, len(unique_rows) - len(kept)


def clean_onboarding(raw: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
    """Run every cleaning step on a raw onboarding frame and report what changed."""
    report = CleaningReport(rows_in=len(raw))
    df = snake_case_columns(raw)
    require_columns(df, ONBOARDING_COLUMNS)
    df, report.blank_strings = strip_strings(df)

    ids = pd.to_numeric(df["employee_id"], errors="coerce")
    valid_id = ids.notna() & (ids > 0) & (ids == ids.round())
    report.invalid_ids = int((~valid_id).sum())
    df = df.loc[valid_id].assign(employee_id=ids[valid_id].astype("int64"))

    df, report.invalid_values = null_invalid_numbers(df, VALID_RANGES)
    df, report.exact_duplicates, report.duplicate_ids = deduplicate_by_key(df, "employee_id")
    report.rows_out = len(df)
    return df, report
