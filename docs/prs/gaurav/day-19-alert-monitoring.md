# Day 19 - Alert monitoring for delayed onboarding

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-19-alert-monitoring` |
| **Base** | `main` - stacked on `gaurav/day-18-cohort-filters` (merge PR 18 first) |
| **Roadmap** | Day 20 (Sun 16 Aug 2026) - *Add alert monitoring (delayed onboarding).* |
| **Type** | `feat` |
| **Size** | 3 code files, +249 / -0 lines (docs excluded) |

## Summary

Adds `pipeline/alerts.py`: seven severity-ranked rules over open onboardings (Delayed, past the expected window, no manager, low training, no buddy, missed check-in, low tool activity) and `python -m pipeline alerts`.

## Why

- Delayed hires should be flagged the day they slip, not found in a monthly report.
- Thresholds come from the whole company (p90 = 17 days), so filtering a cohort never moves the goalposts.

## What changed

- `AlertRule`, `AlertContext`, `evaluate_alerts()`, `summarize_alerts()`, `employees_needing_attention()`.
- Completed hires never alert, however bad their history.
- `--fail-on high` exits 3 when alerts fire (used by the scheduled report). `tests/test_alerts.py`: 7 tests.

## How to test

```bash
python -m pipeline alerts
pytest tests/test_alerts.py
```

## Result

37 hires need attention (every open onboarding): 33 with a high-severity alert, including all 14 Delayed.

## Diff highlight

`pipeline/alerts.py` (excerpt)

```diff
+RULES: tuple[AlertRule, ...] = (
+    AlertRule("DELAYED_STATUS", "high", "Onboarding delayed",
+              lambda d, c: d["onboarding_status"].eq("Delayed"),
+              lambda r, c: f"Delayed after {r.onboarding_days} days with "
+                           f"{r.training_completion_percent:.0f}% of training done"),
+    AlertRule("OVERDUE_IN_PROGRESS", "high", "Past expected completion window",
+              lambda d, c: d["onboarding_status"].eq("In Progress") & (d["onboarding_days"] > c.expected_days),
+              lambda r, c: f"In progress for {r.onboarding_days} days; 90% of hires finish within "
+                           f"{c.expected_days:.0f}"),
+    AlertRule("NO_MANAGER", "high", "No manager assigned",
+              lambda d, c: _open(d) & d["manager_assigned"].eq(False),
+              lambda r, c: "Nobody is accountable for unblocking this hire"),
+    AlertRule("LOW_TRAINING_IN_FLIGHT", "medium", "Training below 50%",
+              lambda d, c: _open(d) & (d["training_completion_percent"] < 50),
+              lambda r, c: f"Only {r.training_completion_percent:.0f}% of mandatory training complete"),
+    AlertRule("NO_BUDDY_IN_FLIGHT", "medium", "No onboarding buddy",
+              lambda d, c: _open(d) & d["buddy_assigned"].eq(False),
+              lambda r, c: "No buddy assigned while onboarding is still open"),
+    AlertRule("MISSED_FIRST_WEEK_CHECKIN", "low", "Missed week-one check-in",
+              lambda d, c: _open(d) & d["first_week_checkin"].eq(False),
+              lambda r, c: "No manager check-in happened in week one"),
+    AlertRule("LOW_TOOL_ACTIVITY", "low", "Low tool activity",
+              lambda d, c: _open(d) & (d["total_active_minutes"] <= c.low_activity_minutes),
+              lambda r, c: f"{r.total_active_minutes} active tool minutes (bottom quartile, "
+                           f"<= {c.low_activity_minutes:.0f})"),
+)
+
+
+def evaluate_alerts(features: pd.DataFrame, context: AlertContext | None = None,
+                    rules: tuple[AlertRule, ...] = RULES) -> pd.DataFrame:
+    """One row per (hire, rule) that fired, most severe first."""
+    context = context or AlertContext.from_features(features)
+    frames = []
+    for rule in rules:
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `pipeline/__main__.py` | 2 | 0 |
| `pipeline/alerts.py` | 152 | 0 |
| `tests/test_alerts.py` | 95 | 0 |
| `docs/prs/gaurav/day-19-alert-monitoring.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
