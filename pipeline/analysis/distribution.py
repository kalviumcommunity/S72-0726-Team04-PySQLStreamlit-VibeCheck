"""Distribution analysis of onboarding completion times.

    python -m pipeline.analysis.distribution                  # Markdown report to stdout
    python -m pipeline.analysis.distribution --output report.md
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd

from . import markdown_table

PERCENTILES = (0.10, 0.25, 0.50, 0.75, 0.90)


def describe_completion_times(df: pd.DataFrame, column: str = "onboarding_days",
                              by: str | None = None) -> pd.DataFrame:
    """Count, centre, spread, percentiles and shape - overall or per group."""
    values = df.loc[df[column].notna()].assign(**{column: lambda d: d[column].astype("float64")})
    groups = [("All", values)] if by is None else [(str(k), g) for k, g in values.groupby(by, observed=True)]
    rows = []
    for name, group in groups:
        v = group[column]
        quantiles = v.quantile(PERCENTILES)
        rows.append({
            "group": name,
            "count": len(v),
            "mean": v.mean(),
            "std": v.std(),
            "min": v.min(),
            **{f"p{round(p * 100)}": quantiles[p] for p in PERCENTILES},
            "max": v.max(),
            "skew": v.skew() if len(v) > 2 else float("nan"),
            "cv": v.std() / v.mean() if v.mean() else float("nan"),
        })
    return pd.DataFrame(rows).round(2)


def histogram(df: pd.DataFrame, column: str = "onboarding_days", bin_width: int = 2) -> pd.DataFrame:
    """Fixed-width bins [start, end) with counts and shares."""
    values = df[column].dropna().astype("float64")
    start = math.floor(values.min() / bin_width) * bin_width
    edges = np.arange(start, values.max() + bin_width + 1, bin_width)
    counts, edges = np.histogram(values, bins=edges)
    table = pd.DataFrame({"bin_start": edges[:-1].astype(int), "bin_end": edges[1:].astype(int), "count": counts})
    table["share"] = (table["count"] / len(values)).round(4)
    return table


def key_findings(features: pd.DataFrame) -> list[str]:
    completed = features[features["onboarding_status"].eq("Completed")]
    overall = describe_completion_times(completed).iloc[0]
    by_dept = describe_completion_times(completed, by="Department").sort_values("p50")
    by_status = describe_completion_times(features, by="onboarding_status").set_index("group")
    slowest, fastest = by_dept.iloc[-1], by_dept.iloc[0]
    findings = [
        f"Completed onboardings take a median of {overall['p50']:.0f} days; "
        f"90% finish within {overall['p90']:.0f} days.",
        f"Spread is {'moderate' if overall['cv'] < 0.5 else 'high'} "
        f"(coefficient of variation {overall['cv']:.2f}, skew {overall['skew']:+.2f}).",
        f"Slowest department by median: {slowest['group']} ({slowest['p50']:.0f} days); "
        f"fastest: {fastest['group']} ({fastest['p50']:.0f} days).",
    ]
    if "Delayed" in by_status.index:
        ratio = by_status.loc["Delayed", "p50"] / overall["p50"]
        findings.append(f"Delayed hires have already spent {ratio:.1f}x the median completed time "
                        f"({by_status.loc['Delayed', 'p50']:.0f} days).")
    return findings


def distribution_report(features: pd.DataFrame, bin_width: int = 2) -> str:
    completed = features[features["onboarding_status"].eq("Completed")]
    hist = histogram(features, bin_width=bin_width)
    scale = 40 / hist["count"].max()
    bars = [f"{start:>3}-{end - 1:<3} {'#' * (max(1, round(count * scale)) if count else 0):<40} {count}"
            for start, end, count in zip(hist["bin_start"], hist["bin_end"], hist["count"])]
    return "\n\n".join([
        "# Onboarding completion-time distribution",
        "## Key findings\n" + "\n".join(f"- {f}" for f in key_findings(features)),
        f"## Completed hires (n={len(completed)})\n" + markdown_table(describe_completion_times(completed)),
        "## By status (open onboardings show days elapsed so far)\n"
        + markdown_table(describe_completion_times(features, by="onboarding_status")),
        "## Completed hires by department\n" + markdown_table(describe_completion_times(completed, by="Department")),
        f"## Histogram, all hires ({bin_width}-day bins)\n```\n" + "\n".join(bars) + "\n```",
    ]) + "\n"


def main(argv: list[str] | None = None) -> int:
    from ..features import build_feature_table

    parser = argparse.ArgumentParser(prog="python -m pipeline.analysis.distribution")
    parser.add_argument("--output", type=Path, help="write the Markdown report to this file")
    parser.add_argument("--bin-width", type=int, default=2)
    args = parser.parse_args(argv)
    report = distribution_report(build_feature_table(), bin_width=args.bin_width)
    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
