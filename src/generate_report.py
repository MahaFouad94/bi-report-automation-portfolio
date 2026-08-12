"""Create an executive KPI report from synthetic CSV data."""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "sample_kpis.csv"
REPORT_PATH = ROOT / "reports" / "sample_executive_report.md"


def as_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def format_value(value: float, unit: str) -> str:
    if unit == "%":
        return f"{value:.1f}%"
    return f"{value:.1f} {unit}"


def format_delta(value: float, unit: str, signed: bool = True) -> str:
    sign = "+" if signed and value > 0 else ""
    if unit == "%":
        return f"{sign}{value:.1f}%"
    return f"{sign}{value:.1f} {unit}"


def score_status(current: float, target: float, higher_is_better: bool) -> str:
    if higher_is_better:
        ratio = current / target if target else 0
        if ratio >= 1:
            return "On Track"
        if ratio >= 0.95:
            return "Watch"
        return "Needs Attention"

    ratio = target / current if current else 0
    if current <= target:
        return "On Track"
    if ratio >= 0.95:
        return "Watch"
    return "Needs Attention"


def direction_text(change: float, higher_is_better: bool) -> str:
    if change == 0:
        return "flat"
    improved = change > 0 if higher_is_better else change < 0
    return "improved" if improved else "declined"


def load_rows() -> list[dict[str, str]]:
    with DATA_PATH.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def build_report(rows: list[dict[str, str]]) -> str:
    enriched = []
    for row in rows:
        current = float(row["current_value"])
        previous = float(row["previous_value"])
        target = float(row["target_value"])
        higher_is_better = as_bool(row["higher_is_better"])
        change = current - previous
        target_gap = current - target if higher_is_better else target - current
        status = score_status(current, target, higher_is_better)

        enriched.append(
            {
                **row,
                "current": current,
                "previous": previous,
                "target": target,
                "higher_is_better_bool": higher_is_better,
                "change": change,
                "target_gap": target_gap,
                "status": status,
            }
        )

    by_status = defaultdict(int)
    for row in enriched:
        by_status[row["status"]] += 1

    on_track = by_status["On Track"]
    watch = by_status["Watch"]
    attention = by_status["Needs Attention"]

    lines = [
        "# Sample Executive KPI Report",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "Data note: This report uses synthetic portfolio data only.",
        "",
        "## Executive Summary",
        "",
        (
            f"The portfolio contains {len(enriched)} KPIs across "
            f"{len(set(row['business_area'] for row in enriched))} business areas. "
            f"{on_track} KPIs are on track, {watch} require monitoring, and "
            f"{attention} need attention."
        ),
        "",
        "## KPI Status Table",
        "",
        "| Business Area | KPI | Current | Previous | Target | Change | Status |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]

    for row in enriched:
        unit = row["unit"]
        lines.append(
            "| {area} | {kpi} | {current} | {previous} | {target} | {change} | {status} |".format(
                area=row["business_area"],
                kpi=row["kpi_name"],
                current=format_value(row["current"], unit),
                previous=format_value(row["previous"], unit),
                target=format_value(row["target"], unit),
                change=format_delta(row["change"], unit),
                status=row["status"],
            )
        )

    lines.extend(["", "## Commentary", ""])

    for row in enriched:
        unit = row["unit"]
        lines.append(
            "- {kpi}: {direction} versus the previous period by {change}; status is {status}.".format(
                kpi=row["kpi_name"],
                direction=direction_text(row["change"], row["higher_is_better_bool"]),
                change=format_delta(abs(row["change"]), unit, signed=False),
                status=row["status"],
            )
        )

    lines.extend(
        [
            "",
            "## Recommended Next Actions",
            "",
            "- Review KPIs marked `Needs Attention` before the next business review.",
            "- Validate source freshness before distributing the final report.",
            "- Add owner, action, and due-date fields if this report becomes an operating tracker.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    rows = load_rows()
    report = build_report(rows)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Wrote report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
