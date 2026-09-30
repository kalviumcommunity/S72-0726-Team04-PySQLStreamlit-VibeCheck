"""One command that tells CI whether the data and the pipeline are healthy.

Steps, in order (a failed contract check stops the run - later steps would only
fail again on the same broken data):

  1. contracts                  every dataset matches the shared schema contracts
  2. data_dictionary            onboarding columns and docs/data_dictionary are in sync
  3. sql_python_reconciliation  SQL KPIs (throwaway SQLite) agree with the pandas pipeline

    python -m pipeline validate
    python -m pipeline validate --json validation.json   # machine-readable, for CI summaries
"""
from __future__ import annotations

import argparse
import json
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .config import Settings
from .data_dictionary import drift_problems
from .db import get_engine, stage_tables
from .features import build_feature_table
from .reconcile import reconcile
from .schemas import load_frames, validate_datasets


@dataclass
class StepResult:
    name: str
    passed: bool
    details: list[str] = field(default_factory=list)


def _reconciliation(frames: dict, settings: Settings | None) -> StepResult:
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        engine = get_engine(f"sqlite:///{Path(tmp, 'validate.db').as_posix()}")
        try:
            stage_tables(engine, frames)
            checks = reconcile(engine, build_feature_table(settings))
        finally:
            engine.dispose()  # release the file so the temp dir can be removed on Windows
    failed = [f"{c.name}: sql={c.sql_value} python={c.python_value}" for c in checks if not c.passed]
    return StepResult("sql_python_reconciliation", not failed, failed or [f"{len(checks)} checks agree"])


def run_validation(settings: Settings | None = None) -> list[StepResult]:
    try:
        frames = load_frames(settings)
    except (FileNotFoundError, ValueError) as exc:
        return [StepResult("contracts", False, [str(exc)])]

    issues = validate_datasets(frames)
    errors = [i for i in issues if i.severity == "error"]
    results = [StepResult("contracts", not errors, [str(i) for i in issues] or ["all datasets match"])]
    if errors:
        return results

    drift = drift_problems(frames["onboarding"])
    results.append(StepResult("data_dictionary", not drift, drift or ["dictionary and dataset agree"]))
    results.append(_reconciliation(frames, settings))
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m pipeline validate")
    parser.add_argument("--json", type=Path, help="also write the results to this JSON file")
    args = parser.parse_args(argv)

    results = run_validation()
    passed = all(r.passed for r in results)
    for result in results:
        print(f"{'PASS' if result.passed else 'FAIL'}  {result.name}")
        for detail in result.details:
            print(f"      {detail}")
    if args.json:
        payload = {"passed": passed, "steps": [asdict(r) for r in results]}
        args.json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
