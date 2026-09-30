"""The SQL layer against a real MySQL server.

Skipped unless VIBECHECK_TEST_MYSQL_URL points at a *throwaway* database - the
tests replace its tables. CI provides one via a mysql:8.4 service container:

    VIBECHECK_TEST_MYSQL_URL=mysql+pymysql://root:pw@127.0.0.1:3306/vibecheck pytest -m mysql
"""
import os
from decimal import Decimal

import pandas as pd
import pytest

from pipeline.db import get_engine, stage_tables
from pipeline.features import build_feature_table
from pipeline.reconcile import reconcile
from pipeline.schemas import load_frames
from pipeline.sql_queries import available_queries, run_query

MYSQL_URL = os.environ.get("VIBECHECK_TEST_MYSQL_URL")

pytestmark = [
    pytest.mark.mysql,
    pytest.mark.skipif(not MYSQL_URL, reason="set VIBECHECK_TEST_MYSQL_URL to run against MySQL"),
]

PARAMS = {"rankings/fastest_per_department": {"top_n": 3}}


@pytest.fixture(scope="module")
def mysql_engine():
    engine = get_engine(MYSQL_URL)
    assert engine.dialect.name == "mysql", "VIBECHECK_TEST_MYSQL_URL must be a MySQL URL"
    stage_tables(engine, load_frames())
    yield engine
    engine.dispose()


@pytest.mark.parametrize("name", available_queries())
def test_every_query_matches_sqlite(mysql_engine, staged_engine, name):
    on_mysql = run_query(mysql_engine, name, PARAMS.get(name))
    on_sqlite = run_query(staged_engine, name, PARAMS.get(name))
    assert not on_mysql.empty
    assert not on_mysql.map(lambda v: isinstance(v, Decimal)).any().any()   # DECIMALs converted
    # Both engines round to 2 dp but may break .xx5 ties differently, hence atol.
    pd.testing.assert_frame_equal(on_mysql, on_sqlite, check_dtype=False, atol=0.011)


def test_mysql_and_python_pipeline_agree(mysql_engine):
    failed = [c for c in reconcile(mysql_engine, build_feature_table()) if not c.passed]
    assert failed == []
