"""Dataset contracts shared by the whole team: columns, keys and cross-table references.

Agreed at the week-1 sync so the onboarding, tool-usage and support-ticket
workstreams all validate against one definition before anything is merged.
Merge strategy: every table joins on ``employee_id``; onboarding is 1:1 with
employees, tool_usage and support_tickets are 1:N and are aggregated per
employee *before* joining so row counts never fan out.

    python -m pipeline.schemas      # validate every dataset in data/; exit 1 on errors
"""
from __future__ import annotations

import sys
from collections.abc import Mapping
from dataclasses import dataclass

import pandas as pd

from .cleaning import ONBOARDING_COLUMNS
from .config import DATASETS, Settings
from .ingest import load_dataset


@dataclass(frozen=True)
class DatasetContract:
    name: str
    grain: str
    primary_key: tuple[str, ...]
    required_columns: tuple[str, ...]
    numeric_columns: tuple[str, ...] = ()
    references: tuple[tuple[str, str], ...] = ()  # (column, "table.column")


_EMPLOYEE_REF = (("employee_id", "employees.employee_id"),)

CONTRACTS: dict[str, DatasetContract] = {
    "employees": DatasetContract(
        "employees", "one row per employee", ("employee_id",),
        ("employee_id", "Department", "JobRole", "Gender", "Age", "Education",
         "BusinessTravel", "YearsAtCompany", "JobLevel", "MonthlyIncome"),
        numeric_columns=("employee_id", "Age", "Education", "YearsAtCompany", "JobLevel", "MonthlyIncome"),
    ),
    "onboarding": DatasetContract(
        "onboarding", "one row per employee (1:1)", ("employee_id",), ONBOARDING_COLUMNS,
        numeric_columns=("employee_id", "training_completion_percent", "onboarding_days"),
        references=_EMPLOYEE_REF,
    ),
    "tool_usage": DatasetContract(
        "tool_usage", "one row per employee, tool and day (1:N)", ("usage_id",),
        ("usage_id", "employee_id", "date", "tool_name", "login_count",
         "active_minutes", "feature_used", "device_type"),
        numeric_columns=("employee_id", "login_count", "active_minutes"),
        references=_EMPLOYEE_REF,
    ),
    "support_tickets": DatasetContract(
        "support_tickets", "one row per ticket (1:N)", ("ticket_id",),
        ("ticket_id", "employee_id", "created_date", "issue_type", "priority",
         "resolution_hours", "status", "assigned_team"),
        numeric_columns=("employee_id", "resolution_hours"),
        references=_EMPLOYEE_REF,
    ),
}


@dataclass(frozen=True)
class ContractIssue:
    dataset: str
    check: str
    detail: str
    severity: str = "error"  # "error" fails validation, "warning" is reported only

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.dataset}.{self.check}: {self.detail}"


def check_contract(df: pd.DataFrame, contract: DatasetContract) -> list[ContractIssue]:
    def issue(check: str, detail: str, severity: str = "error") -> ContractIssue:
        return ContractIssue(contract.name, check, detail, severity)

    missing = [c for c in contract.required_columns if c not in df.columns]
    if missing:  # nothing else can be checked reliably without the agreed columns
        return [issue("required_columns", "missing " + ", ".join(missing))]

    issues = []
    extra = [str(c) for c in df.columns if c not in contract.required_columns]
    if extra:
        issues.append(issue("unexpected_columns", ", ".join(extra), "warning"))
    key = list(contract.primary_key)
    null_keys = int(df[key].isna().any(axis=1).sum())
    if null_keys:
        issues.append(issue("primary_key", f"{null_keys} rows with a null {'/'.join(key)}"))
    duplicate_keys = int(df.dropna(subset=key).duplicated(subset=key).sum())
    if duplicate_keys:
        issues.append(issue("primary_key", f"{duplicate_keys} duplicate {'/'.join(key)} values"))
    for col in contract.numeric_columns:
        bad = int((df[col].notna() & pd.to_numeric(df[col], errors="coerce").isna()).sum())
        if bad:
            issues.append(issue("numeric", f"{bad} non-numeric values in {col}"))
    return issues


def check_references(frames: Mapping[str, pd.DataFrame]) -> list[ContractIssue]:
    """Every foreign key must point at an existing parent row."""
    issues = []
    for name, contract in CONTRACTS.items():
        if name not in frames:
            continue
        for column, target in contract.references:
            table, target_column = target.split(".")
            if table not in frames:
                issues.append(ContractIssue(name, "references", f"cannot check {column}: {table} not loaded", "warning"))
                continue
            child = frames[name]
            if column not in child.columns or target_column not in frames[table].columns:
                continue  # already reported as a missing required column
            values = child[column].dropna()
            orphans = values[~values.isin(frames[table][target_column])]
            if len(orphans):
                sample = ", ".join(str(v) for v in orphans.unique()[:5])
                issues.append(ContractIssue(name, "references",
                                            f"{len(orphans)} rows reference missing {target} (e.g. {sample})"))
    return issues


def validate_datasets(frames: Mapping[str, pd.DataFrame]) -> list[ContractIssue]:
    issues = [i for name, df in frames.items() for i in check_contract(df, CONTRACTS[name])]
    return issues + check_references(frames)


def load_frames(settings: Settings | None = None) -> dict[str, pd.DataFrame]:
    return {name: load_dataset(name, settings=settings)[0] for name in DATASETS}


def main(argv: list[str] | None = None) -> int:
    try:
        issues = validate_datasets(load_frames())
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    for item in issues:
        print(item)
    errors = sum(i.severity == "error" for i in issues)
    print(f"{len(DATASETS)} datasets checked: {errors} errors, {len(issues) - errors} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
