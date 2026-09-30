# Onboarding data dictionary

> Generated from `pipeline/data_dictionary.py` by `python -m pipeline.data_dictionary --write`. Edit the code, not this file.

Source: `data/onboarding.csv` · Grain: one row per employee · Primary key: `employee_id`

| Field | Raw type | Pipeline dtype | Allowed values | Nullable | Description | Business meaning |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| `employee_id` | INTEGER | `int64` | Positive integer, unique | no | Employee identifier (IBM HR `EmployeeNumber`). | Join key to employees, tool usage and support tickets. Exactly one onboarding record per employee. |
| `orientation_completed` | TEXT Yes/No | `boolean` | Yes / No | no | Whether the hire attended company orientation. | First onboarding milestone. A missed orientation means the hire was never formally walked through processes and tooling. |
| `training_completion_percent` | FLOAT | `float64` | 0.0 - 100.0 | no | Share of mandatory training modules completed. | Main readiness signal: `100 - value` is the outstanding training that drives the friction score. |
| `onboarding_days` | INTEGER | `Int64` | 0 - 365 | no | Days taken to finish onboarding (Completed) or elapsed so far (In Progress / Delayed). | Speed to productivity. Basis for time-to-value, completion-time outliers and speed rankings. |
| `onboarding_status` | TEXT | `category` | Completed < In Progress < Delayed | no | Lifecycle state of the onboarding checklist, ordered by severity. | Delayed hires are the intervention list; In Progress hires are watched for overrun. |
| `manager_assigned` | TEXT Yes/No | `boolean` | Yes / No | no | Whether a reporting manager was assigned at start. | Without a manager nobody is accountable for unblocking the hire; a root-cause candidate for delays. |
| `buddy_assigned` | TEXT Yes/No | `boolean` | Yes / No | no | Whether a peer onboarding buddy was assigned. | Reach of the buddy programme. Only 19 of 1,470 hires have no buddy, so buddy vs no-buddy comparisons are indicative, not conclusive. |
| `first_week_checkin` | TEXT Yes/No | `boolean` | Yes / No | no | Whether a manager check-in happened in week one. | Early feedback loop; when it is missed, blockers surface weeks later as tickets or delays. |
| `onboarding_completion_date` | TEXT YYYY-MM-DD | `datetime64` | ISO date; empty while in flight | yes | Date the hire finished onboarding. | Anchors cohort trends by completion month. Must be present for every Completed hire. |
