"""Workspace configuration for the VibeCheck data pipeline.

Every path the pipeline touches is resolved here, so scripts, notebooks, tests
and CI behave the same no matter which directory they are launched from.
"""
from __future__ import annotations

import logging
import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

DATASETS = ("employees", "onboarding", "tool_usage", "support_tickets")

_ROOT_MARKER = Path("data") / "employees.csv"


def find_repo_root(start: Path | None = None) -> Path:
    """Walk up from ``start`` until a directory containing data/employees.csv is found."""
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / _ROOT_MARKER).is_file():
            return candidate
    raise FileNotFoundError(
        f"Could not locate the VibeCheck repo root from {here}: no "
        f"{_ROOT_MARKER.as_posix()} here or in any parent directory. "
        "Set VIBECHECK_DATA_DIR to the folder that holds the datasets."
    )


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    output_dir: Path

    def dataset_path(self, name: str, suffix: str = ".csv") -> Path:
        if name not in DATASETS:
            raise KeyError(f"Unknown dataset {name!r}; expected one of: {', '.join(DATASETS)}")
        return self.data_dir / f"{name}{suffix}"


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Build settings from environment overrides, falling back to the repo layout.

    VIBECHECK_DATA_DIR    folder with employees/onboarding/tool_usage/support_tickets files
    VIBECHECK_OUTPUT_DIR  where exports and local databases are written (default: <root>/outputs)
    """
    env = os.environ if env is None else env
    data_override = env.get("VIBECHECK_DATA_DIR")
    if data_override:
        data_dir = Path(data_override).expanduser().resolve()
        root = data_dir.parent
    else:
        root = find_repo_root(Path(__file__).parent)
        data_dir = root / "data"
    output_dir = Path(env.get("VIBECHECK_OUTPUT_DIR") or root / "outputs").expanduser().resolve()
    return Settings(data_dir=data_dir, output_dir=output_dir)


def configure_logging(level: int = logging.INFO) -> None:
    """One log format for every pipeline CLI."""
    logging.basicConfig(level=level, format="%(levelname)-7s %(name)s: %(message)s")
