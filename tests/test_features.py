import pandas as pd
import pytest

from pipeline.features import build_feature_table, engineer_features, speed_thresholds

STATUSES = ["Completed", "Completed", "Completed", "Delayed", "In Progress"]


@pytest.fixture
def merged():
    return pd.DataFrame({
        "employee_id": [1, 2, 3, 4, 5],
        "onboarding_status": pd.Categorical(STATUSES, categories=["Completed", "In Progress", "Delayed"]),
        "onboarding_days": pd.array([8, 12, 16, 30, 20], dtype="Int64"),
        "onboarding_completion_date": pd.to_datetime(["2026-07-20", "2026-07-20", "2026-07-20", None, None]),
        "training_completion_percent": [95.0, 90.0, 85.0, 30.0, 60.0],
        "orientation_completed": pd.array([True, True, True, False, True], dtype="boolean"),
        "manager_assigned": pd.array([True, True, True, True, True], dtype="boolean"),
        "buddy_assigned": pd.array([True, True, None, False, True], dtype="boolean"),
        "first_week_checkin": pd.array([True, True, False, False, True], dtype="boolean"),
        "tool_sessions": [4, 2, 0, 1, 3],
        "total_logins": [12, 4, 0, 1, 9],
        "total_active_minutes": [240, 60, 0, 10, 90],
        "active_days": [3, 2, 0, 1, 3],
    })


def test_speed_buckets_use_completed_hires_only(merged):
    features = engineer_features(merged, thresholds=(10, 15))
    assert features["onboarding_speed"].tolist() == ["fast", "typical", "slow", "slow", "in_progress"]
    assert speed_thresholds(merged) == (10.0, 14.0)  # quartiles of 8/12/16, Delayed excluded


def test_time_features(merged):
    features = engineer_features(merged, thresholds=(10, 15))
    assert features["days_to_complete"].tolist()[:3] == [8, 12, 16]
    assert features["days_to_complete"].iloc[3:].isna().all()
    assert features.loc[0, "onboarding_start_date"] == pd.Timestamp("2026-07-12")
    assert features.loc[3, "training_gap_pct"] == 70.0


def test_ratios_and_setup_completeness(merged):
    features = engineer_features(merged, thresholds=(10, 15))
    assert features.loc[0, "logins_per_active_day"] == 4.0
    assert features.loc[0, "minutes_per_session"] == 60.0
    assert pd.isna(features.loc[2, "logins_per_active_day"])     # no activity -> NaN, never inf
    assert features.loc[2, "setup_completeness"] == 0.667         # unknown buddy flag is skipped
    assert features.loc[3, "setup_completeness"] == 0.25


def test_new_hire_flag_combines_tenure_and_open_onboarding(merged):
    employees = pd.DataFrame({
        "employee_id": [1, 2, 3, 4, 5],
        "Department": ["Sales"] * 5, "JobRole": ["Rep"] * 5, "JobLevel": [1] * 5,
        "YearsAtCompany": [0, 5, 1, 8, 3],
    })
    features = engineer_features(merged, employees, thresholds=(10, 15))
    assert features["is_new_hire"].tolist() == [True, False, True, True, True]


def test_feature_table_on_real_data():
    table = build_feature_table()
    assert len(table) == table["employee_id"].nunique() == 1470
    assert table["is_new_hire"].sum() == 215
    counts = table["onboarding_speed"].value_counts()
    assert counts["in_progress"] == 23 and counts["slow"] >= 14
    assert table["setup_completeness"].between(0, 1).all()
    assert not table["minutes_per_session"].isin([float("inf")]).any()
