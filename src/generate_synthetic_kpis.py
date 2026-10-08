"""Generate twelve months of synthetic KPI history for the report demo."""

from __future__ import annotations

import csv
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "data" / "sample_kpis.csv"

SEED = 7
MONTHS = [f"2025-{month:02d}" for month in range(1, 13)]

# business area, KPI, unit, higher is better, target, start value, end value, monthly noise
KPIS = [
    ("Operations", "Order Fulfillment Rate", "%", True, 95.0, 90.5, 96.2, 0.6),
    ("Operations", "Average Processing Time", "days", False, 3.5, 4.9, 3.7, 0.12),
    ("Customer Experience", "Customer Satisfaction", "%", True, 90.0, 84.0, 88.0, 0.7),
    ("Customer Experience", "Response Time", "hours", False, 2.0, 3.2, 1.8, 0.12),
    ("Finance", "Budget Utilization", "%", True, 80.0, 75.0, 70.0, 1.0),
    ("Data Quality", "Validated Records", "%", True, 98.0, 92.0, 97.8, 0.5),
]
FIELDS = ["month", "business_area", "kpi_name", "value", "target_value", "unit", "higher_is_better"]


def build_rows() -> list[dict[str, object]]:
    """Each KPI drifts from its start value to its end value with seeded noise."""
    rng = random.Random(SEED)
    rows = []
    last = len(MONTHS) - 1
    for area, name, unit, higher_is_better, target, start, end, noise in KPIS:
        for index, month in enumerate(MONTHS):
            value = start + (end - start) * index / last
            if index not in (0, last):
                value += rng.uniform(-noise, noise)
            rows.append(
                {
                    "month": month,
                    "business_area": area,
                    "kpi_name": name,
                    "value": round(value, 1),
                    "target_value": target,
                    "unit": unit,
                    "higher_is_better": str(higher_is_better).lower(),
                }
            )
    return rows


def main() -> None:
    rows = build_rows()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
