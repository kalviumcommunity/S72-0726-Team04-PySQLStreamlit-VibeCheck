"""Ingestion: read raw VibeCheck datasets from CSV, JSON or JSON-lines files.

    python -m pipeline.ingest onboarding
    python -m pipeline.ingest onboarding --source exports/onboarding.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .config import DATASETS, Settings, configure_logging, load_settings

log = logging.getLogger(__name__)

# Lookup order when no explicit source is given: the committed CSV wins over exports.
SUPPORTED_SUFFIXES = (".csv", ".json", ".jsonl")


@dataclass(frozen=True)
class IngestionReport:
    dataset: str
    source: Path
    rows: int
    columns: tuple[str, ...]
    sha256: str

    def summary(self) -> str:
        return (f"{self.dataset}: {self.rows} rows x {len(self.columns)} columns "
                f"from {self.source.name} (sha256 {self.sha256[:12]})")


def _json_records(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    payload = json.loads(text)
    # Supabase / REST dumps are a bare array; some tools wrap it as {"data": [...]}.
    if isinstance(payload, dict):
        payload = payload.get("data", payload.get("records"))
    if not isinstance(payload, list):
        raise ValueError(f"{path.name}: expected a JSON array of records "
                         "or an object with a 'data' array")
    return payload


def read_table(path: str | Path) -> pd.DataFrame:
    """Read one CSV / JSON / JSONL file into a DataFrame, failing loudly on bad input."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Dataset file not found: {path}")
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError(f"Unsupported file type {suffix!r} for {path.name}; "
                         f"expected one of {', '.join(SUPPORTED_SUFFIXES)}")
    frame = pd.read_csv(path) if suffix == ".csv" else pd.DataFrame.from_records(_json_records(path))
    if frame.empty:
        raise ValueError(f"{path.name} contains no rows")
    return frame


def resolve_source(dataset: str, settings: Settings) -> Path:
    """Find the first existing file for ``dataset`` in the data folder."""
    candidates = [settings.dataset_path(dataset, suffix) for suffix in SUPPORTED_SUFFIXES]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"No file for dataset {dataset!r}; looked for: "
                            + ", ".join(c.name for c in candidates) + f" in {settings.data_dir}")


def load_dataset(dataset: str, source: str | Path | None = None,
                 settings: Settings | None = None) -> tuple[pd.DataFrame, IngestionReport]:
    """Load a named dataset and return it with a provenance report."""
    if dataset not in DATASETS:
        raise KeyError(f"Unknown dataset {dataset!r}; expected one of: {', '.join(DATASETS)}")
    path = Path(source) if source else resolve_source(dataset, settings or load_settings())
    frame = read_table(path)
    report = IngestionReport(
        dataset=dataset,
        source=path.resolve(),
        rows=len(frame),
        columns=tuple(str(c) for c in frame.columns),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    )
    log.info(report.summary())
    return frame, report


def load_onboarding(source: str | Path | None = None,
                    settings: Settings | None = None) -> pd.DataFrame:
    return load_dataset("onboarding", source, settings)[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m pipeline.ingest", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dataset", choices=DATASETS)
    parser.add_argument("--source", help="explicit CSV/JSON/JSONL file instead of data/<dataset>.*")
    args = parser.parse_args(argv)
    configure_logging()
    try:
        frame, report = load_dataset(args.dataset, args.source)
    except (FileNotFoundError, ValueError) as exc:
        log.error("%s", exc)
        return 1
    print(report.summary())
    print(frame.head().to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
