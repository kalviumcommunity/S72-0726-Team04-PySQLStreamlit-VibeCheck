import json

import pytest

from pipeline.config import load_settings
from pipeline.ingest import load_dataset, load_onboarding, main, read_table, resolve_source

RECORDS = [
    {"employee_id": 1, "onboarding_status": "Completed", "onboarding_days": 12},
    {"employee_id": 2, "onboarding_status": "Delayed", "onboarding_days": 40},
]


def test_real_onboarding_csv_loads(settings):
    frame, report = load_dataset("onboarding", settings=settings)
    assert len(frame) == report.rows == 1470
    assert "training_completion_percent" in report.columns
    assert len(report.sha256) == 64


def test_json_array_and_wrapped_json_are_equivalent(tmp_path):
    bare = tmp_path / "bare.json"
    wrapped = tmp_path / "wrapped.json"
    bare.write_text(json.dumps(RECORDS), encoding="utf-8")
    wrapped.write_text(json.dumps({"data": RECORDS}), encoding="utf-8")
    assert read_table(bare).equals(read_table(wrapped))
    assert list(read_table(bare)["onboarding_days"]) == [12, 40]


def test_json_lines_skip_blank_lines(tmp_path):
    path = tmp_path / "onboarding.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in RECORDS) + "\n\n", encoding="utf-8")
    assert len(read_table(path)) == 2


@pytest.mark.parametrize("content, message", [
    ('{"rows": 3}', "JSON array"),
    ("[]", "no rows"),
])
def test_malformed_json_is_rejected(tmp_path, content, message):
    path = tmp_path / "onboarding.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        read_table(path)


def test_unsupported_and_missing_files(tmp_path):
    (tmp_path / "onboarding.xlsx").write_bytes(b"")
    with pytest.raises(ValueError, match="Unsupported"):
        read_table(tmp_path / "onboarding.xlsx")
    with pytest.raises(FileNotFoundError):
        read_table(tmp_path / "nope.csv")


def test_source_resolution_falls_back_to_json(tmp_path):
    settings = load_settings(env={"VIBECHECK_DATA_DIR": str(tmp_path)})
    (tmp_path / "onboarding.json").write_text(json.dumps(RECORDS), encoding="utf-8")
    assert resolve_source("onboarding", settings).name == "onboarding.json"
    assert len(load_onboarding(settings=settings)) == 2
    with pytest.raises(FileNotFoundError, match="tool_usage.csv"):
        resolve_source("tool_usage", settings)


def test_cli_reports_errors_with_exit_code(tmp_path, capsys):
    assert main(["onboarding"]) == 0
    assert "1470 rows" in capsys.readouterr().out
    assert main(["onboarding", "--source", str(tmp_path / "missing.csv")]) == 1
