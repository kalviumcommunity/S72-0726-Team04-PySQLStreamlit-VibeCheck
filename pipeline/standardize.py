"""Standardise onboarding data types: Yes/No flags, dates and status categories.

Runs after pipeline.cleaning. Unrecognised tokens become nulls *and are counted*,
so a new spelling from a source system is reported instead of silently read as False.
"""
from __future__ import annotations

import logging
import re
from dataclasses import asdict, dataclass, field

import numpy as np
import pandas as pd

from .cleaning import clean_onboarding
from .config import Settings
from .ingest import load_onboarding

log = logging.getLogger(__name__)

BOOLEAN_COLUMNS = ("orientation_completed", "manager_assigned", "buddy_assigned", "first_week_checkin")
DATE_COLUMNS = ("onboarding_completion_date",)

TRUE_TOKENS = frozenset({"yes", "y", "true", "t", "1"})
FALSE_TOKENS = frozenset({"no", "n", "false", "f", "0"})

# Ordered by severity, so sorting or max() puts the most worrying status last.
STATUS_ORDER = ("Completed", "In Progress", "Delayed")
_STATUS_ALIASES = {
    "completed": "Completed", "complete": "Completed", "done": "Completed",
    "in progress": "In Progress", "inprogress": "In Progress", "ongoing": "In Progress",
    "delayed": "Delayed", "overdue": "Delayed", "late": "Delayed",
}


@dataclass
class StandardizationReport:
    unknown_booleans: dict[str, int] = field(default_factory=dict)
    unparseable_dates: dict[str, int] = field(default_factory=dict)
    unknown_statuses: int = 0
    completed_without_date: int = 0

    @property
    def issue_count(self) -> int:
        return (sum(self.unknown_booleans.values()) + sum(self.unparseable_dates.values())
                + self.unknown_statuses + self.completed_without_date)

    def as_dict(self) -> dict:
        return asdict(self)


def _token(value: object) -> str | None:
    if value is None or (not isinstance(value, str) and pd.isna(value)):
        return None
    if isinstance(value, (bool, np.bool_)):
        return "true" if value else "false"
    if isinstance(value, (int, float, np.number)) and float(value) in (0.0, 1.0):
        return str(int(value))
    return str(value).strip().lower()


def to_boolean(series: pd.Series) -> tuple[pd.Series, int]:
    """Map Yes/No-style tokens to a nullable boolean. Returns (series, unknown_count)."""
    tokens = series.map(_token)
    mapped = tokens.map(lambda t: True if t in TRUE_TOKENS else False if t in FALSE_TOKENS else None)
    unknown = int((tokens.notna() & mapped.isna()).sum())
    return mapped.astype("boolean"), unknown


def to_date(series: pd.Series) -> tuple[pd.Series, int]:
    """Parse ISO-8601 dates only; ambiguous formats like 01/07/2026 are rejected, not guessed."""
    parsed = pd.to_datetime(series, errors="coerce", format="ISO8601")
    unparseable = int((series.notna() & parsed.isna()).sum())
    return parsed.dt.normalize(), unparseable


def to_status(series: pd.Series) -> tuple[pd.Series, int]:
    """Canonicalise status spellings into an ordered categorical."""
    keys = series.map(lambda v: re.sub(r"[\s_\-]+", " ", t) if (t := _token(v)) else None)
    canonical = keys.map(lambda k: _STATUS_ALIASES.get(k) if k else None)
    unknown = int((keys.notna() & canonical.isna()).sum())
    status = pd.Categorical(canonical, categories=STATUS_ORDER, ordered=True)
    return pd.Series(status, index=series.index, name=series.name), unknown


def standardize_onboarding(clean: pd.DataFrame) -> tuple[pd.DataFrame, StandardizationReport]:
    """Convert a cleaned onboarding frame to analysis-ready dtypes."""
    out = clean.copy()
    report = StandardizationReport()
    for col in BOOLEAN_COLUMNS:
        out[col], report.unknown_booleans[col] = to_boolean(out[col])
    for col in DATE_COLUMNS:
        out[col], report.unparseable_dates[col] = to_date(out[col])
    out["onboarding_status"], report.unknown_statuses = to_status(out["onboarding_status"])
    out["employee_id"] = out["employee_id"].astype("int64")
    out["onboarding_days"] = pd.to_numeric(out["onboarding_days"]).round().astype("Int64")
    out["training_completion_percent"] = pd.to_numeric(out["training_completion_percent"]).astype("float64")
    report.completed_without_date = int(
        (out["onboarding_status"].eq("Completed") & out["onboarding_completion_date"].isna()).sum()
    )
    return out, report


def prepare_onboarding(raw: pd.DataFrame) -> pd.DataFrame:
    """Clean + standardise in one call; data-quality findings are logged, not raised."""
    cleaned, cleaning = clean_onboarding(raw)
    standard, report = standardize_onboarding(cleaned)
    if report.issue_count:
        log.warning("onboarding standardisation issues: %s", report.as_dict())
    log.info("onboarding prepared: %d -> %d rows", cleaning.rows_in, cleaning.rows_out)
    return standard


def load_standardized_onboarding(settings: Settings | None = None) -> pd.DataFrame:
    return prepare_onboarding(load_onboarding(settings=settings))
