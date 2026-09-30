from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from streamlit_app.components.cohort_filters import CohortFilter, apply_cohort_filter

PAGE = Path(__file__).resolve().parents[1] / "streamlit_app" / "onboarding_ops.py"

HIRES = pd.DataFrame({
    "employee_id": [1, 2, 3, 4, 5],
    "Department": ["Sales", "Sales", "Research & Development", "Human Resources", "Sales"],
    "onboarding_status": ["Completed", "Delayed", "In Progress", "Completed", "Completed"],
    "YearsAtCompany": [0, 1, 3, 12, 7],
    "buddy_assigned": pd.array([True, False, True, None, True], dtype="boolean"),
    "is_new_hire": [True, True, True, False, False],
})


def ids(cohort: CohortFilter) -> list[int]:
    return apply_cohort_filter(HIRES, cohort)["employee_id"].tolist()


def test_no_filter_keeps_everyone():
    assert ids(CohortFilter()) == [1, 2, 3, 4, 5]
    assert not CohortFilter().is_active and CohortFilter().describe() == "All hires"


@pytest.mark.parametrize("cohort, expected", [
    (CohortFilter(departments=("Sales",)), [1, 2, 5]),
    (CohortFilter(statuses=("Delayed", "In Progress")), [2, 3]),
    (CohortFilter(tenure_bands=("0-1 yrs",)), [1, 2]),
    (CohortFilter(tenure_bands=("6-10 yrs", "10+ yrs")), [4, 5]),
    (CohortFilter(buddy="Without buddy"), [2]),          # unknown buddy flag matches neither option
    (CohortFilter(buddy="With buddy"), [1, 3, 5]),
    (CohortFilter(new_hires_only=True, departments=("Sales",)), [1, 2]),
])
def test_filters_combine_with_and(cohort, expected):
    assert ids(cohort) == expected


def test_description_and_validation():
    cohort = CohortFilter(departments=("Sales",), tenure_bands=("0-1 yrs",), buddy="Without buddy", new_hires_only=True)
    assert cohort.describe() == "New hires · Sales · Tenure 0-1 yrs · without buddy"
    with pytest.raises(ValueError):
        CohortFilter(tenure_bands=("forever",))
    with pytest.raises(ValueError):
        CohortFilter(buddy="Maybe")


@pytest.fixture
def app():
    return AppTest.from_file(str(PAGE), default_timeout=60).run()


def test_page_filters_to_new_hires(app):
    app.toggle(key="cohort_new_hires").set_value(True).run()
    assert not app.exception
    assert app.caption[0].value.startswith("Showing 215 of 1,470 hires · New hires")
    completion = next(m for m in app.metric if m.label == "Onboarding completion rate")
    assert completion.delta.endswith("pts vs company")


def test_page_handles_an_empty_cohort(app):
    app.multiselect(key="cohort_departments").set_value(["Human Resources"])
    app.multiselect(key="cohort_statuses").set_value(["Delayed"]).run()
    assert not app.exception
    assert "No hires match" in app.info[0].value
    assert len(app.metric) == 0
