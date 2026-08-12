"""Generate synthetic KPI data for the portfolio report demo."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "data" / "sample_kpis.csv"


ROWS = [
    {
        "business_area": "Operations",
        "kpi_name": "Order Fulfillment Rate",
        "current_value": 96.2,
        "previous_value": 91.8,
        "target_value": 95.0,
        "unit": "%",
        "higher_is_better": "true",
    },
    {
        "business_area": "Operations",
        "kpi_name": "Average Processing Time",
        "current_value": 3.7,
        "previous_value": 4.4,
        "target_value": 3.5,
        "unit": "days",
        "higher_is_better": "false",
    },
    {
        "business_area": "Customer Experience",
        "kpi_name": "Customer Satisfaction",
        "current_value": 88.0,
        "previous_value": 85.5,
        "target_value": 90.0,
        "unit": "%",
        "higher_is_better": "true",
    },
    {
        "business_area": "Customer Experience",
        "kpi_name": "Response Time",
        "current_value": 1.8,
        "previous_value": 2.8,
        "target_value": 2.0,
        "unit": "hours",
        "higher_is_better": "false",
    },
    {
        "business_area": "Finance",
        "kpi_name": "Budget Utilization",
        "current_value": 70.0,
        "previous_value": 72.0,
        "target_value": 80.0,
        "unit": "%",
        "higher_is_better": "true",
    },
    {
        "business_area": "Data Quality",
        "kpi_name": "Validated Records",
        "current_value": 97.8,
        "previous_value": 93.4,
        "target_value": 98.0,
        "unit": "%",
        "higher_is_better": "true",
    },
]


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=ROWS[0].keys())
        writer.writeheader()
        writer.writerows(ROWS)

    print(f"Wrote synthetic KPI data to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
