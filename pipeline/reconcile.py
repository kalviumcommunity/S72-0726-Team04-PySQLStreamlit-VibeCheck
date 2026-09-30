"""Validate SQL outputs against the Python pipeline.

The SQL layer reads the *raw* tables (Yes/No strings, free-text statuses); the
Python side reads the cleaned, standardised feature table. When both agree on
the headline KPIs, the department breakdown, the speed rankings and the new-hire
cohort, neither the SQL nor the cleaning logic has drifted.

    python -m pipeline.reconcile              # stages data/ into local SQLite first
    VIBECHECK_DB_URL=mysql+pymysql://... python -m pipeline.reconcile --no-stage
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass

import pandas as pd
from sqlalchemy.engine import Engine

from .db import get_engine, is_sqlite
from .kpis import KPI_KEYS, compute_department_kpis, compute_onboarding_kpis
from .rankings import rank_hires_by_speed
from .sql_queries import cli_engine, onboarding_kpis, run_query

DEPARTMENT_METRICS = ("hires", "completion_rate_pct", "delayed_count", "avg_days_to_complete", "avg_training_pct")


@dataclass(frozen=True)
class Check:
    name: str
    sql_value: float | None
    python_value: float | None
    tolerance: float = 0.01

    @property
    def delta(self) -> float | None:
        if self.sql_value is None or self.python_value is None:
            return None
        return float(self.sql_value) - float(self.python_value)

    @property
    def passed(self) -> bool:
        if self.sql_value is None or self.python_value is None:
            return self.sql_value is None and self.python_value is None
        return abs(self.delta) <= self.tolerance + 1e-9  # both sides round to 2 dp, possibly differently

    def as_dict(self) -> dict:
        return {**asdict(self), "delta": self.delta, "passed": self.passed}


def _value(table: pd.DataFrame, row: object, column: str) -> float | None:
    if row not in table.index or pd.isna(table.at[row, column]):
        return None
    return float(table.at[row, column])


def python_speed_ranks(features: pd.DataFrame) -> pd.DataFrame:
    """pandas equivalent of RANK() OVER (PARTITION BY department ORDER BY days, training DESC)."""
    keys = ["Department", "onboarding_days", "training_completion_percent"]
    completed = features.loc[features["onboarding_status"].eq("Completed"), ["employee_id", *keys]]
    ordered = completed.sort_values(keys, ascending=[True, True, False])
    ordered = ordered.assign(_position=ordered.groupby("Department", observed=True).cumcount() + 1)
    rank = ordered.groupby(keys, observed=True)["_position"].transform("min")
    return ordered.assign(dept_speed_rank=rank)[["employee_id", "dept_speed_rank"]]


def reconcile(engine: Engine, features: pd.DataFrame, tolerance: float = 0.01) -> list[Check]:
    checks: list[Check] = []

    sql_kpis, py_kpis = onboarding_kpis(engine), compute_onboarding_kpis(features)
    checks += [Check(f"overall.{key}", sql_kpis[key], py_kpis[key], tolerance) for key in KPI_KEYS]

    sql_dept = run_query(engine, "kpis/by_department").set_index("department")
    py_dept = compute_department_kpis(features).set_index("department")
    for department in sorted(set(sql_dept.index) | set(py_dept.index)):
        checks += [Check(f"department[{department}].{metric}", _value(sql_dept, department, metric),
                         _value(py_dept, department, metric), tolerance) for metric in DEPARTMENT_METRICS]

    sql_ranks = rank_hires_by_speed(engine)[["employee_id", "dept_speed_rank"]]
    joined = sql_ranks.merge(python_speed_ranks(features), on="employee_id", how="outer", suffixes=("_sql", "_py"))
    agreeing = int((joined["dept_speed_rank_sql"] == joined["dept_speed_rank_py"]).sum())
    checks.append(Check("rankings.dept_speed_rank_agreement", float(len(joined)), float(agreeing), 0))

    cohort = run_query(engine, "kpis/new_hire_cohort").iloc[0]
    checks.append(Check("cohort.new_hires", float(cohort["new_hires"]), float(features["is_new_hire"].sum()), 0))
    return checks


def reconciliation_table(checks: list[Check]) -> pd.DataFrame:
    columns = ["name", "sql_value", "python_value", "delta", "passed"]
    return pd.DataFrame([c.as_dict() for c in checks], columns=columns)


def main(argv: list[str] | None = None) -> int:
    from .features import build_feature_table

    parser = argparse.ArgumentParser(prog="python -m pipeline.reconcile")
    parser.add_argument("--no-stage", action="store_true", help="use the tables already in the database")
    args = parser.parse_args(argv)
    engine = get_engine()
    if is_sqlite(engine.url) and not args.no_stage:  # a shared MySQL database is never overwritten
        engine = cli_engine(stage=True)
    checks = reconcile(engine, build_feature_table())
    failed = [c for c in checks if not c.passed]
    table = reconciliation_table(failed or checks)
    print(table.to_string(index=False))
    print(f"\n{len(checks) - len(failed)}/{len(checks)} checks agree between SQL and Python")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
