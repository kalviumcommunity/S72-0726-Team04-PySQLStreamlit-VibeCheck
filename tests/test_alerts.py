import pandas as pd
import pytest

from pipeline.alerts import (
    EXIT_ALERTS_FOUND,
    AlertContext,
    at_or_above,
    employees_needing_attention,
    evaluate_alerts,
    main,
    summarize_alerts,
)
from pipeline.features import build_feature_table

CONTEXT = AlertContext(expected_days=17.0, low_activity_minutes=100.0)


def hires(**overrides) -> pd.DataFrame:
    base = {
        "employee_id": [1, 2, 3, 4],
        "Department": ["Sales"] * 4,
        "JobRole": ["Rep"] * 4,
        "onboarding_status": ["Completed", "Delayed", "In Progress", "In Progress"],
        "onboarding_days": pd.array([30, 35, 25, 10], dtype="Int64"),
        "training_completion_percent": [40.0, 30.0, 70.0, 80.0],
        "manager_assigned": pd.array([False, False, True, True], dtype="boolean"),
        "buddy_assigned": pd.array([False, True, None, True], dtype="boolean"),
        "first_week_checkin": pd.array([True, True, True, False], dtype="boolean"),
        "total_active_minutes": [50, 500, 90, 400],
    }
    return pd.DataFrame({**base, **overrides})


def codes_for(alerts: pd.DataFrame, employee_id: int) -> set[str]:
    return set(alerts.loc[alerts["employee_id"] == employee_id, "code"])


def test_rules_fire_only_for_open_onboardings():
    alerts = evaluate_alerts(hires(), CONTEXT)
    assert codes_for(alerts, 1) == set()   # completed hires never alert, however bad the history
    assert codes_for(alerts, 2) == {"DELAYED_STATUS", "NO_MANAGER", "LOW_TRAINING_IN_FLIGHT"}
    assert codes_for(alerts, 3) == {"OVERDUE_IN_PROGRESS", "LOW_TOOL_ACTIVITY"}   # unknown buddy is not "no buddy"
    assert codes_for(alerts, 4) == {"MISSED_FIRST_WEEK_CHECKIN"}


def test_alerts_are_sorted_by_severity_with_readable_messages():
    alerts = evaluate_alerts(hires(), CONTEXT)
    assert alerts["severity"].tolist() == sorted(alerts["severity"].tolist(), key=["high", "medium", "low"].index)
    delayed = alerts[alerts["code"] == "DELAYED_STATUS"].iloc[0]
    assert delayed["message"] == "Delayed after 35 days with 30% of training done"
    overdue = alerts[alerts["code"] == "OVERDUE_IN_PROGRESS"].iloc[0]
    assert overdue["message"].endswith("90% of hires finish within 17")


def test_summary_attention_list_and_severity_filter():
    alerts = evaluate_alerts(hires(), CONTEXT)
    summary = summarize_alerts(alerts).set_index("code")
    assert summary.loc["DELAYED_STATUS", "hires"] == 1
    attention = employees_needing_attention(alerts)
    assert attention["employee_id"].tolist()[:2] == [2, 3]
    assert attention.set_index("employee_id").loc[4, "worst_severity"] == "low"
    assert set(at_or_above(alerts, "medium")["severity"]) == {"high", "medium"}


def test_no_open_onboardings_means_no_alerts():
    calm = hires(onboarding_status=["Completed"] * 4)
    alerts = evaluate_alerts(calm, CONTEXT)
    assert alerts.empty and list(alerts.columns)[:4] == ["employee_id", "Department", "JobRole", "severity"]
    assert summarize_alerts(alerts).empty


@pytest.fixture(scope="module")
def features():
    return build_feature_table()


def test_company_wide_context(features):
    context = AlertContext.from_features(features)
    assert context.expected_days == 17.0
    assert context.low_activity_minutes > 0


def test_real_data_every_open_onboarding_is_flagged(features):
    alerts = evaluate_alerts(features)
    open_ids = set(features.loc[features["onboarding_status"].isin(["In Progress", "Delayed"]), "employee_id"])
    assert set(alerts["employee_id"]) == open_ids and len(open_ids) == 37
    assert (summarize_alerts(alerts).set_index("code").loc["DELAYED_STATUS", "hires"]) == 14


def test_cli_writes_csv_and_signals_high_alerts(tmp_path, capsys):
    out = tmp_path / "alerts.csv"
    assert main(["--out", str(out)]) == 0
    assert "37 hires need attention" in capsys.readouterr().out
    assert len(pd.read_csv(out)) > 37
    assert main(["--out", str(out), "--fail-on", "high"]) == EXIT_ALERTS_FOUND
