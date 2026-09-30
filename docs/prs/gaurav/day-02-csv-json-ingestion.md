# Day 02 - Add CSV / JSON / JSON-lines ingestion for the onboarding dataset

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-02-csv-json-ingestion` |
| **Base** | `main` - stacked on `gaurav/day-01-workspace-setup` (merge PR 01 first) |
| **Roadmap** | Day 2 (Wed 29 Jul 2026) - *Write ingestion scripts for CSV/JSON files (onboarding dataset).* |
| **Type** | `feat` |
| **Size** | 2 code files, +185 / -0 lines (docs excluded) |

## Summary

Adds `pipeline/ingest.py`: one loader for CSV, JSON (bare array or Supabase-style `{"data": [...]}`) and JSON-lines files, returning the DataFrame plus an `IngestionReport` (rows, columns, SHA-256).

## Why

- Supabase / REST exports arrive as JSON while the repo ships CSVs; both must load the same way.
- The checksum gives every later export a provenance trail back to the exact input file.

## What changed

- `read_table()` - fails loudly on missing files, unsupported types, malformed JSON and empty files.
- `resolve_source()` - picks `data/<name>.csv`, then `.json`, then `.jsonl`.
- `load_dataset()` / `load_onboarding()` and a CLI: `python -m pipeline.ingest onboarding`.
- `tests/test_ingest.py`: 8 tests.

## How to test

```bash
pytest tests/test_ingest.py
python -m pipeline.ingest onboarding
```

## Result

The committed onboarding CSV loads as 1,470 rows x 9 columns; JSON and JSONL fixtures load identically.

## Diff highlight

`pipeline/ingest.py` (excerpt)

```diff
+def read_table(path: str | Path) -> pd.DataFrame:
+    """Read one CSV / JSON / JSONL file into a DataFrame, failing loudly on bad input."""
+    path = Path(path)
+    if not path.is_file():
+        raise FileNotFoundError(f"Dataset file not found: {path}")
+    suffix = path.suffix.lower()
+    if suffix not in SUPPORTED_SUFFIXES:
+        raise ValueError(f"Unsupported file type {suffix!r} for {path.name}; "
+                         f"expected one of {', '.join(SUPPORTED_SUFFIXES)}")
+    frame = pd.read_csv(path) if suffix == ".csv" else pd.DataFrame.from_records(_json_records(path))
+    if frame.empty:
+        raise ValueError(f"{path.name} contains no rows")
+    return frame
+
+
+def resolve_source(dataset: str, settings: Settings) -> Path:
+    """Find the first existing file for ``dataset`` in the data folder."""
+    candidates = [settings.dataset_path(dataset, suffix) for suffix in SUPPORTED_SUFFIXES]
+    for candidate in candidates:
+        if candidate.is_file():
+            return candidate
+    raise FileNotFoundError(f"No file for dataset {dataset!r}; looked for: "
+                            + ", ".join(c.name for c in candidates) + f" in {settings.data_dir}")
+
+
+def load_dataset(dataset: str, source: str | Path | None = None,
+                 settings: Settings | None = None) -> tuple[pd.DataFrame, IngestionReport]:
+    """Load a named dataset and return it with a provenance report."""
+    if dataset not in DATASETS:
+        raise KeyError(f"Unknown dataset {dataset!r}; expected one of: {', '.join(DATASETS)}")
+    path = Path(source) if source else resolve_source(dataset, settings or load_settings())
+    frame = read_table(path)
+    report = IngestionReport(
+        dataset=dataset,
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `pipeline/ingest.py` | 118 | 0 |
| `tests/test_ingest.py` | 67 | 0 |
| `docs/prs/gaurav/day-02-csv-json-ingestion.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
