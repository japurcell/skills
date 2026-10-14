#!/usr/bin/env python3
"""Check release evidence mechanics through bounded disposable CLI runs."""
from __future__ import annotations

import json
import importlib.util
from dataclasses import replace
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from tool_guard_corpus import PROVIDERS, script_path

CLI = Path(__file__).with_name("verify-hook-release.py")


def load_adapter():
    spec = importlib.util.spec_from_file_location("release_verification", CLI)
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    return adapter


class ReleaseVerificationTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(CLI), *args], capture_output=True,
                              text=True, timeout=30)

    def fixture(self, root: Path, *, logging: bool = True, denial: bool = False,
                trace: Path | None = None) -> None:
        for provider in PROVIDERS:
            script = script_path(root, provider)
            script.parent.mkdir(parents=True)
            (script.parent / "helpers").mkdir()
            (script.parent / "helpers" / "marker.py").write_text("VALUE = 1\n")
            cache = script.parent / "helpers" / "__pycache__"
            cache.mkdir()
            (cache / "source.pyc").write_bytes(b"stale bytecode must not be copied")
            source = (
                "import hashlib, json, os, pathlib, sys\n"
                "from helpers import marker\n"
                "assert os.environ['OBSERVABILITY_TESTING'] == '1'\n"
                "if os.environ.get('PYTHONDONTWRITEBYTECODE'): assert not list(pathlib.Path(__file__).parent.rglob('*.pyc'))\n"
                "payload = sys.stdin.buffer.read(); json.loads(payload)\n"
            )
            if trace is not None:
                source += (
                    "sequence = pathlib.Path(os.environ['HOME']) / 'sequence'\n"
                    "index = int(sequence.read_text()) if sequence.exists() else 0\n"
                    "sequence.write_text(str(index + 1))\n"
                    "with pathlib.Path(" + repr(str(trace)) + ").open('a') as out: out.write(json.dumps(["
                    + repr(root.name) + ", hashlib.sha256(payload).hexdigest(), index]) + '\\n')\n"
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
        self.assertEqual(len(rows), 156)
        adapter = load_adapter()
        for label in ("baseline", "candidate"):
            cases = adapter.selected_cases(Path("."), label, list(rows), "timing")
            self.assertEqual(len(cases), 156)
            self.assertEqual({case.name for case in cases}, set(rows))
        for provider in PROVIDERS:
            self.assertEqual(rows[f"{provider}.guard.search.full-provider-envelope"]["expected"],
                             {"baseline": "deny", "candidate": "allow"})
            self.assertEqual(rows[f"{provider}.guard.danger.full-envelope"]["expected"],
                             {"baseline": "deny", "candidate": "deny"})
            self.assertEqual(rows[f"{provider}.guard.patch.bytes-46899"]["expected"],
                             {"baseline": "allow", "candidate": "allow"})

    def test_matched_warm_calls_are_adjacent_for_both_cases_and_pairs(self) -> None:
        adapter = load_adapter()
        names = ["codex.guard.search.full-provider-envelope", "codex.guard.danger.full-envelope"]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            roots = {label: root / label for label in ("baseline", "candidate")}
            for source in roots.values():
                self.fixture(source)
            selected = {label: adapter.selected_cases(source, label, names, "timing")
                        for label, source in roots.items()}
            names = [case.name for case in selected["baseline"]]
            for samples, warmups in ((25, 3), (2, 0)):
                trace = []

                def invoke(case, repo, home, **kwargs):
                    label = "baseline" if "baseline" in home.parts else "candidate"
                    other = "candidate" if label == "baseline" else "baseline"
                    self.assertTrue((home.parent.parent / other / case.name).is_dir())
                    trace.append((case.name, label, case.expected_decision))
                    observation = kwargs.get("observation")
                    if observation is not None:
                        observation.update(start_monotonic_ns=time.monotonic_ns(),
                                           end_monotonic_ns=time.monotonic_ns())
                    event = "guard_passed" if case.expected_decision == "allow" else "threats_detected"
                    with (home / "guard.log").open("a") as handle:
                        handle.write(json.dumps({"event": event, "mode": "block"}) + "\n")
                    return 7.5, {"decision": case.expected_decision}

                report = {"warm": [], "cold": [], "concurrency": []}
                run = root / f"run-{samples}"
                run.mkdir()
                with patch.object(adapter, "checked_invocation", side_effect=invoke):
                    adapter.measure_timing(report, roots, selected,
                                           run, samples, warmups, 0)
                expected = [(name, label, "allow" if label == "candidate" and name.endswith(".search.full-provider-envelope") else "deny")
                            for order in (("baseline", "candidate"), ("candidate", "baseline"))
                            for name in names for _ in range(1 + warmups + samples) for label in order]
                self.assertEqual(trace, expected)
                for row in report["warm"]:
                    self.assertEqual(len(row["samples_ms"]), samples)
                    self.assertEqual(row["first_process_ms"], 7.5)
                    self.assertEqual(row["logging"]["records"], 1 + warmups + samples)
                    self.assertEqual([call["call_index"] for call in row["invocations"]],
                                     list(range(1 + warmups + samples)))
                    self.assertEqual([call["kind"] for call in row["invocations"]],
                                     ["first"] + ["warmup"] * warmups + ["measured"] * samples)

    @unittest.skipUnless(sys.platform == "darwin", "release execution requires native macOS")
    def test_mechanics_retains_pairs_cold_copies_and_completed_logs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            trace = root / "trace.jsonl"
            self.fixture(root / "baseline", trace=trace)
            self.fixture(root / "candidate", trace=trace)
            output = root / "evidence.json"
            result = self.run_cli("--baseline-root", str(root / "baseline"),
                                  "--candidate-root", str(root / "candidate"),
                                  "--output", str(output), "--mechanics-only",
                                  "--case", "codex.guard.clean",
                                  "--case", "codex.guard.patch.bytes-46899")
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(output.read_text())
            self.assertFalse(report["release_acceptance_eligible"])
            self.assertEqual(report["method"]["warm_order"],
                             [["baseline", "candidate"], ["candidate", "baseline"]])
            self.assertEqual(len(report["warm"]), 8)
            self.assertEqual(len(report["cold"]), 8)
            self.assertIn("adjacent", report["method"]["warm_schedule"])
            names = [row["case"] for row in report["warm"] if row["pair"] == 0 and row["condition"] == "baseline"]
            hashes = {row["case"]: row["input_sha256"] for row in report["warm"]}
            expected = [[label, hashes[name], index]
                        for order in (("baseline", "candidate"), ("candidate", "baseline"))
                        for name in names for index in range(3) for label in order]
            observed = [json.loads(line) for line in trace.read_text().splitlines()]
            self.assertEqual(observed[:24], expected)
            intervals = []
            for row in report["warm"]:
                self.assertEqual(len(row["samples_ms"]), 2)
                self.assertGreater(row["first_process_ms"], 0)
                self.assertEqual(row["logging"]["records"], 3)
                self.assertGreater(row["provider_bytecode_after"], 0)
                self.assertEqual([call["kind"] for call in row["invocations"]], ["first", "measured", "measured"])
                for index, call in enumerate(row["invocations"]):
                    self.assertEqual(call["call_index"], index)
                    self.assertLess(call["start_monotonic_ns"], call["end_monotonic_ns"])
                    intervals.append((call["start_monotonic_ns"], call["end_monotonic_ns"]))
            intervals.sort()
            self.assertTrue(all(left[1] <= right[0] for left, right in zip(intervals, intervals[1:])))
            homes = {row["home_id"] for row in report["cold"]}
            copies = {row["copy_id"] for row in report["cold"]}
            self.assertEqual(len(homes), 8)
            self.assertEqual(len(copies), 8)
            for row in report["cold"]:
                self.assertEqual(row["bytecode_before"], 0)
                self.assertEqual(row["bytecode_after"], 0)
                self.assertEqual(row["logging"]["records"], 1)
            self.assertEqual(len(report["concurrency"]), 2)
            self.assertTrue(report["sources_unchanged"])
            self.assertEqual(report["errors"], [])
            self.assertIn("script_sha256", report)
            self.assertEqual(set(report["harness_sha256"]), {
                "verify-hook-release.py", "benchmark-high-rate-hooks.py", "benchmark-tool-guard-resources.py",
                "tool_guard_corpus.py", "fixtures/tool_guard_vectors.py", "hook_benchmark_support.py",
                "hook_test_support.py",
            })

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
        adapter = load_adapter()
        report = {"warm": [
            {"pair": 0, "case": "codex.guard.clean", "condition": "baseline", "summary": {"median_ms": 10, "p95_ms": 20}},
            {"pair": 0, "case": "codex.guard.clean", "condition": "candidate", "summary": {"median_ms": 13, "p95_ms": 20}},
            {"pair": 1, "case": "codex.guard.clean", "condition": "baseline", "summary": {"median_ms": 10, "p95_ms": 20}},
            {"pair": 1, "case": "codex.guard.clean", "condition": "candidate", "summary": {"median_ms": 6, "p95_ms": 20}},
        ], "cold": []}
        gates = adapter.comparisons(report)
        self.assertEqual([gate["met"] for gate in gates], [False, True])
        self.assertEqual(gates[0]["delta_ms"]["median_ms"], 3)

    def test_budget_subtracts_independent_quantiles(self) -> None:
        adapter = load_adapter()
        baseline = [0] * 23 + [50, 100]
        candidate = [100, 50] + [1] * 23
        report = {"warm": [
            {"pair": 0, "case": "codex.guard.clean", "condition": label,
             "summary": adapter.high_rate.summary(samples)}
            for label, samples in (("baseline", baseline), ("candidate", candidate))
        ], "cold": []}
        gate = adapter.comparisons(report)[0]
        self.assertEqual(gate["delta_ms"], {"median_ms": 1, "p95_ms": 0})
        paired = adapter.high_rate.summary([right - left for left, right in zip(baseline, candidate)])
        self.assertEqual(paired["p95_ms"], 50)
        self.assertNotEqual(gate["delta_ms"]["p95_ms"], paired["p95_ms"])

    def test_warm_pair_rejects_mismatched_cases_before_invocation(self) -> None:
        adapter = load_adapter()
        case = adapter.release_cases(Path("."), "candidate")[0]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for changed, message in ((replace(case, name=case.name + ".other"), "exact case IDs"),
                                     (replace(case, payload=case.payload + b" "), "payload bytes")):
                with self.subTest(message=message), patch.object(adapter, "checked_invocation") as invoke:
                    with self.assertRaisesRegex(ValueError, message):
                        adapter.warm_pair_run({"baseline": case, "candidate": changed},
                                              {label: root for label in ("baseline", "candidate")},
                                              root, {label: root / label for label in ("baseline", "candidate")},
                                              2, 0, 0, {"baseline": {}, "candidate": {}})
                    invoke.assert_not_called()

    def test_missing_or_duplicate_selected_case_is_rejected(self) -> None:
        adapter = load_adapter()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            roots = {label: root / label for label in ("baseline", "candidate")}
            for source in roots.values():
                self.fixture(source)
            cases = adapter.release_cases(roots["baseline"], "baseline")[:1]
            for candidate in ([], cases + cases):
                run = root / f"run-{len(candidate)}"
                run.mkdir()
                with self.subTest(candidate=len(candidate)), patch.object(adapter, "checked_invocation") as invoke:
                    with self.assertRaisesRegex(ValueError, "unique exact case IDs"):
                        adapter.measure_timing({"warm": []}, roots,
                                               {"baseline": cases, "candidate": candidate}, run, 2, 0, 0)
                    invoke.assert_not_called()

    def test_invocation_observation_preserves_inner_elapsed_and_default_result(self) -> None:
        adapter = load_adapter()
        case = adapter.selected_cases(Path("."), "candidate", ["codex.guard.clean"], "timing")[0]
        observation = {"call_index": 4, "kind": "measured"}

        def verify(*args):
            self.assertLessEqual(observation["start_monotonic_ns"], observation["end_monotonic_ns"])

        with patch.object(adapter.high_rate, "invoke", return_value=(7.5, 0, {})), \
                patch.object(adapter.high_rate, "verify_outcome", side_effect=verify):
            observed = adapter.checked_invocation(case, Path("."), Path("."), observation=observation)
        with patch.object(adapter.high_rate, "invoke", return_value=(7.5, 0, {})), \
                patch.object(adapter.high_rate, "verify_outcome"):
            default = adapter.checked_invocation(case, Path("."), Path("."))
        self.assertEqual(observed, default)
        self.assertEqual(observed[0], 7.5)

    def test_malformed_legacy_zero_log_exception_remains_distinct(self) -> None:
        adapter = load_adapter()
        case = next(case for case in adapter.release_cases(Path("."), "baseline")
                    if case.name == "codex.guard.failure")
        with tempfile.TemporaryDirectory() as temporary:
            proof = adapter.verify_logging(Path(temporary), case, 29)
        self.assertEqual(proof["records"], 0)
        self.assertEqual(proof["required_records"], 0)
        self.assertEqual(proof["status"], "legacy transport exception")
        self.assertTrue(proof["legacy_exception"])
        adapter.logging_error(proof)

    @unittest.skipUnless(sys.platform == "darwin", "release execution requires native macOS")
    def test_second_label_failure_retains_both_rows_and_invocation_evidence(self) -> None:
        for failure in ("decision", "logging"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.fixture(root / "baseline")
                self.fixture(root / "candidate", denial=failure == "decision", logging=failure != "logging")
                output = root / "failed.json"
                result = self.run_cli("--baseline-root", str(root / "baseline"),
                                      "--candidate-root", str(root / "candidate"),
                                      "--output", str(output), "--mechanics-only", "--case", "codex.guard.clean")
                self.assertEqual(result.returncode, 1, result.stderr)
                report = json.loads(output.read_text())
                self.assertFalse(report["gates_met"])
                self.assertEqual([row["condition"] for row in report["warm"]], ["baseline", "candidate"])
                baseline, candidate = report["warm"]
                self.assertGreater(baseline["first_process_ms"], 0)
                failed = report["failed_invocation"]
                self.assertGreater(failed["elapsed_ms"], 0)
                self.assertLess(failed["start_monotonic_ns"], failed["end_monotonic_ns"])
                self.assertEqual(failed["end_monotonic_ns"], candidate["invocations"][-1]["end_monotonic_ns"])
                self.assertEqual(failed["output"], {"hookSpecificOutput": {"permissionDecision": "deny"}} if failure == "decision" else {})
                if failure == "decision":
                    self.assertEqual(len(baseline["invocations"]), 1)
                    self.assertEqual(len(candidate["invocations"]), 1)
                    self.assertEqual(failed["call_index"], 0)
                    self.assertEqual(failed["kind"], "first")
                    self.assertLessEqual(baseline["invocations"][0]["end_monotonic_ns"], failed["start_monotonic_ns"])
                else:
                    self.assertEqual(baseline["logging"]["records"], 3)
                    self.assertEqual(candidate["logging"]["records"], 0)
                    self.assertEqual(failed["call_index"], 2)
                    self.assertEqual(len(candidate["samples_ms"]), 2)

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
