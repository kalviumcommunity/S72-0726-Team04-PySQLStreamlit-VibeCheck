import pandas as pd
import pytest

from pipeline.cleaning import (
    clean_onboarding,
    deduplicate_by_key,
    snake_case_columns,
    strip_strings,
    to_snake_case,
)
from pipeline.ingest import load_onboarding


def messy_onboarding() -> pd.DataFrame:
    return pd.DataFrame({
        "Employee ID": [1, 1, 2, 2, "abc", -4, 5, 6],
        "Orientation Completed": [" Yes", " Yes", "No ", "No", "Yes", "Yes", "Yes", ""],
        "Training Completion Percent": [80.0, 80.0, 55.5, None, 70.0, 60.0, 120.0, "n/a"],
        "onboardingDays": [12, 12, 20, 20, 9, 9, -3, 14],
        "Onboarding Status": ["Completed"] * 8,
        "Manager Assigned": ["Yes"] * 8,
        "Buddy Assigned": ["Yes"] * 8,
        "First Week Checkin": ["Yes"] * 8,
        "Onboarding Completion Date": ["2026-07-01"] * 8,
    })


@pytest.mark.parametrize("raw, expected", [
    ("Training Completion Percent", "training_completion_percent"),
    ("onboardingDays", "onboarding_days"),
    ("EmployeeID", "employee_id"),
    ("  JobRole ", "job_role"),
    ("employee_id", "employee_id"),
])
def test_to_snake_case(raw, expected):
    assert to_snake_case(raw) == expected


def test_colliding_column_names_are_rejected():
    with pytest.raises(ValueError, match="collide"):
        snake_case_columns(pd.DataFrame(columns=["EmployeeID", "employee_id"]))


def test_strip_strings_counts_blanks_and_leaves_numbers_alone():
    frame = pd.DataFrame({"a": [" x ", "", None], "b": [1, 2, 3]})
    cleaned, blanks = strip_strings(frame)
    assert blanks == 1
    assert cleaned["a"].iloc[0] == "x" and pd.isna(cleaned["a"].iloc[1])
    assert cleaned["b"].tolist() == [1, 2, 3]


def test_deduplicate_keeps_most_complete_row():
    frame = pd.DataFrame({"id": [7, 7, 7], "x": [1.0, None, 1.0], "y": ["a", "b", "a"]})
    kept, exact, dup_keys = deduplicate_by_key(frame, "id")
    assert (exact, dup_keys, len(kept)) == (1, 1, 1)
    assert kept.iloc[0].to_dict() == {"id": 7, "x": 1.0, "y": "a"}


def test_clean_onboarding_repairs_messy_input():
    cleaned, report = clean_onboarding(messy_onboarding())
    assert cleaned["employee_id"].tolist() == [1, 2, 5, 6]
    assert report.invalid_ids == 2                      # "abc" and -4
    assert (report.exact_duplicates, report.duplicate_ids) == (1, 1)
    assert report.invalid_values == {"training_completion_percent": 2, "onboarding_days": 1}
    assert report.blank_strings == 1
    row2 = cleaned.set_index("employee_id").loc[2]
    assert row2["orientation_completed"] == "No"        # whitespace trimmed
    assert row2["training_completion_percent"] == 55.5  # complete duplicate kept
    assert pd.isna(cleaned.set_index("employee_id").loc[5, "onboarding_days"])


def test_missing_columns_are_named():
    with pytest.raises(ValueError, match="onboarding_status"):
        clean_onboarding(messy_onboarding().drop(columns=["Onboarding Status"]))


def test_committed_dataset_is_already_clean(settings):
    cleaned, report = clean_onboarding(load_onboarding(settings=settings))
    assert report.rows_in == report.rows_out == len(cleaned) == 1470
    assert report.exact_duplicates == report.duplicate_ids == report.invalid_ids == 0
    assert sum(report.invalid_values.values()) == 0
