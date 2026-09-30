# Onboarding Ops — dashboard UX mock

Owner: Gaurav · Roadmap: Week 4, Day 23 ("Mock UX design for dashboard improvements")

## Problems with the single-scroll page

1. KPI cards, the cohort table and the analysis competed for the same scroll; leaders never reached the root-cause findings.
2. Nothing on the page said *why* hires were delayed — only *how many*.
3. There was no obvious home for the alert feed planned for Day 24.

## Proposed layout

```
┌──────────────┬──────────────────────────────────────────────────────────────┐
│ COHORT       │ Onboarding Ops                                               │
│              │ Showing 215 of 1,470 hires · New hires                       │
│ [x] New hires├──────────────────────────────────────────────────────────────┤
│ Department ▾ │ [ Overview ] [ Cohort ] [ Root causes ] [ Alerts ]           │
│ Status     ▾ ├──────────────────────────────────────────────────────────────┤
│ Tenure     ▾ │ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │
│ Buddy        │ │ Completion   │ │ Avg days     │ │ Delayed      │  KPI row  │
│ (•) Any      │ │ 82.8%  -14.7 │ │ 12.2   +0.5  │ │ 14           │  tone +   │
│ ( ) With     │ │ ● Off target │ │ ● On target  │ │ ● Off target │  delta vs │
│ ( ) Without  │ └──────────────┘ └──────────────┘ └──────────────┘  company  │
│              │ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │
│              │ │ Training     │ │ Buddy cover. │ │ Week-1 check │           │
│              │ └──────────────┘ └──────────────┘ └──────────────┘           │
│              │ ┌───────────────────────────┐ ┌───────────────────────────┐  │
│              │ │ Onboarding days by status │ │ Status mix by department  │  │
│              │ └───────────────────────────┘ └───────────────────────────┘  │
└──────────────┴──────────────────────────────────────────────────────────────┘
```

| Tab | Question it answers | Content |
| :--- | :--- | :--- |
| Overview | Are we on target? | Six KPI cards with tone and delta vs company, two charts |
| Cohort | Who is in this group? | Department KPI table, hire list sorted most-urgent first |
| Root causes | Why are hires delayed? | Plain-English findings, lift chart (company-wide, symptoms excluded) |
| Alerts | Who needs help today? | Mock panel now; live severity feed in the Day 24 PR |

## Design decisions

- **Filters stay in the sidebar** so the cohort persists across tabs.
- **Tone is text + colour** (`● On target`), never colour alone, for accessibility.
- **Status colours are shared** with the exported charts (`pipeline.export.STATUS_COLOURS`) through `streamlit_app/theme.py`.
- **Root causes ignore the cohort filter** on purpose: lifts computed on a handful of hires are noise.
- **No custom CSS**: Streamlit's coloured markdown keeps the page readable in both light and dark mode.
