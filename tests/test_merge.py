import pandas as pd
import pytest

from pipeline.ingest import load_dataset
from pipeline.merge import TOOL_COUNT_COLUMNS, aggregate_tool_usage, merge_onboarding_tool_usage
from pipeline.standardize import load_standardized_onboarding

USAGE = pd.DataFrame({
    "usage_id": ["U1", "U2", "U3", "U4"],
    "employee_id": [1, 1, 1, 9],
    "date": ["2026-07-01", "2026-07-01", "2026-07-03", "2026-07-02"],
    "tool_name": ["Slack", "Jira", "Slack", "GitHub"],
    "login_count": [3, "4", 1, 2],
    "active_minutes": [60, 30, 15, 5],
})
ONBOARDING = pd.DataFrame({"employee_id": [1, 2], "onboarding_status": ["Completed", "Delayed"]})


def test_aggregation_is_one_row_per_employee():
    activity = aggregate_tool_usage(USAGE).set_index("employee_id")
    assert activity.loc[1, ["tool_sessions", "total_logins", "total_active_minutes",
                            "distinct_tools", "active_days"]].tolist() == [3, 8, 105, 2, 2]
    assert activity.loc[1, "first_tool_activity"] == pd.Timestamp("2026-07-01")


def test_merge_keeps_every_hire_and_reports_the_join():
    merged, report = merge_onboarding_tool_usage(ONBOARDING, USAGE)
    assert len(merged) == 2
    assert (report.matched, report.onboarding_only, report.orphan_tool_employee_ids) == (1, 1, (9,))
    assert report.match_rate == 0.5
    no_activity = merged.set_index("employee_id").loc[2]
    assert not no_activity["has_tool_activity"]
    assert all(no_activity[c] == 0 for c in TOOL_COUNT_COLUMNS)
    assert pd.isna(no_activity["first_tool_activity"])  # dates are not zero-filled


def test_duplicate_onboarding_rows_are_refused():
    with pytest.raises(ValueError, match="duplicate employee_id"):
        merge_onboarding_tool_usage(pd.concat([ONBOARDING, ONBOARDING.head(1)]), USAGE)


def test_real_join_matches_every_hire():
    usage, _ = load_dataset("tool_usage")
    merged, report = merge_onboarding_tool_usage(load_standardized_onboarding(), usage)
    assert len(merged) == report.onboarding_rows == report.matched == 1470
    assert report.orphan_tool_employee_ids == ()
    assert merged["tool_sessions"].sum() == len(usage)
    assert merged["total_active_minutes"].sum() == usage["active_minutes"].sum()
