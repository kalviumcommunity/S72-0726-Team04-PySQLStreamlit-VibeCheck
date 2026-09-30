"""End-to-end: run the pipeline CLI in a subprocess, exactly as CI and cron do.

Each test builds its own sample workspace (a consistent slice of the committed
datasets) so the runs are fast, isolated and never touch data/ or outputs/.
Run just these with `pytest -m e2e`, or skip them with `pytest -m "not e2e"`.
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from pipeline.alerts import EXIT_ALERTS_FOUND
from pipeline.config import DATASETS

pytestmark = pytest.mark.e2e

ROOT = Path(__file__).resolve().parents[1]


def make_workspace(tmp_path: Path, settings, statuses=("Completed", "In Progress", "Delayed"),
                   completed_sample: int = 200) -> dict[str, str]:
    """Write a slice of the real data (all open onboardings + some completed) and return the env."""
    frames = {name: pd.read_csv(settings.dataset_path(name)) for name in DATASETS}
    onboarding = frames["onboarding"]
    keep = onboarding[onboarding["onboarding_status"].isin(statuses) & (onboarding["onboarding_status"] != "Completed")]
    if "Completed" in statuses:
        keep = pd.concat([keep, onboarding[onboarding["onboarding_status"] == "Completed"].head(completed_sample)])
    ids = set(keep["employee_id"])
    data = tmp_path / "data"
    data.mkdir()
    for name, frame in frames.items():
        frame[frame["employee_id"].isin(ids)].to_csv(data / f"{name}.csv", index=False)
    env = {k: v for k, v in os.environ.items() if not k.startswith("VIBECHECK_")}
    return {**env, "VIBECHECK_DATA_DIR": str(data), "VIBECHECK_OUTPUT_DIR": str(tmp_path / "outputs")}


def run(env: dict, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "pipeline", *args], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=300)


def test_scheduled_run_validate_export_alerts(tmp_path, settings):
    env = make_workspace(tmp_path, settings)

    validate = run(env, "validate", "--json", str(tmp_path / "validation.json"))
    assert validate.returncode == 0, validate.stdout + validate.stderr
    assert json.loads((tmp_path / "validation.json").read_text(encoding="utf-8"))["passed"] is True

    export = run(env, "export")
    assert export.returncode == 0, export.stderr
    out = tmp_path / "outputs"
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["join"]["matched"] == 237          # 37 open onboardings + 200 completed
    for item in manifest["outputs"]:
        assert hashlib.sha256((out / item["path"]).read_bytes()).hexdigest() == item["sha256"]

    alerts = run(env, "alerts", "--fail-on", "high")
    assert alerts.returncode == EXIT_ALERTS_FOUND
    assert "37 hires need attention" in alerts.stdout
    assert (out / "alerts.csv").is_file()


def test_alert_gate_passes_when_every_onboarding_is_complete(tmp_path, settings):
    env = make_workspace(tmp_path, settings, statuses=("Completed",))
    result = run(env, "alerts", "--fail-on", "low")
    assert result.returncode == 0, result.stderr
    assert "No alerts fired." in result.stdout


def test_rerunning_export_reproduces_the_same_data(tmp_path, settings):
    env = make_workspace(tmp_path, settings)
    first, second = tmp_path / "run1", tmp_path / "run2"
    assert run(env, "export", "--out", str(first), "--no-charts").returncode == 0
    assert run(env, "export", "--out", str(second), "--no-charts").returncode == 0
    for csv in first.rglob("*.csv"):
        assert csv.read_bytes() == (second / csv.relative_to(first)).read_bytes(), csv.name


def test_broken_dataset_fails_every_entry_point_loudly(tmp_path, settings):
    env = make_workspace(tmp_path, settings)
    onboarding = Path(env["VIBECHECK_DATA_DIR"]) / "onboarding.csv"
    pd.read_csv(onboarding).drop(columns=["onboarding_status"]).to_csv(onboarding, index=False)

    validate = run(env, "validate")
    assert validate.returncode == 1
    assert "FAIL  contracts" in validate.stdout and "missing onboarding_status" in validate.stdout

    export = run(env, "export")
    assert export.returncode == 1
    assert "Missing required columns: onboarding_status" in export.stderr
    assert not (tmp_path / "outputs" / "manifest.json").exists()   # no half-written export


def test_missing_data_folder_is_reported_not_crashed(tmp_path):
    env = {**os.environ, "VIBECHECK_DATA_DIR": str(tmp_path / "nope"), "VIBECHECK_OUTPUT_DIR": str(tmp_path)}
    result = run(env, "validate")
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
