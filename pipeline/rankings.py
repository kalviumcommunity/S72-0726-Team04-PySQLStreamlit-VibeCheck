"""Rank hires by onboarding speed with SQL window functions.

    RANK / DENSE_RANK   position of each completed hire, fastest first
    NTILE(4)            speed quartile inside the department (1 = fastest)
    PERCENT_RANK        company-wide percentile (0 = fastest)
    AVG() OVER          days above / below the department average
    LAG()               month-over-month change in average completion time

    python -m pipeline.rankings --stage --top 3
"""
from __future__ import annotations

import argparse
import sys

import pandas as pd
from sqlalchemy.engine import Engine

from .sql_queries import StagingRefused, cli_engine, run_query


def rank_hires_by_speed(engine: Engine) -> pd.DataFrame:
    return run_query(engine, "rankings/onboarding_speed")


def fastest_per_department(engine: Engine, top_n: int = 3) -> pd.DataFrame:
    if isinstance(top_n, bool) or not isinstance(top_n, int) or top_n < 1:
        raise ValueError(f"top_n must be a positive integer, got {top_n!r}")
    return run_query(engine, "rankings/fastest_per_department", {"top_n": top_n})


def department_monthly_trend(engine: Engine) -> pd.DataFrame:
    return run_query(engine, "rankings/department_monthly_trend")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m pipeline.rankings")
    parser.add_argument("--top", type=int, default=3, help="hires per department (default 3)")
    parser.add_argument("--stage", action="store_true", help="load data/*.csv into the local SQLite database first")
    args = parser.parse_args(argv)
    try:
        table = fastest_per_department(cli_engine(args.stage), args.top)
    except (StagingRefused, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 2
    print(table.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
