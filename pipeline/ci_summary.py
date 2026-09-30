"""Render a Markdown run summary for GitHub Actions ($GITHUB_STEP_SUMMARY).

    python -m pipeline summary --validation validation.json \
        --manifest outputs/manifest.json --alerts outputs/alerts.csv >> "$GITHUB_STEP_SUMMARY"

Every input is optional, so a run that failed half-way still gets a useful summary.
Output is plain ASCII so it also prints on a Windows console.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .alerts import SEVERITIES


def validation_section(payload: dict | None) -> list[str]:
    if payload is None:
        return ["## Data validation", "", "_Validation did not run._"]
    lines = [f"## Data validation: {'PASSED' if payload['passed'] else 'FAILED'}", "",
             "| Step | Result | Details |", "| :--- | :---: | :--- |"]
    for step in payload["steps"]:
        details = "; ".join(step["details"][:3]).replace("|", "\\|")
        lines.append(f"| {step['name']} | {'pass' if step['passed'] else '**FAIL**'} | {details} |")
    return lines


def export_section(manifest: dict | None) -> list[str]:
    if manifest is None:
        return ["## Export", "", "_No export was produced._"]
    inputs = ", ".join(f"{i['dataset']} ({i['rows']:,} rows)" for i in manifest["inputs"])
    lines = ["## Export", "", f"Inputs: {inputs}", "", "| Output | Rows |", "| :--- | ---: |"]
    for output in manifest["outputs"]:
        rows = "" if output["rows"] is None else f"{output['rows']:,}"
        lines.append(f"| `{output['path']}` | {rows} |")
    return lines


def alerts_section(alerts: pd.DataFrame | None) -> list[str]:
    if alerts is None:
        return ["## Onboarding alerts", "", "_Alerts were not evaluated._"]
    if alerts.empty:
        return ["## Onboarding alerts", "", "No alerts fired."]
    hires = {s: alerts.loc[alerts["severity"] == s, "employee_id"].nunique() for s in SEVERITIES}
    lines = ["## Onboarding alerts", "",
             " | ".join(f"**{s}**: {n} hires" for s, n in hires.items()), "",
             "| Severity | Rule | Hires |", "| :--- | :--- | ---: |"]
    by_rule = alerts.groupby(["severity", "code"])["employee_id"].nunique().reset_index()
    by_rule["order"] = by_rule["severity"].map(SEVERITIES.index)
    for row in by_rule.sort_values(["order", "employee_id"], ascending=[True, False]).itertuples(index=False):
        lines.append(f"| {row.severity} | {row.code} | {row.employee_id} |")
    return lines


def render_summary(validation: dict | None = None, manifest: dict | None = None,
                   alerts: pd.DataFrame | None = None) -> str:
    sections = [validation_section(validation), export_section(manifest), alerts_section(alerts)]
    return "\n\n".join("\n".join(section) for section in sections) + "\n"


def _read_json(path: Path | None) -> dict | None:
    return json.loads(path.read_text(encoding="utf-8")) if path and path.is_file() else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m pipeline summary")
    parser.add_argument("--validation", type=Path, help="JSON from `python -m pipeline validate --json`")
    parser.add_argument("--manifest", type=Path, help="manifest.json from `python -m pipeline export`")
    parser.add_argument("--alerts", type=Path, help="alerts.csv from `python -m pipeline alerts`")
    args = parser.parse_args(argv)
    alerts = pd.read_csv(args.alerts) if args.alerts and args.alerts.is_file() else None
    print(render_summary(_read_json(args.validation), _read_json(args.manifest), alerts), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
