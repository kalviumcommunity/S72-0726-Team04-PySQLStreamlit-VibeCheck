import pandas as pd
import pytest

from pipeline.db import get_engine, stage_tables
from pipeline.rankings import department_monthly_trend, fastest_per_department, main, rank_hires_by_speed


@pytest.fixture(scope="module")
def tie_engine(tmp_path_factory):
    """Six completed hires in one department with deliberate ties on days."""
    employees = pd.DataFrame({"employee_id": [1, 2, 3, 4, 5, 6], "Department": ["Sales"] * 6,
                              "JobRole": ["Rep"] * 6})
    onboarding = pd.DataFrame({
        "employee_id": [1, 2, 3, 4, 5, 6],
        "onboarding_status": ["Completed"] * 5 + ["Delayed"],
        "onboarding_days": [10, 8, 8, 12, 10, 40],
        "training_completion_percent": [90.0, 95.0, 95.0, 80.0, 99.0, 20.0],
        "onboarding_completion_date": ["2026-05-02", "2026-05-20", "2026-06-01", "2026-06-15", "2026-07-01", None],
    })
    engine = get_engine(f"sqlite:///{(tmp_path_factory.mktemp('ties') / 't.db').as_posix()}")
    stage_tables(engine, {"employees": employees, "onboarding": onboarding})
    return engine


def test_rank_semantics_with_ties(tie_engine):
    ranks = rank_hires_by_speed(tie_engine).set_index("employee_id")
    assert 6 not in ranks.index                                          # only completed hires are ranked
    assert ranks["dept_speed_rank"].to_dict() == {2: 1, 3: 1, 5: 3, 1: 4, 4: 5}   # RANK skips after ties
    assert ranks["company_speed_rank"].to_dict() == {2: 1, 3: 1, 5: 2, 1: 2, 4: 3}  # DENSE_RANK does not
    assert ranks.loc[2, "company_percentile"] == 0.0 and ranks.loc[4, "company_percentile"] == 1.0
    assert ranks.loc[4, "days_vs_dept_avg"] == pytest.approx(12 - 9.6)


def test_top_n_includes_ties(tie_engine):
    top = fastest_per_department(tie_engine, top_n=1)
    assert top["employee_id"].tolist() == [2, 3]


def test_monthly_trend_uses_lag_and_rolling_window(tie_engine):
    trend = department_monthly_trend(tie_engine)
    assert trend["completion_month"].tolist() == ["2026-05", "2026-06", "2026-07"]
    assert pd.isna(trend.loc[0, "change_vs_prev_month"])
    assert trend.loc[1, "change_vs_prev_month"] == 10.0 - 9.0
    assert trend.loc[2, "rolling_3_month_avg_days"] == round((9 + 10 + 10) / 3, 2)


@pytest.mark.parametrize("top_n", [0, -2, "3; DROP TABLE onboarding", True])
def test_top_n_is_validated(staged_engine, top_n):
    with pytest.raises(ValueError, match="positive integer"):
        fastest_per_department(staged_engine, top_n)


def test_real_rankings_are_consistent(staged_engine):
    ranks = rank_hires_by_speed(staged_engine)
    assert len(ranks) == 1433
    for department, group in ranks.groupby("department"):
        assert group["dept_speed_rank"].min() == 1
        assert group["dept_completed"].iloc[0] == len(group)
        assert set(group["dept_speed_quartile"]) == {1, 2, 3, 4}
        fastest = group.loc[group["dept_speed_rank"] == 1, "onboarding_days"]
        assert (fastest == group["onboarding_days"].min()).all(), department
    assert ranks["company_percentile"].between(0, 1).all()


def test_cli_prints_top_hires(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("VIBECHECK_OUTPUT_DIR", str(tmp_path))
    assert main(["--stage", "--top", "2"]) == 0
    assert "dept_speed_rank" in capsys.readouterr().out
    assert main(["--top", "0"]) == 2
