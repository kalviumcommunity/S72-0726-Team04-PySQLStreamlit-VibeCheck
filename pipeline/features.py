"""Feature engineering on the merged onboarding + tool-usage table.

    days_to_complete       onboarding_days for Completed hires; null while still onboarding
    onboarding_start_date  completion date minus onboarding days
    training_gap_pct       outstanding training, 100 - training completion
    setup_completeness     share of the four setup milestones done (0-1)
    logins_per_active_day  tool logins per day with any tool activity
    minutes_per_session    active minutes per tool session
    onboarding_speed       fast / typical / slow vs completed hires (Delayed = slow)
    is_new_hire            tenure <= 1 year, or onboarding still open (needs employees)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .config import Settings
from .ingest import load_dataset
from .merge import merge_onboarding_tool_usage
from .standardize import load_standardized_onboarding

SETUP_MILESTONES = ("orientation_completed", "manager_assigned", "buddy_assigned", "first_week_checkin")
EMPLOYEE_COLUMNS = ("Department", "JobRole", "JobLevel", "YearsAtCompany")
NEW_HIRE_MAX_TENURE_YEARS = 1
SPEED_QUANTILES = (0.25, 0.75)
SPEED_LABELS = ("fast", "typical", "slow", "in_progress")
OPEN_STATUSES = ("In Progress", "Delayed")


def speed_thresholds(df: pd.DataFrame) -> tuple[float, float]:
    """(fast_max, slow_min) in days: quartiles of *completed* onboardings."""
    completed = df.loc[df["onboarding_status"].eq("Completed"), "onboarding_days"].dropna().astype("float64")
    if completed.empty:
        raise ValueError("No completed onboardings to calibrate speed buckets against")
    fast_max, slow_min = completed.quantile(SPEED_QUANTILES)
    return float(fast_max), float(slow_min)


def _ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Division that yields NaN instead of inf when the denominator is 0."""
    return numerator.astype("float64") / denominator.astype("float64").where(denominator > 0)


def _mask(condition: pd.Series) -> np.ndarray:
    return condition.to_numpy(dtype=bool, na_value=False)


def engineer_features(merged: pd.DataFrame, employees: pd.DataFrame | None = None,
                      thresholds: tuple[float, float] | None = None) -> pd.DataFrame:
    out = merged.copy()
    status = out["onboarding_status"]
    days = out["onboarding_days"]

    out["days_to_complete"] = days.where(status.eq("Completed"))
    out["onboarding_start_date"] = (out["onboarding_completion_date"]
                                    - pd.to_timedelta(days.astype("float64"), unit="D"))
    out["training_gap_pct"] = (100 - out["training_completion_percent"]).round(1)
    out["setup_completeness"] = out[list(SETUP_MILESTONES)].astype("float64").mean(axis=1).round(3)
    out["logins_per_active_day"] = _ratio(out["total_logins"], out["active_days"]).round(2)
    out["minutes_per_session"] = _ratio(out["total_active_minutes"], out["tool_sessions"]).round(1)

    fast_max, slow_min = thresholds or speed_thresholds(out)
    speed = np.select(
        [_mask(status.eq("Delayed")), _mask(status.eq("In Progress")),
         _mask(days <= fast_max), _mask(days >= slow_min)],
        ["slow", "in_progress", "fast", "slow"],
        default="typical",
    )
    out["onboarding_speed"] = pd.Categorical(speed, categories=SPEED_LABELS)

    if employees is not None:
        out = out.merge(employees[["employee_id", *EMPLOYEE_COLUMNS]], on="employee_id",
                        how="left", validate="one_to_one")
        tenure = pd.to_numeric(out["YearsAtCompany"], errors="coerce")
        out["is_new_hire"] = _mask(tenure <= NEW_HIRE_MAX_TENURE_YEARS) | _mask(out["onboarding_status"].isin(OPEN_STATUSES))
    return out


def build_feature_table(settings: Settings | None = None) -> pd.DataFrame:
    """Load, clean, merge and engineer: the one table every analysis starts from."""
    onboarding = load_standardized_onboarding(settings)
    tool_usage, _ = load_dataset("tool_usage", settings=settings)
    employees, _ = load_dataset("employees", settings=settings)
    merged, _ = merge_onboarding_tool_usage(onboarding, tool_usage)
    return engineer_features(merged, employees)
