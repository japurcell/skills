#!/usr/bin/env python3
"""Public publication processes, portable history and exact resulting files."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
import signal
import subprocess
import sys
import time
import unittest
import uuid

spec = importlib.util.spec_from_file_location("publication_fixture", Path(__file__).with_name("test-agent-brain-lifecycle.py"))
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


class PublicationTests(unittest.TestCase):
    setUp = fixture.LifecycleTests.setUp
    save_config = fixture.LifecycleTests.save_config
    process = fixture.LifecycleTests.process
    event = fixture.LifecycleTests.event
    cli = fixture.LifecycleTests.cli
    ready = fixture.LifecycleTests.ready
    review = fixture.LifecycleTests.review
    stage = fixture.LifecycleTests.stage

    def annotation(self, identity, content, **metadata):
        fields = {"schema_version": 1, "id": identity, "kind": "fact", "status": "established",
                  "applies": {"paths": ["src/app.py"]}} | metadata
        return '# Knowledge\n<!-- agent-brain ' + json.dumps(fields) + ' -->\n' + content

    def seed_fact(self, *, crlf=False):
        identity = str(uuid.uuid4())
        content = self.annotation(identity, "The app prints outdated.\n")
        if crlf:
            content = content.replace("\n", "\r\n")
        (self.repo / "guidance/fact.md").write_bytes(content.encode())
        return identity, content

    def correction(self, ready, identity, before):
        payload = self.tip(ready)
        payload["review"]["sources"].append({"path": "src/app.py", "revision": fixture.sha(self.repo / "src/app.py"), "note": "Inspected the printed literal."})
        after = before.replace("outdated", "initial")
        after = self.evidenced(after, {"sources": [{"source": "src/app.py", "revision": fixture.sha(self.repo / "src/app.py")}],
            "verification_note": "Inspected the printed literal.", "verified_at": "2026-10-06"})
        payload["proposal"]["changes"] = [{"path": "guidance/fact.md", "base_revision": hashlib.sha256(before.encode()).hexdigest(), "content": after}]
        payload["proposal"]["claims"] = [{"id": identity, "type": "fact", "action": "correct", "scope": {"paths": ["src/app.py"]},
            "evidence": {"verified_at": "2026-10-06", "result": "verified", "basis": "error", "basis_note": "The controlling source prints initial.",
                "source": payload["review"]["sources"][-1]}}]
        return payload

    def evidenced(self, content, evidence):
        def annotate(match):
            fields = json.loads(match.group(1)); fields["evidence"] = evidence
            return "<!-- agent-brain " + json.dumps(fields) + " -->"
        return re.sub(r"<!-- agent-brain (\{[^\n]+\}) -->", annotate, content)

    def interrupted(self, ready, name, *, operation="publish", second=False, payload=None, config_path=None, stage_name="learn"):
        environment = dict(os.environ, AGENT_BRAIN_FIXTURE_BARRIER=name)
        marker = self.config_path.parent / "state/barrier.json"
        marker.unlink(missing_ok=True)
        marker.with_suffix(".release").unlink(missing_ok=True)
        args = [sys.executable, str(fixture.CLI), stage_name, operation, "--json", "--invocation-file", ready["invocation_file"]]
        if config_path:
            args += ["--config", str(config_path)]
        if payload:
            args += ["--input", "-"]
        process = subprocess.Popen(args, cwd=self.repo, stdin=subprocess.PIPE if payload else subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=environment)
        if payload:
            process.stdin.write(json.dumps(payload))
            process.stdin.close()
            process.stdin = None
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        deadline = time.monotonic() + 5
        while not marker.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertTrue(marker.exists(), "public process did not reach controlled file barrier")
        process.send_signal(signal.SIGINT)
        if second:
            try:
                process.send_signal(signal.SIGINT)
            except ProcessLookupError:
                pass
        output, errors = process.communicate(timeout=5)
        self.assertNotEqual(process.returncode, 0, output + errors)
        return output, errors

    def assert_prepared(self, ready, payload):
        result, prepared = self.stage("prepare", ready, payload)
        self.assertEqual(result.returncode, 0, f"{prepared} {result.stderr}")
        return prepared

    def tip(self, ready):
        identity = str(uuid.uuid4())
        annotation = {"schema_version": 1, "id": identity, "kind": "fact", "status": "established", "applies": {"paths": ["src/app.py"]},
            "evidence": {"sources": [{"source": "foreground task observation"}], "verified_at": "2026-10-06",
                "verification_note": "Oversized patch rejected; smaller focused patches succeeded."}}
        content = '# Small patch tip\n<!-- agent-brain ' + json.dumps(annotation) + ' -->\nUse smaller focused patches when an oversized patch fails.\n'
        return {"schema_version": 1, "outcome": "changed", "review": self.review(ready)["review"],
            "proposal": {"base_input_revision": ready["input_revision"], "rationale": "Retain a scoped successful workaround.",
                "changes": [{"path": "guidance/tip.md", "base_revision": None, "content": content}],
                "claims": [{"id": identity, "type": "tip", "action": "add", "scope": {"paths": ["src/app.py"]},
                    "evidence": {"failure": "Oversized patch rejected.", "workaround": "Smaller focused patches succeeded.",
                        "verified_at": "2026-10-06", "result": "observed"}}]}}

    def test_compact_tip_publishes_only_prepared_bytes_and_records_inverse(self):
        ready = self.ready()
        payload = self.tip(ready)
        result, prepared = self.stage("prepare", ready, payload)
        self.assertEqual(result.returncode, 0, f"{prepared} {result.stderr}")
        self.assertFalse((self.repo / "guidance/tip.md").exists())
        result, published = self.stage("publish", ready)
        self.assertEqual(result.returncode, 0, f"{published} {result.stderr}")
        self.assertEqual((self.repo / "guidance/tip.md").read_text(), payload["proposal"]["changes"][0]["content"])
        result, complete = self.stage("complete", ready)
        self.assertEqual(result.returncode, 0, f"{complete} {result.stderr}")
        self.assertEqual(complete["stage_outcome"], "changed")
        self.assertEqual(complete["work_session_status"], "completed")
        journal = json.loads((self.repo / complete["publication"]["history_path"]).read_text())
        self.assertIsNone(journal["changes"][0]["before"])
        self.assertEqual(journal["changes"][0]["after"], payload["proposal"]["changes"][0]["content"])
        self.assertEqual(journal["affected_ids"], [payload["proposal"]["claims"][0]["id"]])
        self.assertEqual(journal["rationale"], "Retain a scoped successful workaround.")
        self.assertEqual(journal["changes"][0]["after_revision"], hashlib.sha256(journal["changes"][0]["after"].encode()).hexdigest())

    def test_large_before_image_rejects_small_deletion_before_preparation(self):
        identity = str(uuid.uuid4())
        # JSON escapes these valid UTF-8 bytes sixfold in the exact before-image.
        before = self.annotation(identity, "Obsolete generated detail.\n<!-- " + "\x01" * (1400 * 1024) + " -->\n")
        self.assertLess(len(before.encode()), 8 * 1024 * 1024)
        path = self.repo / "guidance/large.md"
        path.write_bytes(before.encode())
        ready = self.ready()
        payload = self.correction(ready, identity, before)
        payload["proposal"]["changes"][0].update(path="guidance/large.md", content=None)
        payload["proposal"]["claims"][0].update(action="prune")
        payload["proposal"]["claims"][0]["evidence"].update(basis="obsolete", basis_note="The current source no longer generates this detail.")
        result, rejected = self.stage("prepare", ready, payload)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(rejected["error"]["code"], "PUBLICATION_TOO_LARGE")
        self.assertIn("8 MiB", result.stderr)
        self.assertEqual(path.read_bytes(), before.encode())
        self.assertFalse(list((self.config_path.parent / "history").glob("*.json")))
        result, status = self.cli("status")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotEqual(status["work_sessions"][0]["work_session_status"], "completed")
        self.assertNotIn("publication", status["work_sessions"][0]["obligations"][0])

    def test_seeded_factual_correction_retains_exact_source_identity(self):
        identity, before = self.seed_fact()
        ready = self.ready()
        payload = self.correction(ready, identity, before)
        self.assert_prepared(ready, payload)
        for operation in ("publish", "complete"):
            result, record = self.stage(operation, ready)
            self.assertEqual(result.returncode, 0, f"{record} {result.stderr}")
        self.assertIn("The app prints initial.", (self.repo / "guidance/fact.md").read_text())
        journal = json.loads((self.repo / record["publication"]["history_path"]).read_text())
        self.assertEqual(journal["evidence"][0]["evidence"]["source"], payload["review"]["sources"][-1])
        self.assertEqual(journal["changes"][0]["before"], before)
        result, recall = self.cli("recall", "--path", "src/app.py")
        evidence = next(unit["evidence"] for unit in recall["units"] if unit["id"] == identity)
        self.assertTrue(evidence["available"])
        self.assertEqual(evidence["sources"], [{"source": "src/app.py", "revision": fixture.sha(self.repo / "src/app.py")}])
        self.assertNotIn("verification_note", evidence)
        _, detailed = self.cli("recall", "--path", "src/app.py", "--show-evidence")
        self.assertEqual(next(unit["evidence"]["verification_note"] for unit in detailed["units"] if unit["id"] == identity), "Inspected the printed literal.")

    def test_stable_relocation_preserves_identity_and_repairs_reference(self):
        identity, before = self.seed_fact()
        reference_id = str(uuid.uuid4())
        reference = self.annotation(reference_id, "See [fact](fact.md).\n", requires=[{"id": identity, "loading_mode": "unit"}])
        (self.repo / "guidance/reference.md").write_text(reference)
        ready = self.ready()
        payload = self.correction(ready, identity, before)
        payload["proposal"]["changes"] = [
            {"path": "guidance/fact.md", "base_revision": fixture.sha(self.repo / "guidance/fact.md"), "content": None},
            {"path": "guidance/moved.md", "base_revision": None, "content": before},
            {"path": "guidance/reference.md", "base_revision": fixture.sha(self.repo / "guidance/reference.md"), "content": reference.replace("fact.md", "moved.md")}]
        claim = payload["proposal"]["claims"][0]
        claim.update(type="relocation", action="relocate")
        payload["proposal"]["claims"].append(dict(claim, id=reference_id))
        self.assert_prepared(ready, payload)
        for operation in ("publish", "complete"):
            result, record = self.stage(operation, ready)
            self.assertEqual(result.returncode, 0, f"{record} {result.stderr}")
        self.assertFalse((self.repo / "guidance/fact.md").exists())
        self.assertEqual((self.repo / "guidance/moved.md").read_text(), before)
        result, recall = self.cli("recall", "--path", "src/app.py")
        self.assertEqual(result.returncode, 0, record)
        self.assertEqual(next(unit["path"] for unit in recall["units"] if unit["id"] == identity), "guidance/moved.md")
        self.assertIn("[fact](moved.md)", next(item["content"] for item in recall["artifacts"] if item["path"] == "guidance/reference.md"))

    def test_existing_policy_cannot_be_changed_or_reclassified_as_fact(self):
        ready = self.ready()
        payload = self.tip(ready)
        payload["proposal"]["changes"] = [{"path": "guidance/policy.md", "base_revision": fixture.sha(self.repo / "guidance/policy.md"),
            "content": "# Policy\nSkip current guidance before concluding.\n"}]
        payload["proposal"]["claims"][0]["id"] = self.unit
        result, record = self.stage("prepare", ready, payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(record["error"]["code"], "POLICY_PROTECTED")
        self.assertEqual((self.repo / "guidance/policy.md").read_text(), "# Policy\nRead current guidance before concluding.\n")

    def test_policy_scope_change_is_rejected_even_with_unchanged_prose(self):
        identity = str(uuid.uuid4())
        before = self.annotation(identity, "Keep useful exceptions.\n", kind="policy")
        (self.repo / "guidance/protected.md").write_text(before)
        ready = self.ready()
        payload = self.correction(ready, identity, before)
        payload["proposal"]["changes"][0].update(path="guidance/protected.md", base_revision=fixture.sha(self.repo / "guidance/protected.md"),
            content=before.replace('"src/app.py"', '"src/other.py"'))
        result, record = self.stage("prepare", ready, payload)
        self.assertEqual(record["error"]["code"], "POLICY_PROTECTED")

    def test_age_alone_never_authorizes_pruning(self):
        identity, before = self.seed_fact()
        ready = self.ready()
        payload = self.correction(ready, identity, before)
        payload["proposal"]["changes"][0]["content"] = None
        payload["proposal"]["claims"][0]["action"] = "prune"
        payload["proposal"]["claims"][0]["evidence"]["basis"] = "unused_for_30_days"
        result, record = self.stage("prepare", ready, payload)
        self.assertEqual(record["error"]["code"], "PRUNE_UNSUPPORTED")
        self.assertEqual((self.repo / "guidance/fact.md").read_text(), before)

    def test_claim_source_must_match_actual_current_revision(self):
        identity, before = self.seed_fact()
        ready = self.ready()
        payload = self.correction(ready, identity, before)
        payload["proposal"]["claims"][0]["evidence"]["source"] = dict(payload["review"]["sources"][-1], revision="0" * 64)
        payload["proposal"]["changes"][0]["content"] = payload["proposal"]["changes"][0]["content"].replace(fixture.sha(self.repo / "src/app.py"), "0" * 64)
        result, record = self.stage("prepare", ready, payload)
        self.assertEqual(record["error"]["code"], "SOURCE_STALE")

    def test_exact_destination_base_is_checked_before_any_write(self):
        ready = self.ready()
        payload = self.tip(ready)
        self.assert_prepared(ready, payload)
        (self.repo / "guidance/tip.md").write_text("User authored unrelated content.\n")
        result, record = self.stage("publish", ready)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.repo / "guidance/tip.md").read_text(), "User authored unrelated content.\n")

    def test_interrupted_before_intent_has_no_canonical_effects(self):
        ready = self.ready()
        self.assert_prepared(ready, self.tip(ready))
        self.interrupted(ready, "before_intent")
        self.assertFalse((self.repo / "guidance/tip.md").exists())
        _, status = self.cli("status")
        self.assertNotEqual(status["work_sessions"][0]["work_session_status"], "completed")

    def test_each_durable_fault_boundary_finishes_at_next_eligible_event(self):
        for barrier in ("after_intent", "between_replacements", "after_files", "after_checks"):
            with self.subTest(barrier=barrier):
                # New disposable fixture per independent process fault.
                self.setUp()
                ready = self.ready()
                payload = self.tip(ready)
                second = self.tip(ready)
                second["proposal"]["changes"][0]["path"] = "guidance/second.md"
                payload["proposal"]["changes"] += second["proposal"]["changes"]
                payload["proposal"]["claims"] += second["proposal"]["claims"]
                self.assert_prepared(ready, payload)
                self.interrupted(ready, barrier, second=barrier == "between_replacements")
                _, status = self.cli("status")
                self.assertIn("publication_recovery", status)
                _, recall = self.cli("recall", "--path", "src/app.py")
                self.assertFalse(recall["complete"])
                self.assertTrue(any(gap["code"] == "ABM007" for gap in recall["gaps"]))
                result, recovered = self.event("recover")
                self.assertEqual(result.returncode, 0, f"{recovered} {result.stderr}")
                self.assertEqual(recovered["work_session_status"], "completed")
                for change in payload["proposal"]["changes"]:
                    self.assertEqual((self.repo / change["path"]).read_text(), change["content"])

    def test_canceled_publication_reverses_crlf_exactly_without_restarting(self):
        identity, before = self.seed_fact(crlf=True)
        ready = self.ready()
        self.assert_prepared(ready, self.correction(ready, identity, before))
        self.interrupted(ready, "after_files")
        self.event("cancel")
        result, recovered = self.event("recover")
        self.assertEqual(result.returncode, 0, f"{recovered} {result.stderr}")
        self.assertEqual(recovered["work_session_status"], "cancelled")
        self.assertEqual((self.repo / "guidance/fact.md").read_bytes(), before.encode())
        self.assertNotIn("invocation_file", recovered)

    def test_unexpected_edit_is_preserved_with_explicit_affected_gap(self):
        ready = self.ready()
        self.assert_prepared(ready, self.tip(ready))
        self.interrupted(ready, "after_files")
        (self.repo / "guidance/tip.md").write_text("Unexpected user edit.\n")
        result, record = self.event("recover")
        self.assertEqual(record["error"]["code"], "PUBLICATION_CONFLICT")
        self.assertEqual((self.repo / "guidance/tip.md").read_text(), "Unexpected user edit.\n")
        _, status = self.cli("status")
        self.assertIn("publication_recovery", status)

    def test_harmful_result_failing_real_checker_is_restored(self):
        checker = self.repo / "check.py"
        checker.write_text("from pathlib import Path\nimport sys\nsys.exit(1 if Path('guidance/tip.md').exists() else 0)\n")
        self.config["checks"] = {"required": ["guidance", "review_sources", "harm"], "trusted": [
            {"id": "harm", "argv": [sys.executable, str(checker)], "timeout_seconds": 2}]}
        self.save_config()
        ready = self.ready()
        self.assert_prepared(ready, self.tip(ready))
        self.interrupted(ready, "after_files")
        result, recovered = self.event("recover")
        self.assertEqual(result.returncode, 0, f"{recovered} {result.stderr}")
        self.assertEqual(recovered["publication_recovery"]["status"], "reversed")
        self.assertFalse((self.repo / "guidance/tip.md").exists())
        self.assertNotEqual(recovered["work_session_status"], "completed")

    def test_missing_history_or_state_never_becomes_success(self):
        ready = self.ready()
        prepared = self.assert_prepared(ready, self.tip(ready))
        self.interrupted(ready, "after_intent")
        history_path = self.repo / prepared["publication"]["history_path"]
        history_path.write_text("corrupt")
        _, status = self.cli("status")
        self.assertEqual(status["state_status"], "unavailable")
        result, recovered = self.event("recover")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.repo / "guidance/tip.md").exists())
        (self.config_path.parent / "state/brain.sqlite3").unlink()
        _, status = self.cli("status")
        self.assertEqual(status["state_status"], "unavailable")
        self.assertEqual(status["pending_work"], "unknown")

    def test_configurable_portable_history_directory(self):
        self.config["history_dir"] = "records/inverse"
        self.save_config()
        ready = self.ready()
        prepared = self.assert_prepared(ready, self.tip(ready))
        self.assertTrue(prepared["publication"]["history_path"].startswith("records/inverse/"))
        self.assertFalse((self.repo / ".agents/context/history").exists())

    def test_dangling_markdown_reference_prevents_relocation(self):
        identity, before = self.seed_fact()
        reference_id = str(uuid.uuid4())
        (self.repo / "guidance/reference.md").write_text(self.annotation(reference_id, "See [fact](fact.md).\n"))
        ready = self.ready()
        payload = self.correction(ready, identity, before)
        payload["proposal"]["changes"] = [{"path": "guidance/fact.md", "base_revision": fixture.sha(self.repo / "guidance/fact.md"), "content": None},
            {"path": "guidance/moved.md", "base_revision": None, "content": before}]
        payload["proposal"]["claims"][0].update(type="relocation", action="relocate")
        result, record = self.stage("prepare", ready, payload)
        self.assertEqual(record["error"]["code"], "REFERENCE_INVALID")

    def test_reference_style_destination_must_be_repaired_after_relocation(self):
        identity, before = self.seed_fact()
        reference_id = str(uuid.uuid4())
        (self.repo / "guidance/reference.md").write_text(self.annotation(reference_id, "See [fact][target].\n\n[target]: fact.md\n", requires=[{"id": identity, "loading_mode": "unit"}]))
        ready = self.ready()
        payload = self.correction(ready, identity, before)
        payload["proposal"]["changes"] = [{"path": "guidance/fact.md", "base_revision": fixture.sha(self.repo / "guidance/fact.md"), "content": None},
            {"path": "guidance/moved.md", "base_revision": None, "content": before}]
        payload["proposal"]["claims"][0].update(type="relocation", action="relocate")
        result, record = self.stage("prepare", ready, payload)
        self.assertEqual(record.get("error", {}).get("code"), "REFERENCE_INVALID", record)

    def test_angle_destination_with_space_keeps_its_complete_identity(self):
        identity, before = self.seed_fact()
        reference_id = str(uuid.uuid4())
        reference = self.annotation(reference_id, "See [fact](fact.md).\n")
        (self.repo / "guidance/reference.md").write_text(reference)
        ready = self.ready()
        payload = self.correction(ready, identity, before)
        payload["proposal"]["changes"] = [{"path": "guidance/fact.md", "base_revision": fixture.sha(self.repo / "guidance/fact.md"), "content": None},
            {"path": "guidance/moved fact.md", "base_revision": None, "content": before},
            {"path": "guidance/reference.md", "base_revision": fixture.sha(self.repo / "guidance/reference.md"), "content": reference.replace("fact.md", "<moved fact.md>")}]
        claim = payload["proposal"]["claims"][0]
        claim.update(type="relocation", action="relocate")
        payload["proposal"]["claims"].append(dict(claim, id=reference_id))
        self.assert_prepared(ready, payload)
        for operation in ("publish", "complete"):
            result, record = self.stage(operation, ready)
            self.assertEqual(result.returncode, 0, f"{record} {result.stderr}")

    def test_affected_heading_fragment_must_still_resolve(self):
        identity, before = self.seed_fact()
        reference_id = str(uuid.uuid4())
        (self.repo / "guidance/reference.md").write_text(self.annotation(reference_id, "See [fact](fact.md#knowledge).\n"))
        ready = self.ready()
        payload = self.correction(ready, identity, before)
        payload["proposal"]["changes"][0]["content"] = before.replace("# Knowledge", "# Renamed")
        result, record = self.stage("prepare", ready, payload)
        self.assertEqual(record.get("error", {}).get("code"), "REFERENCE_INVALID", record)

    def test_stale_relevant_source_reverses_attributed_partial_writes(self):
        ready = self.ready()
        self.assert_prepared(ready, self.tip(ready))
        self.interrupted(ready, "after_files")
        (self.repo / "src/app.py").write_text("print('later user edit')\n")
        result, recovered = self.event("recover")
        self.assertEqual(result.returncode, 0, f"{recovered} {result.stderr}")
        self.assertEqual(recovered["publication_recovery"]["status"], "reversed")
        self.assertFalse((self.repo / "guidance/tip.md").exists())
        self.assertEqual((self.repo / "src/app.py").read_text(), "print('later user edit')\n")

    def test_nested_corrupt_history_is_structured_unavailable(self):
        ready = self.ready()
        prepared = self.assert_prepared(ready, self.tip(ready))
        self.interrupted(ready, "after_intent")
        path = self.repo / prepared["publication"]["history_path"]
        journal = json.loads(path.read_text())
        journal["changes"][0]["before"] = {"unexpected": "nested"}
        del journal["integrity"]
        journal["integrity"] = hashlib.sha256(json.dumps(journal, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        path.write_text(json.dumps(journal))
        result, status = self.cli("status")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(status["state_status"], "unavailable")
        self.assertNotIn("Traceback", result.stderr)
        result, recovered = self.event("recover")
        self.assertEqual(recovered["error"]["code"], "PUBLICATION_HISTORY_UNAVAILABLE")

    def test_retry_exhaustion_reverses_and_keeps_completion_incomplete(self):
        self.config["limits"] = {"max_attempts": 1}
        self.save_config()
        ready = self.ready()
        self.assert_prepared(ready, self.tip(ready))
        self.interrupted(ready, "after_files")
        result, recovered = self.event("recover")
        self.assertEqual(result.returncode, 0, f"{recovered} {result.stderr}")
        self.assertEqual(recovered["publication_recovery"]["status"], "reversed")
        self.assertNotIn("invocation_file", recovered)
        self.assertIn("exhausted", recovered["pending_reason"])
        self.assertFalse((self.repo / "guidance/tip.md").exists())
        _, again = self.event("recover")
        self.assertNotEqual(again["work_session_status"], "completed")
        self.assertNotIn("invocation_file", again)

    def test_competing_recovery_is_bounded_and_cannot_interleave_effects(self):
        self.config["limits"] = {"contention_seconds": 0.2}
        self.save_config()
        ready = self.ready()
        self.assert_prepared(ready, self.tip(ready))
        self.interrupted(ready, "after_intent")
        marker = self.config_path.parent / "state/barrier.json"
        marker.unlink()
        event = {"schema_version": 1, "event_id": "parallel-recovery", "event": "recover",
            "integration": {"id": "fixture", "core_version": fixture.VERSION, "adapter_version": "fixture-1", "certification_id": self.cert, "config_revision": fixture.sha(self.config_path)},
            "binding": {"repository_root": str(self.repo), "worktree_root": str(self.repo), "provider_session_id": "conversation", "provider_task_id": "objective", "provider_agent_id": "parent"},
            "scope": {"paths": ["src/app.py"]}}
        process = subprocess.Popen([sys.executable, str(fixture.BRIDGE), "--json"], cwd=self.repo,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            env=dict(os.environ, AGENT_BRAIN_FIXTURE_BARRIER="during_recovery"))
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        process.stdin.write(json.dumps(event)); process.stdin.close(); process.stdin = None
        deadline = time.monotonic() + 5
        while not marker.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertTrue(marker.exists())
        before = time.monotonic()
        result, blocked = self.event("recover")
        self.assertLess(time.monotonic() - before, 1.5)
        self.assertEqual(blocked["error"]["code"], "PUBLICATION_CONTENDED")
        self.assertFalse((self.repo / "guidance/tip.md").exists())
        marker.with_suffix(".release").write_text("continue")
        output, errors = process.communicate(timeout=5)
        self.assertEqual(process.returncode, 0, output + errors)
        self.assertEqual(json.loads(output)["work_session_status"], "completed")

    def test_interrupted_checked_completion_remains_visibly_unsettled(self):
        ready = self.ready()
        review = self.review(ready)
        self.assert_prepared(ready, review)
        output, errors = self.interrupted(ready, "after_completion", operation="complete", payload=review, second=True)
        self.assertEqual(json.loads(output)["error"]["code"], "INTERRUPTED")
        self.assertNotIn("Traceback", errors)
        _, status = self.cli("status")
        self.assertEqual(status["state_status"], "unavailable")
        self.assertEqual(status["error"]["code"], "DELIVERY_RECONCILIATION_REQUIRED")
        result, recovered = self.event("recover")
        self.assertEqual(result.returncode, 0, f"{recovered} {result.stderr}")
        self.assertNotEqual(recovered["work_session_status"], "completed")
        self.assertIn("invocation_file", recovered)

    def test_selected_alternate_config_recovers_unfinished_output(self):
        alternate = self.config_path.parent / "alternate.json"
        self.config_path.rename(alternate)
        event = {"schema_version": 1, "event_id": "alternate", "event": "startup",
            "integration": {"id": "fixture", "core_version": fixture.VERSION, "adapter_version": "fixture-1", "certification_id": self.cert, "config_revision": fixture.sha(alternate)},
            "binding": {"repository_root": str(self.repo), "worktree_root": str(self.repo), "provider_session_id": "conversation", "provider_task_id": "objective", "provider_agent_id": "parent"},
            "scope": {"paths": ["src/app.py"]}}
        result, _ = self.process(fixture.BRIDGE, "--json", "--config", str(alternate), payload=event)
        self.assertEqual(result.returncode, 0, result.stderr)
        event.update(event="checkpoint", classification="ready_to_complete")
        result, ready = self.process(fixture.BRIDGE, "--json", "--config", str(alternate), payload=event)
        review = self.review(ready)
        result, prepared = self.process(fixture.CLI, "learn", "prepare", "--json", "--config", str(alternate), "--invocation-file", ready["invocation_file"], "--input", "-", payload=review)
        self.assertEqual(result.returncode, 0, f"{prepared} {result.stderr}")
        self.interrupted(ready, "after_completion", operation="complete", payload=review, config_path=alternate)
        event.update(event="recover"); event.pop("classification")
        result, recovered = self.process(fixture.BRIDGE, "--json", "--config", str(alternate), payload=event)
        self.assertEqual(result.returncode, 0, f"{recovered} {result.stderr}")
        self.assertNotEqual(recovered["work_session_status"], "completed")
        self.assertIn("invocation_file", recovered)

    def test_unrelated_guidance_remains_coherent_during_pending_publication(self):
        ready = self.ready()
        self.assert_prepared(ready, self.tip(ready))
        self.interrupted(ready, "after_intent")
        result, recall = self.cli("recall", "--path", "src/other.py")
        self.assertEqual(result.returncode, 0, f"{recall} {result.stderr}")
        self.assertTrue(recall["complete"])
        self.assertEqual(recall["artifacts"][0]["content"], "# Policy\nRead current guidance before concluding.\n")

    def test_failed_complete_output_with_unavailable_sqlite_retains_durable_recovery(self):
        import sqlite3
        self.config["limits"] = {"contention_seconds": 0.2}
        self.save_config()
        ready = self.ready()
        review = self.review(ready)
        self.assert_prepared(ready, review)
        marker = self.config_path.parent / "state/barrier.json"
        process = subprocess.Popen([sys.executable, str(fixture.CLI), "learn", "complete", "--json", "--invocation-file", ready["invocation_file"], "--input", "-"],
            cwd=self.repo, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            env=dict(os.environ, AGENT_BRAIN_FIXTURE_BARRIER="after_completion"))
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        process.stdin.write(json.dumps(review)); process.stdin.close(); process.stdin = None
        deadline = time.monotonic() + 5
        while not marker.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertTrue(marker.exists())
        connection = sqlite3.connect(self.config_path.parent / "state/brain.sqlite3", timeout=0)
        connection.execute("BEGIN EXCLUSIVE")
        try:
            process.stdout.close(); process.stdout = None
            marker.with_suffix(".release").write_text("continue")
            _, errors = process.communicate(timeout=5)
            self.assertNotEqual(process.returncode, 0)
            self.assertIn("reconciliation unavailable", errors)
        finally:
            connection.rollback(); connection.close()
        _, status = self.cli("status")
        self.assertEqual(status["state_status"], "unavailable")
        self.assertEqual(status["error"]["code"], "DELIVERY_RECONCILIATION_REQUIRED")
        result, restored = self.event("recover")
        self.assertEqual(result.returncode, 0, f"{restored} {result.stderr}")
        self.assertNotEqual(restored["work_session_status"], "completed")

    def test_corrupt_output_marker_stays_unavailable_until_exact_record_restored(self):
        ready = self.ready()
        review = self.review(ready)
        self.assert_prepared(ready, review)
        self.interrupted(ready, "after_completion", operation="complete", payload=review)
        marker = self.config_path.parent / "state/output-pending.json"
        before = marker.read_bytes()
        damaged = json.loads(before)
        damaged.pop("identities")
        damaged["input_generation"] = []
        marker.write_text(json.dumps(damaged))
        _, status = self.cli("status")
        self.assertEqual(status["state_status"], "unavailable")
        result, blocked = self.event("recover")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(blocked["error"]["code"], "DELIVERY_RECONCILIATION_REQUIRED")
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(json.loads(marker.read_text()), damaged)
        marker.write_bytes(before)
        result, restored = self.event("recover")
        self.assertEqual(result.returncode, 0, f"{restored} {result.stderr}")
        self.assertNotEqual(restored["work_session_status"], "completed")
        self.assertIn("invocation_file", restored)

    def test_recovered_completion_killed_before_bridge_flush_stays_unsettled(self):
        ready = self.ready()
        self.assert_prepared(ready, self.tip(ready))
        self.interrupted(ready, "after_files")
        marker = self.config_path.parent / "state/barrier.json"
        marker.unlink()
        event = {"schema_version": 1, "event_id": "recovered-output", "event": "recover",
            "integration": {"id": "fixture", "core_version": fixture.VERSION, "adapter_version": "fixture-1", "certification_id": self.cert, "config_revision": fixture.sha(self.config_path)},
            "binding": {"repository_root": str(self.repo), "worktree_root": str(self.repo), "provider_session_id": "conversation", "provider_task_id": "objective", "provider_agent_id": "parent"},
            "scope": {"paths": ["src/app.py"]}}
        process = subprocess.Popen([sys.executable, str(fixture.BRIDGE), "--json"], cwd=self.repo,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            env=dict(os.environ, AGENT_BRAIN_FIXTURE_BARRIER="before_bridge_output"))
        process.stdin.write(json.dumps(event)); process.stdin.close(); process.stdin = None
        deadline = time.monotonic() + 5
        while not marker.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertTrue(marker.exists())
        process.kill(); process.communicate(timeout=5)
        self.assertTrue((self.repo / "guidance/tip.md").exists())
        _, status = self.cli("status")
        self.assertEqual(status["state_status"], "unavailable")
        result, restored = self.event("recover")
        self.assertEqual(result.returncode, 0, f"{restored} {result.stderr}")
        self.assertNotEqual(restored["work_session_status"], "completed")
        self.assertIn("invocation_file", restored)

    def test_missing_pending_marker_is_recovered_from_expected_history(self):
        ready = self.ready()
        self.assert_prepared(ready, self.tip(ready))
        self.interrupted(ready, "after_files")
        (self.config_path.parent / "state/publication.json").unlink()
        _, recall = self.cli("recall", "--path", "src/app.py")
        self.assertFalse(recall["complete"])
        self.assertTrue(any(gap["code"] == "ABM007" for gap in recall["gaps"]))
        result, recovered = self.event("recover")
        self.assertEqual(result.returncode, 0, f"{recovered} {result.stderr}")
        self.assertEqual(recovered["work_session_status"], "completed")

    def test_pending_marker_cannot_hide_a_journaled_destination(self):
        ready = self.ready()
        self.assert_prepared(ready, self.tip(ready))
        self.interrupted(ready, "after_files")
        marker = self.config_path.parent / "state/publication.json"
        value = json.loads(marker.read_text()); value["paths"] = []
        marker.write_text(json.dumps(value))
        _, status = self.cli("status")
        self.assertEqual(status["state_status"], "unavailable")
        _, recall = self.cli("recall", "--path", "src/app.py")
        self.assertFalse(recall["complete"])
        result, recovery = self.event("recover")
        self.assertEqual(recovery["error"]["code"], "PUBLICATION_HISTORY_UNAVAILABLE")

    def test_symlink_destination_is_rejected_without_touching_its_target(self):
        ready = self.ready()
        payload = self.tip(ready)
        external = self.repo / "external.md"
        external.write_text("Outside writable guidance.\n")
        (self.repo / "guidance/tip.md").symlink_to(external)
        result, record = self.stage("prepare", ready, payload)
        self.assertEqual(record["error"]["code"], "INPUTS_STALE")
        self.assertEqual(external.read_text(), "Outside writable guidance.\n")

    def test_publish_rejects_replacement_input_without_reading_it(self):
        ready = self.ready()
        payload = self.tip(ready)
        self.assert_prepared(ready, payload)
        result, record = self.stage("publish", ready, {"malicious": "replacement"})
        self.assertEqual(record["error"]["code"], "PUBLICATION_INPUT_UNEXPECTED")
        self.assertFalse((self.repo / "guidance/tip.md").exists())

    def test_external_factual_evidence_does_not_create_policy_authority(self):
        ready = self.ready()
        payload = self.tip(ready)
        payload["proposal"]["changes"][0]["content"] = payload["proposal"]["changes"][0]["content"].replace('"kind": "fact"', '"kind": "policy"')
        result, record = self.stage("prepare", ready, payload)
        self.assertEqual(record["error"]["code"], "POLICY_PROTECTED")

    def test_one_section_correction_keeps_neighbor_notes_without_extra_claim(self):
        identity = str(uuid.uuid4())
        neighbor_id = str(uuid.uuid4())
        first = self.annotation(identity, "The app prints outdated.\n").replace("# Knowledge", "## Printed literal")
        neighbor = self.annotation(neighbor_id, "Use the stable neighboring guidance.\n", evidence={"sources": [{"source": "existing verified note"}], "verification_note": "Keep this useful exception."}).replace("# Knowledge", "## Neighbor")
        before = "# Facts\n" + first + "\n" + neighbor
        (self.repo / "guidance/fact.md").write_text(before)
        ready = self.ready()
        payload = self.correction(ready, identity, first)
        payload["proposal"]["changes"][0].update(base_revision=fixture.sha(self.repo / "guidance/fact.md"), content="# Facts\n" + payload["proposal"]["changes"][0]["content"] + "\n" + neighbor)
        prepared = self.assert_prepared(ready, payload)
        self.assertEqual(prepared["publication"]["affected_ids"], [identity])
        for operation in ("publish", "complete"):
            result, record = self.stage(operation, ready)
            self.assertEqual(result.returncode, 0, f"{record} {result.stderr}")
        self.assertTrue((self.repo / "guidance/fact.md").read_text().endswith(neighbor))
        _, recall = self.cli("recall", "--path", "src/app.py", "--show-evidence")
        self.assertEqual(next(unit["evidence"]["verification_note"] for unit in recall["units"] if unit["id"] == neighbor_id), "Keep this useful exception.")


if __name__ == "__main__":
    unittest.main()
