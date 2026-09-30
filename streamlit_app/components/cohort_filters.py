"""Cohort filters for the onboarding dashboard.

``CohortFilter`` is a plain value object and ``apply_cohort_filter`` a pure
function, so filtering is tested without Streamlit; the sidebar only collects choices.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from pipeline.standardize import STATUS_ORDER

TENURE_BANDS: dict[str, tuple[int, int | None]] = {
    "0-1 yrs": (0, 1),
    "2-5 yrs": (2, 5),
    "6-10 yrs": (6, 10),
    "10+ yrs": (11, None),
}
BUDDY_OPTIONS = ("Any", "With buddy", "Without buddy")


@dataclass(frozen=True)
class CohortFilter:
    departments: tuple[str, ...] = ()
    statuses: tuple[str, ...] = ()
    tenure_bands: tuple[str, ...] = ()
    buddy: str = "Any"
    new_hires_only: bool = False

    def __post_init__(self) -> None:
        unknown = [band for band in self.tenure_bands if band not in TENURE_BANDS]
        if unknown or self.buddy not in BUDDY_OPTIONS:
            raise ValueError(f"Invalid cohort filter: tenure bands {unknown}, buddy {self.buddy!r}")

    @property
    def is_active(self) -> bool:
        return self != CohortFilter()

    def describe(self) -> str:
        parts = ["New hires"] if self.new_hires_only else []
        parts += [", ".join(values) for values in (self.departments, self.statuses) if values]
        if self.tenure_bands:
            parts.append("Tenure " + ", ".join(self.tenure_bands))
        if self.buddy != "Any":
            parts.append(self.buddy.lower())
        return " · ".join(parts) or "All hires"


def _as_mask(values: pd.Series) -> np.ndarray:
    return values.to_numpy(dtype=bool, na_value=False)


def _tenure_mask(tenure: pd.Series, bands: tuple[str, ...]) -> np.ndarray:
    mask = np.zeros(len(tenure), dtype=bool)
    for band in bands:
        low, high = TENURE_BANDS[band]
        in_band = tenure >= low if high is None else tenure.between(low, high)
        mask |= _as_mask(in_band)
    return mask


def apply_cohort_filter(df: pd.DataFrame, cohort: CohortFilter) -> pd.DataFrame:
    mask = np.ones(len(df), dtype=bool)
    if cohort.departments:
        mask &= _as_mask(df["Department"].isin(cohort.departments))
    if cohort.statuses:
        mask &= _as_mask(df["onboarding_status"].isin(cohort.statuses))
    if cohort.tenure_bands:
        mask &= _tenure_mask(pd.to_numeric(df["YearsAtCompany"], errors="coerce"), cohort.tenure_bands)
    if cohort.buddy != "Any":
        mask &= _as_mask(df["buddy_assigned"].eq(cohort.buddy == "With buddy"))
    if cohort.new_hires_only:
        mask &= _as_mask(df["is_new_hire"])
    return df[mask]


def render_cohort_sidebar(df: pd.DataFrame, key: str = "cohort") -> CohortFilter:
    import streamlit as st

    present = set(df["onboarding_status"].dropna())
    with st.sidebar:
        st.header("Cohort")
        new_hires = st.toggle("New hires only", key=f"{key}_new_hires",
                              help="Tenure of at most one year, or onboarding still open.")
        departments = st.multiselect("Department", sorted(df["Department"].dropna().unique()), key=f"{key}_departments")
        statuses = st.multiselect("Onboarding status", [s for s in STATUS_ORDER if s in present], key=f"{key}_statuses")
        tenure = st.multiselect("Tenure", list(TENURE_BANDS), key=f"{key}_tenure")
        buddy = st.radio("Onboarding buddy", BUDDY_OPTIONS, horizontal=True, key=f"{key}_buddy")
    return CohortFilter(tuple(departments), tuple(statuses), tuple(tenure), buddy, new_hires)
