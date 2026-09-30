"""Alert monitoring for delayed onboarding.

Rules run over the feature table and emit one alert per (hire, rule):

    DELAYED_STATUS             high    onboarding is flagged Delayed
    OVERDUE_IN_PROGRESS        high    still In Progress past the expected completion window
    NO_MANAGER                 high    open onboarding with no reporting manager
    LOW_TRAINING_IN_FLIGHT     medium  open onboarding with training below 50%
    NO_BUDDY_IN_FLIGHT         medium  open onboarding without a buddy
    MISSED_FIRST_WEEK_CHECKIN  low     open onboarding, no week-one check-in
    LOW_TOOL_ACTIVITY          low     open onboarding in the bottom quartile of tool minutes

Thresholds come from the whole company (p90 completion time, p25 tool minutes),
so filtering the dashboard to a cohort never moves the goalposts.

    python -m pipeline alerts                    # summary + outputs/alerts.csv
    python -m pipeline alerts --fail-on high     # exit 3 when high alerts exist (scheduled CI)
"""
from __future__ import annotations

import argparse
import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .config import configure_logging, load_settings
from .features import OPEN_STATUSES

log = logging.getLogger(__name__)

SEVERITIES = ("high", "medium", "low")  # most urgent first
EXIT_ALERTS_FOUND = 3
ALERT_COLUMNS = ["employee_id", "Department", "JobRole", "severity", "code", "title", "message",
                 "onboarding_status", "onboarding_days", "training_completion_percent"]


@dataclass(frozen=True)
class AlertContext:
    expected_days: float         # 90% of completed onboardings finish within this many days
    low_activity_minutes: float  # bottom-quartile boundary for total active tool minutes

    @classmethod
    def from_features(cls, features: pd.DataFrame) -> AlertContext:
        completed = features.loc[features["onboarding_status"].eq("Completed"), "onboarding_days"]
        return cls(expected_days=float(completed.astype("float64").quantile(0.9)),
                   low_activity_minutes=float(features["total_active_minutes"].quantile(0.25)))


@dataclass(frozen=True)
class AlertRule:
    code: str
    severity: str
    title: str
    applies: Callable[[pd.DataFrame, AlertContext], pd.Series]
    message: Callable[[object, AlertContext], str]  # receives an itertuples() row


def _open(d: pd.DataFrame) -> pd.Series:
    return d["onboarding_status"].isin(OPEN_STATUSES)


RULES: tuple[AlertRule, ...] = (
    AlertRule("DELAYED_STATUS", "high", "Onboarding delayed",
              lambda d, c: d["onboarding_status"].eq("Delayed"),
              lambda r, c: f"Delayed after {r.onboarding_days} days with "
                           f"{r.training_completion_percent:.0f}% of training done"),
    AlertRule("OVERDUE_IN_PROGRESS", "high", "Past expected completion window",
              lambda d, c: d["onboarding_status"].eq("In Progress") & (d["onboarding_days"] > c.expected_days),
              lambda r, c: f"In progress for {r.onboarding_days} days; 90% of hires finish within "
                           f"{c.expected_days:.0f}"),
    AlertRule("NO_MANAGER", "high", "No manager assigned",
              lambda d, c: _open(d) & d["manager_assigned"].eq(False),
              lambda r, c: "Nobody is accountable for unblocking this hire"),
    AlertRule("LOW_TRAINING_IN_FLIGHT", "medium", "Training below 50%",
              lambda d, c: _open(d) & (d["training_completion_percent"] < 50),
              lambda r, c: f"Only {r.training_completion_percent:.0f}% of mandatory training complete"),
    AlertRule("NO_BUDDY_IN_FLIGHT", "medium", "No onboarding buddy",
              lambda d, c: _open(d) & d["buddy_assigned"].eq(False),
              lambda r, c: "No buddy assigned while onboarding is still open"),
    AlertRule("MISSED_FIRST_WEEK_CHECKIN", "low", "Missed week-one check-in",
              lambda d, c: _open(d) & d["first_week_checkin"].eq(False),
              lambda r, c: "No manager check-in happened in week one"),
    AlertRule("LOW_TOOL_ACTIVITY", "low", "Low tool activity",
              lambda d, c: _open(d) & (d["total_active_minutes"] <= c.low_activity_minutes),
              lambda r, c: f"{r.total_active_minutes} active tool minutes (bottom quartile, "
                           f"<= {c.low_activity_minutes:.0f})"),
)


def evaluate_alerts(features: pd.DataFrame, context: AlertContext | None = None,
                    rules: tuple[AlertRule, ...] = RULES) -> pd.DataFrame:
    """One row per (hire, rule) that fired, most severe first."""
    context = context or AlertContext.from_features(features)
    frames = []
    for rule in rules:
        hits = features[rule.applies(features, context).to_numpy(dtype=bool, na_value=False)]
        if len(hits):
            messages = [rule.message(row, context) for row in hits.itertuples(index=False)]
            frames.append(hits.assign(severity=rule.severity, code=rule.code, title=rule.title, message=messages))
    alerts = pd.concat(frames) if frames else pd.DataFrame(columns=ALERT_COLUMNS)
    alerts = alerts[[c for c in ALERT_COLUMNS if c in alerts.columns]].copy()
    alerts["severity"] = pd.Categorical(alerts["severity"], categories=SEVERITIES, ordered=True)
    return alerts.sort_values(["severity", "employee_id", "code"]).reset_index(drop=True)


def summarize_alerts(alerts: pd.DataFrame) -> pd.DataFrame:
    return (alerts.groupby(["severity", "code", "title"], observed=True)["employee_id"]
                  .nunique().rename("hires").reset_index())


def employees_needing_attention(alerts: pd.DataFrame) -> pd.DataFrame:
    """One row per hire: worst severity, number of alerts and the rule codes."""
    grouped = alerts.groupby("employee_id")
    table = pd.DataFrame({
        "worst_severity": grouped["severity"].min(),
        "alerts": grouped.size(),
        "codes": grouped["code"].agg(", ".join),
    }).reset_index()
    return table.sort_values(["worst_severity", "alerts"], ascending=[True, False]).reset_index(drop=True)


def at_or_above(alerts: pd.DataFrame, severity: str) -> pd.DataFrame:
    return alerts[alerts["severity"] <= severity]


def main(argv: list[str] | None = None) -> int:
    from .features import build_feature_table

    parser = argparse.ArgumentParser(prog="python -m pipeline alerts")
    parser.add_argument("--out", type=Path, help="CSV path (default: <output dir>/alerts.csv)")
    parser.add_argument("--fail-on", choices=SEVERITIES,
                        help=f"exit {EXIT_ALERTS_FOUND} if any alert at or above this severity fired")
    args = parser.parse_args(argv)
    configure_logging()

    alerts = evaluate_alerts(build_feature_table())
    out = args.out or load_settings().output_dir / "alerts.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    alerts.to_csv(out, index=False, lineterminator="\n")
    print(summarize_alerts(alerts).to_string(index=False) if len(alerts) else "No alerts fired.")
    print(f"\n{alerts['employee_id'].nunique()} hires need attention; details in {out}")
    if args.fail_on and len(at_or_above(alerts, args.fail_on)):
        log.warning("alerts at or above %r severity fired", args.fail_on)
        return EXIT_ALERTS_FOUND
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
