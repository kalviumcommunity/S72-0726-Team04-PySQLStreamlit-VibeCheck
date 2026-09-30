# Day 23 - End-to-end tests of the automated pipeline

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-23-e2e-pipeline-tests` |
| **Base** | `main` - stacked on `gaurav/day-22-dashboard-alerts` (merge PR 22 first) |
| **Roadmap** | Day 25 (Fri 21 Aug 2026) - *Test automated pipeline end-to-end.* |
| **Type** | `test` |
| **Size** | 2 code files, +105 / -0 lines (docs excluded) |

## Summary

Runs the real CLI in subprocesses - exactly as CI and the scheduled job do - against generated sample workspaces: validate -> export -> alerts, the alert gate, reproducibility, and broken or missing data.

## Why

- Unit tests do not prove the commands work together, with real exit codes, from a clean process.

## What changed

- `tests/test_e2e_pipeline.py`: 5 tests, each in its own isolated workspace (never touches `data/` or `outputs/`).
- `e2e` marker registered in `pytest.ini` (`pytest -m "not e2e"` for quick runs).

## How to test

```bash
pytest -m e2e
```

## Result

All 5 pass (~10 s). Writing them surfaced a defect: four commands print raw tracebacks when data is missing. It is fixed in the Day 25 bug-fix PR.

## Diff highlight

`tests/test_e2e_pipeline.py` (excerpt)

```diff
+def test_scheduled_run_validate_export_alerts(tmp_path, settings):
+    env = make_workspace(tmp_path, settings)
+
+    validate = run(env, "validate", "--json", str(tmp_path / "validation.json"))
+    assert validate.returncode == 0, validate.stdout + validate.stderr
+    assert json.loads((tmp_path / "validation.json").read_text(encoding="utf-8"))["passed"] is True
+
+    export = run(env, "export")
+    assert export.returncode == 0, export.stderr
+    out = tmp_path / "outputs"
+    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
+    assert manifest["join"]["matched"] == 237          # 37 open onboardings + 200 completed
+    for item in manifest["outputs"]:
+        assert hashlib.sha256((out / item["path"]).read_bytes()).hexdigest() == item["sha256"]
+
+    alerts = run(env, "alerts", "--fail-on", "high")
+    assert alerts.returncode == EXIT_ALERTS_FOUND
+    assert "37 hires need attention" in alerts.stdout
+    assert (out / "alerts.csv").is_file()
+
+
+def test_alert_gate_passes_when_every_onboarding_is_complete(tmp_path, settings):
+    env = make_workspace(tmp_path, settings, statuses=("Completed",))
+    result = run(env, "alerts", "--fail-on", "low")
+    assert result.returncode == 0, result.stderr
+    assert "No alerts fired." in result.stdout
+
+
+def test_rerunning_export_reproduces_the_same_data(tmp_path, settings):
+    env = make_workspace(tmp_path, settings)
+    first, second = tmp_path / "run1", tmp_path / "run2"
+    assert run(env, "export", "--out", str(first), "--no-charts").returncode == 0
+    assert run(env, "export", "--out", str(second), "--no-charts").returncode == 0
+    for csv in first.rglob("*.csv"):
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `pytest.ini` | 2 | 0 |
| `tests/test_e2e_pipeline.py` | 103 | 0 |
| `docs/prs/gaurav/day-23-e2e-pipeline-tests.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
