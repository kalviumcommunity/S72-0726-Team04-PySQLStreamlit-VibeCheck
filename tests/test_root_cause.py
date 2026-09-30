import numpy as np
import pandas as pd
import pytest

from pipeline.analysis.root_cause import (
    Factor,
    delay_rate_by,
    rank_root_causes,
    root_cause_findings,
)
from pipeline.features import build_feature_table


def features_frame():
    # 10 new hires: 3 delayed. Everyone without a buddy is delayed; one buddy-less hire is tenured.
    return pd.DataFrame({
        "employee_id": range(1, 12),
        "is_new_hire": [True] * 10 + [False],
        "onboarding_status": ["Delayed"] * 3 + ["Completed"] * 7 + ["Completed"],
        "buddy_assigned": pd.array([False, False, True] + [True] * 7 + [False], dtype="boolean"),
        "team": ["a", "a", "b", "a", "b", "b", "b", "b", "b", "b", "a"],
    })


NO_BUDDY = Factor("no_buddy", "No buddy", lambda d: d["buddy_assigned"].eq(False))
TEAM_A = Factor("team_a", "Team A", lambda d: d["team"].eq("a"))


def test_lift_risk_difference_and_coverage():
    row = rank_root_causes(features_frame(), [NO_BUDDY], min_support=1).iloc[0]
    assert (row["hires_with_factor"], row["delayed_with_factor"]) == (2, 2)
    assert row["delay_rate_with_pct"] == 100.0
    assert row["delay_rate_without_pct"] == 12.5          # 1 delayed of 8 with a buddy
    assert row["lift"] == 8.0
    assert row["coverage_pct"] == pytest.approx(66.67)


def test_small_factors_are_marked_unreliable_and_ranked_last():
    table = rank_root_causes(features_frame(), [NO_BUDDY, TEAM_A], min_support=3)
    assert table["factor"].tolist() == ["team_a", "no_buddy"]
    assert table["reliable"].tolist() == [True, False]


def test_perfect_separation_gives_infinite_lift():
    only_delayed = Factor("delayed_flag", "x", lambda d: d["onboarding_status"].eq("Delayed"))
    table = rank_root_causes(features_frame(), [only_delayed], min_support=1)
    assert np.isinf(table.loc[0, "lift"])
    assert "no delays without it" in root_cause_findings(table)[0]


def test_delay_rate_by_group():
    table = delay_rate_by(features_frame(), "team").set_index("team")
    assert table.loc["a", "delay_rate_pct"] == pytest.approx(66.67)   # 2 of 3 new hires in team a
    assert table.loc["b", "hires"] == 7


def test_real_data_every_manager_less_hire_is_delayed():
    table = rank_root_causes(build_feature_table()).set_index("factor")
    assert table.loc["no_manager", "delay_rate_with_pct"] == 100.0
    assert table.loc["no_manager", "lift"] > 10
    assert table.loc["entry_level_role", "lift"] < 1.5                # job level is not a driver
    assert table.index.get_loc("low_training") > table.index.get_loc("no_manager")  # symptoms rank after causes
    findings = root_cause_findings(table.reset_index())
    assert any(f.startswith("No reporting manager assigned: 100% delayed") for f in findings)
    assert findings[-1].endswith("likely a symptom, not a cause")
