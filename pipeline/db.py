"""Database access for the SQL layer: MySQL on shared environments, SQLite locally.

    VIBECHECK_DB_URL=mysql+pymysql://user:password@host:3306/vibecheck   # team MySQL
    (unset)                                                               # sqlite:///<outputs>/vibecheck.db

The shared database is loaded by the team's SQL-integration loader. ``stage_tables``
only exists so KPI queries can run on a laptop or in CI from the committed CSVs.
"""
from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine, make_url

from .config import Settings, load_settings


def database_url(settings: Settings | None = None, env: Mapping[str, str] | None = None) -> str:
    env = os.environ if env is None else env
    if env.get("VIBECHECK_DB_URL"):
        return env["VIBECHECK_DB_URL"]
    settings = settings or load_settings(env)
    return f"sqlite:///{(settings.output_dir / 'vibecheck.db').as_posix()}"


def is_sqlite(url: str | URL) -> bool:
    return make_url(url).get_backend_name() == "sqlite"


def get_engine(url: str | None = None) -> Engine:
    url = url or database_url()
    parsed = make_url(url)
    if is_sqlite(parsed) and parsed.database not in (None, "", ":memory:"):
        Path(parsed.database).parent.mkdir(parents=True, exist_ok=True)
    return create_engine(parsed, pool_pre_ping=True)


def safe_url(url: str | URL) -> str:
    """URL for logs and error messages, with the password masked."""
    return make_url(url).render_as_string(hide_password=True)


def stage_tables(engine: Engine, frames: Mapping[str, pd.DataFrame], if_exists: str = "replace") -> dict[str, int]:
    """Write raw DataFrames to same-named tables in one transaction; returns row counts."""
    with engine.begin() as conn:
        for name, frame in frames.items():
            frame.to_sql(name, conn, index=False, if_exists=if_exists, chunksize=1000)
    return {name: len(frame) for name, frame in frames.items()}
