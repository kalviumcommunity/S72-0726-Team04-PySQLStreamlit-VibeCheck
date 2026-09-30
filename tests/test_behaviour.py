import math

import pandas as pd
import pytest

from pipeline.analysis.behaviour import (
    behaviour_findings,
    cohens_d,
    compare_fast_vs_slow,
    effect_label,
    tool_minutes_by_speed,
)
from pipeline.features import build_feature_table
from pipeline.ingest import load_dataset


def features_frame():
    return pd.DataFrame({
        "employee_id": [1, 2, 3, 4, 5, 6],
        "is_new_hire": [True, True, True, True, True, False],
        "onboarding_speed": ["fast", "fast", "fast", "slow", "slow", "slow"],
        "total_active_minutes": [300, 320, 340, 100, 120, 999],
        "training_completion_percent": [95.0, 90.0, 92.0, 40.0, 60.0, 99.0],
    })


def test_cohens_d_on_known_samples():
    assert cohens_d(pd.Series([1, 2, 3]), pd.Series([4, 5, 6])) == pytest.approx(3.0)
    assert math.isnan(cohens_d(pd.Series([1]), pd.Series([4, 5])))


@pytest.mark.parametrize("d, label", [(0.1, "negligible"), (-0.3, "small"), (0.6, "medium"), (-1.2, "large")])
def test_effect_labels(d, label):
    assert effect_label(d) == label


def test_comparison_uses_new_hires_only_and_flags_small_groups():
    table = compare_fast_vs_slow(features_frame(), metrics=["total_active_minutes", "training_completion_percent"])
    minutes = table.set_index("metric").loc["total_active_minutes"]
    assert (minutes["fast_n"], minutes["slow_n"]) == (3, 2)   # the tenured slow hire is excluded
    assert minutes["slow_mean"] == 110 and minutes["difference"] == -210
    assert not minutes["reliable"]
    assert behaviour_findings(table)[0].endswith("treat as indicative")


def test_tool_minutes_count_non_users_as_zero():
    usage = pd.DataFrame({"employee_id": [1, 1, 4], "tool_name": ["Slack", "Jira", "Slack"],
                          "active_minutes": [60, 30, 20]})
    table = tool_minutes_by_speed(features_frame(), usage).set_index("tool_name")
    assert table.loc["Slack", "fast"] == 20.0   # 60 minutes over 3 fast hires
    assert table.loc["Slack", "slow"] == 10.0   # 20 minutes over 2 slow new hires
    assert table.loc["Jira", "slow"] == 0.0


def test_missing_new_hire_flag_is_explained():
    with pytest.raises(KeyError, match="employees table"):
        compare_fast_vs_slow(features_frame().drop(columns="is_new_hire"))


def test_real_data_slow_onboarders_have_less_training():
    features = build_feature_table()
    table = compare_fast_vs_slow(features).set_index("metric")
    assert table["reliable"].all()
    assert table.loc["training_completion_percent", "cohens_d"] < -0.5
    tools = tool_minutes_by_speed(features, load_dataset("tool_usage")[0])
    assert set(tools["tool_name"]) == {"Slack", "Jira", "GitHub", "Confluence", "VS Code", "Google Workspace", "Notion"}
