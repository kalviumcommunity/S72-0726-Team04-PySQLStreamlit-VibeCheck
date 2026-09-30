"""Run the named SQL files under pipeline/sql/ against the configured database.

The queries are portable across MySQL 8 and SQLite 3.25+ (CTEs, CASE, window
functions; no engine-specific date functions), so the same file runs in CI and
against the team database.

    python -m pipeline.sql_queries --list
    python -m pipeline.sql_queries kpis/overall --stage   # stage data/*.csv into local SQLite first
"""
from __future__ import annotations

import argparse
import sys
from decimal import Decimal
from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from .db import get_engine, is_sqlite, safe_url, stage_tables

SQL_DIR = Path(__file__).parent / "sql"


def available_queries() -> list[str]:
    return sorted(p.relative_to(SQL_DIR).with_suffix("").as_posix() for p in SQL_DIR.rglob("*.sql"))


def load_query(name: str) -> str:
    if name not in available_queries():  # also blocks paths like ../../secrets
        raise KeyError(f"Unknown query {name!r}; available: {', '.join(available_queries())}")
    return (SQL_DIR / f"{name}.sql").read_text(encoding="utf-8")


def _decimals_to_float(frame: pd.DataFrame) -> pd.DataFrame:
    """MySQL returns DECIMAL for SUM/AVG/ROUND; make results match SQLite's floats."""
    for col in frame.columns:
        values = frame[col].dropna()
        if len(values) and values.map(lambda v: isinstance(v, Decimal)).all():
            frame[col] = frame[col].astype("float64")
    return frame


def run_query(engine: Engine, name: str, params: dict | None = None) -> pd.DataFrame:
    with engine.connect() as conn:
        frame = pd.read_sql(text(load_query(name)), conn, params=params or {})
    return _decimals_to_float(frame)


class StagingRefused(RuntimeError):
    """--stage was pointed at a shared (non-SQLite) database."""


def cli_engine(stage: bool = False) -> Engine:
    """Engine for command-line use; ``stage`` loads data/*.csv, but only into local SQLite."""
    from .schemas import load_frames

    engine = get_engine()
    if stage:
        if not is_sqlite(engine.url):
            raise StagingRefused(f"Refusing to overwrite tables in {safe_url(engine.url)}; "
                                 "--stage is for local SQLite only.")
        stage_tables(engine, load_frames())
    return engine


def onboarding_kpis(engine: Engine) -> dict[str, float | None]:
    """Headline KPIs from kpis/overall as a plain dict."""
    row = run_query(engine, "kpis/overall").iloc[0]
    return {key: None if pd.isna(value) else float(value) for key, value in row.items()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m pipeline.sql_queries")
    parser.add_argument("query", nargs="?", help="e.g. kpis/overall")
    parser.add_argument("--list", action="store_true", help="list available queries")
    parser.add_argument("--stage", action="store_true", help="load data/*.csv into the local SQLite database first")
    args = parser.parse_args(argv)
    if args.list or not args.query:
        print("\n".join(available_queries()))
        return 0

    try:
        print(run_query(cli_engine(args.stage), args.query).to_string(index=False))
    except StagingRefused as exc:
        print(exc, file=sys.stderr)
        return 2
    except KeyError as exc:
        print(exc.args[0], file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
