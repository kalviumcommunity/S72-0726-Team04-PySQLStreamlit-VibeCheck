# Day 01 - Set up the Python pipeline workspace and fix the repo-wide lib/ ignore rule

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-01-workspace-setup` |
| **Base** | `main` |
| **Roadmap** | Day 1 (Tue 28 Jul 2026) - *Set up Python workspace, GitHub repo, and folder structure for the project.* |
| **Type** | `chore` |
| **Size** | 7 code files, +134 / -2 lines (docs excluded) |

## Summary

Creates the `pipeline/` package, pytest configuration and a single place (`pipeline/config.py`) where every path is resolved, so scripts, notebooks, tests and CI find `data/` no matter which directory they are started from.

## Why

- The previous notebooks broke unless the working directory was exactly `ML model/` (AUDIT R5).
- `.gitignore` contained an unanchored `lib/` rule that also matched `frontend/src/lib/` - that is why `api.ts` / `utils.ts` never reached git and the frontend build failed (AUDIT B1).

## What changed

- `pipeline/config.py`: `find_repo_root()`, `Settings`, `load_settings()` with `VIBECHECK_DATA_DIR` / `VIBECHECK_OUTPUT_DIR` overrides, shared `configure_logging()`.
- `requirements-pipeline.txt` and `pytest.ini` (`pythonpath = .` so `pytest` works from the repo root).
- `.gitignore`: `lib/` -> `/lib/` (root only), ignore `outputs/` and `.pytest_cache/`.
- `tests/test_config.py`: 6 tests (nested-directory lookup, helpful error, env overrides).

## How to test

```bash
pip install -r requirements-pipeline.txt
pytest tests/test_config.py
git check-ignore frontend/src/lib/api.ts   # prints nothing now
```

## Result

6 tests pass. `frontend/src/lib/` is no longer ignored, so the frontend's lib files can be committed.

## Diff highlight

`pipeline/config.py` (excerpt)

```diff
+def find_repo_root(start: Path | None = None) -> Path:
+    """Walk up from ``start`` until a directory containing data/employees.csv is found."""
+    here = (start or Path.cwd()).resolve()
+    for candidate in (here, *here.parents):
+        if (candidate / _ROOT_MARKER).is_file():
+            return candidate
+    raise FileNotFoundError(
+        f"Could not locate the VibeCheck repo root from {here}: no "
+        f"{_ROOT_MARKER.as_posix()} here or in any parent directory. "
+        "Set VIBECHECK_DATA_DIR to the folder that holds the datasets."
+    )
+
+
+@dataclass(frozen=True)
+class Settings:
+    data_dir: Path
+    output_dir: Path
+
+    def dataset_path(self, name: str, suffix: str = ".csv") -> Path:
+        if name not in DATASETS:
+            raise KeyError(f"Unknown dataset {name!r}; expected one of: {', '.join(DATASETS)}")
+        return self.data_dir / f"{name}{suffix}"
+
+
+def load_settings(env: Mapping[str, str] | None = None) -> Settings:
+    """Build settings from environment overrides, falling back to the repo layout.
+
+    VIBECHECK_DATA_DIR    folder with employees/onboarding/tool_usage/support_tickets files
+    VIBECHECK_OUTPUT_DIR  where exports and local databases are written (default: <root>/outputs)
+    """
+    env = os.environ if env is None else env
+    data_override = env.get("VIBECHECK_DATA_DIR")
+    if data_override:
+        data_dir = Path(data_override).expanduser().resolve()
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `.gitignore` | 9 | 2 |
| `pipeline/__init__.py` | 3 | 0 |
| `pipeline/config.py` | 63 | 0 |
| `pytest.ini` | 5 | 0 |
| `requirements-pipeline.txt` | 6 | 0 |
| `tests/conftest.py` | 9 | 0 |
| `tests/test_config.py` | 39 | 0 |
| `docs/prs/gaurav/day-01-workspace-setup.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
