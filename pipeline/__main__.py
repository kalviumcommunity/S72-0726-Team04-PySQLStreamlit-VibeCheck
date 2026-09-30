"""VibeCheck pipeline command line.

usage: python -m pipeline <command> [options]

commands:
  validate     run every data check CI runs (contracts, dictionary, SQL vs Python)
  ingest       load one dataset and print a summary
  contracts    validate every dataset against the shared schema contracts
  dictionary   print / regenerate / check the onboarding data dictionary
  kpis         run a named SQL query from pipeline/sql/
  rankings     fastest completed hires per department (SQL window functions)
  reconcile    check that SQL and Python KPIs agree
  export       write cleaned data, analysis tables, charts and a manifest
  alerts       flag hires whose onboarding needs attention
  summary      Markdown run summary for GitHub Actions

Run `python -m pipeline <command> --help` for a command's options.
"""
from __future__ import annotations

import importlib
import sys

COMMANDS = {
    "validate": "pipeline.validate",
    "ingest": "pipeline.ingest",
    "contracts": "pipeline.schemas",
    "dictionary": "pipeline.data_dictionary",
    "kpis": "pipeline.sql_queries",
    "rankings": "pipeline.rankings",
    "reconcile": "pipeline.reconcile",
    "export": "pipeline.export",
    "alerts": "pipeline.alerts",
    "summary": "pipeline.ci_summary",
}


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    if argv[0] not in COMMANDS:
        print(f"unknown command {argv[0]!r}\n\n{__doc__.strip()}", file=sys.stderr)
        return 2
    return importlib.import_module(COMMANDS[argv[0]]).main(argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
