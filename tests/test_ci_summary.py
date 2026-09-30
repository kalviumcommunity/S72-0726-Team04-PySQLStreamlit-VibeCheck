import json

import pandas as pd

from pipeline.ci_summary import main, render_summary

VALIDATION = {"passed": False, "steps": [
    {"name": "contracts", "passed": True, "details": ["all datasets match"]},
    {"name": "sql_python_reconciliation", "passed": False, "details": ["overall.delayed_count: sql=14 python=15"]},
]}
MANIFEST = {
    "inputs": [{"dataset": "onboarding", "rows": 1470}],
    "outputs": [{"path": "clean/onboarding_clean.csv", "rows": 1470}, {"path": "charts/x.html", "rows": None}],
}
ALERTS = pd.DataFrame({"employee_id": [1, 1, 2, 3], "severity": ["high", "low", "high", "medium"],
                       "code": ["DELAYED_STATUS", "LOW_TOOL_ACTIVITY", "NO_MANAGER", "NO_BUDDY_IN_FLIGHT"]})


def test_full_summary():
    text = render_summary(VALIDATION, MANIFEST, ALERTS)
    assert "## Data validation: FAILED" in text
    assert "| sql_python_reconciliation | **FAIL** | overall.delayed_count: sql=14 python=15 |" in text
    assert "Inputs: onboarding (1,470 rows)" in text
    assert "| `clean/onboarding_clean.csv` | 1,470 |" in text and "| `charts/x.html` |  |" in text
    assert "**high**: 2 hires | **medium**: 1 hires | **low**: 1 hires" in text
    rules = [line for line in text.splitlines() if line.startswith("| high") or line.startswith("| low")]
    assert rules[0].startswith("| high")                      # most severe rules listed first
    assert text.isascii()


def test_missing_inputs_still_render():
    text = render_summary()
    assert "_Validation did not run._" in text and "_No export was produced._" in text
    assert "_Alerts were not evaluated._" in text
    assert "No alerts fired." in render_summary(alerts=ALERTS.head(0))


def test_cli_reads_files_and_tolerates_missing_ones(tmp_path, capsys):
    (tmp_path / "validation.json").write_text(json.dumps(VALIDATION), encoding="utf-8")
    ALERTS.to_csv(tmp_path / "alerts.csv", index=False)
    assert main(["--validation", str(tmp_path / "validation.json"), "--alerts", str(tmp_path / "alerts.csv"),
                 "--manifest", str(tmp_path / "missing.json")]) == 0
    out = capsys.readouterr().out
    assert "FAILED" in out and "_No export was produced._" in out and "NO_MANAGER" in out
