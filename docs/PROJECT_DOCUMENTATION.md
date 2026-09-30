# VibeCheck — Project Documentation

**Operational Data & Onboarding Analytics** · Kalvium S72 · Team 04 — Aayush, Gaurav, Vedant

> Leadership has no visibility into which operational friction points slow down new-hire productivity in their
> first month. VibeCheck combines HR data, onboarding checklists, internal tool usage and IT support tickets to
> show *who* is struggling, *why*, and *what to do next*.

---

## 1. At a glance

| | |
| :--- | :--- |
| **Users** | Leadership, HR/onboarding team, IT helpdesk |
| **Data** | 4 datasets, 1,470 employees, ~7,800 tool-usage logs, ~890 support tickets (`data/`) |
| **Interfaces** | Next.js dashboard (via the Django API) · Streamlit *Onboarding Ops* console · CLI · scheduled report |
| **Stack** | Python 3.10+, pandas, SQLAlchemy (MySQL 8 / SQLite), Streamlit, Plotly · Django REST Framework · Next.js · XGBoost |
| **Quality gates** | ~200 automated tests (179 pipeline, 9 MySQL, 10 API), schema contracts, SQL-vs-Python reconciliation, GitHub Actions |

### Key findings (committed data)

- **97.5%** of hires completed onboarding; completed onboardings take a median **12 days** (90% within 17).
- **37 open onboardings** (23 In Progress, 14 Delayed) — all of them new hires; **33** raise a high-severity alert.
- **Every new hire without a manager is Delayed** (7 of 7, 100% vs 3%, 29.7× lift).
- Low tool engagement is the widest signal: the bottom quartile of tool minutes covers **93%** of delayed hires (38.8× lift).
- Slow onboarders complete less training (Cohen's d −0.57) and spend fewer minutes on every tool except Slack.
- Job level is *not* a driver (1.05×). The buddy comparison is indicative only — just 19 of 1,470 hires have no buddy.

---

## 2. Architecture

```
                     ┌───────────────────────── data/ (CSV snapshots) ─────────────────────────┐
                     │ employees · onboarding · tool_usage · support_tickets                    │
                     └───────────────┬───────────────────────────────┬──────────────────────────┘
                                     │                               │  (optional) Supabase REST
               ┌─────────────────────▼────────────┐        ┌─────────▼──────────────┐
               │ pipeline/ (Python data pipeline) │        │ backend/ (Django API)  │
               │ ingest → clean → standardise     │        │ /api/kpis /charts      │
               │ → contracts → merge → features   │        │ /employees[/id]        │
               │ → analysis · alerts · export     │        └─────────┬──────────────┘
               │ SQL layer: MySQL 8 / SQLite      │                  │ JSON
               └──────┬───────────────┬───────────┘        ┌─────────▼──────────────┐
                      │               │                    │ frontend/ (Next.js)    │
        ┌─────────────▼──────┐  ┌─────▼──────────────┐     │ leadership dashboard   │
        │ streamlit_app/     │  │ outputs/ + CI      │     └────────────────────────┘
        │ Onboarding Ops     │  │ exports, manifest, │
        │ (ops console)      │  │ alerts, summaries  │     ML model/ (notebooks 01–06)
        └────────────────────┘  └────────────────────┘     → risk_scores.csv, best_model.pkl
```

| Layer | Folder | Owner | Purpose |
| :--- | :--- | :--- | :--- |
| Data | `data/` | Vedant (generation) | Source datasets and the ERD (`data/README.md`) |
| Data pipeline + SQL | `pipeline/` | Gaurav | Ingestion, cleaning, contracts, features, analysis, SQL KPIs, alerts, exports |
| Ops console | `streamlit_app/` | Gaurav | KPI cards, cohort filters, root causes, live alerts |
| API | `backend/` | Aayush (+ Gaurav: audit & fixes) | Django REST endpoints consumed by the frontend |
| Dashboard | `frontend/` | Aayush | Next.js leadership dashboard |
| ML | `ML model/` | Aayush | High-friction classifier and risk scores |
| Automation | `.github/` | Gaurav | Validation, tests (incl. MySQL), backend tests, scheduled report |

---

## 3. Data

Four datasets joined on `employee_id` (full schema and ERD: [`data/README.md`](../data/README.md); field meanings:
[`docs/data_dictionary/onboarding.md`](data_dictionary/onboarding.md)).

| Dataset | Grain | Rows | Key |
| :--- | :--- | ---: | :--- |
| `employees` | one row per employee | 1,470 | `employee_id` |
| `onboarding` | one row per employee (1:1) | 1,470 | `employee_id` |
| `tool_usage` | employee × tool × day (1:N) | 7,810 | `usage_id` |
| `support_tickets` | one row per ticket (1:N) | 890 | `ticket_id` |

**Join strategy (agreed at the week-1 sync):** 1:N tables are aggregated per employee *before* joining, and every
join is validated one-to-one, so row counts never fan out. Contracts live in `pipeline/schemas.py`.

**Cohort definition:** a *new hire* has ≤ 1 year tenure **or** an onboarding still In Progress / Delayed (215 people).
The same definition is used by the Python features, the SQL `new_hire_cohort` query and the API audit.

---

## 4. Data pipeline (`pipeline/`)

| Stage | Module | What it does |
| :--- | :--- | :--- |
| Config | `config.py` | Resolves repo root, `VIBECHECK_DATA_DIR`, `VIBECHECK_OUTPUT_DIR` |
| Ingest | `ingest.py` | CSV / JSON / JSONL loader with row counts and SHA-256 provenance |
| Clean | `cleaning.py` | Column names, whitespace, invalid IDs, out-of-range values (nulled, not clipped), duplicates |
| Standardise | `standardize.py` | Nullable booleans, strict ISO dates, ordered status categories |
| Document | `data_dictionary.py` | Field meanings in code; `--check` detects drift |
| Contracts | `schemas.py` | Keys, required/numeric columns and foreign keys for all four datasets |
| Outliers | `outliers.py` | IQR and MAD fences, per department with small-group fallback |
| Merge | `merge.py` | Per-employee tool aggregates, validated 1:1 join, `JoinReport` |
| Features | `features.py` | Days to complete, speed bucket, setup completeness, `is_new_hire`; `build_feature_table()` |
| Analysis | `analysis/` | Completion-time distribution, fast vs slow behaviour, delay root causes |
| KPIs | `kpis.py` | pandas KPIs (same names as the SQL aliases) for any cohort |
| SQL | `db.py`, `sql_queries.py`, `rankings.py`, `sql/` | MySQL/SQLite engine, KPI queries, window-function rankings |
| Reconcile | `reconcile.py` | SQL (raw tables) vs Python (clean frames): 26 checks |
| Alerts | `alerts.py` | 7 severity-ranked rules for open onboardings |
| Export | `export.py` | Clean data, analysis tables, Plotly charts, `manifest.json` |
| Validate | `validate.py` | Contracts + dictionary + reconciliation in one command |
| CI summary | `ci_summary.py` | Markdown for `$GITHUB_STEP_SUMMARY` |

### Command line

```bash
python -m pipeline validate            # contracts, data dictionary, SQL vs Python
python -m pipeline export              # outputs/: clean data, analysis, charts, manifest
python -m pipeline alerts --fail-on high
python -m pipeline kpis kpis/overall --stage
python -m pipeline rankings --stage --top 3
python -m pipeline reconcile
python -m pipeline --help              # every command
```

Errors (missing data, unreachable database) print one line and exit 1; set `VIBECHECK_DEBUG=1` for the traceback.

### SQL layer (MySQL)

- `VIBECHECK_DB_URL=mysql+pymysql://user:password@host:3306/vibecheck` targets the team MySQL; unset, a local SQLite
  file under `outputs/` is used. Passwords are masked in all output.
- Queries in `pipeline/sql/kpis/` and `pipeline/sql/rankings/` are portable across MySQL 8 and SQLite 3.25+
  (CTEs, `CASE`, `RANK`/`DENSE_RANK`/`NTILE`/`PERCENT_RANK`/`LAG`, `ROWS BETWEEN`; no engine-specific date functions).
- `--stage` loads the CSVs **only into local SQLite**; it refuses to overwrite tables in a shared database.

---

## 5. Onboarding Ops console (`streamlit_app/`)

```bash
streamlit run streamlit_app/onboarding_ops.py
```

| Tab | Answers | Content |
| :--- | :--- | :--- |
| Overview | Are we on target? | 6 KPI cards with target tone and delta vs company, 2 charts |
| Cohort | Who is in this group? | Department KPIs, hires sorted most-urgent first |
| Root causes | Why are hires delayed? | Plain-English findings and lift chart (company-wide) |
| Alerts | Who needs help today? | Severity counters, filters, alert list, CSV download |

Sidebar filters: new hires only, department, status, tenure band, buddy. Layout rationale:
[`docs/ux/onboarding-ops-wireframe.md`](ux/onboarding-ops-wireframe.md).

---

## 6. Django API and Next.js dashboard

| Endpoint | Returns |
| :--- | :--- |
| `GET /api/kpis/` | Average onboarding days, time-to-value, average tickets |
| `GET /api/charts/` | Friction bars, top IT blockers, tool adoption, buddy impact |
| `GET /api/employees/` | Employees ranked by friction score, with ML risk |
| `GET /api/employees/<id>/` | One employee with tickets and tool usage |

Data comes from Supabase when `SUPABASE_URL` / `SUPABASE_ANON_KEY` are set (paginated past the 1,000-row cap) and
from `data/*.csv` otherwise; every fallback is logged. The Next.js app (`frontend/`) reads
`NEXT_PUBLIC_API_BASE_URL`. Known correctness issues in the friction score and KPIs, and their proposed fixes, are
catalogued in [`AUDIT.md`](../AUDIT.md).

## 7. ML model

Notebooks `ML model/01…06` go from EDA to a scoring pipeline: a high-friction classifier (XGBoost) with SHAP
interpretation, producing `risk_scores.csv` and `best_model.pkl`. The API uses the model when `xgboost` is
installed and otherwise falls back to the precomputed risk scores.

---

## 8. Setup

```bash
# Pipeline + Streamlit (Python 3.10+)
pip install -r requirements-pipeline.txt
pytest                                     # unit, dashboard and end-to-end tests
python -m pipeline validate
streamlit run streamlit_app/onboarding_ops.py

# API
cd backend && pip install -r requirements.txt && python manage.py test api && python manage.py runserver

# Frontend
cd frontend && npm install && npm run dev  # http://localhost:3000
```

| Variable | Used by | Default |
| :--- | :--- | :--- |
| `VIBECHECK_DATA_DIR` | pipeline | `<repo>/data` |
| `VIBECHECK_OUTPUT_DIR` | pipeline | `<repo>/outputs` (git-ignored) |
| `VIBECHECK_DB_URL` | SQL layer | local SQLite in the output folder |
| `VIBECHECK_TEST_MYSQL_URL` | `pytest -m mysql` | unset → MySQL tests skipped |
| `VIBECHECK_DEBUG` | pipeline CLI | unset → one-line errors |
| `SUPABASE_URL`, `SUPABASE_ANON_KEY` | backend | unset → CSV fallback |

---

## 9. Quality and automation

| Workflow | Trigger | Runs |
| :--- | :--- | :--- |
| `pipeline-validation.yml` | PRs / pushes touching the pipeline | `validate` + summary; tests on Python 3.10/3.12/3.13; every SQL query on MySQL 8.4 |
| `backend-tests.yml` | PRs / pushes touching `backend/`, `data/`, `ML model/` | `manage.py check` + API tests |
| `onboarding-report.yml` | 09:00 IST Mon–Fri, manual | validate → export → alerts → job summary + 14-day artifact |

Test markers: `pytest -m "not e2e"` for a quick run, `pytest -m e2e` for subprocess runs of the CLI,
`pytest -m mysql` with `VIBECHECK_TEST_MYSQL_URL` set.

---

## 10. Limitations and next steps

- The datasets are partly synthetic; findings are associations, not causal effects.
- The buddy comparison rests on 19 hires without a buddy — treat it as a hypothesis.
- The API's friction score and "per hire" KPI have documented issues (see `AUDIT.md`) awaiting a coordinated
  backend + frontend change.
- The MySQL CI job is designed but was not executed locally; confirm its first run on GitHub.

## 11. Team and PR log

Roadmap: 30 days (28 Jul – 26 Aug 2026). Per-PR documentation lives in [`docs/prs/`](prs/README.md).
