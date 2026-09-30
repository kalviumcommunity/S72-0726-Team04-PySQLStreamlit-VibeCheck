from decimal import Decimal

import pandas as pd
import pytest

from pipeline.db import database_url, get_engine, is_sqlite, safe_url
from pipeline.sql_queries import (
    _decimals_to_float,
    available_queries,
    load_query,
    main,
    onboarding_kpis,
    run_query,
)


def test_query_catalogue():
    assert {"kpis/overall", "kpis/by_department", "kpis/status_breakdown",
            "kpis/new_hire_cohort", "kpis/completions_by_month"} <= set(available_queries())


@pytest.mark.parametrize("name", ["kpis/nope", "../db", "kpis/../../pipeline/db"])
def test_unknown_or_traversing_names_are_rejected(name):
    with pytest.raises(KeyError, match="Unknown query"):
        load_query(name)


def test_overall_kpis_on_real_data(staged_engine):
    kpis = onboarding_kpis(staged_engine)
    assert (kpis["total_hires"], kpis["completed_count"], kpis["delayed_count"]) == (1470, 1433, 14)
    assert kpis["completion_rate_pct"] == 97.48
    assert kpis["buddy_coverage_pct"] == 98.71
    assert kpis["avg_days_to_complete"] == 11.68


def test_breakdowns_add_up(staged_engine):
    by_dept = run_query(staged_engine, "kpis/by_department")
    assert by_dept["department"].tolist() == ["Human Resources", "Research & Development", "Sales"]
    assert by_dept["hires"].sum() == 1470 and by_dept["delayed_count"].sum() == 14
    status = run_query(staged_engine, "kpis/status_breakdown")
    assert status["hires"].tolist() == [1433, 23, 14]
    assert status["share_pct"].sum() == pytest.approx(100, abs=0.02)
    months = run_query(staged_engine, "kpis/completions_by_month")
    assert months["completions"].sum() == 1433
    assert months["completion_month"].is_monotonic_increasing


def test_new_hire_cohort_matches_python_definition(staged_engine):
    cohort = run_query(staged_engine, "kpis/new_hire_cohort").iloc[0]
    assert cohort["new_hires"] == 215 and cohort["delayed_count"] == 14


def test_mysql_decimals_become_floats():
    frame = _decimals_to_float(pd.DataFrame({"rate": [Decimal("97.48"), None], "label": ["a", "b"]}))
    assert frame["rate"].dtype == "float64" and frame["label"].tolist() == ["a", "b"]


def test_database_url_defaults_to_local_sqlite(tmp_path):
    url = database_url(env={"VIBECHECK_OUTPUT_DIR": str(tmp_path)})
    assert is_sqlite(url) and url.endswith("/vibecheck.db")
    mysql = "mysql+pymysql://vibe:s3cret@db.internal:3306/vibecheck"
    assert database_url(env={"VIBECHECK_DB_URL": mysql}) == mysql
    assert "s3cret" not in safe_url(mysql) and not is_sqlite(mysql)


def test_sqlite_parent_directory_is_created(tmp_path):
    engine = get_engine(f"sqlite:///{(tmp_path / 'nested' / 'x.db').as_posix()}")
    with engine.connect():
        pass
    assert (tmp_path / "nested" / "x.db").is_file()


def test_cli_refuses_to_stage_into_a_shared_database(monkeypatch, capsys):
    monkeypatch.setenv("VIBECHECK_DB_URL", "mysql+pymysql://vibe:pw@db.internal/vibecheck")
    assert main(["kpis/overall", "--stage"]) == 2
    assert "Refusing to overwrite" in capsys.readouterr().err


def test_cli_runs_a_query_against_local_sqlite(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("VIBECHECK_OUTPUT_DIR", str(tmp_path))
    assert main(["kpis/status_breakdown", "--stage"]) == 0
    assert "In Progress" in capsys.readouterr().out
    assert main(["kpis/missing"]) == 2
