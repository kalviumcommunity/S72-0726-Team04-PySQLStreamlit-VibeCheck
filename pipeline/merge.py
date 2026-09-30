"""Merge onboarding with tool usage and validate the join.

tool_usage is 1:N per employee, so it is aggregated to one row per employee
first; the join itself is then enforced as one-to-one. Only the activity count
columns are zero-filled for hires with no activity - text and date columns stay
null, so a missing value is never silently turned into 0.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd

log = logging.getLogger(__name__)

TOOL_COUNT_COLUMNS = ("tool_sessions", "total_logins", "total_active_minutes", "distinct_tools", "active_days")


@dataclass(frozen=True)
class JoinReport:
    onboarding_rows: int
    matched: int
    onboarding_only: int
    orphan_tool_employee_ids: tuple[int, ...]

    @property
    def match_rate(self) -> float:
        return self.matched / self.onboarding_rows if self.onboarding_rows else 0.0

    def summary(self) -> str:
        return (f"onboarding+tool_usage: {self.matched}/{self.onboarding_rows} matched "
                f"({self.match_rate:.1%}), {self.onboarding_only} without activity, "
                f"{len(self.orphan_tool_employee_ids)} orphan tool-usage employees")


def aggregate_tool_usage(tool_usage: pd.DataFrame) -> pd.DataFrame:
    """One row per employee: sessions, logins, minutes, distinct tools and active days."""
    usage = tool_usage.assign(
        employee_id=pd.to_numeric(tool_usage["employee_id"], errors="coerce").astype("Int64"),
        date=pd.to_datetime(tool_usage["date"], errors="coerce", format="ISO8601"),
        login_count=pd.to_numeric(tool_usage["login_count"], errors="coerce"),
        active_minutes=pd.to_numeric(tool_usage["active_minutes"], errors="coerce"),
    ).dropna(subset=["employee_id"])
    return (usage.groupby("employee_id")
                 .agg(tool_sessions=("usage_id", "count"),
                      total_logins=("login_count", "sum"),
                      total_active_minutes=("active_minutes", "sum"),
                      distinct_tools=("tool_name", "nunique"),
                      active_days=("date", "nunique"),
                      first_tool_activity=("date", "min"),
                      last_tool_activity=("date", "max"))
                 .reset_index())


def merge_onboarding_tool_usage(onboarding: pd.DataFrame,
                                tool_usage: pd.DataFrame) -> tuple[pd.DataFrame, JoinReport]:
    """Left-join per-employee tool activity onto onboarding (one row per hire)."""
    duplicated = onboarding.loc[onboarding["employee_id"].duplicated(), "employee_id"]
    if len(duplicated):
        raise ValueError(f"onboarding has duplicate employee_id values: {sorted(duplicated.unique())[:5]}")

    activity = aggregate_tool_usage(tool_usage)
    left = onboarding.assign(employee_id=onboarding["employee_id"].astype("Int64"))
    merged = left.merge(activity, on="employee_id", how="left", validate="one_to_one", indicator=True)

    orphans = activity.loc[~activity["employee_id"].isin(left["employee_id"]), "employee_id"]
    report = JoinReport(
        onboarding_rows=len(left),
        matched=int((merged["_merge"] == "both").sum()),
        onboarding_only=int((merged["_merge"] == "left_only").sum()),
        orphan_tool_employee_ids=tuple(int(i) for i in orphans),
    )
    merged["has_tool_activity"] = merged["_merge"].eq("both")
    for col in TOOL_COUNT_COLUMNS:
        merged[col] = merged[col].fillna(0).astype("int64")
    merged = merged.drop(columns="_merge")
    merged["employee_id"] = merged["employee_id"].astype("int64")

    if report.orphan_tool_employee_ids:
        log.warning("tool usage for employees without onboarding records: %s",
                    list(report.orphan_tool_employee_ids)[:10])
    log.info(report.summary())
    return merged, report
