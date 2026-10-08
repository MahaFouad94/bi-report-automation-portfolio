import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from generate_report import build_report, direction_text, score_status, sparkline, summarize  # noqa: E402


def row(month, value, name="Response Time", unit="hours", target=2.0, higher_is_better="false"):
    return {
        "month": month,
        "business_area": "Customer Experience",
        "kpi_name": name,
        "value": str(value),
        "target_value": str(target),
        "unit": unit,
        "higher_is_better": higher_is_better,
    }


class ScoreStatusTests(unittest.TestCase):
    def test_higher_is_better_bands(self):
        self.assertEqual(score_status(96, 95, True), "On Track")
        self.assertEqual(score_status(91, 95, True), "Watch")
        self.assertEqual(score_status(80, 95, True), "Needs Attention")

    def test_lower_is_better_bands(self):
        self.assertEqual(score_status(1.8, 2.0, False), "On Track")
        self.assertEqual(score_status(2.1, 2.0, False), "Watch")
        self.assertEqual(score_status(3.0, 2.0, False), "Needs Attention")

    def test_zero_target_or_value_does_not_divide_by_zero(self):
        self.assertEqual(score_status(5, 0, True), "Needs Attention")
        self.assertEqual(score_status(0, 2, False), "Needs Attention")


class ReportTests(unittest.TestCase):
    def test_falling_value_counts_as_improvement_when_lower_is_better(self):
        self.assertEqual(direction_text(-0.5, False), "improved")
        self.assertEqual(direction_text(-0.5, True), "declined")

    def test_sparkline_has_one_bar_per_value(self):
        self.assertEqual(len(sparkline([1, 2, 3, 4])), 4)
        self.assertEqual(sparkline([2, 2, 2]), "▁▁▁")

    def test_summary_uses_latest_month_regardless_of_row_order(self):
        rows = [row("2025-03", 1.8), row("2025-01", 3.2), row("2025-02", 2.4)]
        (summary,) = summarize(rows)
        self.assertEqual(summary["current"], 1.8)
        self.assertEqual(summary["previous"], 2.4)
        self.assertAlmostEqual(summary["period_change"], -1.4)
        self.assertEqual(summary["status"], "On Track")

    def test_report_lists_kpis_needing_attention(self):
        rows = [row("2025-01", 3.2), row("2025-02", 3.0)]
        report = build_report(rows)
        self.assertIn("recovery plan for: Response Time", report)


if __name__ == "__main__":
    unittest.main()
