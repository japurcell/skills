#!/usr/bin/env python3
"""Check release evidence mechanics through bounded disposable CLI runs."""
from __future__ import annotations

import json
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tool_guard_corpus import PROVIDERS, script_path

CLI = Path(__file__).with_name("verify-hook-release.py")


class ReleaseVerificationTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(CLI), *args], capture_output=True,
                              text=True, timeout=30)

    def fixture(self, root: Path, *, logging: bool = True, denial: bool = False) -> None:
        for provider in PROVIDERS:
            script = script_path(root, provider)
            script.parent.mkdir(parents=True)
            (script.parent / "helpers").mkdir()
            (script.parent / "helpers" / "marker.py").write_text("VALUE = 1\n")
            cache = script.parent / "helpers" / "__pycache__"
            cache.mkdir()
            (cache / "source.pyc").write_bytes(b"stale bytecode must not be copied")
            source = (
                "import json, os, pathlib, sys\n"
                "from helpers import marker\n"
                "assert os.environ['OBSERVABILITY_TESTING'] == '1'\n"
                "if os.environ.get('PYTHONDONTWRITEBYTECODE'): assert not list(pathlib.Path(__file__).parent.rglob('*.pyc'))\n"
                "json.load(sys.stdin)\n"
            )
            if logging:
                source += (
                    "path = pathlib.Path(os.environ['TOOL_GUARD_LOG_DIR'])\n"
                    "if " + repr(provider == "gemini") + ": path = path / 'guard.log'\n"
                    "path.parent.mkdir(parents=True, exist_ok=True)\n"
                    "with path.open('a') as out: out.write(json.dumps({'event': 'guard_passed', 'mode': 'block'}) + '\\n')\n"
                )
            response = ({"decision": "deny" if denial else "allow"} if provider == "gemini"
                        else {"hookSpecificOutput": {"permissionDecision": "deny"}} if denial
                        else {"permissionDecision": "allow", "hookSpecificOutput": {"permissionDecision": "allow"}}
                        if provider == "copilot" else {})
            source += "print(" + repr(json.dumps(response)) + ")\n"
            script.write_text(source)

    def test_public_list_maps_baseline_without_historical_mode(self) -> None:
        result = self.run_cli("--list")
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = {row["case"]: row for row in json.loads(result.stdout)}
        for provider in PROVIDERS:
            self.assertEqual(rows[f"{provider}.guard.search.full-provider-envelope"]["expected"],
                             {"baseline": "deny", "candidate": "allow"})
            self.assertEqual(rows[f"{provider}.guard.danger.full-envelope"]["expected"],
                             {"baseline": "deny", "candidate": "deny"})
            self.assertEqual(rows[f"{provider}.guard.patch.bytes-46899"]["expected"],
                             {"baseline": "allow", "candidate": "allow"})

    @unittest.skipUnless(sys.platform == "darwin", "release execution requires native macOS")
    def test_mechanics_retains_pairs_cold_copies_and_completed_logs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root / "baseline")
            self.fixture(root / "candidate")
            output = root / "evidence.json"
            result = self.run_cli("--baseline-root", str(root / "baseline"),
                                  "--candidate-root", str(root / "candidate"),
                                  "--output", str(output), "--mechanics-only",
                                  "--case", "codex.guard.clean")
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(output.read_text())
            self.assertFalse(report["release_acceptance_eligible"])
            self.assertEqual(report["method"]["warm_order"],
                             [["baseline", "candidate"], ["candidate", "baseline"]])
            self.assertEqual(len(report["warm"]), 4)
            self.assertEqual(len(report["cold"]), 4)
            for row in report["warm"]:
                self.assertEqual(len(row["samples_ms"]), 2)
                self.assertGreater(row["first_process_ms"], 0)
                self.assertEqual(row["logging"]["records"], 3)
                self.assertGreater(row["provider_bytecode_after"], 0)
            homes = {row["home_id"] for row in report["cold"]}
            copies = {row["copy_id"] for row in report["cold"]}
            self.assertEqual(len(homes), 4)
            self.assertEqual(len(copies), 4)
            for row in report["cold"]:
                self.assertEqual(row["bytecode_before"], 0)
                self.assertEqual(row["bytecode_after"], 0)
                self.assertEqual(row["logging"]["records"], 1)
            self.assertEqual(len(report["concurrency"]), 2)
            self.assertTrue(report["sources_unchanged"])
            self.assertEqual(report["errors"], [])
            self.assertIn("script_sha256", report)

    @unittest.skipUnless(sys.platform == "darwin", "release execution requires native macOS")
    def test_valid_case_without_logging_is_failure_with_retained_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root / "baseline", logging=False)
            self.fixture(root / "candidate")
            output = root / "failed.json"
            result = self.run_cli("--baseline-root", str(root / "baseline"),
                                  "--candidate-root", str(root / "candidate"),
                                  "--output", str(output), "--mechanics-only",
                                  "--case", "codex.guard.clean")
            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads(output.read_text())
            self.assertIn("completed guard records", " ".join(report["errors"]))
            self.assertEqual(report["warm"][0]["logging"]["records"], 0)
            self.assertGreater(report["warm"][0]["first_process_ms"], 0)

    @unittest.skipUnless(sys.platform == "darwin", "RSS collection requires native macOS")
    def test_resources_keep_separate_rss_launch_and_completed_logging(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root / "baseline")
            self.fixture(root / "candidate")
            output = root / "resources.json"
            result = self.run_cli("--baseline-root", str(root / "baseline"),
                                  "--candidate-root", str(root / "candidate"),
                                  "--output", str(output), "--mechanics-only",
                                  "--mode", "resources", "--case", "codex.resources.strict-max")
            report = json.loads(output.read_text())
            self.assertEqual(result.returncode, 0, result.stderr + str(report["errors"]))
            self.assertEqual(len(report["resources"]), 2)
            for row in report["resources"]:
                self.assertEqual(len(row["samples_ms"]), 2)
                self.assertEqual(row["logging"]["records"], 4)
                self.assertGreater(row["peak_rss_bytes"], 0)
                self.assertEqual(row["ceiling_ms"], 500)

    def test_budget_keeps_isolated_pair_violation(self) -> None:
        spec = importlib.util.spec_from_file_location("release_verification", CLI)
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        report = {"warm": [
            {"pair": 0, "case": "codex.guard.clean", "condition": "baseline", "summary": {"median_ms": 10, "p95_ms": 20}},
            {"pair": 0, "case": "codex.guard.clean", "condition": "candidate", "summary": {"median_ms": 13, "p95_ms": 20}},
            {"pair": 1, "case": "codex.guard.clean", "condition": "baseline", "summary": {"median_ms": 10, "p95_ms": 20}},
            {"pair": 1, "case": "codex.guard.clean", "condition": "candidate", "summary": {"median_ms": 6, "p95_ms": 20}},
        ], "cold": []}
        gates = adapter.comparisons(report)
        self.assertEqual([gate["met"] for gate in gates], [False, True])
        self.assertEqual(gates[0]["delta_ms"]["median_ms"], 3)

    def test_exact_filter_and_output_preservation(self) -> None:
        result = self.run_cli("--list", "--case", "codex.guard.missing")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "original.json"
            output.write_text("original failed evidence\n")
            result = self.run_cli("--baseline-root", temporary, "--candidate-root", temporary,
                                  "--output", str(output), "--mechanics-only")
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("already exists", result.stderr)
            self.assertEqual(output.read_text(), "original failed evidence\n")

    @unittest.skipUnless(sys.platform == "darwin", "release execution requires native macOS")
    def test_wrong_decision_retains_failed_sample_and_unverified_baseline_stops(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root / "baseline", denial=True)
            self.fixture(root / "candidate")
            output = root / "failed.json"
            arguments = ("--baseline-root", str(root / "baseline"),
                         "--candidate-root", str(root / "candidate"),
                         "--output", str(output), "--case", "codex.guard.clean")
            result = self.run_cli(*arguments)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("baseline runtime fingerprints do not match", result.stderr)
            self.assertFalse(output.exists())
            result = self.run_cli(*arguments, "--mechanics-only")
            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads(output.read_text())
            self.assertGreater(report["failed_invocation"]["elapsed_ms"], 0)
            self.assertEqual(report["failed_invocation"]["output"]["hookSpecificOutput"]["permissionDecision"], "deny")
            self.assertFalse(report["gates_met"])

    @unittest.skipUnless(sys.platform == "darwin", "release execution requires native macOS")
    def test_changed_source_cannot_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            baseline = root / "baseline"
            candidate = root / "candidate"
            self.fixture(baseline)
            self.fixture(candidate)
            original_helper = script_path(candidate, "codex").parent / "helpers" / "marker.py"
            script = script_path(candidate, "codex")
            with script.open("a") as handle:
                handle.write("pathlib.Path(" + repr(str(original_helper)) + ").write_text('VALUE = 2\\n')\n")
            output = root / "changed.json"
            result = self.run_cli("--baseline-root", str(baseline), "--candidate-root", str(candidate),
                                  "--output", str(output), "--mechanics-only", "--case", "codex.guard.clean")
            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads(output.read_text())
            self.assertFalse(report["sources_unchanged"])
            self.assertIn("sources changed", " ".join(report["errors"]))


if __name__ == "__main__":
    unittest.main()
