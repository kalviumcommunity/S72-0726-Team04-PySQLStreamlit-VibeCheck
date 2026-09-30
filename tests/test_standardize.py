import pandas as pd
import pytest

from pipeline.standardize import (
    STATUS_ORDER,
    load_standardized_onboarding,
    standardize_onboarding,
    to_boolean,
    to_date,
    to_status,
)


def test_boolean_tokens_and_unknowns():
    values = pd.Series(["Yes", " no ", "Y", "FALSE", 1, 0.0, True, None, "maybe"])
    parsed, unknown = to_boolean(values)
    assert str(parsed.dtype) == "boolean"
    assert parsed.iloc[:7].tolist() == [True, False, True, False, True, False, True]
    assert pd.isna(parsed.iloc[7]) and pd.isna(parsed.iloc[8])
    assert unknown == 1  # "maybe" is reported; None is simply missing


def test_status_aliases_are_canonicalised_and_ordered():
    parsed, unknown = to_status(pd.Series(["completed", "IN-PROGRESS", "in_progress", "Overdue", "Paused", None]))
    assert parsed.tolist()[:4] == ["Completed", "In Progress", "In Progress", "Delayed"]
    assert unknown == 1
    assert list(parsed.cat.categories) == list(STATUS_ORDER)
    assert parsed.max() == "Delayed"


def test_only_iso_dates_are_accepted():
    parsed, bad = to_date(pd.Series(["2026-07-01", "2026-07-01T09:30:00", "01/07/2026", "2026-13-40", None]))
    assert parsed.iloc[0] == parsed.iloc[1] == pd.Timestamp("2026-07-01")
    assert parsed.iloc[2:].isna().all()
    assert bad == 2


def test_report_flags_completed_rows_without_a_date():
    frame = pd.DataFrame({
        "employee_id": [1, 2],
        "orientation_completed": ["Yes", "No"],
        "training_completion_percent": [90.0, 40.0],
        "onboarding_days": [10.0, 30.0],
        "onboarding_status": ["Completed", "Delayed"],
        "manager_assigned": ["Yes", "Yes"],
        "buddy_assigned": ["Yes", "No"],
        "first_week_checkin": ["Yes", "No"],
        "onboarding_completion_date": [None, None],
    })
    _, report = standardize_onboarding(frame)
    assert report.completed_without_date == 1
    assert report.issue_count == 1


@pytest.fixture(scope="module")
def onboarding():
    return load_standardized_onboarding()


def test_real_dataset_gets_analysis_ready_dtypes(onboarding):
    assert all(str(onboarding[c].dtype) == "boolean" for c in
               ("orientation_completed", "manager_assigned", "buddy_assigned", "first_week_checkin"))
    assert pd.api.types.is_datetime64_any_dtype(onboarding["onboarding_completion_date"])
    assert isinstance(onboarding["onboarding_status"].dtype, pd.CategoricalDtype)
    assert str(onboarding["onboarding_days"].dtype) == "Int64"


def test_real_dataset_has_no_standardisation_issues(onboarding):
    counts = onboarding["onboarding_status"].value_counts()
    assert (counts["Completed"], counts["In Progress"], counts["Delayed"]) == (1433, 23, 14)
    assert int((~onboarding["buddy_assigned"]).sum()) == 19
    in_flight = onboarding["onboarding_status"].isin(["In Progress", "Delayed"])
    assert onboarding.loc[in_flight, "onboarding_completion_date"].isna().all()
