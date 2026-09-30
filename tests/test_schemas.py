import shutil

import pandas as pd
import pytest

from pipeline.config import DATASETS
from pipeline.schemas import CONTRACTS, check_contract, check_references, load_frames, main, validate_datasets


@pytest.fixture(scope="module")
def frames():
    return load_frames()


def test_committed_datasets_satisfy_every_contract(frames):
    assert validate_datasets(frames) == []


def test_every_dataset_has_a_contract():
    assert set(CONTRACTS) == set(DATASETS)


def test_missing_columns_short_circuit(frames):
    issues = check_contract(frames["onboarding"].drop(columns=["onboarding_status"]), CONTRACTS["onboarding"])
    assert [(i.check, i.detail) for i in issues] == [("required_columns", "missing onboarding_status")]


def test_key_and_numeric_problems_are_reported(frames):
    tickets = frames["support_tickets"].head(5).copy()
    tickets = pd.concat([tickets, tickets.head(1)], ignore_index=True)       # duplicate ticket_id
    tickets["ticket_id"] = tickets["ticket_id"].astype(object)
    tickets.loc[1, "ticket_id"] = None                                        # null key
    tickets["resolution_hours"] = tickets["resolution_hours"].astype(object)
    tickets.loc[2, "resolution_hours"] = "two days"                           # not a number
    tickets["source_system"] = "zendesk"                                      # unagreed column
    found = {(i.check, i.severity) for i in check_contract(tickets, CONTRACTS["support_tickets"])}
    assert found == {("primary_key", "error"), ("numeric", "error"), ("unexpected_columns", "warning")}


def test_orphan_foreign_keys_are_reported(frames):
    usage = frames["tool_usage"].head(3).copy()
    usage.loc[0, "employee_id"] = 999_999
    issues = check_references({"employees": frames["employees"], "tool_usage": usage})
    assert len(issues) == 1 and "999999" in issues[0].detail


def test_reference_check_needs_the_parent_table(frames):
    issues = check_references({"onboarding": frames["onboarding"]})
    assert [i.severity for i in issues] == ["warning"]


def test_cli_fails_on_a_broken_workspace(tmp_path, monkeypatch, settings, capsys):
    assert main([]) == 0
    for name in DATASETS:
        shutil.copy(settings.dataset_path(name), tmp_path)
    onboarding = pd.read_csv(tmp_path / "onboarding.csv")
    onboarding.drop(columns=["buddy_assigned"]).to_csv(tmp_path / "onboarding.csv", index=False)
    monkeypatch.setenv("VIBECHECK_DATA_DIR", str(tmp_path))
    assert main([]) == 1
    assert "missing buddy_assigned" in capsys.readouterr().out
