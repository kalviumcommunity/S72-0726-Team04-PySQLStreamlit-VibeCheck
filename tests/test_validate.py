import json
import re
import shutil
from pathlib import Path

import pandas as pd

from pipeline.__main__ import COMMANDS
from pipeline.config import DATASETS, load_settings
from pipeline.validate import main, run_validation

WORKFLOWS = Path(__file__).resolve().parents[1] / ".github" / "workflows"


def copy_workspace(settings, target: Path) -> Path:
    target.mkdir()
    for name in DATASETS:
        shutil.copy(settings.dataset_path(name), target)
    return target


def test_committed_data_passes_every_step():
    results = run_validation()
    assert [r.name for r in results] == ["contracts", "data_dictionary", "sql_python_reconciliation"]
    assert all(r.passed for r in results), results
    assert results[-1].details[0].endswith("checks agree")


def test_contract_failure_stops_the_run(settings, tmp_path):
    data = copy_workspace(settings, tmp_path / "data")
    tickets = pd.read_csv(data / "support_tickets.csv")
    tickets.loc[0, "employee_id"] = 999_999
    tickets.to_csv(data / "support_tickets.csv", index=False)
    results = run_validation(load_settings(env={"VIBECHECK_DATA_DIR": str(data)}))
    assert [(r.name, r.passed) for r in results] == [("contracts", False)]
    assert "999999" in results[0].details[0]


def test_missing_dataset_is_a_failed_step(tmp_path):
    results = run_validation(load_settings(env={"VIBECHECK_DATA_DIR": str(tmp_path)}))
    assert not results[0].passed and "employees" in results[0].details[0]


def test_json_output_for_ci(tmp_path, capsys):
    report = tmp_path / "validation.json"
    assert main(["--json", str(report)]) == 0
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["passed"] is True and len(payload["steps"]) == 3
    assert "PASS  contracts" in capsys.readouterr().out


def test_workflows_only_call_real_pipeline_commands():
    used = {m for path in WORKFLOWS.glob("*.yml")
            for m in re.findall(r"python -m pipeline (\w+)", path.read_text(encoding="utf-8"))}
    assert "validate" in used
    assert used <= set(COMMANDS)
