"""Create an executive KPI report from synthetic monthly KPI history."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "sample_kpis.csv"
REPORT_PATH = ROOT / "reports" / "sample_executive_report.md"
CHART_PATH = ROOT / "reports" / "kpi_trends.svg"

WATCH_THRESHOLD = 0.95
SPARK_BARS = "▁▂▃▄▅▆▇█"
STATUS_COLORS = {"On Track": "#16a34a", "Watch": "#d97706", "Needs Attention": "#dc2626"}


def as_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def format_value(value: float, unit: str) -> str:
    if unit == "%":
        return f"{value:.1f}%"
    return f"{value:.1f} {unit}"


def format_delta(value: float, unit: str, signed: bool = True) -> str:
    sign = "+" if signed and value > 0 else ""
    if unit == "%":
        return f"{sign}{value:.1f} pts"
    return f"{sign}{value:.1f} {unit}"


def score_status(current: float, target: float, higher_is_better: bool) -> str:
    """Compare a KPI with its target, allowing a 5% band before raising attention."""
    if higher_is_better:
        attainment = current / target if target else 0.0
    else:
        attainment = target / current if current else 0.0
    if attainment >= 1:
        return "On Track"
    if attainment >= WATCH_THRESHOLD:
        return "Watch"
    return "Needs Attention"


def direction_text(change: float, higher_is_better: bool) -> str:
    if change == 0:
        return "was flat"
    improved = change > 0 if higher_is_better else change < 0
    return "improved" if improved else "declined"


def movement_text(change: float, unit: str, higher_is_better: bool) -> str:
    """'improved by 0.6 pts', or just 'was flat' when nothing moved."""
    direction = direction_text(change, higher_is_better)
    if change == 0:
        return direction
    return f"{direction} by {format_delta(abs(change), unit, signed=False)}"


def sparkline(values: list[float]) -> str:
    low, high = min(values), max(values)
    if high == low:
        return SPARK_BARS[0] * len(values)
    scale = (len(SPARK_BARS) - 1) / (high - low)
    return "".join(SPARK_BARS[round((value - low) * scale)] for value in values)


def load_rows(path: Path = DATA_PATH) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def summarize(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    """One summary per KPI: latest value against target, last month and the first month."""
    history: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        history[(row["business_area"], row["kpi_name"])].append(row)

    summaries = []
    for (area, name), kpi_rows in history.items():
        kpi_rows.sort(key=lambda row: row["month"])
        values = [float(row["value"]) for row in kpi_rows]
        latest = kpi_rows[-1]
        target = float(latest["target_value"])
        higher_is_better = as_bool(latest["higher_is_better"])
        summaries.append(
            {
                "business_area": area,
                "kpi_name": name,
                "unit": latest["unit"],
                "higher_is_better": higher_is_better,
                "month": latest["month"],
                "values": values,
                "current": values[-1],
                "previous": values[-2] if len(values) > 1 else values[-1],
                "target": target,
                "month_change": values[-1] - values[-2] if len(values) > 1 else 0.0,
                "period_change": values[-1] - values[0],
                "status": score_status(values[-1], target, higher_is_better),
            }
        )
    return summaries


def build_chart(summaries: list[dict[str, object]]) -> str:
    """Small-multiple line charts, one per KPI, with the target as a dashed line."""
    columns, cell_w, cell_h, pad = 3, 280, 150, 18
    rows_needed = -(-len(summaries) // columns)
    width, height = columns * cell_w, rows_needed * cell_h + 10
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'font-family="Segoe UI, Arial, sans-serif" font-size="12">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
    ]
    for index, kpi in enumerate(summaries):
        x0 = (index % columns) * cell_w + pad
        y0 = (index // columns) * cell_h + 34
        plot_w, plot_h = cell_w - 2 * pad, cell_h - 64
        values, target = kpi["values"], kpi["target"]
        low, high = min(values + [target]), max(values + [target])
        span = (high - low) or 1.0

        def y_at(value: float) -> float:
            return y0 + plot_h - (value - low) / span * plot_h

        points = " ".join(
            f"{x0 + plot_w * i / (len(values) - 1):.1f},{y_at(value):.1f}" for i, value in enumerate(values)
        )
        color = STATUS_COLORS[kpi["status"]]
        parts.extend(
            [
                f'<text x="{x0}" y="{y0 - 14}" font-weight="600" fill="#1f2937">{kpi["kpi_name"]}</text>',
                f'<line x1="{x0}" y1="{y_at(target):.1f}" x2="{x0 + plot_w}" y2="{y_at(target):.1f}" '
                'stroke="#9ca3af" stroke-dasharray="4 3"/>',
                f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.5"/>',
                f'<text x="{x0}" y="{y0 + plot_h + 18}" fill="#4b5563">'
                f'{format_value(kpi["current"], kpi["unit"])} against target {format_value(target, kpi["unit"])}'
                f" · {kpi['status']}</text>",
            ]
        )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def build_report(rows: list[dict[str, str]]) -> str:
    summaries = summarize(rows)
    counts = Counter(kpi["status"] for kpi in summaries)
    months = sorted({row["month"] for row in rows})
    areas = {kpi["business_area"] for kpi in summaries}

    lines = [
        "# Sample Executive KPI Report",
        "",
        f"Reporting month: {months[-1]} (history from {months[0]})",
        "",
        "Data note: This report uses synthetic portfolio data only.",
        "",
        "## Executive Summary",
        "",
        (
            f"The report covers {len(summaries)} KPIs across {len(areas)} business areas. "
            f"{counts['On Track']} are on track, {counts['Watch']} are within 5% of target and need monitoring, "
            f"and {counts['Needs Attention']} need attention."
        ),
        "",
        "![KPI trends against target](kpi_trends.svg)",
        "",
        "## KPI Status Table",
        "",
        "| Business Area | KPI | Current | Previous | Target | Change | 12-month trend | Status |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for kpi in summaries:
        unit = kpi["unit"]
        lines.append(
            f"| {kpi['business_area']} | {kpi['kpi_name']} | {format_value(kpi['current'], unit)} | "
            f"{format_value(kpi['previous'], unit)} | {format_value(kpi['target'], unit)} | "
            f"{format_delta(kpi['month_change'], unit)} | {sparkline(kpi['values'])} | {kpi['status']} |"
        )

    lines.extend(["", "## Commentary", ""])
    for kpi in summaries:
        unit = kpi["unit"]
        lines.append(
            f"- {kpi['kpi_name']} {movement_text(kpi['month_change'], unit, kpi['higher_is_better'])} "
            f"on the month and {movement_text(kpi['period_change'], unit, kpi['higher_is_better'])} "
            f"since {months[0]}; status is {kpi['status']}."
        )

    attention = [kpi["kpi_name"] for kpi in summaries if kpi["status"] == "Needs Attention"]
    lines.extend(["", "## Recommended Next Actions", ""])
    if attention:
        lines.append(f"- Agree an owner and recovery plan for: {', '.join(attention)}.")
    lines.extend(
        [
            "- Validate source freshness before distributing the final report.",
            "- Add owner, action, and due-date fields if this report becomes an operating tracker.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    rows = load_rows()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(build_report(rows), encoding="utf-8")
    CHART_PATH.write_text(build_chart(summarize(rows)), encoding="utf-8")
    print(f"Wrote report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
