#!/usr/bin/env python3
"""Check release evidence mechanics through bounded disposable CLI runs."""
from __future__ import annotations

import hashlib
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
                "import fcntl, hashlib, json, os, pathlib, sys\n"
                "from helpers import marker\n"
                "assert os.environ['OBSERVABILITY_TESTING'] == '1'\n"
                "if os.environ.get('PYTHONDONTWRITEBYTECODE'): assert not list(pathlib.Path(__file__).parent.rglob('*.pyc'))\n"
                "payload = sys.stdin.buffer.read(); json.loads(payload)\n"
            )
            if trace is not None:
                source += (
                    "sequence_lock = open(pathlib.Path(os.environ['HOME']) / 'sequence.lock', 'w')\n"
                    "fcntl.flock(sequence_lock, fcntl.LOCK_EX)\n"
                    "sequence = pathlib.Path(os.environ['HOME']) / 'sequence'\n"
                    "index = int(sequence.read_text()) if sequence.exists() else 0\n"
                    "sequence.write_text(str(index + 1))\n"
                    "with pathlib.Path(" + repr(str(trace)) + ").open('a') as out: out.write(json.dumps(["
                    + repr(root.name) + ", hashlib.sha256(payload).hexdigest(), index]) + '\\n')\n"
                    "fcntl.flock(sequence_lock, fcntl.LOCK_UN)\n"
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

    def measurement_evidence(self, mode="timing"):
        adapter = load_adapter()
        name = "codex.guard.clean" if mode == "timing" else "codex.resources.strict-max"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root / "baseline")
            self.fixture(root / "candidate")
            output = root / "evidence.json"
            result = self.run_cli("--baseline-root", str(root / "baseline"),
                                  "--candidate-root", str(root / "candidate"),
                                  "--output", str(output), "--mechanics-only", "--mode", mode, "--case", name)
            self.assertEqual(result.returncode, 0, result.stderr + str(json.loads(output.read_text()).get("errors")))
            report = json.loads(output.read_text())
            selected = {label: adapter.selected_cases(root / label, label, [name], mode)
                        for label in ("baseline", "candidate")}
            return report, selected

    def test_v2_preserves_old_universes_and_adds_reviewed_capacity(self):
        adapter = load_adapter()
        path = CLI.parent / "fixtures/tool_guard_file_operations_expectations.json"
        for section, count in (("timing", 279), ("resources", 231)):
            old = adapter.selected_cases(Path("."), "baseline", [], section, "file-operations-v1", path)
            new = adapter.selected_cases(Path("."), "baseline", [], section, "file-operations-v2", path)
            self.assertEqual(len(new), count)
            by_name = {c.name: c for c in new}
            for case in old:
                self.assertEqual(case.payload, by_name[case.name].payload)
                self.assertEqual(case.fixture_metadata["contract"], by_name[case.name].fixture_metadata["contract"])
            if section == "resources":
                other = adapter.resources.selected_cases(Path("."), "file-operations-v2", path, "baseline")
                self.assertEqual([(c.name, c.payload, c.fixture_metadata) for c in new],
                                 [(c.name, c.payload, c.fixture_metadata) for c in other])

    def test_v2_rejects_stale_reader_proofs_before_filtering(self):
        adapter = load_adapter()
        path = CLI.parent / "fixtures/tool_guard_file_operations_expectations.json"
        original = json.loads(path.read_text())
        for mutation in ("missing", "extra", "classification", "markers", "boolean", "incomplete", "false_absence", "wrong_cause"):
            document = json.loads(json.dumps(original))
            suite = document["fixture_sets"]["file-operations-v2"]
            entry = suite["timing"]["codex.guard.capacity-1048576.raw-interior-max"]
            if mutation == "missing": suite["throughput_partition"]["established"].pop()
            elif mutation == "extra": suite["throughput_partition"]["observations"].append("codex.guard.unknown")
            elif mutation == "classification":
                old = suite["throughput_partition"]["established"].pop()
                new = suite["throughput_partition"]["observations"].pop()
                suite["throughput_partition"]["established"].append(new)
                suite["throughput_partition"]["observations"].append(old)
            elif mutation == "markers": entry["structural_markers"] += 1
            elif mutation == "boolean": entry["reader_limits"]["baseline"]["max_bytes"] = True
            elif mutation == "incomplete": del entry["reader_limits"]["candidate"]
            elif mutation == "false_absence":
                entry["candidate"] = json.loads(json.dumps(entry["baseline"]))
                entry["candidate"]["attribution"]["cause"] = "input_invalid"
            else:
                suite["timing"]["codex.guard.capacity-1048576.raw-interior-overflow"]["candidate"]["attribution"]["cause"] = "input_invalid"
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                altered = Path(temporary) / "expectations.json"
                altered.write_text(json.dumps(document))
                with self.assertRaises(ValueError):
                    adapter.selected_cases(Path("."), "candidate", ["codex.guard.clean"], "timing", "file-operations-v2", altered)

    def test_v2_reference_partition_and_complete_comparisons(self):
        adapter = load_adapter()
        name = "codex.guard.capacity-1048576.native-max"
        report = {"comparison_reference": "original", "throughput_partition": {
            "established": ["codex.guard.clean"], "observations": [name]},
            "warm": [{"pair": pair, "case": case, "condition": condition,
                      "summary": {"median_ms": 10 if condition == "baseline" else 100, "p95_ms": 100}}
                     for pair in (0, 1) for case in ("codex.guard.clean", name)
                     for condition in ("baseline", "candidate")], "cold": []}
        rows = adapter.comparisons(report)
        observations = [row for row in rows if row["case"] == name]
        self.assertTrue(all(row["met"] is None and row["classification"] == "changed-workload-observation" for row in observations))
        report["comparison_reference"] = "equivalent"
        self.assertTrue(all(row["met"] is False and row["classification"] == "gated" for row in adapter.comparisons(report)))
        with self.assertRaisesRegex(ValueError, "complete"):
            adapter.validate_measurements(report, {label: adapter.selected_cases(Path("."), label, ["codex.guard.clean", name], "timing", "file-operations-v2", adapter.DEFAULT_EXPECTATIONS)
                                                  for label in ("baseline", "candidate")}, "timing", 25, 3, 25,
                                          reference="equivalent", partition=report["throughput_partition"])
        for reference, condition in (("equivalent", "baseline"), ("original", "candidate")):
            result = self.run_cli("--list", "--comparison-reference", reference, "--baseline-condition", condition)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("condition", result.stderr)

    def test_v2_absent_audit_requires_independent_reader_overflow(self):
        adapter = load_adapter()
        from hook_benchmark_support import prepare_failure, verify_audit
        case = adapter.selected_cases(Path("."), "candidate", ["codex.resources.capacity-1048576.raw-interior-overflow"],
                                      "resources", "file-operations-v2", adapter.DEFAULT_EXPECTATIONS)[0]
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            prepare_failure(case, home)
            proof = verify_audit(home, case, 1)
            self.assertTrue(proof["failure_injection"]["valid_json"])
            self.assertTrue(proof["failure_injection"]["reader_limit_exceeded"])
            limits = {**case.fixture_metadata["reader_limits"], "max_bytes": len(case.payload)}
            false = replace(case, fixture_metadata={**case.fixture_metadata, "reader_limits": limits})
            with self.assertRaisesRegex(ValueError, "boundary"):
                prepare_failure(false, home)
            with self.assertRaisesRegex(ValueError, "boundary"):
                verify_audit(home, false, 1)
            stale = replace(case, fixture_metadata={**case.fixture_metadata, "structural_markers": True})
            with self.assertRaisesRegex(ValueError, "marker"):
                prepare_failure(stale, home)
        original = json.loads(adapter.DEFAULT_EXPECTATIONS.read_text())
        suite = original["fixture_sets"]["file-operations-v2"]
        malformed = "codex.resources.capacity-1048576.raw-marker-exhaustion"
        suite["resources"][malformed]["injection"] = "raw-envelope"
        with tempfile.TemporaryDirectory() as temporary:
            altered = Path(temporary) / "expectations.json"
            altered.write_text(json.dumps(original))
            with self.assertRaises(ValueError):
                adapter.selected_cases(Path("."), "candidate", [], "resources", "file-operations-v2", altered)

    def test_reader_limits_require_positive_integer_bounds(self):
        from fixtures.tool_guard_resource_cases import valid_reader_limits
        valid = [{"max_bytes": 1, "max_markers": None}, {"max_bytes": 1, "max_markers": 1},
                 {"max_bytes": 2 ** 100, "max_markers": 2 ** 100}]
        invalid = [None, [], True, 1, "limits", {}, {"max_bytes": 1}, {"max_markers": 1},
                   {"max_bytes": 1, "max_markers": None, "extra": 1}]
        invalid.extend({"max_bytes": value, "max_markers": None} for value in (None, True, False, 0, -1, 1.0, "1"))
        invalid.extend({"max_bytes": 1, "max_markers": value} for value in (True, False, 0, -1, 1.0, "1"))
        for value in valid:
            with self.subTest(valid=value):
                self.assertTrue(valid_reader_limits(value))
        for value in invalid:
            with self.subTest(invalid=value):
                self.assertFalse(valid_reader_limits(value))

    def test_transport_failure_is_rechecked_after_preparation(self):
        adapter = load_adapter()
        from hook_benchmark_support import prepare_failure, verify_audit
        names = ["codex.resources.transport.malformed", "codex.resources.capacity-1048576.raw-marker-exhaustion"]
        cases = adapter.selected_cases(Path("."), "candidate", names, "resources",
                                       "file-operations-v2", adapter.DEFAULT_EXPECTATIONS)
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            for case in cases:
                with self.subTest(case=case.name):
                    current = prepare_failure(case, home)
                    self.assertIsNotNone(verify_audit(home, current, 1)["failure_injection"])
                    with self.assertRaisesRegex(ValueError, "transport failure condition missing"):
                        verify_audit(home, replace(current, payload=b"{}"), 1)
                    if "reader_limits" in current.fixture_metadata:
                        stale = {**current.fixture_metadata, "structural_markers": current.fixture_metadata["structural_markers"] + 1}
                        with self.assertRaisesRegex(ValueError, "stale structural marker count"):
                            verify_audit(home, replace(current, fixture_metadata=stale), 1)

    @unittest.skipUnless(sys.platform == "darwin", "release execution requires native macOS")
    def test_complete_evidence_rejects_each_missing_or_duplicate_row(self):
        adapter = load_adapter()
        report, selected = self.measurement_evidence()
        adapter.validate_measurements(report, selected, "timing", 2, 0, 2)
        for section in ("warm", "cold", "comparisons"):
            for change in ("missing", "duplicate"):
                altered = json.loads(json.dumps(report))
                if change == "missing": altered[section].pop()
                else: altered[section].append(altered[section][0])
                with self.subTest(section=section, change=change), self.assertRaisesRegex(ValueError, "incomplete"):
                    adapter.validate_measurements(altered, selected, "timing", 2, 0, 2)

    @unittest.skipUnless(sys.platform == "darwin", "release execution requires native macOS")
    def test_complete_timing_evidence_rejects_missing_or_forged_call_proof(self):
        adapter = load_adapter()
        report, selected = self.measurement_evidence()
        adapter.validate_measurements(report, selected, "timing", 2, 0, 2)
        mutations = [("warm", key) for key in ("first_output", "outputs", "samples_ms", "logging", "contract", "input_sha256")]
        mutations += [("cold", key) for key in ("outcome", "logging", "contract", "input_sha256")]
        for section, key in mutations:
            altered = json.loads(json.dumps(report))
            del altered[section][0][key]
            with self.subTest(section=section, missing=key), self.assertRaises(ValueError):
                adapter.validate_measurements(altered, selected, "timing", 2, 0, 2)
        for mutation in ("sample_count", "output_count", "wrong_hash", "wrong_contract", "wrong_audit", "missing_comparison_gate", "missing_failure_proof", "wrong_method", "duplicate_cold_copy", "boolean_bytecode"):
            altered = json.loads(json.dumps(report))
            if mutation == "sample_count": altered["warm"][0]["samples_ms"].pop()
            elif mutation == "output_count": altered["warm"][0]["outputs"].pop()
            elif mutation == "wrong_hash": altered["warm"][0]["input_sha256"] = "0" * 64
            elif mutation == "wrong_contract": altered["warm"][0]["contract"]["decision"] = "deny"
            elif mutation == "wrong_audit": altered["warm"][0]["logging"]["records"] = 0
            elif mutation == "missing_failure_proof": del altered["warm"][0]["logging"]["failure_injection"]
            elif mutation == "wrong_method": altered["method"]["samples"] = 1
            elif mutation == "duplicate_cold_copy": altered["cold"][1]["copy_id"] = altered["cold"][0]["copy_id"]
            elif mutation == "boolean_bytecode": altered["cold"][0]["bytecode_before"] = False
            else: altered["comparisons"][0]["met"] = None
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                adapter.validate_measurements(altered, selected, "timing", 2, 0, 2)
        altered = json.loads(json.dumps(report))
        row = next(row for row in altered["warm"] if row["condition"] == "candidate" and row["pair"] == 0)
        row["samples_ms"] = [1000, 1000]
        row["summary"] = adapter.high_rate.summary(row["samples_ms"])
        altered["comparisons"] = adapter.comparisons(altered)
        failed = next(row for row in altered["comparisons"] if row["met"] is False)
        failed["met"] = 0
        with self.assertRaises(ValueError):
            adapter.validate_measurements(altered, selected, "timing", 2, 0, 2)

    def test_resource_loader_rejects_consistently_forged_timing_partition(self):
        adapter = load_adapter()
        document = json.loads(adapter.DEFAULT_EXPECTATIONS.read_text())
        suite = document["fixture_sets"]["file-operations-v2"]
        suite["timing"]["codex.guard.unknown"] = suite["timing"].pop("codex.guard.clean")
        names = suite["throughput_partition"]["established"]
        names[names.index("codex.guard.clean")] = "codex.guard.unknown"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "expectations.json"
            path.write_text(json.dumps(document))
            with self.assertRaisesRegex(ValueError, "partition"):
                adapter.resources.selected_cases(Path("."), "file-operations-v2", path, "candidate")

    @unittest.skipUnless(sys.platform == "darwin", "native macOS RSS required")
    def test_complete_resource_evidence_requires_calls_audits_and_native_rss(self):
        adapter = load_adapter()
        report, selected = self.measurement_evidence("resources")
        adapter.validate_measurements(report, selected, "resources", 2, 0, 2)
        for key in ("first_output", "outputs", "samples_ms", "logging", "contract", "input_sha256", "peak_rss_bytes"):
            altered = json.loads(json.dumps(report))
            del altered["resources"][0][key]
            with self.subTest(missing=key), self.assertRaises(ValueError):
                adapter.validate_measurements(altered, selected, "resources", 2, 0, 2)
        for mutation in ("sample_count", "output_count", "wrong_audit", "wrong_ceiling", "wrong_rss"):
            altered = json.loads(json.dumps(report))
            row = altered["resources"][0]
            if mutation == "sample_count": row["samples_ms"].pop()
            elif mutation == "output_count": row["outputs"].pop()
            elif mutation == "wrong_audit": row["logging"]["records"] = 0
            elif mutation == "wrong_ceiling": row["ceiling_met"] = not row["ceiling_met"]
            else: row["peak_rss_bytes"] = None
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                adapter.validate_measurements(altered, selected, "resources", 2, 0, 2)

    def test_reviewed_contracts_reject_missing_unknown_stale_and_wrong_mode(self) -> None:
        source = CLI.parent / "fixtures/tool_guard_file_operations_expectations.json"
        original = json.loads(source.read_text())
        for mutation in ("missing", "unknown", "stale", "mode", "contradictory", "missing_attribution", "wrong_enforcement", "invalid_type",
                         "written_missing", "written_partial", "written_conflict", "warn_missing", "silent_extra"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                document = json.loads(json.dumps(original))
                cases = document["fixture_sets"]["file-operations-v1"]["timing"]
                target = cases["codex.guard.clean"]
                if mutation == "missing": del cases["codex.guard.clean"]
                elif mutation == "unknown": cases["codex.guard.unknown"] = target
                elif mutation == "stale": target["input_sha256"] = "0" * 64
                elif mutation == "mode": target["candidate"]["mode"] = "warn"
                elif mutation == "contradictory": target["candidate"]["audit"]["records_per_call"] = 0
                elif mutation == "missing_attribution": cases["codex.guard.audit-unavailable.warn.finding"]["candidate"]["attribution"] = {}
                elif mutation == "wrong_enforcement": cases["codex.guard.audit-unavailable.warn.finding"]["candidate"]["attribution"]["enforcement"] = "deny"
                elif mutation == "invalid_type": cases["codex.guard.clean"] = None
                elif mutation == "warn_missing": cases["codex.guard.mode.warn.finding"]["candidate"]["attribution"] = {}
                elif mutation == "silent_extra":
                    target["candidate"]["attribution"] = {"security_outcome": "clean", "audit_outcome": "written", "enforcement": "allow", "cause": "unexpected"}
                else:
                    pair = cases["codex.guard.writer.quoted-document.execution"]["candidate"]
                    if mutation == "written_missing": pair["attribution"] = {}
                    elif mutation == "written_partial": del pair["attribution"]["cause"]
                    else: pair["attribution"]["security_outcome"] = "incomplete"
                path = Path(temporary) / "expectations.json"
                path.write_text(json.dumps(document))
                result = self.run_cli("--list", "--fixture-set", "file-operations-v1",
                                      "--expectations", str(path), "--case", "codex.guard.clean")
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_versioned_runners_agree_on_shared_resources(self) -> None:
        adapter = load_adapter()
        path = CLI.parent / "fixtures/tool_guard_file_operations_expectations.json"
        for fixture_set, count in (("historical-v1", 108), ("file-operations-v1", 171), ("file-operations-v2", 231)):
            for condition in ("baseline", "candidate"):
                with self.subTest(fixture_set=fixture_set, condition=condition):
                    release = adapter.selected_cases(Path("."), condition, [], "resources", fixture_set, path)
                    standalone = adapter.resources.selected_cases(Path("."), fixture_set, path, condition)
                    self.assertEqual(len(release), count)
                    self.assertTrue(all(case.repo == "clean" for case in release))
                    self.assertEqual([(c.name, c.script, c.payload, c.environment, c.expected_decision, c.fixture_metadata) for c in release],
                                     [(c.name, c.script, c.payload, c.environment, c.expected_decision, c.fixture_metadata) for c in standalone])

    def test_resource_contracts_are_validated_before_exact_filtering(self) -> None:
        adapter = load_adapter()
        document = json.loads(adapter.DEFAULT_EXPECTATIONS.read_text())
        document["fixture_sets"]["historical-v1"]["resources"]["gemini.resources.strict-max"]["input_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "expectations.json"
            path.write_text(json.dumps(document))
            with self.assertRaisesRegex(ValueError, "stale fixture hash"):
                adapter.selected_cases(Path("."), "candidate", ["codex.resources.strict-max"],
                                       "resources", "historical-v1", path)

    def test_writer_execution_pairs_require_the_executable_finding(self) -> None:
        adapter = load_adapter()
        path = CLI.parent / "fixtures/tool_guard_file_operations_expectations.json"
        for mode in ("timing", "resources"):
            cases = adapter.selected_cases(Path("."), "candidate", [], mode, "file-operations-v1", path)
            pairs = [case for case in cases if ".writer." in case.name and case.name.endswith(".execution")]
            self.assertEqual(len(pairs), 9)
            for case in pairs:
                with self.subTest(case=case.name):
                    contract = case.fixture_metadata["contract"]
                    self.assertEqual(contract["decision"], "deny")
                    self.assertEqual(contract["attribution"]["security_outcome"], "findings")
                    self.assertEqual(contract["attribution"]["cause"], "force_push_protected_branch")

    def test_response_attribution_requires_one_authoritative_suffix(self) -> None:
        adapter = load_adapter()
        contract = {"decision": "deny", "attribution": {
            "security_outcome": "findings", "audit_outcome": "written",
            "enforcement": "deny", "cause": "force_push_protected_branch"}}
        suffix = ("security_outcome=findings; audit_outcome=written; enforcement=deny; "
                  "build=0123456789abcdef; profile=shell_v1; route=native; cause=force_push_protected_branch.")

        def response(provider, reason):
            if provider == "codex":
                return {"hookSpecificOutput": {"permissionDecision": "deny", "permissionDecisionReason": reason}}
            if provider == "copilot":
                return {"permissionDecision": "deny", "permissionDecisionReason": reason,
                        "hookSpecificOutput": {"permissionDecision": "deny", "permissionDecisionReason": reason}}
            return {"decision": "deny", "reason": reason}

        for provider in ("codex", "copilot", "gemini"):
            good = "Tool Guardian blocked execution. " + suffix
            adapter.validate_response(contract, response(provider, good), provider=provider)
            bad_cause = good.replace("cause=force_push_protected_branch.", "cause=other.")
            mutations = [
                response(provider, "previous_cause=force_push_protected_branch; " + bad_cause),
                response(provider, good[:-1] + "; cause=other."),
                response(provider, good[:-1] + "; cause=force_push_protected_branch."),
                response(provider, good + " " + suffix.replace("cause=force_push_protected_branch.", "cause=other.")),
                {**response(provider, bad_cause), "unrelated": good},
                {**response(provider, "missing suffix"), "unrelated": good},
            ]
            if provider == "copilot":
                contradictory = response(provider, good)
                contradictory["permissionDecisionReason"] = bad_cause
                mutations.append(contradictory)
            for index, output in enumerate(mutations):
                with self.subTest(provider=provider, mutation=index), self.assertRaises(ValueError):
                    adapter.validate_response(contract, output, provider=provider)

    def test_historical_fixture_hashes_and_expectations_are_pinned(self) -> None:
        adapter = load_adapter()
        digests = {
            ("timing", "baseline"): "16f662c2d2b1c041613f8a6f2b79b26b64637a6904651d187b2505e8f4094dd6",
            ("timing", "candidate"): "2b211b3f5bbe34cade8b88202132ddc80fa429fdcbe0e02aac0fc727ab73215e",
            ("resources", "baseline"): "173af2be33560b9ef733579b749e83d3abe07ee5dd6320e31fb9ceac30d06789",
            ("resources", "candidate"): "173af2be33560b9ef733579b749e83d3abe07ee5dd6320e31fb9ceac30d06789",
        }
        for mode, count in (("timing", 156), ("resources", 108)):
            for condition in ("baseline", "candidate"):
                cases = adapter.selected_cases(Path("."), condition, [], mode)
                self.assertEqual(len(cases), count)
                rows = [(case.name, hashlib.sha256(case.payload).hexdigest(), case.expected_decision) for case in cases]
                self.assertEqual(hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest(),
                                 digests[mode, condition])
                self.assertFalse(any("writer.quoted-document" in case.name for case in cases))
                self.assertTrue(all(case.environment["GUARD_MODE"] == "block" for case in cases))

    def test_failure_contracts_through_real_public_entrypoints(self) -> None:
        adapter = load_adapter()
        expectations = CLI.parent / "fixtures/tool_guard_file_operations_expectations.json"
        root = CLI.resolve().parents[1]
        cases = adapter.selected_cases(root, "baseline", [], "resources", "file-operations-v1", expectations)
        with tempfile.TemporaryDirectory() as temporary:
            for case in cases:
                if not any(text in case.name for text in ("audit-unavailable", "bootstrap", "transport.malformed", ".mode.warn.")):
                    continue
                with self.subTest(case=case.name):
                    home = Path(temporary) / case.name
                    home.mkdir()
                    current = adapter.prepared_case(case, root, home=home)
                    adapter.checked_invocation(current, Path(temporary), home)
                    proof = adapter.verify_logging(home, current, 1)
                    adapter.logging_error(proof)
                    self.assertEqual(proof["status"], case.fixture_metadata["contract"]["audit"]["outcome"])
                    if case.fixture_metadata["injection"] != "none":
                        self.assertIsNotNone(proof["failure_injection"])

    @unittest.skipUnless(sys.platform == "darwin", "release execution requires native macOS")
    def test_wrong_mode_and_unexpected_allow_retain_failed_evidence(self) -> None:
        for kind in ("mode", "allow"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.fixture(root / "baseline")
                self.fixture(root / "candidate")
                if kind == "mode":
                    script = script_path(root / "candidate", "codex")
                    script.write_text(script.read_text().replace("'mode': 'block'", "'mode': 'warn'"))
                output = root / "failed.json"
                result = self.run_cli("--baseline-root", str(root / "baseline"), "--candidate-root", str(root / "candidate"),
                                      "--output", str(output), "--mechanics-only", "--case",
                                      "codex.guard.clean" if kind == "mode" else "codex.guard.finding")
                self.assertEqual(result.returncode, 1, result.stderr)
                report = json.loads(output.read_text())
                self.assertFalse(report["gates_met"])
                self.assertIn("mode mismatch" if kind == "mode" else "expected deny", " ".join(report["errors"]))

    @unittest.skipUnless(sys.platform == "darwin", "release execution requires native macOS")
    def test_clean_warn_pass_rejects_unexpected_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root / "baseline")
            self.fixture(root / "candidate")
            script = script_path(root / "baseline", "codex")
            script.write_text(script.read_text().replace("print('{}')", "print('{\"hookSpecificOutput\": {\"permissionDecision\": \"allow\"}, \"systemMessage\": \"unexpected warning\"}')"))
            output = root / "failed.json"
            result = self.run_cli("--baseline-root", str(root / "baseline"), "--candidate-root", str(root / "candidate"),
                                  "--fixture-set", "file-operations-v1", "--expectations",
                                  str(CLI.parent / "fixtures/tool_guard_file_operations_expectations.json"),
                                  "--output", str(output), "--mechanics-only", "--case", "codex.guard.mode.warn.clean")
            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads(output.read_text())
            self.assertIn("ordinary guardian passes must be silent", " ".join(report["errors"]))

    @unittest.skipUnless(sys.platform == "darwin", "release execution requires native macOS")
    def test_completed_record_attribution_is_required_and_checked(self) -> None:
        for field, value in ((None, None), ("enforcement", "deny"), ("security_outcome", "findings"), ("audit_outcome", "failed")):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.fixture(root / "baseline")
                self.fixture(root / "candidate")
                if field is not None:
                    script = script_path(root / "baseline", "codex")
                    record = {"event": "guard_passed", "mode": "block", "enforcement": "allow",
                              "security_outcome": "clean", "audit_outcome": "written"}
                    record[field] = value
                    script.write_text(script.read_text().replace("{'event': 'guard_passed', 'mode': 'block'}", repr(record)))
                output = root / "failed.json"
                result = self.run_cli("--baseline-root", str(root / "baseline"), "--candidate-root", str(root / "candidate"),
                                      "--fixture-set", "file-operations-v1", "--expectations",
                                      str(CLI.parent / "fixtures/tool_guard_file_operations_expectations.json"),
                                      "--output", str(output), "--mechanics-only", "--case", "codex.guard.clean")
                self.assertEqual(result.returncode, 1, result.stderr)
                report = json.loads(output.read_text())
                self.assertIn("completed audit attribution mismatch", " ".join(report["errors"]))

    def test_resource_latency_excludes_response_validation(self) -> None:
        adapter = load_adapter()
        contract = {"mode": "block", "decision": "allow", "attribution": {}}
        from hook_benchmark_support import disposable_environment
        from fixtures import tool_guard_resource_cases
        with tempfile.TemporaryDirectory() as temporary:
            with patch.object(tool_guard_resource_cases, "validate_response", side_effect=lambda *_, **__: time.sleep(0.06)):
                start = time.perf_counter()
                result = adapter.resources.checked_run([sys.executable, "-c", "print('{}')"], b"{}",
                                                       disposable_environment(Path(temporary), "codex"),
                                                       "codex", "allow", contract=contract)
                wall_ms = (time.perf_counter() - start) * 1000
            self.assertLess(result.elapsed_ms, wall_ms - 50)

    def test_versioned_fixture_cli_requires_reviewed_expectations(self) -> None:
        result = self.run_cli("--list", "--fixture-set", "file-operations-v1")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("--expectations", result.stderr)
        result = self.run_cli("--list", "--fixture-set", "file-operations-v1",
                              "--expectations", str(CLI.parent / "fixtures/tool_guard_file_operations_expectations.json"),
                              "--baseline-ref", "260c578ace3514c4f2f741f51d970fc2e938786d")
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = {row["case"]: row for row in json.loads(result.stdout)}
        self.assertEqual(rows["codex.guard.writer.quoted-document"]["expected"],
                         {"baseline": "deny", "candidate": "allow"})

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
            self.assertEqual(result.returncode, 0, result.stderr + str(json.loads(output.read_text())["errors"]))
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
                "hook_test_support.py", "fixtures/tool_guard_resource_cases.py", "reviewed_expectations",
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
