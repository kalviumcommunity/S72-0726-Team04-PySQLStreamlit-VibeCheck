import hashlib
import json

import pandas as pd
import pytest

from pipeline.__main__ import COMMANDS
from pipeline.__main__ import main as pipeline_main
from pipeline.analysis.root_cause import rank_root_causes
from pipeline.export import build_charts, export_all
from pipeline.features import build_feature_table


def csv_checksums(manifest):
    return {i["path"]: i["sha256"] for i in manifest["outputs"] if i["path"].endswith(".csv")}


@pytest.fixture(scope="module")
def exported(tmp_path_factory):
    out = tmp_path_factory.mktemp("export")
    return out, export_all(out_dir=out)


def test_manifest_matches_files_on_disk(exported):
    out, manifest = exported
    assert [i["dataset"] for i in manifest["inputs"]] == ["employees", "onboarding", "tool_usage", "support_tickets"]
    assert manifest["join"]["matched"] == 1470
    for item in manifest["outputs"]:
        path = out / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"], item["path"]
        if item["rows"] is not None:
            assert len(pd.read_csv(path)) == item["rows"], item["path"]
    assert json.loads((out / "manifest.json").read_text(encoding="utf-8")) == manifest


def test_expected_outputs_are_written(exported):
    out, manifest = exported
    paths = {item["path"] for item in manifest["outputs"]}
    assert {"clean/onboarding_clean.csv", "clean/onboarding_features.csv", "analysis/delay_root_causes.csv",
            "charts/completion_time_histogram.html"} <= paths
    features = pd.read_csv(out / "clean/onboarding_features.csv")
    assert len(features) == 1470 and "onboarding_speed" in features
    outliers = pd.read_csv(out / "analysis/completion_outliers.csv")
    assert outliers["is_outlier"].all()
    assert "cdn.plot.ly" in (out / "charts/status_by_department.html").read_text(encoding="utf-8")


def test_csv_exports_are_deterministic(exported, tmp_path):
    _, first = exported
    second = export_all(out_dir=tmp_path, include_charts=False)
    assert csv_checksums(first) == csv_checksums(second)
    assert not any(i["path"].startswith("charts/") for i in second["outputs"])


def test_charts_skip_symptoms_and_infinite_lift():
    features = build_feature_table()
    charts = build_charts(features, rank_root_causes(features))
    assert set(charts) == {"completion_time_histogram", "status_by_department", "delay_root_causes"}
    factors = set(charts["delay_root_causes"].data[0].y)
    assert "Training below 60%" not in factors and "No reporting manager assigned" in factors


def test_command_line_dispatch(tmp_path, capsys):
    assert set(COMMANDS) >= {"ingest", "kpis", "reconcile", "export"}
    assert pipeline_main([]) == 0 and "usage: python -m pipeline" in capsys.readouterr().out
    assert pipeline_main(["explode"]) == 2
    assert pipeline_main(["export", "--out", str(tmp_path), "--no-charts"]) == 0
    assert "clean/onboarding_features.csv" in capsys.readouterr().out
    assert (tmp_path / "manifest.json").is_file()
