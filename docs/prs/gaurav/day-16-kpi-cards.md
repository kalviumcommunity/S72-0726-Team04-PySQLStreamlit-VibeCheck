# Day 16 - Onboarding KPI cards and the Streamlit Onboarding Ops page

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-16-kpi-cards` |
| **Base** | `main` - stacked on `gaurav/day-15-sql-python-reconciliation` (merge PR 15 first) |
| **Roadmap** | Day 17 (Thu 13 Aug 2026) - *Design KPI cards (onboarding completion rate).* |
| **Type** | `feat` |
| **Size** | 6 code files, +185 / -0 lines (docs excluded) |

## Summary

Adds `streamlit_app/`: six KPI cards (completion rate, days to complete, delayed hires, training, buddy coverage, first-week check-ins), each with a target-based tone, and the `onboarding_ops.py` page that shows them.

## Why

- Targets live in code (`KPI_SPECS`) so they are reviewed like code, not buried in the UI.
- Card logic is pure Python and unit-tested; Streamlit only renders.

## What changed

- `KpiSpec` / `KpiCard`, `tone_for()`, `format_value()`, `build_kpi_cards()` (deltas vs a benchmark for rates, not counts).
- Tone shown as text + colour (`On target` / `Watch` / `Off target`) - not colour alone.
- Page smoke-tested headlessly with `streamlit.testing.v1.AppTest`. `tests/test_kpi_cards.py`: 13 tests.

## How to test

```bash
streamlit run streamlit_app/onboarding_ops.py
pytest tests/test_kpi_cards.py
```

## Result

Completion 97.5% (on target), 11.7 days (on target), 14 delayed (off target), training 88.9% (watch).

## Diff highlight

`streamlit_app/components/kpi_cards.py` (excerpt)

```diff
+def tone_for(value: float | None, spec: KpiSpec) -> str:
+    if value is None:
+        return "neutral"
+    if spec.higher_is_better:
+        return "good" if value >= spec.target else "bad" if value < spec.floor else "warn"
+    return "good" if value <= spec.target else "bad" if value > spec.floor else "warn"
+
+
+def format_value(value: float | None, unit: str) -> str:
+    if value is None:
+        return "—"
+    if unit == "%":
+        return f"{value:.1f}%"
+    if unit == " days":
+        return f"{value:.1f} days"
+    return f"{value:,.0f}"
+
+
+def build_kpi_cards(kpis: Mapping[str, float | None], benchmark: Mapping[str, float | None] | None = None,
+                    specs: Sequence[KpiSpec] = KPI_SPECS) -> list[KpiCard]:
+    """One card per spec. With a benchmark (e.g. company-wide KPIs), rates show a delta."""
+    cards = []
+    for spec in specs:
+        value = kpis.get(spec.key)
+        reference = (benchmark or {}).get(spec.key)
+        delta = None
+        if spec.unit and value is not None and reference is not None:  # counts are not comparable across cohorts
+            unit = " pts" if spec.unit == "%" else spec.unit
+            delta = f"{value - reference:+.1f}{unit} vs company"
+        cards.append(KpiCard(spec.label, format_value(value, spec.unit), tone_for(value, spec), spec.help,
+                             delta, "normal" if spec.higher_is_better else "inverse"))
+    return cards
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `requirements-pipeline.txt` | 1 | 0 |
| `streamlit_app/__init__.py` | 1 | 0 |
| `streamlit_app/components/__init__.py` | 1 | 0 |
| `streamlit_app/components/kpi_cards.py` | 99 | 0 |
| `streamlit_app/onboarding_ops.py` | 30 | 0 |
| `tests/test_kpi_cards.py` | 53 | 0 |
| `docs/prs/gaurav/day-16-kpi-cards.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
