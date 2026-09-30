"""Regression tests: CLI commands report data and database problems in one line, not a traceback."""
import pytest

from pipeline.__main__ import main


@pytest.fixture
def missing_data(tmp_path, monkeypatch):
    monkeypatch.setenv("VIBECHECK_DATA_DIR", str(tmp_path / "no-such-folder"))
    monkeypatch.setenv("VIBECHECK_OUTPUT_DIR", str(tmp_path / "out"))
    monkeypatch.delenv("VIBECHECK_DB_URL", raising=False)
    monkeypatch.delenv("VIBECHECK_DEBUG", raising=False)


@pytest.mark.parametrize("command", [
    # These four used to crash with a traceback (found by the Day 25 end-to-end tests).
    ["alerts"],
    ["reconcile"],
    ["rankings", "--stage"],
    ["kpis", "kpis/overall", "--stage"],
])
def test_missing_data_folder_is_one_clear_line(missing_data, capsys, command):
    assert main(command) == 1
    err = capsys.readouterr().err
    assert err.startswith("error: No file for dataset") and "no-such-folder" in err
    assert "Traceback" not in err


@pytest.mark.parametrize("command", [["export"], ["validate"]])
def test_commands_with_their_own_reporting_still_exit_1(missing_data, command):
    assert main(command) == 1


def test_unreachable_database_is_reported_without_sql(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("VIBECHECK_DB_URL", f"sqlite:///{tmp_path.as_posix()}")  # a folder is not a database
    assert main(["kpis", "kpis/overall"]) == 1
    err = capsys.readouterr().err
    assert err.startswith("database error: ") and "SELECT" not in err


def test_debug_mode_keeps_the_traceback(missing_data, monkeypatch):
    monkeypatch.setenv("VIBECHECK_DEBUG", "1")
    with pytest.raises(FileNotFoundError):
        main(["alerts"])
