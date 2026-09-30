import pandas as pd
import pytest

from pipeline.ingest import load_dataset
from pipeline.outliers import detect_completion_outliers, iqr_bounds, mad_bounds, summarize_outliers
from pipeline.standardize import load_standardized_onboarding


def frame(days, groups=None):
    data = {"employee_id": range(1, len(days) + 1), "onboarding_days": days}
    if groups:
        data["Department"] = groups
    return pd.DataFrame(data)


def test_iqr_flags_the_long_tail():
    result = detect_completion_outliers(frame([8, 9, 10, 11, 12, 13, 14, 60]), method="iqr")
    assert result.loc[result["is_outlier"], "onboarding_days"].tolist() == [60.0]
    assert result.loc[result["is_outlier"], "direction"].tolist() == ["high"]


def test_mad_survives_a_zero_mad():
    low, high = mad_bounds(pd.Series([5, 5, 5, 5, 5, 6, 50], dtype=float))
    assert low < 5 < 6 < high < 50


def test_bounds_helpers_agree_on_symmetric_data():
    values = pd.Series(range(1, 101), dtype=float)
    assert iqr_bounds(values)[0] < 1 and iqr_bounds(values)[1] > 100
    assert mad_bounds(values)[1] > 100


def test_small_groups_fall_back_to_company_bounds():
    days = [10, 11, 12, 13, 14, 15] * 4 + [40, 10, 12]
    groups = ["Big"] * 25 + ["Tiny"] * 2
    result = detect_completion_outliers(frame(days, groups), group_by="Department", min_group_size=20)
    assert set(result.loc[result["Department"] == "Tiny", "bounds_scope"]) == {"all"}
    assert set(result.loc[result["Department"] == "Big", "bounds_scope"]) == {"Big"}
    summary = summarize_outliers(result).set_index("bounds_scope")
    assert summary.loc["Big", "outliers_high"] == 1


def test_missing_values_are_skipped_and_bad_method_rejected():
    result = detect_completion_outliers(frame([10, None, 12, 11]))
    assert len(result) == 3
    with pytest.raises(ValueError, match="method"):
        detect_completion_outliers(frame([1, 2]), method="zscore")


@pytest.fixture(scope="module")
def onboarding_with_department():
    employees, _ = load_dataset("employees")
    return load_standardized_onboarding().merge(employees[["employee_id", "Department"]], on="employee_id")


@pytest.mark.parametrize("method, group_by", [("iqr", None), ("mad", "Department")])
def test_completed_hires_are_never_flagged_on_real_data(onboarding_with_department, method, group_by):
    result = detect_completion_outliers(onboarding_with_department, method=method, group_by=group_by)
    flagged = result[result["is_outlier"]]
    assert len(flagged) >= 5
    assert not flagged["onboarding_status"].eq("Completed").any()
    assert set(flagged["direction"]) == {"high"}
