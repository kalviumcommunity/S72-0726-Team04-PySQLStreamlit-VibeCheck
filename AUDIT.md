# VibeCheck — Code Audit & Fix Report

**Project:** S72-0726-Team04-PySQLStreamlit-VibeCheck
**Team:** Ayush · Gaurav · Vedant
**Date:** 20 August 2026

**Verdict going in:** the project did not run. The frontend could not build at all (a whole directory of imported modules was missing), the backend had no dependency manifest, and the ML model silently failed to load — so the dashboard was quietly reporting a 0% risk score for all 1,470 employees.

**Verdict going out:** backend runs with 14 passing tests, frontend builds and lints clean, the ML pipeline runs end-to-end from notebook 01 to 06, and the friction score now produces an actionable list instead of a wall of 100s.

---

## Severity summary

| Severity | Count | Meaning |
| :--- | :--- | :--- |
| 🔴 Blocker | 4 | Project does not run or build |
| 🟠 Correctness | 9 | Runs, but produces wrong or misleading output |
| 🟡 Robustness | 6 | Fails badly on the unhappy path |
| 🔵 Security | 4 | Unsafe defaults for anything beyond localhost |
| ⚪ Hygiene | 6 | Docs, tests, repo cleanliness |
| | **29** | |

---

## 🔴 Blockers

### B1 — `frontend/src/lib/` did not exist
`page.tsx` imported `@/lib/api`, and all four shadcn UI components imported `cn` from `@/lib/utils`. Neither file was in the repo. `next build` failed immediately; `npm run dev` served a runtime error page.

**Fixed:** created `src/lib/utils.ts` (the `cn` helper) and `src/lib/api.ts` — a typed client with interfaces for every payload, a configurable base URL, and a real error type.

### B2 — `backend/requirements.txt` did not exist
The README's setup instructions (`pip install -r requirements.txt`) failed on a fresh clone. Worse, `api/utils.py` imported `supabase` at module scope, so a missing optional dependency took down the whole Django app.

**Fixed:** added `backend/requirements.txt` with every dependency pinned — including `xgboost`, which was needed to unpickle the model but appeared nowhere in the project. `supabase` is now imported lazily inside the function that uses it.

### B3 — `next build` failed on the `tw-animate-css` import
`globals.css` did `@import "tw-animate-css"`. That package declares only a `"style"` export condition, which Turbopack's CSS resolver ignores, and its `exports` map blocks the deep path — so both the bare specifier and `tw-animate-css/dist/tw-animate.css` fail with "Module not found".

**Fixed:** imported via relative path, with a comment explaining why. (A `turbopack.resolveAlias` in `next.config.ts` was tried first; it does not apply to CSS imports.)

### B4 — Missing `__init__.py` / migrations package
`backend/api/__init__.py`, `backend/config/__init__.py` and `backend/api/migrations/__init__.py` were empty files that had not survived; without them Django cannot import the app package and `manage.py test` dies with a relative-import error.

**Fixed:** restored.

---

## 🟠 Correctness

### C1 — The friction score was unbounded, then clipped, so almost everyone scored 100
```python
friction_score = (ticket_count * 10) + (avg_resolution * 2) - (training_completion_percent * 0.5)
friction_score = friction_score.clip(0, 100)
```
`avg_resolution` is in hours and unbounded — a single Critical ticket can take 72 hours. That one term contributes 144 points on its own, swamping everything else. The top-ranked "high-friction" employee in the live output was **#1607, with 91.7% training completion and one ticket**, pinned to 100.0.

**Fixed:** a weighted composite of three normalised signals, bounded to 0–100 by construction (weights sum to 1.0), with no clipping:

| Component | Weight | Saturates at |
| :--- | :--- | :--- |
| Outstanding training (`100 − training%`) | 50% | — (already 0–100) |
| Ticket volume | 30% | 5 tickets |
| Avg resolution time | 20% | 48 hours |

The worst employee is now **#1111 — 15.2% training, 3 tickets, status Delayed, score 62.2**, which is the answer a human would give.

### C2 — The `> 70` threshold could never fire on the corrected scale
Once the score was no longer clipped to 100, the observed distribution was median 8.5, p90 23.5, max 62.2. Nothing crossed 70, so the alert banner would never appear and the intervention grid would always be empty.

**Fixed:** recalibrated to `HIGH_FRICTION_THRESHOLD = 40` / `MEDIUM = 25`, chosen against the actual distribution. That flags 17 employees — **and all 17 are new hires**, which is a good independent sanity check on the metric. Both thresholds are returned by the API so the frontend never hard-codes them. A regression test asserts the threshold selects a non-empty, non-trivial set.

