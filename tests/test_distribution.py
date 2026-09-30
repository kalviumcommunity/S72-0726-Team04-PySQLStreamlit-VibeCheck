import pandas as pd
import pytest

from pipeline.analysis import markdown_table
from pipeline.analysis.distribution import (
    describe_completion_times,
    distribution_report,
    histogram,
    key_findings,
    main,
)
from pipeline.features import build_feature_table


def test_describe_known_values():
    stats = describe_completion_times(pd.DataFrame({"onboarding_days": list(range(1, 11)) + [None]})).iloc[0]
    assert (stats["group"], stats["count"], stats["mean"], stats["p50"], stats["max"]) == ("All", 10, 5.5, 5.5, 10)


def test_describe_by_group():
    df = pd.DataFrame({"onboarding_days": [10, 12, 30, 40], "team": ["a", "a", "b", "b"]})
    stats = describe_completion_times(df, by="team").set_index("group")
    assert stats.loc["a", "mean"] == 11 and stats.loc["b", "mean"] == 35


def test_histogram_bins_cover_every_value():
    df = pd.DataFrame({"onboarding_days": [5, 6, 7, 12, 13, 43]})
    hist = histogram(df, bin_width=2)
    assert hist["count"].sum() == 6
    assert hist["share"].sum() == pytest.approx(1.0)
    assert (hist["bin_end"] - hist["bin_start"]).eq(2).all()
    assert hist.iloc[0]["bin_start"] == 4 and hist.iloc[-1]["bin_end"] > 43


def test_markdown_table_formats_floats_and_escapes_pipes():
    table = markdown_table(pd.DataFrame({"name": ["a|b"], "value": [1.234]}))
    assert table.splitlines() == ["| name | value |", "| :--- | ---: |", "| a\\|b | 1.23 |"]


@pytest.fixture(scope="module")
def features():
    return build_feature_table()


def test_findings_on_real_data(features):
    findings = key_findings(features)
    assert findings[0].startswith("Completed onboardings take a median of 12 days")
    assert any(f.startswith("Delayed hires have already spent 3.0x") for f in findings)


def test_report_sections(features, tmp_path):
    report = distribution_report(features)
    for heading in ("## Key findings", "## Completed hires (n=1433)", "## By status", "## Histogram"):
        assert heading in report
    assert main(["--output", str(tmp_path / "dist.md")]) == 0
    assert (tmp_path / "dist.md").read_text(encoding="utf-8") == report
