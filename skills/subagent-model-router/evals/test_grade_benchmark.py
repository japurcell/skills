"""Regression checks for the router's published decision contract."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from grade_benchmark import grade


def decision(tier, model, reason="task fit and cost", **extra):
    return {"tier": tier, "model": model, "reason": reason, **extra}


class RoutingGraderTests(unittest.TestCase):
    def passes(self, scenario, value):
        return all(item["passed"] for item in grade(scenario, value))

    def test_meaningful_code_diff_requires_standard(self):
        self.assertTrue(self.passes("ordinary-review", decision("Standard", "gpt-5.4-mini")))
        self.assertFalse(self.passes("ordinary-review", decision("Fast", "gpt-6-luna")))
        self.assertFalse(self.passes("ordinary-review", decision("Standard", "unknown")))

    def test_style_only_single_file_review_allows_fast(self):
        self.assertTrue(self.passes("style-review", decision("Fast", "gpt-5-mini")))
        self.assertTrue(self.passes("style-review", decision("Standard", "gpt-6-sol")))
        self.assertFalse(self.passes("style-review", decision("Fast", "gpt-6-sol")))
        self.assertFalse(self.passes("style-review", decision("Standard", "unknown")))
        self.assertFalse(self.passes("style-review", decision("Premium", "gpt-6-astra")))

    def test_security_review_requires_premium(self):
        self.assertTrue(self.passes("security-review", decision("Premium", "gpt-6-astra")))
        self.assertTrue(self.passes("security-review", decision(
            "Premium", "gpt-6-sol", effort="high"
        )))
        self.assertFalse(self.passes("security-review", decision("Premium", "gpt-6-sol")))
        self.assertFalse(self.passes("security-review", decision("Standard", "gpt-6-sol")))

    def test_unavailable_model_requires_same_tier_fallback(self):
        self.assertTrue(self.passes("review-fallback", decision(
            "Standard", "gpt-5.4-mini", fallback="gpt-6-sol unavailable; same-tier fallback"
        )))
        self.assertFalse(self.passes("review-fallback", decision(
            "Fast", "gpt-5-mini", fallback="gpt-6-sol unavailable"
        )))
        self.assertFalse(self.passes("review-fallback", decision(
            "Standard", "gpt-5.4-mini", fallback="same-tier fallback"
        )))

    def test_effort_controls_luna_tier(self):
        self.assertFalse(self.passes("ordinary-review", decision("Standard", "gpt-6-luna")))
        self.assertTrue(self.passes("ordinary-review", decision(
            "Standard", "gpt-6-luna", effort="max"
        )))
        self.assertFalse(self.passes("style-review", decision(
            "Fast", "gpt-6-luna", effort="max"
        )))

    def test_catalog_named_luna_fallback_is_fast(self):
        self.assertTrue(self.passes("style-review", decision("Fast", "gpt-5.6-luna")))

    def test_benchmark_cli_writes_failing_grade_for_fast_logic_review(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "eval-0-ordinary-review/with_skill/run-1/outputs"
            output.mkdir(parents=True)
            (output / "decision.json").write_text(
                json.dumps(decision("Fast", "gpt-5-mini")), encoding="utf-8"
            )
            grader = Path(__file__).with_name("grade_benchmark.py")
            result = subprocess.run(
                [sys.executable, str(grader), directory],
                capture_output=True, text=True, timeout=5,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads((output.parent / "grading.json").read_text(encoding="utf-8"))
            self.assertGreater(report["summary"]["failed"], 0)

    def test_bounded_execution_and_environment_diagnosis_stay_fast(self):
        self.assertTrue(self.passes("bounded-work", decision("Fast", "gpt-5-mini")))
        self.assertTrue(self.passes("environment-failure", decision(
            "Fast", "gpt-5-mini", "diagnose missing dependency before escalating"
        )))
        self.assertFalse(self.passes("environment-failure", decision(
            "Premium", "gpt-6-astra", "diagnose missing dependency"
        )))
        self.assertFalse(self.passes("environment-failure", decision(
            "Fast", "gpt-5-mini", "high quality"
        )))

    def test_connected_code_change_uses_standard(self):
        self.assertTrue(self.passes("connected-work", decision("Standard", "gpt-6-sol")))
        self.assertFalse(self.passes("connected-work", decision("Fast", "gpt-5-mini")))

    def test_benchmark_cli_grades_missing_decision_as_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "eval-0-ordinary-review/with_skill/run-1"
            run.mkdir(parents=True)
            grader = Path(__file__).with_name("grade_benchmark.py")
            result = subprocess.run(
                [sys.executable, str(grader), directory],
                capture_output=True, text=True, timeout=5,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads((run / "grading.json").read_text(encoding="utf-8"))
            self.assertEqual(report["summary"]["passed"], 0)


if __name__ == "__main__":
    unittest.main()
