# Day 25 - Bug fixes: clean CLI errors, Supabase row cap, optional supabase; project documentation

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-25-bug-fixes` |
| **Base** | `main` - stacked on `gaurav/day-24-finalise-workflows` (merge PR 24 first) |
| **Roadmap** | Day 28 (Mon 24 Aug 2026) - *Bug fixes.* |
| **Type** | `fix` |
| **Size** | 6 code files, +243 / -13 lines (docs excluded) |

## Summary

Fixes three real defects and hands over the project documentation.

## Why

- **Pipeline CLI** - `alerts`, `reconcile`, `rankings` and `kpis` crashed with raw tracebacks on missing data or an unreachable DB. They now print one line and exit 1 (`VIBECHECK_DEBUG=1` keeps the traceback).
- **Backend: silently truncated data** - Supabase/PostgREST returns at most 1,000 rows per select, so `tool_usage` (7,810 rows) was cut to 1,000. Reads are now paginated.
- **Backend: crash without supabase** - `supabase` was imported at module level, so the whole API failed to start without that optional package. The import is now lazy; empty responses and fetch errors fall back to CSV *with a logged warning*.
- `backend/requirements.txt` was missing (AUDIT B2).

## What changed

- `pipeline/__main__.py` error handling; `tests/test_cli_errors.py` (8 tests - 5 fail without the fix).
- `backend/api/utils.py` rewrite; 5 new Django tests with a fake Supabase client (no network).
- `backend/requirements.txt` and `.github/workflows/backend-tests.yml`.
- `docs/PROJECT_DOCUMENTATION.md` (whole project) and a README section for the pipeline.

## How to test

```bash
pytest
cd backend && python manage.py test api
```

## Result

179 pipeline tests + 10 Django tests pass. With the old `utils.py` the API cannot even import (`No module named 'supabase'`).

## Diff highlight

`backend/api/utils.py` (excerpt)

```diff
+def _fetch_all_rows(table_name: str) -> list:
+    table = get_supabase_client().table(table_name)
+    rows, start = [], 0
+    while True:
+        page = table.select("*").range(start, start + PAGE_SIZE - 1).execute().data or []
+        rows.extend(page)
+        if len(page) < PAGE_SIZE:
+            return rows
+        start += PAGE_SIZE
+
+
+def _read_local_csv(table_name: str) -> pd.DataFrame:
+    csv_path = os.path.join(DATA_DIR, f'{table_name}.csv')
+    if not os.path.exists(csv_path):
+        raise FileNotFoundError(
+            f"No data for '{table_name}': Supabase is unavailable and {csv_path} is missing. "
+            f"Restore it with `git checkout -- data/{table_name}.csv`."
+        )
+    return pd.read_csv(csv_path)
+
 
 def fetch_table_as_df(table_name: str) -> pd.DataFrame:
+    """Read a table from Supabase when configured, otherwise from data/<table>.csv."""
+    if not supabase_configured():
+        return _read_local_csv(table_name)
     try:
-        client = get_supabase_client()
-        response = client.table(table_name).select("*").execute()
-        return pd.DataFrame(response.data)
+        rows = _fetch_all_rows(table_name)
+        if not rows:
+            raise ValueError(f"Supabase returned no rows for '{table_name}'")
+        return pd.DataFrame(rows)
     except Exception:
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `.github/workflows/backend-tests.yml` | 46 | 0 |
| `backend/api/tests.py` | 62 | 0 |
| `backend/api/utils.py` | 52 | 12 |
| `backend/requirements.txt` | 18 | 0 |
| `pipeline/__main__.py` | 21 | 1 |
| `tests/test_cli_errors.py` | 44 | 0 |
| `docs/prs/gaurav/day-25-bug-fixes.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
