import pandas as pd

from pipeline.data_dictionary import (
    ONBOARDING_FIELDS,
    drift_problems,
    main,
    missing_columns,
    render_markdown,
    undocumented_columns,
)
from pipeline.ingest import load_onboarding
from pipeline.standardize import prepare_onboarding


def test_every_column_is_documented(settings):
    raw = load_onboarding(settings=settings)
    assert undocumented_columns(raw) == []
    assert missing_columns(raw) == []


def test_documented_dtypes_match_the_standardised_frame(settings):
    standard = prepare_onboarding(load_onboarding(settings=settings))
    for field in ONBOARDING_FIELDS:
        assert str(standard[field.name].dtype).startswith(field.dtype), field.name


def test_business_meaning_is_filled_in():
    assert all(len(f.business_meaning) > 30 for f in ONBOARDING_FIELDS)


def test_markdown_has_one_table_row_per_field():
    doc = render_markdown()
    assert sum(line.startswith("| `") for line in doc.splitlines()) == len(ONBOARDING_FIELDS)
    assert "Completed < In Progress < Delayed" in doc


def test_committed_doc_is_up_to_date():
    assert main(["--check"]) == 0


def test_drift_is_reported(tmp_path):
    frame = pd.DataFrame(columns=[f.name for f in ONBOARDING_FIELDS if f.name != "buddy_assigned"] + ["Hire Source"])
    problems = drift_problems(frame, doc_path=tmp_path / "missing.md")
    assert "column not in dictionary: hire_source" in problems
    assert "documented column missing from dataset: buddy_assigned" in problems
    assert any("stale" in p for p in problems)
