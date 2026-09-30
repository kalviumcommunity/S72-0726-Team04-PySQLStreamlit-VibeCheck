"""Export cleaned datasets, analysis tables and charts, with a provenance manifest.

    python -m pipeline export                        # -> outputs/
    python -m pipeline export --out build/run --no-charts

    clean/onboarding_clean.csv       cleaned + standardised onboarding records
    clean/onboarding_features.csv    merged feature table, one row per hire
    analysis/*.csv                   distribution, histogram, outliers, delay root causes
    charts/*.html                    interactive Plotly charts
    manifest.json                    input checksums -> output rows and checksums
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from . import __version__
from .analysis.distribution import describe_completion_times, histogram
from .analysis.root_cause import rank_root_causes
from .config import DATASETS, Settings, configure_logging, load_settings
from .features import engineer_features
from .ingest import load_dataset
from .merge import merge_onboarding_tool_usage
from .outliers import detect_completion_outliers
from .standardize import prepare_onboarding

log = logging.getLogger(__name__)

STATUS_COLOURS = {"Completed": "#2e7d32", "In Progress": "#f9a825", "Delayed": "#c62828"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_charts(features: pd.DataFrame, root_causes: pd.DataFrame) -> dict:
    """Plotly figures keyed by output name; pure, so the dashboard can reuse them."""
    import plotly.express as px

    order = {"onboarding_status": list(STATUS_COLOURS)}
    days = px.histogram(features.assign(onboarding_days=features["onboarding_days"].astype("float64")),
                        x="onboarding_days", color="onboarding_status", nbins=40, barmode="overlay",
                        category_orders=order, color_discrete_map=STATUS_COLOURS,
                        title="Onboarding days by status", labels={"onboarding_days": "Onboarding days"})
    mix = (features.groupby(["Department", "onboarding_status"], observed=True).size()
                   .rename("hires").reset_index())
    mix["share_pct"] = (100 * mix["hires"] / mix.groupby("Department")["hires"].transform("sum")).round(2)
    status = px.bar(mix, x="Department", y="share_pct", color="onboarding_status", category_orders=order,
                    color_discrete_map=STATUS_COLOURS, hover_data=["hires"],
                    title="Onboarding status mix by department", labels={"share_pct": "Share of hires (%)"})
    causes = root_causes[~root_causes["symptom"] & np.isfinite(root_causes["lift"])].sort_values("lift")
    lift = px.bar(causes, x="lift", y="description", orientation="h", text="lift",
                  title="Delay-rate lift by factor (new hires)",
                  labels={"lift": "Delay rate with factor / without", "description": ""})
    for figure in (days, status, lift):
        figure.update_layout(template="plotly_white", legend_title_text="")
    return {"completion_time_histogram": days, "status_by_department": status, "delay_root_causes": lift}


def export_all(settings: Settings | None = None, out_dir: str | Path | None = None,
               include_charts: bool = True) -> dict:
    settings = settings or load_settings()
    out = Path(out_dir or settings.output_dir)
    frames, inputs = {}, []
    for name in DATASETS:
        frames[name], report = load_dataset(name, settings=settings)
        inputs.append({"dataset": name, "file": report.source.name, "rows": report.rows, "sha256": report.sha256})

    onboarding = prepare_onboarding(frames["onboarding"])
    merged, join = merge_onboarding_tool_usage(onboarding, frames["tool_usage"])
    features = engineer_features(merged, frames["employees"])
    root_causes = rank_root_causes(features)
    outliers = detect_completion_outliers(features, group_by="Department")

    tables = {
        "clean/onboarding_clean.csv": onboarding,
        "clean/onboarding_features.csv": features,
        "analysis/completion_time_distribution.csv": describe_completion_times(features, by="onboarding_status"),
        "analysis/completion_time_histogram.csv": histogram(features),
        "analysis/completion_outliers.csv": outliers[outliers["is_outlier"]],
        "analysis/delay_root_causes.csv": root_causes,
    }
    outputs = []
    for relative, frame in tables.items():
        path = out / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False, lineterminator="\n")
        outputs.append({"path": relative, "rows": len(frame), "sha256": _sha256(path)})
    if include_charts:
        for name, figure in build_charts(features, root_causes).items():
            path = out / "charts" / f"{name}.html"
            path.parent.mkdir(parents=True, exist_ok=True)
            figure.write_html(path, include_plotlyjs="cdn")
            outputs.append({"path": f"charts/{name}.html", "rows": None, "sha256": _sha256(path)})

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pipeline_version": __version__,
        "inputs": inputs,
        "join": {"onboarding_rows": join.onboarding_rows, "matched": join.matched,
                 "orphan_tool_employee_ids": list(join.orphan_tool_employee_ids)},
        "outputs": outputs,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    log.info("exported %d files to %s", len(outputs), out)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m pipeline export")
    parser.add_argument("--out", type=Path, help="output folder (default: VIBECHECK_OUTPUT_DIR or outputs/)")
    parser.add_argument("--no-charts", action="store_true", help="skip the Plotly HTML charts")
    args = parser.parse_args(argv)
    configure_logging()
    try:
        manifest = export_all(out_dir=args.out, include_charts=not args.no_charts)
    except (FileNotFoundError, ValueError) as exc:
        log.error("%s", exc)
        return 1
    for item in manifest["outputs"]:
        rows = "" if item["rows"] is None else f"{item['rows']:>6} rows"
        print(f"{item['path']:<48}{rows}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
