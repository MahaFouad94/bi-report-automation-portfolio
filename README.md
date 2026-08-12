# BI Report Automation Portfolio

An NDA-safe portfolio project that demonstrates how KPI data can be converted into an executive-ready performance report.

This repository uses only synthetic sample data. It does not contain client files, internal dashboards, confidential metrics, private business logic, or data from any employer or signed NDA.

## Project Goal

Business teams often need fast, repeatable reporting from dashboards and KPI tables. This project shows a simple reporting workflow:

1. Generate synthetic KPI data.
2. Compare current performance against targets and previous-period values.
3. Classify KPI status.
4. Create a concise executive report in Markdown.

The structure is intentionally simple so the workflow is easy to inspect, reuse, and explain.

## What This Demonstrates

- Python automation for business reporting
- KPI variance analysis
- Target and previous-period comparison
- Executive summary generation
- Clean project documentation
- Safe portfolio design without sensitive data

## Repository Structure

```text
.
├── data/
│   └── sample_kpis.csv
├── docs/
│   ├── nda-safety.md
│   └── project-notes.md
├── reports/
│   └── sample_executive_report.md
├── src/
│   ├── generate_report.py
│   └── generate_synthetic_kpis.py
├── .gitignore
├── LICENSE
└── README.md
```

## Quick Start

Generate the synthetic KPI dataset:

```bash
python src/generate_synthetic_kpis.py
```

Generate the executive report:

```bash
python src/generate_report.py
```

The generated output will be saved to:

```text
reports/sample_executive_report.md
```

## Sample KPI Logic

Each KPI includes:

- Business area
- KPI name
- Current value
- Previous value
- Target value
- Unit
- Higher-is-better flag

The report calculates:

- Change from previous period
- Gap to target
- Status: `On Track`, `Watch`, or `Needs Attention`

## Example Use Cases

This public version is generic, but the same pattern can support:

- Monthly business reviews
- Dashboard narrative summaries
- KPI monitoring reports
- Data-quality summaries
- Executive status updates

## Privacy And NDA Position

This project is designed for public portfolio use. All data is invented, and all business areas are generic.

See [docs/nda-safety.md](docs/nda-safety.md) for the safety checklist.

## Tools

- Python
- CSV
- Markdown
- GitHub

## Author

Maha Fouad

Data Scientist | BI Developer | AI Automation Engineer
