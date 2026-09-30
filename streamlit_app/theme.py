"""Design tokens for the Onboarding Ops dashboard.

One place for page chrome, tab order and status/tone colours, so every component
speaks the same visual language. Tones use Streamlit's built-in coloured markdown
(``:green[...]``) rather than injected CSS, so they stay legible in light and dark themes.
"""
from __future__ import annotations

from pipeline.export import STATUS_COLOURS  # charts and dashboard share one status palette

PAGE_TITLE = "VibeCheck · Onboarding Ops"
TABS = ("Overview", "Cohort", "Root causes", "Alerts")

TONE_BADGES = {
    "good": ":green[● On target]",
    "warn": ":orange[● Watch]",
    "bad": ":red[● Off target]",
    "neutral": ":gray[● No data]",
}

STATUS_BADGES = {
    "Completed": ":green[Completed]",
    "In Progress": ":orange[In Progress]",
    "Delayed": ":red[Delayed]",
}

__all__ = ["PAGE_TITLE", "STATUS_BADGES", "STATUS_COLOURS", "TABS", "TONE_BADGES", "configure_page", "section"]


def configure_page() -> None:
    import streamlit as st

    st.set_page_config(page_title=PAGE_TITLE, layout="wide", initial_sidebar_state="expanded")


def section(title: str, caption: str | None = None) -> None:
    """Consistent section heading: a subheader with an optional one-line explanation."""
    import streamlit as st

    st.subheader(title)
    if caption:
        st.caption(caption)
