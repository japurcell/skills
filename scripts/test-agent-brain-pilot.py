#!/usr/bin/env python3
"""Independent literals at the pilot calculator's public process boundary."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import importlib.util

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "scripts/fixtures/agent-brain/calculator-spec.json"


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agent-brain-pilot-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.spec = json.loads(SPEC.read_text())
        self.records = json.loads((SPEC.parent / "calculator-records.json").read_text())
        for pair in self.records["observations"]:
            for arm in ("baseline", "candidate"):
                evidence = pair[arm]["evidence"]
                snapshot = self.root / evidence["snapshot"]
                snapshot.mkdir(parents=True)
                (snapshot / "result.txt").write_text("Required policy retained.\n")
                review = {"schema_version": 1, "pair_id": pair["pair_id"], "arm": arm,
                    "reviewer": "offline-fixture-human", "kind": "independent_human",
                    "outcome": "passed", "checks": {"policy-retained": "passed"},
                    "snapshot": evidence["snapshot"], "artifacts": evidence["artifacts"],
                    "rubric_revision": hashlib.sha256(json.dumps(self.spec["checks"], sort_keys=True).encode()).hexdigest()}
                review_path = self.root / evidence["review"]["path"]
                review_path.write_text(json.dumps(review))
                evidence["review"]["revision"] = hashlib.sha256(review_path.read_bytes()).hexdigest()

    def run_calculator(self, records=None, spec=None, raw=None, env=None):
        path = self.root / "records.json"
        path.write_text(raw if raw is not None else json.dumps(records or self.records))
        selected = SPEC
        if spec is not None:
            selected = self.root / "spec.json"
            selected.write_text(json.dumps(spec))
            value = json.loads(path.read_text())
            value["spec_revision"] = hashlib.sha256(selected.read_bytes()).hexdigest()
            path.write_text(json.dumps(value))
        result = subprocess.run([sys.executable, str(ROOT / "scripts/validate-agent-brain-pilot.py"),
            "--spec", str(selected), "--records", str(path), "--artifact-root", str(self.root)],
            capture_output=True, text=True, encoding="utf-8", timeout=10, env=env)
        return result, json.loads(result.stdout) if result.stdout else None

    def test_literal_median_and_nearest_rank_keep_pairs_and_fixture_limits(self):
        result, report = self.run_calculator()
        self.assertEqual(result.returncode, 0, result.stderr)
        cohort = report["cohorts"][0]
        self.assertEqual(cohort["baseline"]["guidance_tokens"], {"median": 250.0, "p95": 400})
        self.assertEqual(cohort["candidate"]["guidance_tokens"], {"median": 150.0, "p95": 240})
        self.assertEqual(len(cohort["pairs"]), 4)
        self.assertEqual(cohort["calculator_gates"], "met")
        self.assertEqual(report["product_acceptance"], "incomplete")
        self.assertEqual(cohort["usage"]["candidate"], {"status": "unavailable", "total": None, "unit": None})

    def test_actual_artifact_failure_cannot_be_overruled_by_claimed_success(self):
        path = self.root / "p1/candidate/result.txt"
        path.write_text("Policy removed.\n")
        self.records["observations"][0]["candidate"]["evidence"]["artifacts"]["policy-retained"] = hashlib.sha256(path.read_bytes()).hexdigest()
        evidence = self.records["observations"][0]["candidate"]["evidence"]
        review_path = self.root / evidence["review"]["path"]
        review = json.loads(review_path.read_text())
        review["artifacts"] = evidence["artifacts"]
        review_path.write_text(json.dumps(review))
        evidence["review"]["revision"] = hashlib.sha256(review_path.read_bytes()).hexdigest()
        result, report = self.run_calculator()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["cohorts"][0]["quality"], "failed")
        self.assertEqual(report["cohorts"][0]["calculator_gates"], "failed")

    def test_every_failed_pair_remains_and_regression_blocks_gates(self):
        self.records["observations"][1]["candidate"]["task_outcome"] = "failed"
        self.records["observations"][1]["system_caused_regression"] = True
        result, report = self.run_calculator()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(report["cohorts"][0]["pairs"]), 4)
        self.assertEqual(report["cohorts"][0]["calculator_gates"], "failed")

    def test_missing_visibility_or_human_review_is_incomplete(self):
        for field in ("delivery_complete", "window_complete", "independent_review"):
            with self.subTest(field=field):
                value = copy.deepcopy(self.records)
                value["observations"][0]["candidate"][field] = False
                result, report = self.run_calculator(value)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(report["cohorts"][0]["calculator_gates"], "incomplete")

    def test_unknown_stale_duplicate_partial_and_mismatched_cohorts_reject(self):
        mutations = [lambda v: v.update(spec_revision="0" * 64),
            lambda v: v["observations"].pop(),
            lambda v: v["observations"].append(copy.deepcopy(v["observations"][0])),
            lambda v: v["observations"][0].update(cohort="unknown"),
            lambda v: v["observations"][0].update(configuration="different"),
            lambda v: v["observations"][0].update(tokenizer="unfrozen"),
            lambda v: v["observations"][0].update(window="unfrozen"),
            lambda v: v["observations"][0].update(order="candidate_first")]
        for mutate in mutations:
            value = copy.deepcopy(self.records)
            mutate(value)
            result, _ = self.run_calculator(value)
            self.assertEqual(result.returncode, 2, result.stderr)

    def test_strict_json_numeric_and_usage_boundaries(self):
        for raw in ('{"schema_version":1,"schema_version":1}', '{"value":NaN}', '{"value":Infinity}', '{"value":1e9999}', '{'):
            result, _ = self.run_calculator(raw=raw)
            self.assertEqual(result.returncode, 2)
        for field, bad in (("guidance_tokens", True), ("duration_seconds", -1), ("retrieval_seconds", "5")):
            value = copy.deepcopy(self.records)
            value["observations"][0]["candidate"][field] = bad
            result, _ = self.run_calculator(value)
            self.assertEqual(result.returncode, 2)
        value = copy.deepcopy(self.records)
        value["observations"][0]["candidate"]["usage"] = {"status": "observed", "value": 20, "unit": "account_percent"}
        self.assertEqual(self.run_calculator(value)[0].returncode, 2)

    def test_missing_prerequisite_and_missing_cohort_are_explicit_incomplete(self):
        spec = copy.deepcopy(self.spec)
        spec["cohorts"][0]["prerequisites"]["provider_build"] = None
        result, report = self.run_calculator(spec=spec)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("provider_build", report["cohorts"][0]["incomplete_checks"])
        self.assertEqual(report["cohorts"][0]["calculator_gates"], "incomplete")
        self.records["observations"] = []
        result, report = self.run_calculator()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["cohorts"][0]["status"], "incomplete")

    def test_path_escape_unknown_check_and_semantic_self_report_reject(self):
        spec = copy.deepcopy(self.spec)
        spec["checks"][0]["path"] = "../outside.txt"
        self.assertEqual(self.run_calculator(spec=spec)[0].returncode, 2)
        value = copy.deepcopy(self.records)
        value["observations"][0]["candidate"]["checks"]["invented"] = "passed"
        self.assertEqual(self.run_calculator(value)[0].returncode, 2)

    def test_each_arm_has_distinct_pinned_artifacts_and_attributed_review(self):
        for mutate in (
            lambda v: v["observations"][1]["candidate"]["evidence"].update(snapshot="p1/candidate"),
            lambda v: v["observations"][0]["candidate"]["evidence"]["review"].update(revision="0" * 64),
            lambda v: v["observations"][0]["candidate"]["evidence"]["review"].update(reviewer=""),
            lambda v: v["observations"][0]["candidate"]["evidence"]["artifacts"].update({"policy-retained": "0" * 64})):
            value = copy.deepcopy(self.records)
            mutate(value)
            self.assertEqual(self.run_calculator(value)[0].returncode, 2)
        value = copy.deepcopy(self.records)
        value["observations"][0]["candidate"]["independent_review"] = "agent says yes"
        self.assertEqual(self.run_calculator(value)[0].returncode, 2)

    def test_nonmatching_equivalence_and_incomplete_usage_remain_incomplete(self):
        value = copy.deepcopy(self.records)
        value["observations"][0]["candidate"]["knowledge_revision"] = "changed"
        self.assertEqual(self.run_calculator(value)[0].returncode, 2)
        value = copy.deepcopy(self.records)
        value["observations"][0]["baseline"]["usage"] = {"status": "unavailable", "value": None, "unit": None}
        result, report = self.run_calculator(value)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["cohorts"][0]["usage"]["baseline"]["status"], "incomplete")

    def test_malformed_measured_cohort_is_rejected_without_traceback(self):
        spec = json.loads((SPEC.parent / "pilot-spec.json").read_text())
        records = json.loads((SPEC.parent / "pilot-records-pending.json").read_text())
        for value in (None, 1, "cohort", []):
            with self.subTest(value=value):
                malformed = copy.deepcopy(spec)
                malformed["cohorts"][0] = value
                result, report = self.run_calculator(records=records, spec=malformed)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIsNone(report)
                self.assertNotIn("Traceback", result.stderr)

    def test_fixture_prerequisites_and_sixty_ids_cannot_certify_product(self):
        # Public review reproduced a false pass with 60 copies of one variant,
        # no longitudinal cycles and fixture-only prerequisite strings.
        spec = copy.deepcopy(self.spec)
        spec["kind"] = "measured_pilot"
        cohort = spec["cohorts"][0]
        cohort["schedule"] = [dict(cohort["schedule"][0], id="single-variant-" + str(i)) for i in range(60)]
        cohort["critical_schedule"] = [{"id": "only-policy-" + str(i), "check_id": "policy-retained", "pair_id": None} for i in range(3)]
        self.records["observations"] = []
        result, report = self.run_calculator(spec=spec)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIsNone(report)

    def test_utf8_json_ignores_redirected_legacy_encoding(self):
        spec = copy.deepcopy(self.spec)
        spec["freeze_id"] = "qualification-é-知识"
        result, report = self.run_calculator(spec=spec, env=dict(os.environ, PYTHONIOENCODING="cp1252"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["freeze_id"], spec["freeze_id"])

    def test_input_only_provider_usage_is_incomplete_total(self):
        for pair in self.records["observations"]:
            pair["baseline"]["usage"] = {"status": "observed", "value": 10, "unit": "input_tokens"}
        result, report = self.run_calculator()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["cohorts"][0]["usage"]["baseline"], {"status": "incomplete", "total": None, "unit": None, "observed_input_tokens": 40})

    def test_broken_output_is_failure_without_successful_partial_report(self):
        read_fd, write_fd = os.pipe()
        os.close(read_fd)
        try:
            result = subprocess.run([sys.executable, str(ROOT / "scripts/validate-agent-brain-pilot.py"),
                "--spec", str(SPEC), "--records", str(SPEC.parent / "calculator-records.json"),
                "--artifact-root", str(SPEC.parent / "calculator-artifacts")], stdout=write_fd,
                stderr=subprocess.PIPE, text=True, timeout=10)
        finally:
            os.close(write_fd)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("pilot validation", result.stderr)

    def test_complete_frozen_pending_plan_is_reviewable_and_never_passes(self):
        spec_path = SPEC.parent / "pilot-spec.json"
        records_path = SPEC.parent / "pilot-records-pending.json"
        result = subprocess.run([sys.executable, str(ROOT / "scripts/validate-agent-brain-pilot.py"),
            "--spec", str(spec_path), "--records", str(records_path), "--artifact-root", str(self.root)],
            capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["product_acceptance"], "incomplete")
        self.assertEqual(len(report["cohorts"]), 7)
        self.assertTrue(all(c["status"] == "incomplete" for c in report["cohorts"]))

    def test_measured_manifest_cannot_remove_variants_cycles_paths_or_critical_cases(self):
        frozen = json.loads((SPEC.parent / "pilot-spec.json").read_text())
        for mutate in (
            lambda s: s["cohorts"][0]["schedule"].pop(),
            lambda s: s["cohorts"][0]["critical_schedule"].pop(),
            lambda s: s["cohorts"].pop(),
            lambda s: s.update(workload_manifest_revision="0" * 64),
            lambda s: s["cohorts"][0]["prerequisites"].update(provider_build="not-a-native-build"),
            lambda s: s["cohorts"][0].update(knowledge_revision="other-knowledge")):
            spec = copy.deepcopy(frozen)
            mutate(spec)
            records = {"schema_version": 1, "spec_revision": "filled-by-harness", "observations": [], "critical_observations": []}
            self.assertEqual(self.run_calculator(records=records, spec=spec)[0].returncode, 2)

    def critical_fixture(self, *, standalone=False):
        spec = copy.deepcopy(self.spec)
        records = copy.deepcopy(self.records)
        pair_id = None if standalone else "p1"
        spec["cohorts"][0]["critical_schedule"] = [{"id": "critical-1", "check_id": "policy-retained", "pair_id": pair_id}]
        metrics = [{"task_id": "probe-parent", "session_id": "probe-parent-session", "executor": "primary",
            "guidance_tokens": 30, "duration_seconds": 2, "retrieval_seconds": 0, "delivery_complete": True,
            "window_complete": True, "usage": {"status": "observed", "value": 2, "unit": "credits"},
            "stage_boundaries": ["arrival", "settled"]}, {"task_id": "probe-child", "session_id": "probe-child-session",
            "executor": "child", "guidance_tokens": 20, "duration_seconds": 1, "retrieval_seconds": 0,
            "delivery_complete": True, "window_complete": True, "usage": {"status": "observed", "value": 3, "unit": "credits"},
            "stage_boundaries": ["arrival", "settled"]}] if standalone else None
        critical = {"cohort": "fixture", "id": "critical-1", "check_id": "policy-retained", "pair_id": pair_id,
            "outcome": "passed", "reviewer": "offline-fixture-human", "task_metrics": metrics,
            "evidence_path": "critical.json", "evidence_revision": "filled"}
        candidate = records["observations"][0]["candidate"]["evidence"]
        proof = copy.deepcopy({key: critical[key] for key in ("cohort", "id", "check_id", "pair_id", "outcome", "reviewer", "task_metrics")})
        proof.update(schema_version=1, kind="independent_native_observation", configuration="fixture-config-v1",
            spec_revision=hashlib.sha256(json.dumps(spec).encode()).hexdigest(),
            rubric_revision=hashlib.sha256(json.dumps(spec["checks"], sort_keys=True).encode()).hexdigest(),
            overlap=None if standalone else {"pair_id": "p1", "window": self.spec["cohorts"][0]["window"],
                "snapshot": candidate["snapshot"], "artifacts": candidate["artifacts"]},
            source_artifacts={"p1/candidate/result.txt": candidate["artifacts"]["policy-retained"]},
            review_note="Offline artifact-bound review fixture, never actual native evidence.")
        self.pin_critical(critical, proof)
        records["critical_observations"] = [critical]
        return spec, records, proof

    def pin_critical(self, critical, proof):
        path = self.root / critical["evidence_path"]
        path.write_text(json.dumps(proof))
        critical["evidence_revision"] = hashlib.sha256(path.read_bytes()).hexdigest()

    def test_native_critical_original_source_and_overlap_are_pinned(self):
        spec, records, proof = self.critical_fixture()
        result, report = self.run_calculator(records=records, spec=spec)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["cohorts"][0]["calculator_gates"], "met")
        proof["source_artifacts"] = {"missing-native.json": "0" * 64}
        self.pin_critical(records["critical_observations"][0], proof)
        result, report = self.run_calculator(records=records, spec=spec)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["cohorts"][0]["calculator_gates"], "incomplete")
        proof["source_artifacts"] = {"p1/candidate/result.txt": "0" * 64}
        self.pin_critical(records["critical_observations"][0], proof)
        result, _ = self.run_calculator(records=records, spec=spec)
        self.assertEqual(result.returncode, 2)
        self.assertIn("native critical observation artifact changed", result.stderr)

    def test_native_critical_typed_version_and_mismatched_window_reject(self):
        for mutate in (lambda p: p.update(schema_version=True), lambda p: p["overlap"].update(window="outside-task")):
            spec, records, proof = self.critical_fixture()
            mutate(proof)
            self.pin_critical(records["critical_observations"][0], proof)
            self.assertEqual(self.run_calculator(records=records, spec=spec)[0].returncode, 2)

    def test_parent_child_standalone_usage_is_included_once(self):
        spec, records, _ = self.critical_fixture(standalone=True)
        result, report = self.run_calculator(records=records, spec=spec)
        self.assertEqual(result.returncode, 0, result.stderr)
        cohort = report["cohorts"][0]
        self.assertEqual(cohort["usage"]["candidate"], {"status": "incomplete", "total": 5, "unit": "credits"})
        self.assertEqual(cohort["paired_usage"]["candidate"]["status"], "unavailable")
        self.assertEqual(len(cohort["standalone_probes"]), 2)

    def test_reused_standalone_executor_windows_and_numeric_boolean_proof_reject(self):
        spec, records, proof = self.critical_fixture(standalone=True)
        proof["task_metrics"][0]["delivery_complete"] = 1
        self.pin_critical(records["critical_observations"][0], proof)
        self.assertEqual(self.run_calculator(records=records, spec=spec)[0].returncode, 2)
        spec, records, proof = self.critical_fixture(standalone=True)
        second = copy.deepcopy(records["critical_observations"][0])
        second.update(id="critical-2", evidence_path="critical-2.json")
        spec["cohorts"][0]["critical_schedule"].append({"id": "critical-2", "check_id": "policy-retained", "pair_id": None})
        for item in (records["critical_observations"][0], second):
            revised = copy.deepcopy(proof)
            revised.update(id=item["id"], spec_revision=hashlib.sha256(json.dumps(spec).encode()).hexdigest())
            self.pin_critical(item, revised)
        records["critical_observations"].append(second)
        result, _ = self.run_calculator(records=records, spec=spec)
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot reuse", result.stderr)

    def test_frozen_child_execution_count_mismatch_rejects(self):
        spec, records, _ = self.critical_fixture(standalone=True)
        frozen = json.loads((SPEC.parent / "pilot-spec.json").read_text())
        item = records["critical_observations"][0]
        item.update(cohort="codex-desktop-interactive", id="native-child-delivery-1", check_id="native-child-delivery")
        item["task_metrics"].pop()
        records["observations"] = []
        result, _ = self.run_calculator(records=records, spec=frozen)
        self.assertEqual(result.returncode, 2)
        self.assertIn("execution/session counts", result.stderr)


class ValidationClockTests(unittest.TestCase):
    """Synthetic certified evidence exercises admission, never native proof."""
    def setUp(self):
        spec = importlib.util.spec_from_file_location("pilot_adapter_fixture", ROOT / "scripts/test-agent-brain-adapters.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.fixture = module.AdapterTests("test_provider_start_resume_scope_and_completion_foreground")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.native()
        self.fixture.config["maintenance"] = {"enabled": True}
        self.fixture.save_config()

    def certified_clock(self, proof_overrides=None):
        f = self.fixture
        proof = {"schema_version": 1, "certification_id": f.cert, "provider": "codex",
            "provider_version": "offline-build-1", "entry_mode": "cli", "context_consumed": True,
            "decisions_consumed": True, "events": f.support["native_events"],
            "watchdog_observed": True, "foreground_route_observed": True}
        proof.update(proof_overrides or {})
        proof_path = f.repo / "synthetic-native-proof.json"
        proof_path.write_text(json.dumps(proof))
        f.support.update(status="certified", evidence={"path": proof_path.name,
            "revision": hashlib.sha256(proof_path.read_bytes()).hexdigest()})
        plan = {"schema_version": 1, "kind": "disposable_validation_clock", "integration_id": "fixture",
            "worktree_root": str(f.repo), "config_path": str(f.config_path.relative_to(f.repo)), "config_revision": hashlib.sha256(f.config_path.read_bytes()).hexdigest(),
            "support_binding": hashlib.sha256(json.dumps(f.support, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "allowed_utc": ["2026-10-01T00:00:00Z", "2026-10-08T00:00:00Z"]}
        path = f.config_path.parent / "validation-clock-plan.json"
        path.write_text(json.dumps(plan))
        revision = hashlib.sha256(path.read_bytes()).hexdigest()
        f.support["validation_clock"] = {"path": str(path.relative_to(f.repo)), "revision": revision}
        f.save_support()
        clock = f.config_path.parent / "state/validation-clock.json"
        clock.parent.mkdir(exist_ok=True)
        clock.write_text(json.dumps({"integration_id": "fixture", "plan_revision": revision,
            "utc": "2026-10-01T00:00:00Z"}))
        return path, clock

    def test_exact_certified_disposable_clock_and_real_authority_time(self):
        _, clock = self.certified_clock()
        result, envelope = self.fixture.adapter_event("SessionStart", source="startup")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Read current guidance", json.dumps(envelope))
        result, status = self.fixture.cli("status")
        self.assertEqual(status["maintenance"]["cycle"]["started_on"], "2026-10-01")
        # A 2026-10-01 calendar cannot expire a newly issued real-time handle.
        result, stop = self.fixture.adapter_event("Stop")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("foreground", json.dumps(stop))

    def test_clock_cannot_authorize_offline_record_or_unfrozen_date(self):
        _, clock = self.certified_clock()
        f = self.fixture
        value = json.loads(clock.read_text())
        value["utc"] = "2026-10-09T00:00:00Z"
        clock.write_text(json.dumps(value))
        result, envelope = f.adapter_event("SessionStart", source="startup")
        self.assertIn("NATIVE_UNSUPPORTED", json.dumps(envelope))
        self.assertFalse((f.config_path.parent / "state/brain.sqlite3").exists())
        _, status = f.cli("status")
        self.assertFalse(status["runtime_state_present"])
        self.assertEqual(status["active_context"], "unavailable")
        f.support.update(status="offline_fixture", evidence="offline_translation_only")
        f.save_support()
        result, envelope = f.adapter_event("SessionStart", source="startup")
        self.assertIn("NATIVE_UNSUPPORTED", json.dumps(envelope))

    def test_plan_or_config_drift_and_legacy_native_clock_reject(self):
        path, _ = self.certified_clock()
        path.write_text(path.read_text() + " ")
        result, envelope = self.fixture.adapter_event("SessionStart", source="startup")
        self.assertIn("NATIVE_UNSUPPORTED", json.dumps(envelope))

    def test_configuration_drift_rejects_before_initialization(self):
        self.certified_clock()
        self.fixture.config["maintenance"] = {"enabled": False}
        self.fixture.save_config()
        _, envelope = self.fixture.adapter_event("SessionStart", source="startup")
        self.assertIn("NATIVE_UNSUPPORTED", json.dumps(envelope))
        self.assertFalse((self.fixture.config_path.parent / "state/brain.sqlite3").exists())
        _, status = self.fixture.cli("status")
        self.assertFalse(status["runtime_state_present"])
        self.assertEqual(status["active_context"], "unavailable")

    def test_certified_legacy_fixture_clock_and_unpinned_override_reject(self):
        _, clock = self.certified_clock()
        legacy = clock.with_name("fixture-clock.json")
        legacy.write_text('{"utc":"2026-10-01T00:00:00Z"}')
        _, envelope = self.fixture.adapter_event("SessionStart", source="startup")
        self.assertIn("NATIVE_UNSUPPORTED", json.dumps(envelope))
        legacy.unlink()
        self.fixture.support.pop("validation_clock")
        self.fixture.save_support()
        _, envelope = self.fixture.adapter_event("SessionStart", source="startup")
        self.assertIn("NATIVE_UNSUPPORTED", json.dumps(envelope))

    def test_native_certificate_typed_fields_cannot_accept_numeric_booleans(self):
        self.certified_clock({"context_consumed": 1})
        _, envelope = self.fixture.adapter_event("SessionStart", source="startup")
        self.assertIn("NATIVE_UNSUPPORTED", json.dumps(envelope))
        self.assertFalse((self.fixture.config_path.parent / "state/brain.sqlite3").exists())

    def test_frozen_calendar_advances_two_checked_process_cycles(self):
        _, clock = self.certified_clock()
        f = self.fixture
        for session, utc in (("first", "2026-10-01T00:00:00Z"), ("second", "2026-10-08T00:00:00Z")):
            value = json.loads(clock.read_text())
            value["utc"] = utc
            clock.write_text(json.dumps(value))
            _, startup = f.adapter_event("SessionStart", session_id=session, source="startup")
            self.assertNotIn("NATIVE_UNSUPPORTED", json.dumps(startup))
            _, stopped = f.adapter_event("Stop", session_id=session)
            result, ready = f.run_foreground(stopped, "ready_to_complete")
            self.assertEqual(result.returncode, 0, (ready, result.stderr))
            reviewed = f.review(dict(ready, obligations=[o for o in ready["obligations"] if o["kind"] == "learn"]))
            for operation in ("prepare", "complete"):
                result, completed = f.stage(operation, ready, reviewed)
                self.assertEqual(result.returncode, 0, (completed, result.stderr))
            result, dream = f.run_foreground(stopped, "ready_to_complete")
            self.assertEqual(result.returncode, 0, (dream, result.stderr))
            assigned = next(o for o in dream["obligations"] if o["kind"] == "dream")
            reviewed = f.review(dict(dream, obligations=[assigned]))
            reviewed["dispositions"] = [{"id": identity, "revision": revision, "disposition": "reviewed",
                "factual_verification": "uncertain", "note": "Retained current guidance without invented verification."}
                for identity, revision in assigned["batch"]["targets"].items()]
            for operation in ("prepare", "complete"):
                result, completed = f.cli("dream", operation, "--invocation-file", dream["invocation_file"], "--input", "-", payload=reviewed)
                self.assertEqual(result.returncode, 0, (completed, result.stderr))
        _, status = f.cli("status")
        self.assertEqual([c["closed_on"] for c in status["maintenance"]["closed_cycles"]], ["2026-10-01", "2026-10-08"])


if __name__ == "__main__":
    unittest.main()
