#!/usr/bin/env python3
"""Offline public maintenance behavior through registered foreground processes."""
from __future__ import annotations

import importlib.util
from contextlib import closing
import json
import os
from pathlib import Path
import subprocess
import sqlite3
import sys
import unittest
import uuid

spec = importlib.util.spec_from_file_location("maintenance_fixture", Path(__file__).with_name("test-agent-brain-publication.py"))
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


class MaintenanceTests(unittest.TestCase):
    save_config = fixture.PublicationTests.save_config
    process = fixture.PublicationTests.process
    event = fixture.PublicationTests.event
    cli = fixture.PublicationTests.cli
    ready = fixture.PublicationTests.ready
    stage = fixture.PublicationTests.stage
    annotation = fixture.PublicationTests.annotation
    seed_fact = fixture.PublicationTests.seed_fact
    tip = fixture.PublicationTests.tip
    correction = fixture.PublicationTests.correction
    evidenced = fixture.PublicationTests.evidenced
    interrupted = fixture.PublicationTests.interrupted

    def setUp(self):
        fixture.PublicationTests.setUp(self)
        self.config["maintenance"] = {"enabled": True}
        self.save_config()

    def review(self, ready):
        assigned = dict(ready, obligations=[item for item in ready["obligations"] if item["kind"] == "learn"])
        return fixture.PublicationTests.review(self, assigned)

    def clock(self, utc):
        path = self.config_path.parent / "state/fixture-clock.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps({"utc": utc}))

    def fact(self, name, content="Keep useful qualification.\n", *, status="established", **metadata):
        identity = str(uuid.uuid4())
        (self.repo / "guidance" / (name + ".md")).write_text(self.annotation(identity, content, status=status, **metadata))
        return identity

    def dream_ready(self, task="objective", **fields):
        self.event("startup", task=task, **fields)
        result, ready = self.event("checkpoint", task=task, classification="ready_to_complete")
        self.assertEqual(result.returncode, 0, result.stderr)
        for operation in ("prepare", "complete"):
            result, _ = self.stage(operation, ready, self.review(ready))
            self.assertEqual(result.returncode, 0, result.stderr)
        result, dream = self.event("recover", task=task)
        self.assertEqual(result.returncode, 0, result.stderr)
        return dream

    def dream_review(self, ready):
        item = next(item for item in ready["obligations"] if item["kind"] == "dream")
        return {"schema_version": 1, "outcome": "no_change", "review": {
            "scope": item["scope"], "guidance": [{key: unit[key] for key in ("id", "content_revision", "input_revision")}
                for unit in ready["delivery"]["units"]],
            "sources": [{"path": "guidance/policy.md", "revision": fixture.fixture.sha(self.repo / "guidance/policy.md"),
                         "note": "Reviewed current required policy."}], "note": "Checked the exact assigned guidance; retained its qualifications."},
            "dispositions": [{"id": identity, "revision": revision, "disposition": "reviewed",
                "factual_verification": "uncertain", "note": "Reviewed guidance without claiming new factual verification."}
                for identity, revision in item["batch"]["targets"].items()]}

    def dream_stage(self, operation, ready, payload=None):
        return self.cli("dream", operation, "--invocation-file", ready["invocation_file"],
                        *(["--input", "-"] if payload is not None else []), payload=payload)

    def finish_dream(self, ready):
        payload = self.dream_review(ready)
        for operation in ("prepare", "complete"):
            result, completed = self.dream_stage(operation, ready, payload)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(completed["work_session_status"], "completed")
        return self.cli("status")[1]["maintenance"]

    def test_activation_is_due_and_assigned_dream_blocks_learn_completion(self):
        self.config.pop("maintenance")
        self.save_config()
        _, start = self.event("startup")
        self.assertTrue(start["maintenance"]["due"])
        ready = self.ready()
        self.assertEqual([item["kind"] for item in ready["obligations"]], ["learn", "dream"])
        for operation in ("prepare", "complete"):
            result, completed = self.stage(operation, ready, self.review(ready))
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(completed["work_session_status"], "ready_to_complete")
        _, ready = self.event("recover")
        self.assertEqual(ready["next_action"]["kind"], "dream")
        _, package = self.cli("dream", "start", "--invocation-file", ready["invocation_file"])
        batch = package["work_package"]["batch"]
        self.assertEqual(batch["primary_ids"], [self.unit])
        self.assertEqual(batch["markdown_content_bytes"], 50)
        self.assertGreater(batch["guidance_metadata_bytes"], 0)
        self.assertEqual(batch["content_bytes"], batch["markdown_content_bytes"] + batch["guidance_metadata_bytes"])
        self.assertFalse(batch["oversized"])

    def test_two_full_cycles_use_utc_dates_and_coalesce_missed_intervals(self):
        self.clock("2026-10-01T23:59:59Z")
        for name in ("a", "b", "c", "d", "e", "f"):
            self.fact(name)
        first = self.dream_ready("first")
        cycle_id = first["maintenance"]["cycle"]["id"]
        status = self.finish_dream(first)
        self.assertTrue(status["due"])
        self.assertIsNone(status["last_completed_on"])
        self.clock("2026-10-02T00:00:00Z")
        second = self.dream_ready("second")
        self.assertEqual(second["maintenance"]["cycle"]["id"], cycle_id)
        status = self.finish_dream(second)
        self.assertFalse(status["due"])
        self.assertEqual(status["last_completed_on"], "2026-10-02")
        self.assertEqual(len(status["closed_cycles"]), 1)
        self.clock("2026-10-09T00:30:00+02:00")
        _, before = self.event("startup", task="before-boundary")
        self.assertFalse(before["maintenance"]["due"])
        self.clock("2026-10-30T00:00:00Z")
        third = self.dream_ready("third")
        self.assertNotEqual(third["maintenance"]["cycle"]["id"], cycle_id)
        status = self.finish_dream(third)
        self.assertTrue(status["due"])
        status = self.finish_dream(self.dream_ready("fourth"))
        self.assertFalse(status["due"])
        self.assertEqual(len(status["closed_cycles"]), 2)
        self.assertEqual(status["last_completed_on"], "2026-10-30")

    def test_fresh_flags_cannot_starve_quiet_finite_targets_or_expand_cycle(self):
        quiet = [self.fact("quiet-" + str(index)) for index in range(8)]
        candidate = self.fact("candidate", status="candidate")
        first = self.dream_ready("first", review_flags=[candidate])
        frozen = set(first["maintenance"]["cycle"]["targets"])
        seen = set()
        for index, ready in enumerate((first,)):
            item = next(item for item in ready["obligations"] if item["kind"] == "dream")
            self.assertIsNotNone(item["batch"]["quiet_id"])
            self.assertLessEqual(len(item["batch"]["primary_ids"]), 5)
            seen.update(item["batch"]["primary_ids"])
            self.finish_dream(ready)
        later = self.fact("later-flag", status="candidate")
        ready = self.dream_ready("second", review_flags=[later])
        self.assertEqual(set(ready["maintenance"]["cycle"]["targets"]), frozen)
        self.assertEqual(ready["maintenance"]["cycle"]["later_ids"], [later])
        item = next(item for item in ready["obligations"] if item["kind"] == "dream")
        self.assertIsNotNone(item["batch"]["quiet_id"])
        self.assertNotIn(later, item["batch"]["primary_ids"])
        seen.update(item["batch"]["primary_ids"])
        status = self.finish_dream(ready)
        self.assertFalse(status["due"])
        self.assertTrue(set(quiet).issubset(seen))
        self.assertEqual(status["closed_cycles"][0]["later_ids"], [later])

    def test_scoped_no_change_rejects_unassigned_and_stale_dispositions(self):
        for name in ("a", "b", "c", "d", "e", "f"):
            self.fact(name)
        ready = self.dream_ready()
        payload = self.dream_review(ready)
        payload["dispositions"].append({"id": str(uuid.uuid4()), "revision": "0" * 64,
            "disposition": "reviewed", "factual_verification": "uncertain", "note": "Outside scope."})
        result, rejected = self.dream_stage("prepare", ready, payload)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(rejected["error"]["code"], "DREAM_SCOPE_MISMATCH")
        payload = self.dream_review(ready)
        payload["dispositions"][0]["revision"] = "0" * 64
        result, rejected = self.dream_stage("prepare", ready, payload)
        self.assertEqual(rejected["error"]["code"], "DREAM_SCOPE_MISMATCH")
        _, status = self.cli("status")
        self.assertTrue(status["maintenance"]["due"])
        self.assertTrue(all(target["credit"] is None for target in status["maintenance"]["cycle"]["targets"].values()))

    def test_changed_prior_credit_is_reviewed_again_before_cycle_clock_resets(self):
        first_id = self.fact("a")
        for name in ("b", "c", "d", "e", "f"):
            self.fact(name)
        first = self.dream_ready("first")
        self.finish_dream(first)
        path = self.repo / "guidance/a.md"
        path.write_text(path.read_text() + "A useful counterexample remains.\n")
        second = self.dream_ready("second")
        target = second["maintenance"]["cycle"]["targets"][first_id]
        self.assertIsNone(target["credit"])
        assigned = next(item for item in second["obligations"] if item["kind"] == "dream")
        self.assertIn(first_id, assigned["batch"]["primary_ids"])
        status = self.finish_dream(second)
        self.assertFalse(status["due"])
        checked = status["closed_cycles"][0]["targets"][first_id]
        self.assertEqual(checked["credit"]["revision"], checked["revision"])
        self.assertEqual(checked["credit"]["factual_verification"], "uncertain")

    def test_oversized_required_closure_is_whole_and_runs_alone(self):
        large = self.fact("a-large", "Keep this complete line.\n" * 2000)
        self.fact("b-small")
        ready = self.dream_ready()
        assigned = next(item for item in ready["obligations"] if item["kind"] == "dream")
        self.assertEqual(assigned["batch"]["primary_ids"], [large])
        self.assertTrue(assigned["batch"]["oversized"])
        self.assertGreater(assigned["batch"]["content_bytes"], 32768)
        artifact = next(item for item in ready["delivery"]["artifacts"] if item["path"] == "guidance/a-large.md")
        self.assertEqual(artifact["content"].count("Keep this complete line.\n"), 2000)
        self.assertTrue(artifact["content"].endswith("Keep this complete line.\n" * 2000))
        self.assertTrue(self.finish_dream(ready)["due"])

    def test_undeliverable_mapped_target_stays_whole_assigned_and_incomplete(self):
        identity = str(uuid.uuid4())
        self.config["mapped_units"].append({"id": identity, "path": "guidance/unavailable.md",
            "selector": {"type": "document"}, "kind": "fact", "status": "established",
            "applies": {"paths": ["other/file.py"]}})
        self.save_config()
        _, ready = self.event("startup")
        self.assertIn(identity, ready["maintenance"]["cycle"]["targets"])
        _, ready = self.event("checkpoint", classification="ready_to_complete")
        dream = next(item for item in ready["obligations"] if item["kind"] == "dream")
        self.assertIn(identity, dream["batch"]["primary_ids"])
        self.assertNotEqual(dream["status"], "completed")
        _, status = self.cli("status")
        self.assertTrue(status["maintenance"]["due"])
        self.assertIsNone(status["maintenance"]["cycle"]["targets"][identity]["credit"])
        self.assertFalse(status["maintenance"]["cycle"]["structural_complete"])

    def test_evidenced_candidate_resolution_records_disposition_before_queue_removal(self):
        identity = str(uuid.uuid4())
        self.config["candidate_dir"] = "portable/candidates"
        self.config["history_dir"] = "portable/history"
        self.save_config()
        path = self.repo / "portable/candidates/claim.md"
        path.parent.mkdir(parents=True)
        before = self.annotation(identity, "The app prints outdated.\n", status="candidate")
        path.write_text(before)
        ready = self.dream_ready()
        payload = self.correction(ready, identity, before)
        review = self.dream_review(ready)
        payload["review"] = review["review"]
        payload["review"]["sources"].append({"path": "src/app.py", "revision": fixture.fixture.sha(self.repo / "src/app.py"), "note": "Inspected initial printed literal."})
        payload["dispositions"] = review["dispositions"]
        disposition = next(item for item in payload["dispositions"] if item["id"] == identity)
        disposition.update(disposition="resolved", factual_verification="verified", note="Current source resolves the candidate.")
        after = payload["proposal"]["changes"][0]["content"].replace('"status": "candidate"', '"status": "established"')
        payload["proposal"]["changes"] = [{"path": "portable/candidates/claim.md", "base_revision": fixture.fixture.sha(path), "content": None},
            {"path": "guidance/resolved.md", "base_revision": None, "content": after}]
        result, prepared = self.dream_stage("prepare", ready, payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        journal_path = self.repo / prepared["publication"]["history_path"]
        journal = json.loads(journal_path.read_text())
        self.assertEqual(journal["payload"]["dispositions"], payload["dispositions"])
        self.assertEqual(path.read_text(), before)
        for operation in ("publish", "complete"):
            result, completed = self.dream_stage(operation, ready)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(path.exists())
        self.assertEqual((self.repo / "guidance/resolved.md").read_text(), after)
        _, status = self.cli("status")
        self.assertFalse(status["maintenance"]["due"])
        target = status["maintenance"]["closed_cycles"][0]["targets"][identity]
        self.assertEqual(target["credit"]["publication_id"], completed["publication"]["id"])
        self.assertEqual(target["credit"]["revision"], target["revision"])

    def test_thirty_day_cleanup_preserves_pins_pending_work_and_identity_container(self):
        self.clock("2026-10-01T00:00:00Z")
        ready = self.dream_ready("closed")
        self.finish_dream(ready)
        session_id = ready["identities"]["work_session_id"]
        invocation = Path(ready["invocation_file"])
        pins = self.config_path.parent / "state/validation-pins.json"
        pins.write_text(json.dumps({"schema_version": 1, "work_session_ids": [session_id], "cycle_ids": []}))
        self.clock("2026-10-30T23:59:59Z")
        self.event("startup", task="pending")
        _, status = self.cli("status")
        self.assertIn(session_id, [item["work_session_id"] for item in status["work_sessions"]])
        self.clock("2026-10-31T00:00:00Z")
        self.event("resume", task="pending")
        _, status = self.cli("status")
        self.assertIn(session_id, [item["work_session_id"] for item in status["work_sessions"]])
        pins.unlink()
        self.event("resume", task="pending")
        _, status = self.cli("status")
        self.assertNotIn(session_id, [item["work_session_id"] for item in status["work_sessions"]])
        self.assertEqual(len(status["work_sessions"]), 1)
        self.assertTrue(status["maintenance"]["due"])
        self.assertFalse(invocation.exists())
        self.assertTrue((self.config_path.parent / "state/brain.sqlite3").is_file())
        self.assertTrue((self.config_path.parent / "state/binding.json").is_file())
        self.assertEqual(status["maintenance"]["cleanup"]["pending_files"], [])

    def test_prune_needs_evidence_and_preserves_a_useful_counterexample(self):
        identity = self.fact("obsolete", "The app prints outdated.\n")
        counterexample = self.fact("counterexample", "Keep old behavior when the compatibility flag is set.\n")
        before = (self.repo / "guidance/obsolete.md").read_text()
        counterexample_bytes = (self.repo / "guidance/counterexample.md").read_bytes()
        ready = self.dream_ready()
        payload = self.correction(ready, identity, before)
        reviewed = self.dream_review(ready)
        payload["review"] = reviewed["review"]
        payload["review"]["sources"].append({"path": "src/app.py", "revision": fixture.fixture.sha(self.repo / "src/app.py"), "note": "Current source prints initial."})
        payload["dispositions"] = reviewed["dispositions"]
        next(item for item in payload["dispositions"] if item["id"] == identity).update(disposition="resolved", factual_verification="verified")
        payload["proposal"]["changes"] = [{"path": "guidance/obsolete.md", "base_revision": fixture.fixture.sha(self.repo / "guidance/obsolete.md"), "content": None}]
        claim = payload["proposal"]["claims"][0]
        claim.update(action="prune")
        claim["evidence"].update(basis="inactive", basis_note="Age alone.")
        result, rejected = self.dream_stage("prepare", ready, payload)
        self.assertEqual(rejected["error"]["code"], "PRUNE_UNSUPPORTED")
        self.assertEqual((self.repo / "guidance/obsolete.md").read_text(), before)
        claim["evidence"].update(basis="obsolete", basis_note="The exact current source prints initial instead.")
        result, prepared = self.dream_stage("prepare", ready, payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        for operation in ("publish", "complete"):
            result, completed = self.dream_stage(operation, ready)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.repo / "guidance/obsolete.md").exists())
        self.assertEqual((self.repo / "guidance/counterexample.md").read_bytes(), counterexample_bytes)
        journal = json.loads((self.repo / completed["publication"]["history_path"]).read_text())
        self.assertEqual(journal["changes"][0]["before"], before)
        self.assertNotIn(counterexample, journal["affected_ids"])

    def test_inaccessible_candidate_is_reviewed_without_factual_verification_or_pruning(self):
        identity = self.fact("uncertain", "Unconfirmed version-specific claim.\n", status="candidate")
        path = self.repo / "guidance/uncertain.md"
        before = path.read_bytes()
        ready = self.dream_ready()
        payload = self.dream_review(ready)
        next(item for item in payload["dispositions"] if item["id"] == identity).update(
            disposition="unresolved", factual_verification="unavailable", note="Required external evidence remains inaccessible.")
        for operation in ("prepare", "complete"):
            result, completed = self.dream_stage(operation, ready, payload)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(path.read_bytes(), before)
        _, status = self.cli("status")
        credit = status["maintenance"]["closed_cycles"][0]["targets"][identity]["credit"]
        self.assertEqual(credit["disposition"], "unresolved")
        self.assertEqual(credit["factual_verification"], "unavailable")

    def test_recovered_dream_publication_credits_exact_result_after_output_delivery(self):
        self.recovered_publication()

    def recovered_publication(self, *, cross_task=False):
        identity, before = self.seed_fact()
        ready = self.dream_ready()
        payload = self.correction(ready, identity, before)
        reviewed = self.dream_review(ready)
        payload["review"] = reviewed["review"]
        payload["review"]["sources"].append({"path": "src/app.py", "revision": fixture.fixture.sha(self.repo / "src/app.py"), "note": "Current printed literal is initial."})
        payload["dispositions"] = reviewed["dispositions"]
        next(item for item in payload["dispositions"] if item["id"] == identity).update(disposition="resolved", factual_verification="verified")
        result, _ = self.dream_stage("prepare", ready, payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.interrupted(ready, "after_files", stage_name="dream")
        _, interrupted = self.cli("status")
        self.assertTrue(interrupted["maintenance"]["due"])
        result, recovered = self.event("startup" if cross_task else "recover", task="new-task" if cross_task else "objective")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(recovered["publication_recovery"]["status"], "completed")
        _, status = self.cli("status")
        self.assertEqual(status["state_status"], "available")
        self.assertFalse(status["maintenance"]["due"])
        target = status["maintenance"]["closed_cycles"][0]["targets"][identity]
        self.assertEqual(target["credit"]["revision"], target["revision"])
        self.assertEqual(target["credit"]["publication_id"], recovered["publication_recovery"]["id"])
        self.assertIn("The app prints initial.", (self.repo / "guidance/fact.md").read_text())
        if cross_task:
            self.assertNotEqual(recovered["identities"]["work_session_id"], ready["identities"]["work_session_id"])
            self.assertEqual(recovered["work_session_status"], "active")
            self.assertFalse((self.config_path.parent / "state/output-pending.json").exists())

    def test_recovery_settles_the_prior_task_before_delivering_new_task_context(self):
        self.recovered_publication(cross_task=True)

    def test_failed_dream_output_preserves_pending_work_without_credit(self):
        ready = self.dream_ready()
        payload = self.dream_review(ready)
        result, _ = self.dream_stage("prepare", ready, payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        process = subprocess.Popen([sys.executable, str(fixture.fixture.CLI), "dream", "complete", "--json",
            "--invocation-file", ready["invocation_file"], "--input", "-"], cwd=self.repo,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        process.stdout.close()
        process.stdout = None
        _, errors = process.communicate(json.dumps(payload), timeout=8)
        self.assertNotEqual(process.returncode, 0, errors)
        _, status = self.cli("status")
        self.assertTrue(status["maintenance"]["due"])
        self.assertIsNone(status["maintenance"]["cycle"]["targets"][self.unit]["credit"])
        self.assertNotEqual(status["work_sessions"][0]["work_session_status"], "completed")
        self.assertFalse(self.finish_dream(self.dream_ready())["due"])

    def test_final_publication_invalidates_prior_credit_for_changed_reference(self):
        identity = self.fact("a-source", "The app prints outdated.\n")
        for name in ("b", "c", "d", "e"):
            self.fact(name)
        dependent = self.fact("f-dependent", "Keep this qualified summary.\n", requires=[{"id": identity, "loading_mode": "unit"}])
        self.finish_dream(self.dream_ready("first"))
        ready = self.dream_ready("second")
        assigned = next(item for item in ready["obligations"] if item["kind"] == "dream")
        self.assertNotIn(identity, assigned["batch"]["primary_ids"])
        self.assertIn(dependent, assigned["batch"]["primary_ids"])
        self.assertIn(identity, [item["id"] for item in ready["delivery"]["units"]])
        before = (self.repo / "guidance/a-source.md").read_text()
        payload = self.correction(ready, identity, before)
        payload["proposal"]["changes"][0]["path"] = "guidance/a-source.md"
        reviewed = self.dream_review(ready)
        payload["review"] = reviewed["review"]
        payload["review"]["sources"].append({"path": "src/app.py", "revision": fixture.fixture.sha(self.repo / "src/app.py"), "note": "Inspected current printed initial literal."})
        payload["dispositions"] = reviewed["dispositions"]
        result, _ = self.dream_stage("prepare", ready, payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        for operation in ("publish", "complete"):
            result, completed = self.dream_stage(operation, ready)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(completed["work_session_status"], "completed")
        _, status = self.cli("status")
        self.assertTrue(status["maintenance"]["due"])
        self.assertIsNone(status["maintenance"]["last_completed_on"])
        self.assertIsNone(status["maintenance"]["cycle"]["targets"][identity]["credit"])
        self.assertFalse(self.finish_dream(self.dream_ready("third"))["due"])

    def test_portable_history_reference_retains_closed_operational_record_after_thirty_days(self):
        self.clock("2026-10-01T00:00:00Z")
        identity, before = self.seed_fact()
        ready = self.dream_ready()
        payload = self.correction(ready, identity, before)
        reviewed = self.dream_review(ready)
        payload["review"] = reviewed["review"]
        payload["review"]["sources"].append({"path": "src/app.py", "revision": fixture.fixture.sha(self.repo / "src/app.py"), "note": "Inspected current initial literal."})
        payload["dispositions"] = reviewed["dispositions"]
        next(item for item in payload["dispositions"] if item["id"] == identity).update(disposition="resolved", factual_verification="verified")
        result, _ = self.dream_stage("prepare", ready, payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        for operation in ("publish", "complete"):
            result, completed = self.dream_stage(operation, ready)
            self.assertEqual(result.returncode, 0, result.stderr)
        history_path = self.repo / completed["publication"]["history_path"]
        inverse_bytes = history_path.read_bytes()
        self.clock("2026-11-01T00:00:00Z")
        self.event("startup", task="later")
        _, status = self.cli("status")
        self.assertIn(ready["identities"]["work_session_id"], [item["work_session_id"] for item in status["work_sessions"]])
        self.assertEqual(history_path.read_bytes(), inverse_bytes)
        self.assertTrue(Path(ready["invocation_file"]).is_file())

    def test_damaged_maintenance_records_are_unavailable_and_preserved(self):
        ready = self.dream_ready()
        self.dream_stage("prepare", ready, self.dream_review(ready))
        database = self.config_path.parent / "state/brain.sqlite3"
        # The database is used only to seed faults. All assertions observe the
        # public CLI/bridge and exact unchanged files, never private tables.
        with closing(sqlite3.connect(database)) as connection:
            baseline = json.loads(connection.execute("SELECT record FROM runtime WHERE id=1").fetchone()[0])
        mutations = (
            lambda value: value["maintenance"]["cycle"]["targets"][self.unit].update(credit={}),
            lambda value: value["maintenance"]["cycle"]["targets"][self.unit].update(revision="z" * 64),
            lambda value: value["maintenance"]["cleanup"].update(pending_files=[".agents/context/state/brain.sqlite3"]),
            lambda value: next(item for session in value["sessions"].values() for item in session["obligations"].values() if item["kind"] == "dream")["batch"]["primary_ids"].append(str(uuid.uuid4())),
            lambda value: next(item for session in value["sessions"].values() for item in session["obligations"].values() if item["kind"] == "dream")["dispositions"][0].update(revision="0" * 64),
        )
        for mutate in mutations:
            seeded = json.loads(json.dumps(baseline))
            mutate(seeded)
            with closing(sqlite3.connect(database)) as connection:
                connection.execute("UPDATE runtime SET record=? WHERE id=1", (json.dumps(seeded),))
                connection.commit()
            expected_bytes = database.read_bytes()
            for operation in ("status", "doctor"):
                result, status = self.cli(operation)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(status["state_status"], "unavailable")
                self.assertEqual(status["work_session_status"], "incomplete")
                self.assertNotIn("Traceback", result.stderr)
            result, recovered = self.event("recover")
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(recovered["error"]["code"], "STATE_UNAVAILABLE")
            self.assertEqual(database.read_bytes(), expected_bytes)


if __name__ == "__main__":
    unittest.main()
