# Day 17 - Export cleaned datasets, analysis tables and charts with a manifest

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-17-export-datasets-charts` |
| **Base** | `main` - stacked on `gaurav/day-16-kpi-cards` (merge PR 16 first) |
| **Roadmap** | Day 18 (Fri 14 Aug 2026) - *Export cleaned datasets + charts.* |
| **Type** | `feat` |
| **Size** | 4 code files, +248 / -0 lines (docs excluded) |

## Summary

Adds `python -m pipeline export`. It writes the cleaned onboarding data, the feature table, four analysis tables, three interactive Plotly charts and a `manifest.json` linking input checksums to output rows and checksums. It also adds `pipeline/__main__.py`, one CLI for every pipeline command.

## Why

- Teammates (reporting, dashboard) need stable files instead of re-running notebooks.

## What changed

- `export_all()` and `build_charts()` (pure, reused by the dashboard).
- Deterministic CSVs (`\n` line endings, stable ordering) - re-running produces byte-identical files.
- `python -m pipeline <ingest|contracts|dictionary|kpis|rankings|reconcile|export>`.
- `tests/test_export.py`: 5 tests.

## How to test

```bash
python -m pipeline export --out outputs
pytest tests/test_export.py
```

## Result

Every manifest checksum matches the file on disk, and two runs produce identical CSVs.

## Diff highlight

`pipeline/export.py` (excerpt)

```diff
+def export_all(settings: Settings | None = None, out_dir: str | Path | None = None,
+               include_charts: bool = True) -> dict:
+    settings = settings or load_settings()
+    out = Path(out_dir or settings.output_dir)
+    frames, inputs = {}, []
+    for name in DATASETS:
+        frames[name], report = load_dataset(name, settings=settings)
+        inputs.append({"dataset": name, "file": report.source.name, "rows": report.rows, "sha256": report.sha256})
+
+    onboarding = prepare_onboarding(frames["onboarding"])
+    merged, join = merge_onboarding_tool_usage(onboarding, frames["tool_usage"])
+    features = engineer_features(merged, frames["employees"])
+    root_causes = rank_root_causes(features)
+    outliers = detect_completion_outliers(features, group_by="Department")
+
+    tables = {
+        "clean/onboarding_clean.csv": onboarding,
+        "clean/onboarding_features.csv": features,
+        "analysis/completion_time_distribution.csv": describe_completion_times(features, by="onboarding_status"),
+        "analysis/completion_time_histogram.csv": histogram(features),
+        "analysis/completion_outliers.csv": outliers[outliers["is_outlier"]],
+        "analysis/delay_root_causes.csv": root_causes,
+    }
+    outputs = []
+    for relative, frame in tables.items():
+        path = out / relative
+        path.parent.mkdir(parents=True, exist_ok=True)
+        frame.to_csv(path, index=False, lineterminator="\n")
+        outputs.append({"path": relative, "rows": len(frame), "sha256": _sha256(path)})
+    if include_charts:
+        for name, figure in build_charts(features, root_causes).items():
+            path = out / "charts" / f"{name}.html"
+            path.parent.mkdir(parents=True, exist_ok=True)
+            figure.write_html(path, include_plotlyjs="cdn")
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `pipeline/__main__.py` | 44 | 0 |
| `pipeline/export.py` | 134 | 0 |
| `requirements-pipeline.txt` | 1 | 0 |
| `tests/test_export.py` | 69 | 0 |
| `docs/prs/gaurav/day-17-export-datasets-charts.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