### C3 — "Avg Tickets per Hire" was computed over the entire company
```python
new_hire_ids = df_onb['employee_id'].unique()   # all 1,470 employees
```
Every employee has an onboarding row, so the "new hire" filter selected everyone. The KPI labelled *per hire* was a company-wide average: **0.6 tickets**.

**Fixed:** defined the cohort explicitly (`YearsAtCompany <= 1` **or** onboarding status In Progress/Delayed) — 215 people. The real figure is **1.5 tickets per new hire**, 2.5× the number being displayed. `avg_onboarding_days` moved from 12.1 to 15.0 for the same reason.

### C4 — The ML model failed silently and the dashboard showed "ML Risk: 0.0%"
```python
except Exception as e:
    print(f"Error loading ML model: {e}")
    ml_predictions = pd.DataFrame(columns=['employee_id', 'predicted_risk'])
```
Combined with `.fillna({'predicted_risk': 0})` downstream and `emp.predicted_risk !== undefined` in the card component, a failed model load rendered as a confident **0% risk for every employee**. On a clean environment this fired immediately, because `xgboost` was not a declared dependency.

**Fixed:** the loader logs through Django's logging config instead of `print`, `predicted_risk` stays `null` rather than becoming 0, the API reports `ml_model_available`, and the frontend hides the badges and shows an explicit warning banner when the model is unavailable.

### C5 — The high-risk count only counted the returned page
The API returned `merged.head(100)`; the frontend then computed `employees.filter(e => e.friction_score > 70).length`. Any high-risk employee ranked 101st or lower was invisible to the count.

**Fixed:** `total_high_risk` is computed server-side over the whole dataset and returned alongside the page.

### C6 — The "High-Friction Employees" grid ignored the threshold
```js
const topHighRiskEmployees = employees.slice(0, 6);
```
The first six rows were always shown under a "requiring immediate intervention" heading — even when nobody was above the threshold. With the score fixed, that would label six perfectly healthy hires as emergencies.

**Fixed:** filters on the threshold first, and renders an explicit empty state when nobody qualifies.

### C7 — Scaler leakage inflated the reported model scores
Notebook 03 called `StandardScaler().fit_transform()` across the **entire** dataset before notebook 04 split it. Test-fold means and variances leaked into training.

**Fixed:** scaling moved into a `Pipeline(StandardScaler, model)` inside `RandomizedSearchCV`, so it is refit on every CV fold and on the training split only. `engineered_data.csv` is now saved unscaled (and is human-readable again). The saved artefact is the whole pipeline, so no consumer has to remember to scale its input.

### C8 — Model selection used the test set
Notebook 04 picked the winning model by comparing ROC-AUC **on the test set**, turning the held-out set into a second validation set and overstating the final number.

**Fixed:** selection is now by cross-validated training score (CV folds also raised 3 → 5); the test set is touched exactly once, after selection. Honest held-out result on the retrained model: **ROC-AUC 0.662, accuracy 0.629**.

### C9 — `early_unique_tools` counted unique *features*, not unique tools
```python
early_unique_tools=('feature_used', 'nunique')
```
The feature was named, and later interpreted in SHAP output, as a count of distinct tools adopted. It was actually counting distinct features used.

**Fixed:** `early_unique_tools` now aggregates `tool_name`; `early_unique_features` was added separately so no signal is lost. Both appear in the retrained model's importances.

---

## 🟡 Robustness

### R1 — A dead backend spun forever
`Promise.all([...]).then(...)` had no `.catch()`. Stop the Django server and the dashboard sat on "Loading insights..." indefinitely with no error, no retry, nothing in the UI.

**Fixed:** full error state with the actual failure message and a Try Again button; `AbortController` cancels in-flight requests on unmount.

### R2 — `fetch_table_as_df` swallowed every exception
A bare `except Exception` around the Supabase call meant an auth failure, a network timeout and a missing table all silently degraded to reading CSVs, with no log line. A misconfigured Supabase deployment would look like a working one.

**Fixed:** the fallback is logged with a stack trace; an empty Supabase response is treated as a failure (it used to return an empty DataFrame, which then blew up downstream on a missing-column `KeyError`); a missing CSV raises a message that says how to restore it.

### R3 — The API base URL was hard-coded
The missing `lib/api.ts` had to have pointed at a literal localhost URL. **Fixed:** `NEXT_PUBLIC_API_BASE_URL`, with `.env.local.example` committed.

### R4 — Blanket `.fillna(0)` coerced categorical columns
`pd.merge(...).fillna(0)` filled *every* column, so a missing `JobRole` or `Department` would silently become the integer `0`. **Fixed:** only the numeric count columns are zero-filled, in both `views.py` and notebook 02.

### R5 — Notebooks broke unless the CWD was exactly `ML model/`
Every path was relative (`'../data/employees.csv'`, `'master_data.csv'`). Running a notebook from the repo root — the normal thing to do in VS Code — failed with `FileNotFoundError`.

