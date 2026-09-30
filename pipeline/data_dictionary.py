"""Data dictionary: what every onboarding field means for the business.

The dictionary lives in code so it can be checked against the real dataset:

    python -m pipeline.data_dictionary            # print the Markdown
    python -m pipeline.data_dictionary --write    # regenerate docs/data_dictionary/onboarding.md
    python -m pipeline.data_dictionary --check    # exit 1 if the doc or the dataset has drifted
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .cleaning import snake_case_columns
from .ingest import load_onboarding

DOC_PATH = Path(__file__).resolve().parents[1] / "docs" / "data_dictionary" / "onboarding.md"


@dataclass(frozen=True)
class FieldSpec:
    name: str
    raw_type: str
    dtype: str  # dtype after pipeline.standardize (prefix match, e.g. "datetime64")
    allowed: str
    nullable: bool
    description: str
    business_meaning: str


ONBOARDING_FIELDS: tuple[FieldSpec, ...] = (
    FieldSpec("employee_id", "INTEGER", "int64", "Positive integer, unique", False,
              "Employee identifier (IBM HR `EmployeeNumber`).",
              "Join key to employees, tool usage and support tickets. Exactly one onboarding record per employee."),
    FieldSpec("orientation_completed", "TEXT Yes/No", "boolean", "Yes / No", False,
              "Whether the hire attended company orientation.",
              "First onboarding milestone. A missed orientation means the hire was never formally walked "
              "through processes and tooling."),
    FieldSpec("training_completion_percent", "FLOAT", "float64", "0.0 - 100.0", False,
              "Share of mandatory training modules completed.",
              "Main readiness signal: `100 - value` is the outstanding training that drives the friction "
              "score."),
    FieldSpec("onboarding_days", "INTEGER", "Int64", "0 - 365", False,
              "Days taken to finish onboarding (Completed) or elapsed so far (In Progress / Delayed).",
              "Speed to productivity. Basis for time-to-value, completion-time outliers and speed rankings."),
    FieldSpec("onboarding_status", "TEXT", "category", "Completed < In Progress < Delayed", False,
              "Lifecycle state of the onboarding checklist, ordered by severity.",
              "Delayed hires are the intervention list; In Progress hires are watched for overrun."),
    FieldSpec("manager_assigned", "TEXT Yes/No", "boolean", "Yes / No", False,
              "Whether a reporting manager was assigned at start.",
              "Without a manager nobody is accountable for unblocking the hire; a root-cause candidate for delays."),
    FieldSpec("buddy_assigned", "TEXT Yes/No", "boolean", "Yes / No", False,
              "Whether a peer onboarding buddy was assigned.",
              "Reach of the buddy programme. Only 19 of 1,470 hires have no buddy, so buddy vs no-buddy "
              "comparisons are indicative, not conclusive."),
    FieldSpec("first_week_checkin", "TEXT Yes/No", "boolean", "Yes / No", False,
              "Whether a manager check-in happened in week one.",
              "Early feedback loop; when it is missed, blockers surface weeks later as tickets or delays."),
    FieldSpec("onboarding_completion_date", "TEXT YYYY-MM-DD", "datetime64", "ISO date; empty while in flight", True,
              "Date the hire finished onboarding.",
              "Anchors cohort trends by completion month. Must be present for every Completed hire."),
)


def documented_names() -> list[str]:
    return [f.name for f in ONBOARDING_FIELDS]


def undocumented_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in snake_case_columns(df).columns if c not in documented_names()]


def missing_columns(df: pd.DataFrame) -> list[str]:
    columns = set(snake_case_columns(df).columns)
    return [name for name in documented_names() if name not in columns]


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def render_markdown() -> str:
    lines = [
        "# Onboarding data dictionary",
        "",
        "> Generated from `pipeline/data_dictionary.py` by "
        "`python -m pipeline.data_dictionary --write`. Edit the code, not this file.",
        "",
        "Source: `data/onboarding.csv` · Grain: one row per employee · Primary key: `employee_id`",
        "",
        "| Field | Raw type | Pipeline dtype | Allowed values | Nullable | Description | Business meaning |",
        "| :--- | :--- | :--- | :--- | :---: | :--- | :--- |",
    ]
    for f in ONBOARDING_FIELDS:
        cells = [f"`{f.name}`", f.raw_type, f"`{f.dtype}`", f.allowed, "yes" if f.nullable else "no",
                 f.description, f.business_meaning]
        lines.append("| " + " | ".join(_cell(c) for c in cells) + " |")
    return "\n".join(lines) + "\n"


def drift_problems(df: pd.DataFrame, doc_path: Path = DOC_PATH) -> list[str]:
    problems = [f"column not in dictionary: {c}" for c in undocumented_columns(df)]
    problems += [f"documented column missing from dataset: {c}" for c in missing_columns(df)]
    current = doc_path.read_text(encoding="utf-8").replace("\r\n", "\n") if doc_path.is_file() else ""
    if current != render_markdown():
        problems.append(f"{doc_path.name} is stale; run `python -m pipeline.data_dictionary --write`")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m pipeline.data_dictionary")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help=f"regenerate {DOC_PATH.name}")
    mode.add_argument("--check", action="store_true", help="fail if the doc or dataset drifted")
    args = parser.parse_args(argv)
    if args.write:
        DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
        DOC_PATH.write_text(render_markdown(), encoding="utf-8", newline="\n")
        print(f"wrote {DOC_PATH}")
        return 0
    if args.check:
        problems = drift_problems(load_onboarding())
        for problem in problems:
            print(f"DRIFT: {problem}")
        return 1 if problems else 0
    print(render_markdown(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
