# Day 24 - Finalise GitHub workflows: test matrix, MySQL job, scheduled report

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-24-finalise-workflows` |
| **Base** | `main` - stacked on `gaurav/day-23-e2e-pipeline-tests` (merge PR 23 first) |
| **Roadmap** | Day 26 (Sat 22 Aug 2026) - *Finalise GitHub workflows.* |
| **Type** | `ci` |
| **Size** | 8 code files, +306 / -8 lines (docs excluded) |

## Summary

Completes CI and automation. Adds a Python 3.10 / 3.12 / 3.13 test matrix (covers pandas 2.x and 3.x), a job that runs every SQL query on a real MySQL 8.4 service container, and a weekday scheduled report that uploads the outputs and writes a job summary. Also adds a team PR template.

## Why

- The SQL layer targets MySQL, so it must be tested on MySQL, not only on SQLite.

## What changed

- `tests/test_mysql_integration.py`: every query must match SQLite and reconcile with Python (skipped unless `VIBECHECK_TEST_MYSQL_URL` is set).
- `PyMySQL[rsa]`: MySQL 8's default `caching_sha2_password` auth needs `cryptography`.
- `python -m pipeline summary`: ASCII Markdown for `$GITHUB_STEP_SUMMARY`.
- `onboarding-report.yml`: 09:00 IST Mon-Fri; alerts firing does not hide the report. `tests/test_ci_summary.py`: 3 tests.

## How to test

```bash
pytest
python -m pipeline summary --validation validation.json
```

## Result

Local: 171 passed, 9 skipped (MySQL). All SQL files parse under the MySQL and SQLite dialects. The MySQL job itself runs on GitHub; it could not run locally (no Docker engine).

## Diff highlight

`.github/workflows/pipeline-validation.yml` (excerpt)

```diff
+concurrency:
+  group: ${{ github.workflow }}-${{ github.ref }}
+  cancel-in-progress: true
+
 jobs:
   validate:
-    name: Validate data and test the pipeline
+    name: Validate datasets
     runs-on: ubuntu-latest
-    timeout-minutes: 15
+    timeout-minutes: 10
     steps:
       - uses: actions/checkout@v5
-
       - uses: actions/setup-python@v6
         with:
           python-version: "3.12"
           cache: pip
           cache-dependency-path: requirements-pipeline.txt
-
       - name: Install pipeline dependencies
         run: pip install -r requirements-pipeline.txt
-
       - name: Validate datasets (contracts, data dictionary, SQL vs Python)
-        run: python -m pipeline validate
+        run: python -m pipeline validate --json validation.json
+      - name: Publish validation summary
+        if: always()
+        run: python -m pipeline summary --validation validation.json >> "$GITHUB_STEP_SUMMARY"
 
-      - name: Run pipeline tests
+  test:
+    name: Tests (Python ${{ matrix.python-version }})
+    runs-on: ubuntu-latest
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `.github/pull_request_template.md` | 15 | 0 |
| `.github/workflows/onboarding-report.yml` | 65 | 0 |
| `.github/workflows/pipeline-validation.yml` | 62 | 7 |
| `pipeline/__main__.py` | 2 | 0 |
| `pipeline/ci_summary.py` | 80 | 0 |
| `pytest.ini` | 1 | 0 |
| `requirements-pipeline.txt` | 1 | 1 |
| `tests/test_ci_summary.py` | 44 | 0 |
| `tests/test_mysql_integration.py` | 51 | 0 |
| `docs/prs/gaurav/day-24-finalise-workflows.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
