import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "wording_trial.py"


class WordingTrialTest(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.bundle = self.root / "fan-out"
        self.bundle.mkdir()
        self.original = "---\nname: fan-out\ndescription: Explain local fallback.\n---\n\nExplain local fallback.\n"
        (self.bundle / "SKILL.md").write_text(self.original)
        (self.bundle / "router.txt").write_text("fast")
        self.trial = self.root / "trial"

    def run_cut(self, cut):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "cut", str(self.bundle), str(self.trial), cut],
            capture_output=True, text=True,
        )

    def test_prepares_isolated_candidate_with_exact_body_cut(self):
        run = self.run_cut("local ")
        self.assertEqual(run.returncode, 0, run.stderr)
        body = (self.trial / "SKILL.md").read_text()
        self.assertEqual(body, self.original.replace("\nExplain local", "\nExplain"))
        self.assertEqual((self.trial / "router.txt").read_text(), "fast")
        self.assertEqual((self.bundle / "SKILL.md").read_text(), self.original)
        self.assertEqual(json.loads(run.stdout)["candidate_body_words"], 2)

    def test_failed_trials_preserve_inputs_and_existing_candidates(self):
        for cut in ["description:", "a", ""]:
            with self.subTest(cut=cut):
                run = self.run_cut(cut)
                self.assertEqual(run.returncode, 2, run.stderr)
                self.assertFalse(self.trial.exists())
        self.assertEqual(self.run_cut("local ").returncode, 0)
        old = (self.trial / "SKILL.md").read_bytes()
        self.assertEqual(self.run_cut("fallback").returncode, 2)
        self.assertEqual((self.trial / "SKILL.md").read_bytes(), old)

    def test_invalid_utf8_leaves_no_partial_candidate(self):
        source = self.bundle / "SKILL.md"
        source.write_bytes(source.read_bytes() + bytes([255]))
        result = self.run_cut("local ")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertFalse(self.trial.exists())

    def test_cached_suite_selects_shortest_qualified_and_retains_mixed_runs(self):
        self.assertEqual(self.run_cut("local ").returncode, 0)
        suite = self.root / "suite.json"
        (self.root / "conditions").write_text("fixture coordinator; router v1")
        for case in ["dispatch", "fallback"]:
            (self.root / case).write_text(case)
        suite.write_text(json.dumps({"conditions": "conditions",
                                     "cases": {"dispatch": "dispatch", "fallback": "fallback"}}))

        def cli(command, *args):
            run = subprocess.run([sys.executable, str(SCRIPT), command, str(suite),
                                  str(self.root / "ledger.db"), *map(str, args)],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            return json.loads(run.stdout)

        def record(bundle, case, verdict, trace):
            proof = self.root / trace
            proof.write_text(f"fixture {trace}")
            cli("record", bundle, case, verdict, proof)

        def status():
            return cli("status", self.bundle, self.trial)

        record(self.bundle, "dispatch", "borderline", "first")
        self.assertEqual(status()["candidates"][0]["cases"]["dispatch"]["status"], "repeat")
        record(self.bundle, "dispatch", "pass", "second")
        record(self.bundle, "fallback", "pass", "third")
        record(self.trial, "fallback", "pass", "fourth")
        record(self.trial, "fallback", "fail", "fifth")
        report = status()
        self.assertEqual(report["winner"], str(self.bundle))
        mixed = report["candidates"][1]["cases"]["fallback"]
        self.assertEqual(mixed["status"], "rejected")
        self.assertEqual(len(mixed["runs"]), 2)
        (self.bundle / "router.txt").write_text("new route")
        self.assertIsNone(status()["winner"])
        self.assertEqual(status()["candidates"][0]["cases"]["dispatch"]["status"], "pending")
        (self.root / "conditions").write_text("different provider")
        self.assertEqual(status()["candidates"][1]["cases"]["fallback"]["status"], "pending")

    def test_blocked_case_waits_for_changed_conditions_or_new_evidence(self):
        suite = self.root / "suite.json"
        conditions = self.root / "provider"
        conditions.write_text("offline")
        (self.root / "case").write_text("requires live dispatch")
        suite.write_text(json.dumps({"conditions": "provider", "cases": {"dispatch": "case"}}))
        ledger = self.root / "ledger.db"

        def cli(command, *args):
            run = subprocess.run([sys.executable, str(SCRIPT), command, str(suite),
                                  str(ledger), str(self.bundle), *map(str, args)],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            return json.loads(run.stdout)

        denied = self.root / "diagnostic.txt"
        denied.write_text("Provider unavailable")
        cli("record", "dispatch", "blocked", denied)
        report = cli("status")
        self.assertIsNone(report["winner"])
        self.assertEqual(report["candidates"][0]["cases"]["dispatch"]["status"], "blocked")
        conditions.write_text("available")
        self.assertEqual(cli("status")["candidates"][0]["cases"]["dispatch"]["status"], "pending")
        conditions.write_text("offline")
        proof = self.root / "restored-run"
        proof.mkdir()
        (proof / "grading.json").write_text(json.dumps({
            "expectations": [{"passed": True}], "summary": {"passed": 1, "failed": 0, "total": 1}
        }))
        cli("record", "dispatch", "graded", proof)
        report = cli("status")
        self.assertEqual(report["winner"], str(self.bundle))
        self.assertEqual([r["verdict"] for r in report["candidates"][0]["cases"]["dispatch"]["runs"]],
                         ["blocked", "pass"])


if __name__ == "__main__":
    unittest.main()
