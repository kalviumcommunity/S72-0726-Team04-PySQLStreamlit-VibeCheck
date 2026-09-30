import pandas as pd
import pytest

from pipeline.features import build_feature_table
from pipeline.kpis import KPI_KEYS, compute_department_kpis, compute_onboarding_kpis
from pipeline.reconcile import Check, main, python_speed_ranks, reconcile, reconciliation_table


@pytest.fixture(scope="module")
def features():
    return build_feature_table()


def test_check_semantics():
    assert Check("a", 97.48, 97.475).passed
    assert Check("rounding modes differ by one cent", 11.68, 11.67).passed
    assert not Check("b", 97.48, 97.0).passed
    assert Check("both empty", None, None).passed and not Check("one empty", None, 1.0).passed
    assert Check("c", 3.0, 1.0).as_dict()["delta"] == 2.0


def test_python_kpis_handle_an_empty_cohort(features):
    kpis = compute_onboarding_kpis(features.head(0))
    assert kpis["total_hires"] == 0 and kpis["completion_rate_pct"] is None and kpis["avg_training_pct"] is None
    assert set(kpis) == set(KPI_KEYS)


def test_python_department_kpis_shape(features):
    table = compute_department_kpis(features)
    assert table["department"].tolist() == ["Human Resources", "Research & Development", "Sales"]
    assert table["hires"].sum() == 1470


def test_python_ranks_follow_sql_rank_semantics():
    features = pd.DataFrame({
        "employee_id": [1, 2, 3, 4], "Department": ["S"] * 4, "onboarding_status": ["Completed"] * 4,
        "onboarding_days": [8, 8, 9, 7], "training_completion_percent": [90.0, 90.0, 80.0, 50.0],
    })
    assert python_speed_ranks(features).set_index("employee_id")["dept_speed_rank"].to_dict() == {4: 1, 1: 2, 2: 2, 3: 4}


def test_sql_and_python_agree_on_real_data(staged_engine, features):
    checks = reconcile(staged_engine, features)
    failed = reconciliation_table([c for c in checks if not c.passed])
    assert failed.empty, failed.to_string()
    names = {c.name for c in checks}
    assert {"overall.completion_rate_pct", "rankings.dept_speed_rank_agreement", "cohort.new_hires"} <= names
    assert any(n.startswith("department[Sales].") for n in names)


def test_drift_between_sql_and_python_is_caught(staged_engine, features):
    drifted = features.copy()
    drifted["onboarding_status"] = drifted["onboarding_status"].astype("object")
    drifted.loc[drifted.index[0], "onboarding_status"] = "Delayed"   # a cleaning bug on the Python side
    failed = {c.name for c in reconcile(staged_engine, drifted) if not c.passed}
    assert {"overall.delayed_count", "overall.completed_count", "rankings.dept_speed_rank_agreement"} <= failed


def test_cli_reports_agreement(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("VIBECHECK_OUTPUT_DIR", str(tmp_path))
    assert main([]) == 0
    assert "checks agree between SQL and Python" in capsys.readouterr().out
