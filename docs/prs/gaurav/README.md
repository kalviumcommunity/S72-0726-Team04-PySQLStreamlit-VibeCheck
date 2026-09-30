# Gaurav - day-wise PRs

Owner of data ingestion and cleaning, the SQL layer, pipeline automation, GitHub workflows and the
Onboarding Ops console (roadmap: *Gaurav -> data ingestion, cleaning, pipeline automation, GitHub workflows*).

Branches are **stacked**: each `day-NN` branch is built on `day-(NN-1)`. Open the PRs against `main` and merge
them in order with **Create a merge commit** so every later PR shows only its own day's diff.

| PR | Branch | Roadmap day | Title | Doc |
| :---: | :--- | :---: | :--- | :---: |
| 01 | `gaurav/day-01-workspace-setup` | 1 | Set up the Python pipeline workspace and fix the repo-wide lib/ ignore rule | [doc](day-01-workspace-setup.md) |
| 02 | `gaurav/day-02-csv-json-ingestion` | 2 | Add CSV / JSON / JSON-lines ingestion for the onboarding dataset | [doc](day-02-csv-json-ingestion.md) |
| 03 | `gaurav/day-03-onboarding-cleaning` | 3 | Add reusable cleaning functions for onboarding data | [doc](day-03-onboarding-cleaning.md) |
| 04 | `gaurav/day-04-type-standardisation` | 4 | Standardise onboarding dates, Yes/No flags and status categories | [doc](day-04-type-standardisation.md) |
| 05 | `gaurav/day-05-data-dictionary` | 5 | Add a code-backed data dictionary for onboarding fields | [doc](day-05-data-dictionary.md) |
| 06 | `gaurav/day-06-completion-outliers` | 6 | Detect outliers in onboarding completion times (IQR and MAD) | [doc](day-06-completion-outliers.md) |
| 07 | `gaurav/day-07-schema-contracts` | 7 | Team sync: shared schema contracts and join strategy for all four datasets | [doc](day-07-schema-contracts.md) |
| 08 | `gaurav/day-08-merge-tool-usage` | 8 | Merge onboarding with tool usage and validate the join | [doc](day-08-merge-tool-usage.md) |
| 09 | `gaurav/day-09-feature-engineering` | 9 | Engineer onboarding features (days to complete, speed bucket, new-hire flag) | [doc](day-09-feature-engineering.md) |
| 10 | `gaurav/day-10-completion-distribution` | 10 | Distribution analysis of onboarding completion times | [doc](day-10-completion-distribution.md) |
| 11 | `gaurav/day-11-fast-vs-slow-behaviour` | 11 | Behavioural analysis of new hires: fast vs slow onboarders | [doc](day-11-fast-vs-slow-behaviour.md) |
| 12 | `gaurav/day-12-delay-root-causes` | 12 | Root-cause investigation for delayed onboarding | [doc](day-12-delay-root-causes.md) |
| 13 | `gaurav/day-13-sql-onboarding-kpis` | 13 | SQL layer: MySQL-ready engine and onboarding KPI queries | [doc](day-13-sql-onboarding-kpis.md) |
| 14 | `gaurav/day-14-sql-window-rankings` | 15 | Rank hires by onboarding speed with SQL window functions | [doc](day-14-sql-window-rankings.md) |
| 15 | `gaurav/day-15-sql-python-reconciliation` | 16 | Validate SQL outputs against the Python pipeline | [doc](day-15-sql-python-reconciliation.md) |
| 16 | `gaurav/day-16-kpi-cards` | 17 | Onboarding KPI cards and the Streamlit Onboarding Ops page | [doc](day-16-kpi-cards.md) |
| 17 | `gaurav/day-17-export-datasets-charts` | 18 | Export cleaned datasets, analysis tables and charts with a manifest | [doc](day-17-export-datasets-charts.md) |

Compare link pattern: `https://github.com/kalviumcommunity/S72-0726-Team04-PySQLStreamlit-VibeCheck/compare/main...<branch>`