**Fixed:** a shared root-resolution cell walks up from the CWD to find `data/employees.csv`, and raises a clear message if it cannot.

### R6 — `next/font/google` needs network at build time
`layout.tsx` fetches Inter from Google Fonts during `next build`. On an offline or proxied build machine the build fails outright. Not changed (it works on a normal dev machine) but worth knowing before a CI run: switch to `next/font/local` if the build box is sandboxed.

---

## 🔵 Security

All four are in `backend/config/settings.py`, all four are the `django-admin startproject` defaults left untouched.

| Issue | Was | Now |
| :--- | :--- | :--- |
| **S1** Secret key committed to git | Literal `'django-insecure-&$p1z4@uk…'` in the repo | Read from `DJANGO_SECRET_KEY`; start-up **fails** if unset when `DEBUG=False`; insecure fallback only in debug |
| **S2** `DEBUG = True` hard-coded | Always on — full tracebacks and settings to any visitor | `DJANGO_DEBUG` env var |
| **S3** `ALLOWED_HOSTS = ['*']` | Accepts any Host header → cache poisoning, forged password-reset links | `DJANGO_ALLOWED_HOSTS`, defaults to localhost, required when not in debug |
| **S4** `CORS_ALLOW_ALL_ORIGINS = True` | **Any website on the internet** could read this API from a logged-in visitor's browser | `CORS_ALLOWED_ORIGINS`, defaults to the two dashboard origins |

Also added: a `LOGGING` config so warnings surface in the console, and `.env.example` documenting every variable. `.gitignore` now covers `db.sqlite3` (which is committed to the repo) and `.env.local`.

---

## ⚪ Hygiene

- **H1 — Zero tests.** `api/tests.py` was the scaffold comment. Added **14 tests**: friction-score bounds and ordering, a direct regression test for the C1 employee (#1607-style: 91.7% training must *not* be high-friction), new-hire cohort logic, Yes/No parsing, and endpoint contract tests covering payload shape, sort order, chronological dates, the department filter, and a 400 on a bad `limit`.
- **H2 — README described a project that didn't exist.** It referenced `src/lib/` (missing), `requirements.txt` (missing), and a root `.env` with no example. `data/README.md` still tells you to run `generate_datasets.py`, which is not in the repo. Rewrote the README: corrected friction-score maths, added an API reference table, honest ML performance numbers, and the test command.
- **H3 — `__pycache__/app.cpython-314.pyc` is committed at the repo root** — a compiled artefact of a deleted Streamlit `app.py`. `.gitignore` covers `__pycache__/`, but the file was tracked before that rule existed, so it persists. Run `git rm --cached "__pycache__/app.cpython-314.pyc"`.
- **H4 — The repo is named `PySQLStreamlit`** but contains no Streamlit and no SQL — it's Django + Next.js + pandas. Worth a note in the README so reviewers aren't confused.
- **H5 — `FrictionScatter` is a bar chart.** The component name and the README both said scatter plot. Kept the bar chart (1,470 overlapping points is unreadable) and corrected the docs; also removed a meaningless `dataKey="avg_tickets"` on a categorical `YAxis`.
- **H6 — Non-functional filter controls.** The "All Departments" and "Last 30 Days" dropdowns were decorative `<select>` elements with one hard-coded option. The department filter now works end-to-end (client-side filter plus a `?department=` query param on the API); the date filter was removed rather than left as a fake control.

---

## Analytical caveat worth putting on a slide

**The buddy-programme comparison is on wildly unbalanced groups.** In the dataset, **1,451 employees have a buddy and 19 do not**. The 89.4% vs 55.5% training-completion gap looks dramatic, but 19 people is not a sample you can draw a causal conclusion from. The chart now displays both group sizes and a caution note. This isn't a code bug — it's a claim in the README that the data doesn't support.

Similarly: `time_to_value` is `avg_onboarding_days + 7`. The 7 is an assumption, not a measurement. It's now named `RAMP_UP_DAYS`, commented as an explicit business assumption, and labelled as such in the UI.

---

## Verification performed

| Check | Result |
| :--- | :--- |
| `python manage.py test api` | **14 passed** |
| All three endpoints against the real CSVs | 200, sane values |
| `npx tsc --noEmit` | clean |
| `npx eslint .` | clean (0 errors, 0 warnings) |
| `npx next build` | succeeds |
| Notebooks 01 → 06 executed end-to-end | all pass; artefacts regenerated |

Regenerated ML artefacts: `best_model.pkl` (now a Pipeline), `engineered_data.csv` (unscaled), `master_data.csv`, `risk_scores.csv`, `X_test.csv`, `y_test.csv`, `test_employee_ids.csv`, `feature_importance.csv`, `shap_summary.png`.
