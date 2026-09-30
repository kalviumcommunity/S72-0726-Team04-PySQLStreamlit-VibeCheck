# Day 20 - GitHub Actions workflow for pipeline validation

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-20-ci-pipeline-validation` |
| **Base** | `main` - stacked on `gaurav/day-19-alert-monitoring` (merge PR 19 first) |
| **Roadmap** | Day 22 (Tue 18 Aug 2026) - *Set up GitHub Actions for pipeline validation.* |
| **Type** | `ci` |
| **Size** | 4 code files, +195 / -0 lines (docs excluded) |

## Summary

Adds `python -m pipeline validate` - schema contracts, data-dictionary drift and SQL-vs-Python reconciliation in one command - and a GitHub Actions workflow that runs it plus the test suite on every pipeline-related PR.

## Why

- A bad data drop or a cleaning regression should fail a PR, not a demo.

## What changed

- `pipeline/validate.py` with `StepResult`, `--json` output, and early exit when contracts fail.
- `.github/workflows/pipeline-validation.yml` (path-filtered, read-only permissions).
- A test ensures workflows only call real `python -m pipeline` commands. `tests/test_validate.py`: 5 tests.

## How to test

```bash
python -m pipeline validate
pytest tests/test_validate.py
```

## Result

PASS contracts, PASS data_dictionary, PASS sql_python_reconciliation (26 checks agree).

## Diff highlight

`pipeline/validate.py` (excerpt)

```diff
+def run_validation(settings: Settings | None = None) -> list[StepResult]:
+    try:
+        frames = load_frames(settings)
+    except (FileNotFoundError, ValueError) as exc:
+        return [StepResult("contracts", False, [str(exc)])]
+
+    issues = validate_datasets(frames)
+    errors = [i for i in issues if i.severity == "error"]
+    results = [StepResult("contracts", not errors, [str(i) for i in issues] or ["all datasets match"])]
+    if errors:
+        return results
+
+    drift = drift_problems(frames["onboarding"])
+    results.append(StepResult("data_dictionary", not drift, drift or ["dictionary and dataset agree"]))
+    results.append(_reconciliation(frames, settings))
+    return results
+
+
+def main(argv: list[str] | None = None) -> int:
+    parser = argparse.ArgumentParser(prog="python -m pipeline validate")
+    parser.add_argument("--json", type=Path, help="also write the results to this JSON file")
+    args = parser.parse_args(argv)
+
+    results = run_validation()
+    passed = all(r.passed for r in results)
+    for result in results:
+        print(f"{'PASS' if result.passed else 'FAIL'}  {result.name}")
+        for detail in result.details:
+            print(f"      {detail}")
+    if args.json:
+        payload = {"passed": passed, "steps": [asdict(r) for r in results]}
+        args.json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
+    return 0 if passed else 1
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `.github/workflows/pipeline-validation.yml` | 53 | 0 |
| `pipeline/__main__.py` | 2 | 0 |
| `pipeline/validate.py` | 84 | 0 |
| `tests/test_validate.py` | 56 | 0 |
| `docs/prs/gaurav/day-20-ci-pipeline-validation.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
