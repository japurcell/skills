#!/usr/bin/env python3
"""Public common-protocol fixtures; never native provider certification."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import signal
import sqlite3
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import threading
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "skills/agent-brain/scripts/agent-brain.py"
BRIDGE = CLI.parent / "integration-bridge.py"
VERSION = json.loads((CLI.parents[1] / "schemas/version.json").read_text())["bundle_version"]
EVENTS = ["startup", "task", "scope", "checkpoint", "resume", "context_lost", "recover", "pause", "cancel", "child_start", "child_stop"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class LifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="agent-brain-protocol-")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name).resolve()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.config_path = self.repo / ".agents/context/config.json"
        self.config_path.parent.mkdir(parents=True)
        (self.repo / ".gitignore").write_text(".agents/context/state/\n")
        (self.repo / "guidance").mkdir()
        (self.repo / "guidance/policy.md").write_text("# Policy\nRead current guidance before concluding.\n")
        (self.repo / "src").mkdir()
        (self.repo / "src/app.py").write_text("print('initial')\n")
        self.unit = str(uuid.uuid4())
        self.repository_id = str(uuid.uuid4())
        self.cert = str(uuid.uuid4())
        self.config = {
            "schema_version": 1, "repository_id": self.repository_id,
            "knowledge_roots": [{"path": "guidance", "ownership": "agent_brain"}],
            "mapped_units": [{"id": self.unit, "path": "guidance/policy.md", "selector": {"type": "document"},
                "kind": "policy", "status": "established", "applies": {"paths": ["src/**"]}}],
            "startup": [{"id": self.unit, "loading_mode": "whole"}],
            "providers": {"fixture": {"enabled": True, "kind": "protocol_fixture",
                "core_version": VERSION, "adapter_version": "fixture-1", "schema_version": 1,
                "certification_id": self.cert, "support_record": ".agents/context/fixture.json",
                "events": EVENTS, "max_attempts": 3}},
            "checks": {"required": ["guidance", "review_sources"], "trusted": []},
            "maintenance": {"enabled": False},
        }
        self.save_config()
        (self.config_path.parent / "fixture.json").write_text(json.dumps({
            "schema_version": 1, "kind": "protocol_fixture", "repository_id": self.repository_id,
            "worktree_root": str(self.repo), "core_version": VERSION, "adapter_version": "fixture-1",
            "certification_id": self.cert, "events": EVENTS,
        }))
        self.sequence = 0

    def save_config(self) -> None:
        self.config_path.write_text(json.dumps(self.config))

    def process(self, executable: Path, *args: str, payload: object = None,
                repo: Path | None = None) -> tuple[subprocess.CompletedProcess[str], dict]:
        result = subprocess.run([sys.executable, str(executable), *args], cwd=repo or self.repo,
            input=json.dumps(payload) if payload is not None else "", text=True,
            capture_output=True, timeout=8, check=False)
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail(f"No public JSON result: {result.returncode}: {result.stdout!r} {result.stderr!r}")
        return result, data

    def event(self, kind: str, *, agent: str = "parent", task: str = "objective",
              repo: Path | None = None, **fields: object) -> tuple[subprocess.CompletedProcess[str], dict]:
        self.sequence += 1
        current_root = repo or self.repo
        event = {"schema_version": 1, "event_id": f"event-{self.sequence}", "event": kind,
            "integration": {"id": "fixture", "core_version": VERSION, "adapter_version": "fixture-1",
                "certification_id": self.cert, "config_revision": sha(current_root / ".agents/context/config.json")},
            "binding": {"repository_root": str(self.repo), "worktree_root": str(current_root),
                "provider_session_id": "conversation", "provider_task_id": task,
                "provider_agent_id": agent},
            "scope": {"paths": ["src/app.py"]}}
        event.update(fields)
        return self.process(BRIDGE, "--json", payload=event, repo=current_root)

    def cli(self, *args: str, payload: object = None) -> tuple[subprocess.CompletedProcess[str], dict]:
        return self.process(CLI, *args, "--json", payload=payload)

    def ready(self, agent: str = "parent") -> dict:
        self.event("startup", agent=agent)
        result, record = self.event("checkpoint", agent=agent, classification="ready_to_complete")
        self.assertEqual(result.returncode, 0, result.stderr)
        return record

    def review(self, ready: dict) -> dict:
        return {"schema_version": 1, "outcome": "no_change", "review": {
            "scope": ready["obligations"][-1]["scope"],
            "guidance": [{key: unit[key] for key in ("id", "content_revision", "input_revision")}
                         for unit in ready["delivery"]["units"]],
            "sources": [{"path": "guidance/policy.md", "revision": sha(self.repo / "guidance/policy.md"),
                         "note": "Reviewed the controlling policy at its current source revision."}],
            "note": "The reviewed scope has no durable correction or lesson to publish."}}

    def stage(self, operation: str, ready: dict, payload: object = None) -> tuple[subprocess.CompletedProcess[str], dict]:
        return self.cli("learn", operation, "--invocation-file", ready["invocation_file"],
                        *( ["--input", "-"] if payload is not None else []), payload=payload)

    def test_startup_and_clarifications_keep_one_objective(self) -> None:
        result, start = self.event("startup")
        self.assertEqual(result.returncode, 0, f"{result.stderr} {start}")
        self.assertTrue(start["delivery"]["complete"])
        self.assertEqual(start["delivery"]["artifacts"][0]["content"],
            "# Policy\nRead current guidance before concluding.\n")
        identities = start["identities"]
        for name in ("repository_id", "worktree_id", "work_session_id", "task_id", "agent_id"):
            uuid.UUID(identities[name])
        _, waiting = self.event("checkpoint", classification="awaiting_user")
        _, clarification = self.event("task")
        self.assertEqual(clarification["identities"], identities)
        self.assertEqual(waiting["work_session_status"], "awaiting_user")
        self.assertEqual(clarification["work_session_status"], "active")
        _, unknown = self.event("checkpoint")
        self.assertEqual(unknown["next_action"]["kind"], "checkpoint")
        self.assertEqual(unknown["obligations"], [])
        result, status = self.cli("status")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(status["work_sessions"]), 1)
        self.assertEqual(status["work_sessions"][0]["checkpoint"], "active")

    def test_utf8_stdin_ignores_ambient_encoding_for_bridge_and_review(self) -> None:
        original = self.repo / "guidance/policy.md"
        renamed = self.repo / "guidance/política.md"
        original.rename(renamed)
        self.config["mapped_units"][0]["path"] = "guidance/política.md"
        self.save_config()
        event = {"schema_version": 1, "event_id": "inicio-é", "event": "startup",
            "integration": {"id": "fixture", "core_version": VERSION, "adapter_version": "fixture-1",
                "certification_id": self.cert, "config_revision": sha(self.config_path)},
            "binding": {"repository_root": str(self.repo), "worktree_root": str(self.repo),
                "provider_session_id": "conversación", "provider_task_id": "objetivo",
                "provider_agent_id": "agente-é"}, "scope": {"paths": ["src/app.py"]}}
        environment = dict(os.environ, PYTHONIOENCODING="cp1252")
        startup = subprocess.run([sys.executable, str(BRIDGE), "--json"], cwd=self.repo,
            input=json.dumps(event, ensure_ascii=False).encode("utf-8"), capture_output=True,
            timeout=8, env=environment)
        self.assertEqual(startup.returncode, 0, startup.stderr)
        event.update(event="checkpoint", event_id="listo-é", classification="ready_to_complete")
        checkpoint = subprocess.run([sys.executable, str(BRIDGE), "--json"], cwd=self.repo,
            input=json.dumps(event, ensure_ascii=False).encode("utf-8"), capture_output=True,
            timeout=8, env=environment)
        self.assertEqual(checkpoint.returncode, 0, checkpoint.stderr)
        ready = json.loads(checkpoint.stdout)
        self.assertEqual(ready["identities"], json.loads(startup.stdout)["identities"])
        review = {"schema_version": 1,
            "outcome": "no_change", "review": {"scope": ready["obligations"][-1]["scope"],
                "guidance": [{key: unit[key] for key in ("id", "content_revision", "input_revision")}
                             for unit in ready["delivery"]["units"]],
                "sources": [{"path": "guidance/política.md", "revision": sha(renamed), "note": "Revisada política."}],
                "note": "Sin cambios."}}
        for operation in ("prepare", "complete"):
            result = subprocess.run([sys.executable, str(CLI), "learn", operation, "--json",
                "--invocation-file", ready["invocation_file"], "--input", "-"], cwd=self.repo,
                input=json.dumps(review, ensure_ascii=False).encode("utf-8"), capture_output=True,
                timeout=8, env=environment)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["work_session_status"], "completed")

    def test_noncanonical_certification_identity_is_rejected_before_state(self) -> None:
        canonical = "aaaaaaaa-1111-4111-8111-aaaaaaaaaaaa"
        self.cert = canonical.upper()
        self.config["providers"]["fixture"]["certification_id"] = self.cert
        self.save_config()
        support_path = self.config_path.parent / "fixture.json"
        support = json.loads(support_path.read_text())
        support["certification_id"] = self.cert
        support_path.write_text(json.dumps(support))
        result, rejected = self.event("startup")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(rejected["error"]["code"], "INPUT_INVALID")
        self.assertFalse((self.config_path.parent / "state").exists())
        self.config["providers"]["fixture"]["certification_id"] = canonical
        self.save_config()
        result, rejected = self.event("startup")
        self.assertEqual(rejected["error"]["code"], "INTEGRATION_MISMATCH")
        self.cert = canonical
        result, rejected = self.event("startup")
        self.assertEqual(rejected["error"]["code"], "SUPPORT_RECORD_INVALID")
        self.assertFalse((self.config_path.parent / "state").exists())
        support["certification_id"] = canonical
        support_path.write_text(json.dumps(support))
        ready = self.ready()
        result, _ = self.stage("prepare", ready, self.review(ready))
        self.assertEqual(result.returncode, 0, result.stderr)
        result, complete = self.stage("complete", ready, self.review(ready))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(complete["work_session_status"], "completed")

    def test_decoder_integer_limit_is_structured_at_config_process_seams(self) -> None:
        for raw in ("9" * 5000, "[" * 2000 + "0" + "]" * 2000):
            source = json.dumps(self.config).replace('"schema_version": 1', '"schema_version": ' + raw, 1)
            self.config_path.write_text(source)
            for command in ("status", "doctor"):
                result, rejected = self.cli(command)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(rejected["setup_status"], "invalid")
                self.assertNotIn("Traceback", result.stderr)
            result, rejected = self.cli("recall")
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(rejected["error"]["code"], "CONFIGURATION_INVALID")
        self.assertFalse((self.config_path.parent / "state").exists())

    def test_oversized_durable_time_is_unavailable_without_traceback(self) -> None:
        ready = self.ready()
        database = self.config_path.parent / "state/brain.sqlite3"
        before = database.read_bytes()
        binding = json.loads((database.parent / "binding.json").read_text())
        for raw_time in ("9" * 400, "9" * 5000, "[" * 2000 + "0" + "]" * 2000):
            owner = {"obligation_id": ready["obligations"][0]["id"], "agent_id": ready["identities"]["agent_id"],
                     "generation": 1, "expires_at": "oversized-time"}
            seeded = json.dumps(binding | {"revision": 0, "ownership_generation": 1, "owner": owner,
                                          "sessions": {}, "invocations": {}}).replace('"oversized-time"', raw_time)
            connection = sqlite3.connect(database)
            try:
                connection.execute("UPDATE runtime SET record=? WHERE id=1", (seeded,))
                connection.commit()
            finally:
                connection.close()
            for command in ("status", "doctor"):
                result, rejected = self.cli(command)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(rejected["state_status"], "unavailable")
                self.assertEqual(rejected["work_session_status"], "incomplete")
                self.assertNotIn("Traceback", result.stderr)
            result, rejected = self.event("recover")
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(rejected["error"]["code"], "STATE_UNAVAILABLE")
            database.write_bytes(before)

    def test_invalid_utf8_stdin_is_structured_and_invalid_authority_reads_no_input(self) -> None:
        environment = dict(os.environ, PYTHONIOENCODING="cp1252")
        bad_bridge = subprocess.run([sys.executable, str(BRIDGE), "--json"], cwd=self.repo,
            input=b"\xff", capture_output=True, timeout=8, env=environment)
        self.assertEqual(json.loads(bad_bridge.stdout)["error"]["code"], "INPUT_INVALID")
        self.assertFalse((self.config_path.parent / "state").exists())
        ready = self.ready()
        invalid_review = json.dumps(self.review(ready)).encode().replace(
            b"The reviewed scope", b"\xffThe reviewed scope")
        for invocation, expected in ((ready["invocation_file"], "INPUT_INVALID"),
                                     (str(self.repo / "absent-invocation.json"), "INVOCATION_INVALID")):
            result = subprocess.run([sys.executable, str(CLI), "learn", "prepare", "--json",
                "--invocation-file", invocation, "--input", "-"], cwd=self.repo,
                input=invalid_review, capture_output=True, timeout=8, env=environment)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)["error"]["code"], expected)

    def test_checked_no_change_is_the_only_completion_signal(self) -> None:
        ready = self.ready()
        self.assertEqual(ready["work_session_status"], "ready_to_complete")
        result, start = self.stage("start", ready)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(start["stage_outcome"], "incomplete")
        self.assertIn("procedure", start["work_package"])
        _, status = self.cli("status")
        self.assertEqual(status["work_sessions"][0]["work_session_status"], "ready_to_complete")
        review = self.review(ready)
        result, prepared = self.stage("prepare", ready, review)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(prepared["stage_outcome"], "incomplete")
        self.assertEqual({receipt["checker_id"] for receipt in prepared["check_receipts"]},
                         {"guidance", "review_sources"})
        result, completed = self.stage("complete", ready, review)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(completed["stage_outcome"], "no_change")
        self.assertEqual(completed["work_session_status"], "completed")
        result, duplicate = self.event("checkpoint", classification="ready_to_complete")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(duplicate["stage_outcome"], "no_change")
        self.assertEqual(duplicate["work_session_status"], "completed")
        self.assertEqual(len(duplicate["obligations"]), 1)

    def test_duplicate_callbacks_join_and_stage_callbacks_do_not_recurse(self) -> None:
        ready = self.ready()
        _, duplicate = self.event("checkpoint", classification="ready_to_complete")
        self.assertEqual(duplicate["invocation_file"], ready["invocation_file"])
        self.assertEqual(duplicate["obligations"][0]["id"], ready["obligations"][0]["id"])
        self.assertEqual(duplicate["obligations"][0]["attempt_count"], 1)
        _, callback = self.event("checkpoint", classification="ready_to_complete", stage_generated=ready["attempt_id"])
        self.assertEqual(len(callback["obligations"]), 1)
        self.assertEqual(callback["next_action"]["kind"], "none")
        self.assertNotIn("invocation_file", callback)

    def test_unverified_assertions_and_invented_receipts_do_not_complete(self) -> None:
        ready = self.ready()
        assertion = {"schema_version": 1, "outcome": "no_change", "passed": True,
                     "check_receipts": ["invented"], "review": self.review(ready)["review"]}
        result, rejected = self.stage("complete", ready, assertion)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(rejected["stage_outcome"], "incomplete")
        _, status = self.cli("status")
        self.assertNotEqual(status["work_sessions"][0]["work_session_status"], "completed")

    def test_failed_actual_checker_is_bounded_and_duplicates_do_not_reset_attempts(self) -> None:
        self.config["checks"]["trusted"] = [{"id": "project", "argv": [sys.executable, "-c", "raise SystemExit(7)"], "timeout_seconds": 1}]
        self.config["checks"]["required"].append("project")
        self.save_config()
        ready = self.ready()
        review = self.review(ready)
        for expected in (1, 2, 3):
            result, failure = self.stage("prepare", ready, review)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(failure["stage_outcome"], "incomplete")
            self.assertEqual(failure["check_receipts"][-1]["exit_code"], 7)
            _, duplicate = self.event("checkpoint", classification="ready_to_complete")
            self.assertEqual(duplicate["obligations"][0]["attempt_count"], expected)
        result, failure = self.stage("prepare", ready, review)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(failure["error"]["code"], "ATTEMPTS_EXHAUSTED")
        _, recovered = self.event("recover")
        self.assertEqual(recovered["obligations"][0]["attempt_count"], 3)
        self.assertNotIn("invocation_file", recovered)

    def test_only_one_semantic_repair_is_allowed(self) -> None:
        ready = self.ready()
        bad = self.review(ready)
        bad["review"]["guidance"][0]["input_revision"] = "0" * 64
        result, _ = self.stage("prepare", ready, bad)
        self.assertNotEqual(result.returncode, 0)
        _, duplicate = self.event("checkpoint", classification="ready_to_complete")
        self.assertEqual(duplicate["obligations"][0]["semantic_repairs"], 1)
        result, _ = self.stage("prepare", ready, bad)
        self.assertNotEqual(result.returncode, 0)
        result, blocked = self.stage("prepare", ready, self.review(ready))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(blocked["error"]["code"], "SEMANTIC_REPAIR_EXHAUSTED")

    def test_relevant_input_drift_invalidates_prepared_and_completed_results(self) -> None:
        ready = self.ready()
        review = self.review(ready)
        self.stage("prepare", ready, review)
        (self.repo / "src/app.py").write_text("print('changed')\n")
        result, stale = self.stage("complete", ready, review)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(stale["error"]["code"], "INPUTS_STALE")
        _, renewed = self.event("recover")
        self.assertGreater(renewed["input_generation"], ready["input_generation"])
        self.assertEqual(renewed["obligations"][0]["id"], ready["obligations"][0]["id"])
        result, unprepared = self.stage("complete", renewed, self.review(renewed))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(unprepared["error"]["code"], "REVIEW_NOT_PREPARED")
        self.stage("prepare", renewed, self.review(renewed))
        self.stage("complete", renewed, self.review(renewed))
        (self.repo / "guidance/policy.md").write_text("# Policy\nUpdated controlling guidance.\n")
        _, changed = self.event("checkpoint", classification="ready_to_complete")
        self.assertEqual(changed["stage_outcome"], "incomplete")
        self.assertGreater(changed["input_generation"], renewed["input_generation"])

    def test_context_loss_restores_content_and_invalidates_old_review(self) -> None:
        ready = self.ready()
        self.stage("prepare", ready, self.review(ready))
        result, restored = self.event("context_lost")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertGreater(restored["context_generation"], ready["context_generation"])
        self.assertEqual(restored["delivery"]["artifacts"][0]["content"],
                         ready["delivery"]["artifacts"][0]["content"])
        result, revoked = self.stage("complete", ready, self.review(ready))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(revoked["error"]["code"], "INVOCATION_REVOKED")
        result, fresh = self.stage("complete", restored, self.review(restored))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(fresh["error"]["code"], "REVIEW_NOT_PREPARED")

    def test_invalid_expired_and_cross_stage_handles_fail_before_semantic_input(self) -> None:
        self.config["limits"] = {"lease_seconds": 0.15}
        self.save_config()
        ready = self.ready()
        result, mismatch = self.cli("dream", "start", "--invocation-file", ready["invocation_file"], "--input", "does-not-exist.json")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(mismatch["error"]["code"], "INVOCATION_MISMATCH")
        invocation = Path(ready["invocation_file"])
        original = invocation.read_bytes()
        invocation.write_text(json.dumps({"schema_version": 1, "handle": "invented"}))
        result, invalid = self.stage("prepare", ready, self.review(ready))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(invalid["error"]["code"], "INVOCATION_INVALID")
        invocation.write_bytes(original)
        time.sleep(0.2)
        result, expired = self.cli("learn", "prepare", "--invocation-file", ready["invocation_file"], "--input", "does-not-exist.json")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(expired["error"]["code"], "INVOCATION_EXPIRED")
        _, callback = self.event("checkpoint", classification="ready_to_complete", timestamp=4102444800)
        self.assertNotIn("invocation_file", callback)
        _, recovered = self.event("recover", timestamp=0)
        self.assertIn("invocation_file", recovered)
        self.assertGreater(recovered["ownership_generation"], ready["ownership_generation"])

    def test_two_agents_retrieve_but_cannot_steal_live_ownership(self) -> None:
        ready = self.ready()
        result, other = self.event("startup", agent="second")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotEqual(other["identities"]["agent_id"], ready["identities"]["agent_id"])
        self.assertTrue(other["delivery"]["complete"])
        _, pending = self.event("checkpoint", agent="second", classification="ready_to_complete")
        self.assertNotIn("invocation_file", pending)
        self.assertEqual(pending["obligations"][0]["owner_agent_id"], ready["identities"]["agent_id"])
        result, _ = self.stage("start", ready)
        self.assertEqual(result.returncode, 0)

    def test_pause_and_cancel_revoke_without_resurrecting_objective(self) -> None:
        for event_kind, expected in (("pause", "paused"), ("cancel", "cancelled")):
            with self.subTest(event=event_kind):
                task = event_kind
                self.event("startup", task=task)
                _, ready = self.event("checkpoint", task=task, classification="ready_to_complete")
                _, stopped = self.event(event_kind, task=task)
                self.assertEqual(stopped["work_session_status"], expected)
                result, revoked = self.stage("start", ready)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(revoked["error"]["code"], "INVOCATION_REVOKED")
                for next_event in ("resume", "task", "recover", "checkpoint"):
                    _, resumed = self.event(next_event, task=task, classification="ready_to_complete")
                    self.assertEqual(resumed["work_session_status"], expected)
                    self.assertNotIn("invocation_file", resumed)
                    self.assertEqual(len(resumed["obligations"]), 1)

    def test_missing_and_corrupt_expected_state_are_visible_and_not_recreated(self) -> None:
        self.ready()
        database = self.repo / ".agents/context/state/brain.sqlite3"
        recoverable = database.read_bytes()
        for content in (None, b"broken state"):
            with self.subTest(content=content):
                if content is None:
                    database.unlink()
                else:
                    database.write_bytes(content)
                _, status = self.cli("status")
                self.assertEqual(status["state_status"], "unavailable")
                self.assertEqual(status["pending_work"], "unknown")
                result, failed = self.event("recover")
                self.assertEqual(result.returncode, 1)
                self.assertEqual(failed["error"]["code"], "STATE_UNAVAILABLE")
                self.assertEqual(database.read_bytes() if database.exists() else None, content)
                database.write_bytes(recoverable)

    def test_registered_children_settle_scope_before_parent_completion(self) -> None:
        self.event("startup")
        result, child = self.event("child_start", agent="child", parent_agent_id="parent", assigned_obligations=["scope_review"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(child["delivery"]["complete"])
        _, parent = self.event("checkpoint", classification="ready_to_complete")
        self.assertNotIn("invocation_file", parent)
        _, child_ready = self.event("child_stop", agent="child", classification="ready_to_complete")
        self.assertEqual(child_ready["obligations"][-1]["kind"], "child_review")
        review = self.review(child_ready)
        result, _ = self.stage("prepare", child_ready, review)
        self.assertEqual(result.returncode, 0)
        result, completed_child = self.stage("complete", child_ready, review)
        self.assertEqual(result.returncode, 0)
        self.assertNotEqual(completed_child["work_session_status"], "completed")
        _, parent_ready = self.event("recover")
        review = self.review(parent_ready)
        review["review"]["scope"] = parent_ready["obligations"][0]["scope"]
        self.stage("prepare", parent_ready, review)
        result, completed = self.stage("complete", parent_ready, review)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(completed["work_session_status"], "completed")
        self.assertEqual([obligation["kind"] for obligation in completed["obligations"]].count("learn"), 1)

    def test_broken_bridge_output_preserves_pending_without_usable_delivery(self) -> None:
        self.event("startup")
        event = {"schema_version": 1, "event_id": "closed-output", "event": "checkpoint",
            "integration": {"id": "fixture", "core_version": VERSION, "adapter_version": "fixture-1",
                "certification_id": self.cert, "config_revision": sha(self.config_path)},
            "binding": {"repository_root": str(self.repo), "worktree_root": str(self.repo),
                "provider_session_id": "conversation", "provider_task_id": "objective", "provider_agent_id": "parent"},
            "scope": {"paths": ["src/app.py"]}, "classification": "ready_to_complete"}
        with subprocess.Popen([sys.executable, str(BRIDGE), "--json"], cwd=self.repo,
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            process.stdout.close()
            process.stdin.write(json.dumps(event))
            process.stdin.close()
            diagnostic = process.stderr.read()
            code = process.wait(timeout=5)
        self.assertEqual(code, 1, diagnostic)
        _, status = self.cli("status")
        session = status["work_sessions"][0]
        self.assertFalse(session["agents"][0]["delivery_complete"])
        self.assertEqual(session["work_session_status"], "incomplete")
        self.assertEqual(session["obligations"][0]["stage_outcome"], "incomplete")

    def test_human_start_delivers_the_complete_work_package(self) -> None:
        ready = self.ready()
        result = subprocess.run([sys.executable, str(CLI), "learn", "start", "--invocation-file", ready["invocation_file"]],
                                cwd=self.repo, text=True, capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Read current guidance before concluding.", result.stdout)
        self.assertIn("src/app.py", result.stdout)
        self.assertIn(ready["input_revision"], result.stdout)

    def test_child_scope_expansion_requires_review_of_current_assignment(self) -> None:
        self.event("startup")
        self.event("child_start", agent="child", parent_agent_id="parent")
        _, original = self.event("child_stop", agent="child", classification="ready_to_complete")
        old_review = self.review(original)
        self.stage("prepare", original, old_review)
        (self.repo / "src/other.py").write_text("print('other')\n")
        _, expanded = self.event("scope", agent="child", scope={"paths": ["src/other.py"]})
        _, ready = self.event("child_stop", agent="child", classification="ready_to_complete")
        self.assertEqual(ready["obligations"][0]["scope"]["paths"], ["src/app.py", "src/other.py"])
        result, stale = self.stage("prepare", ready, old_review)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(stale["error"]["code"], "REVIEW_SCOPE_MISMATCH")

    def test_linked_worktrees_keep_independent_state_and_reject_copied_bindings(self) -> None:
        ready = self.ready()
        subprocess.run(["git", "add", "--", ".gitignore", ".agents/context/config.json", ".agents/context/fixture.json", "guidance", "src"], cwd=self.repo, check=True)
        subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "fixture"], cwd=self.repo, check=True)
        other = self.repo / "other-worktree"
        subprocess.run(["git", "worktree", "add", "-q", "--detach", str(other)], cwd=self.repo, check=True)
        support = other / ".agents/context/fixture.json"
        value = json.loads(support.read_text())
        value["worktree_root"] = str(other)
        support.write_text(json.dumps(value))
        result, started = self.event("startup", repo=other)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(started["identities"]["repository_id"], ready["identities"]["repository_id"])
        self.assertNotEqual(started["identities"]["worktree_id"], ready["identities"]["worktree_id"])
        _, other_ready = self.event("checkpoint", repo=other, classification="ready_to_complete")
        self.assertIn("invocation_file", other_ready)
        original_database = self.repo / ".agents/context/state/brain.sqlite3"
        other_database = other / ".agents/context/state/brain.sqlite3"
        other_before = other_database.read_bytes()
        other_database.write_bytes(original_database.read_bytes())
        result, rejected = self.event("recover", repo=other)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(rejected["error"]["code"], "STATE_UNAVAILABLE")
        other_database.write_bytes(other_before)
        result, _ = self.stage("start", ready)
        self.assertEqual(result.returncode, 0)

    def test_invalid_binding_disabled_provider_and_stale_config_do_not_create_state(self) -> None:
        binding = {"repository_root": str(self.repo), "worktree_root": str(self.repo / "src"),
                   "provider_session_id": "conversation", "provider_task_id": "objective", "provider_agent_id": "parent"}
        result, failed = self.event("startup", binding=binding)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(failed["error"]["code"], "BINDING_INVALID")
        self.assertFalse((self.repo / ".agents/context/state").exists())
        self.config["providers"]["fixture"]["enabled"] = False
        self.save_config()
        result, failed = self.event("startup")
        self.assertEqual(failed["error"]["code"], "INTEGRATION_DISABLED")
        self.assertFalse((self.repo / ".agents/context/state").exists())
        self.config["providers"]["fixture"]["enabled"] = True
        self.save_config()
        integration = {"id": "fixture", "core_version": VERSION, "adapter_version": "fixture-1", "certification_id": self.cert, "config_revision": "0" * 64}
        _, failed = self.event("startup", integration=integration)
        self.assertEqual(failed["error"]["code"], "CONFIGURATION_STALE")
        self.assertFalse((self.repo / ".agents/context/state").exists())
        self.config["providers"]["fixture"]["kind"] = "native"
        self.save_config()
        _, failed = self.event("startup")
        self.assertEqual(failed["error"]["code"], "NATIVE_SUPPORT_UNAVAILABLE")
        self.assertFalse((self.repo / ".agents/context/state").exists())

    def test_actual_check_timeout_runs_only_in_foreground_and_cannot_claim_pass(self) -> None:
        self.config["checks"]["trusted"] = [{"id": "long", "argv": [sys.executable, "-c", "import time; time.sleep(2)"], "timeout_seconds": 0.1}]
        self.config["checks"]["required"].append("long")
        self.save_config()
        ready = self.ready()
        self.assertEqual(ready["obligations"][0]["check_receipts"], [])
        before = time.monotonic()
        result, checked = self.stage("prepare", ready, self.review(ready))
        self.assertLess(time.monotonic() - before, 1.5)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(checked["check_receipts"][-1]["timed_out"])

    def test_provider_cap_is_tighter_than_shared_attempt_cap(self) -> None:
        self.config["providers"]["fixture"]["max_attempts"] = 1
        self.config["checks"]["required"].append("fail")
        self.config["checks"]["trusted"] = [{"id": "fail", "argv": [sys.executable, "-c", "raise SystemExit(1)"], "timeout_seconds": 1}]
        self.save_config()
        ready = self.ready()
        self.stage("prepare", ready, self.review(ready))
        result, failed = self.stage("prepare", ready, self.review(ready))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(failed["error"]["code"], "ATTEMPTS_EXHAUSTED")
        _, duplicate = self.event("recover")
        self.assertEqual(duplicate["obligations"][0]["attempt_count"], 1)

    def test_sqlite_contention_is_bounded_and_pending_work_survives(self) -> None:
        ready = self.ready()
        database = self.repo / ".agents/context/state/brain.sqlite3"
        # An external writer holds the SQLite lock, without querying private
        # tables. Only public bridge result and status establish behavior.
        connection = sqlite3.connect(database, isolation_level=None)
        try:
            connection.execute("BEGIN EXCLUSIVE")
            before = time.monotonic()
            result, failed = self.event("recover")
            self.assertLess(time.monotonic() - before, 2.5)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(failed["error"]["code"], "STATE_CONTENDED")
            self.assertTrue(failed["error"]["retry_eligible"])
        finally:
            connection.rollback()
            connection.close()
        _, status = self.cli("status")
        self.assertEqual(status["work_sessions"][0]["obligations"][0]["id"], ready["obligations"][0]["id"])

    def test_nonfinite_duplicate_and_malformed_events_are_rejected_without_state(self) -> None:
        for raw in ('{"schema_version":NaN}', '{"schema_version":Infinity}', '{"timestamp":1e400}', '{"schema_version":1,"schema_version":1}', '[]', '{broken', "[" * 2000 + "0" + "]" * 2000):
            result = subprocess.run([sys.executable, str(BRIDGE), "--json"], cwd=self.repo, input=raw,
                                    text=True, capture_output=True, timeout=3)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(json.loads(result.stdout)["error"]["code"], "INPUT_INVALID")
            self.assertFalse((self.repo / ".agents/context/state").exists())

    def test_structurally_corrupt_expected_state_remains_machine_readable(self) -> None:
        self.ready()
        database = self.repo / ".agents/context/state/brain.sqlite3"
        before = database.read_bytes()
        binding = json.loads((database.parent / "binding.json").read_text())
        for sessions in ({"broken": {"id": None}}, {"0" * 64: {"id": "invalid"}}):
            seeded = binding | {"revision": 0, "ownership_generation": 0, "owner": None,
                                "sessions": sessions, "invocations": {}}
            connection = sqlite3.connect(database)
            try:
                connection.execute("UPDATE runtime SET record=? WHERE id=1", (json.dumps(seeded),))
                connection.commit()
            finally:
                connection.close()
            for command in ("status", "doctor"):
                result, status = self.cli(command)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(status["state_status"], "unavailable")
                self.assertEqual(status["work_session_status"], "incomplete")
                self.assertNotIn("Traceback", result.stderr)
            result, failed = self.event("recover")
            self.assertEqual(result.returncode, 1)
            self.assertEqual(failed["error"]["code"], "STATE_UNAVAILABLE")
            database.write_bytes(before)

    def test_failed_complete_output_revokes_completion_and_authority(self) -> None:
        ready = self.ready()
        review = self.review(ready)
        self.stage("prepare", ready, review)
        with subprocess.Popen([sys.executable, str(CLI), "learn", "complete", "--invocation-file", ready["invocation_file"], "--input", "-", "--json"],
                              cwd=self.repo, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            process.stdout.close()
            process.stdin.write(json.dumps(review))
            process.stdin.close()
            diagnostic = process.stderr.read()
            code = process.wait(timeout=5)
        self.assertEqual(code, 1, diagnostic)
        _, status = self.cli("status")
        self.assertEqual(status["work_sessions"][0]["work_session_status"], "incomplete")
        self.assertEqual(status["work_sessions"][0]["obligations"][0]["stage_outcome"], "incomplete")
        result, old = self.stage("complete", ready, review)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(old["error"]["code"], "INVOCATION_REVOKED")

    def test_expired_owner_recovery_is_generation_bound_and_old_owner_cannot_finish(self) -> None:
        self.config["limits"] = {"lease_seconds": 0.2}
        self.save_config()
        ready = self.ready()
        self.event("startup", agent="second")
        time.sleep(0.25)
        _, recovered = self.event("recover", agent="second")
        self.assertIn("invocation_file", recovered)
        self.assertGreater(recovered["ownership_generation"], ready["ownership_generation"])
        result, failed = self.stage("complete", ready, self.review(ready))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(failed["error"]["code"], "INVOCATION_REVOKED")

    def test_contention_budget_carries_through_output_settlement(self) -> None:
        self.config["limits"] = {"contention_seconds": 0.4}
        self.save_config()
        self.event("startup")
        (self.repo / "guidance/policy.md").write_text("# Policy\n" + "A current controlling policy.\n" * 6000)
        event = json.loads((CLI.parents[1] / "examples/integration-event-v1.json").read_text())
        event["integration"].update(core_version=VERSION, certification_id=self.cert, config_revision=sha(self.config_path))
        event["binding"].update(repository_root=str(self.repo), worktree_root=str(self.repo))
        database = self.repo / ".agents/context/state/brain.sqlite3"
        first_lock = sqlite3.connect(database, isolation_level=None, check_same_thread=False)
        first_lock.execute("BEGIN EXCLUSIVE")
        def release_first() -> None:
            time.sleep(0.3)
            first_lock.rollback()
        release = threading.Thread(target=release_first)
        release.start()
        second_lock = sqlite3.connect(database, isolation_level=None)
        try:
            with subprocess.Popen([sys.executable, str(BRIDGE), "--json"], cwd=self.repo,
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                process.stdin.write(json.dumps(event).encode())
                process.stdin.close()
                prefix = process.stdout.read(4096)
                self.assertTrue(prefix)
                # Large public output keeps the bridge between its state
                # transaction and output settlement while this second lock is
                # acquired. No private tables are queried.
                second_lock.execute("BEGIN EXCLUSIVE")
                before = time.monotonic()
                rest = process.stdout.read()
                diagnostic = process.stderr.read()
                code = process.wait(timeout=5)
                elapsed = time.monotonic() - before
            self.assertEqual(code, 1, diagnostic)
            self.assertLess(elapsed, 0.3, f"output phase reset its spent contention budget: {elapsed}")
            self.assertEqual(json.loads(prefix + rest)["stage_outcome"], "incomplete")
        finally:
            second_lock.rollback()
            second_lock.close()
            release.join(timeout=2)
            first_lock.close()
        _, status = self.cli("status")
        self.assertFalse(status["work_sessions"][0]["agents"][0]["delivery_complete"])

    def test_child_settlement_is_invalidated_when_relevant_inputs_change(self) -> None:
        self.event("startup")
        self.event("child_start", agent="child", parent_agent_id="parent")
        _, child = self.event("child_stop", agent="child", classification="ready_to_complete")
        self.stage("prepare", child, self.review(child))
        self.stage("complete", child, self.review(child))
        (self.repo / "src/app.py").write_text("print('after child review')\n")
        _, parent = self.event("checkpoint", classification="ready_to_complete")
        self.assertNotIn("invocation_file", parent)
        _, status = self.cli("status")
        assigned = next(agent for agent in status["work_sessions"][0]["agents"] if agent["parent_agent_id"])
        self.assertNotEqual(assigned["status"], "completed")

    def test_registered_child_without_assignments_needs_delivery_but_no_full_learn(self) -> None:
        self.event("startup")
        self.event("child_start", agent="child", parent_agent_id="parent", assigned_obligations=[])
        _, stopped = self.event("child_stop", agent="child", classification="ready_to_complete")
        self.assertEqual(stopped["obligations"], [])
        self.assertNotIn("invocation_file", stopped)
        _, parent = self.event("checkpoint", classification="ready_to_complete")
        self.assertEqual([obligation["kind"] for obligation in parent["obligations"]], ["learn"])
        self.assertIn("invocation_file", parent)

    def test_late_child_registration_invalidates_previously_completed_parent(self) -> None:
        ready = self.ready()
        self.stage("prepare", ready, self.review(ready))
        self.stage("complete", ready, self.review(ready))
        _, child = self.event("child_start", agent="child", parent_agent_id="parent")
        self.assertEqual(child["work_session_status"], "incomplete")
        _, parent = self.event("checkpoint", classification="ready_to_complete")
        self.assertNotIn("invocation_file", parent)

    def test_child_delivery_and_work_package_use_its_assigned_scope(self) -> None:
        parent_unit = str(uuid.uuid4())
        (self.repo / "guidance/parent.md").write_text("# Parent detail\nThis context applies only to the parent's file.\n")
        (self.repo / "src/parent.py").write_text("print('parent')\n")
        self.config["mapped_units"].append({"id": parent_unit, "path": "guidance/parent.md", "selector": {"type": "document"},
            "kind": "fact", "status": "established", "applies": {"paths": ["src/parent.py"]}})
        self.save_config()
        self.event("startup", scope={"paths": ["src/parent.py"]})
        _, child = self.event("child_start", agent="child", parent_agent_id="parent")
        self.assertNotIn(parent_unit, [unit["id"] for unit in child["delivery"]["units"]])
        _, ready = self.event("child_stop", agent="child", classification="ready_to_complete")
        _, package = self.stage("start", ready)
        self.assertNotIn(parent_unit, [unit["id"] for unit in package["work_package"]["guidance"]["units"]])

    def test_interrupted_check_retains_pending_and_retries_without_cancelling_objective(self) -> None:
        program = "from pathlib import Path; import time; Path('check-started').write_text('started'); time.sleep(4) if not Path('check-allow').exists() else None"
        self.config["checks"]["required"].append("interruptible")
        self.config["checks"]["trusted"] = [{"id": "interruptible", "argv": [sys.executable, "-c", program], "timeout_seconds": 5}]
        self.save_config()
        ready = self.ready()
        with subprocess.Popen([sys.executable, str(CLI), "learn", "prepare", "--invocation-file", ready["invocation_file"], "--input", "-", "--json"],
                              cwd=self.repo, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            process.stdin.write(json.dumps(self.review(ready)))
            process.stdin.close()
            process.stdin = None
            deadline = time.monotonic() + 3
            while not (self.repo / "check-started").exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue((self.repo / "check-started").exists())
            before = time.monotonic()
            process.send_signal(signal.SIGINT)
            stdout, stderr = process.communicate(timeout=3)
            self.assertLess(time.monotonic() - before, 2.5)
        self.assertEqual(process.returncode, 130, stderr)
        self.assertEqual(json.loads(stdout)["stage_outcome"], "incomplete")
        _, status = self.cli("status")
        self.assertEqual(status["work_sessions"][0]["work_session_status"], "incomplete")
        (self.repo / "check-allow").write_text("allow")
        _, recovered = self.event("recover")
        result, prepared = self.stage("prepare", recovered, self.review(recovered))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(prepared["obligations"][0]["attempt_count"], 2)

    def test_examples_and_public_results_align_with_versioned_schemas(self) -> None:
        self.event("startup")
        bundle = CLI.parents[1]
        event = json.loads((bundle / "examples/integration-event-v1.json").read_text())
        event["integration"].update(core_version=VERSION, certification_id=self.cert, config_revision=sha(self.config_path))
        event["binding"].update(repository_root=str(self.repo), worktree_root=str(self.repo))
        result, ready = self.process(BRIDGE, "--json", payload=event)
        self.assertEqual(result.returncode, 0, result.stderr)
        review = json.loads((bundle / "examples/review-v1.json").read_text())
        review["review"]["scope"] = ready["obligations"][0]["scope"]
        review["review"]["guidance"] = self.review(ready)["review"]["guidance"]
        review["review"]["sources"][0]["revision"] = sha(self.repo / "guidance/policy.md")
        result, prepared = self.stage("prepare", ready, review)
        self.assertEqual(result.returncode, 0, result.stderr)
        result, completed = self.stage("complete", ready, review)
        self.assertEqual(result.returncode, 0, result.stderr)
        schema = json.loads((bundle / "schemas/lifecycle-result-v1.schema.json").read_text())
        for public in (ready, prepared, completed):
            self.assertFalse(set(public) - schema["properties"].keys())
            self.assertTrue(set(schema["required"]).issubset(public))
            self.assertIn(public["operation_status"], schema["properties"]["operation_status"]["enum"])
            self.assertIn(public["stage_outcome"], schema["properties"]["stage_outcome"]["enum"])
        _, status = self.cli("status")
        inspection_schema = json.loads((bundle / "schemas/inspection-v1.schema.json").read_text())
        self.assertFalse(set(status) - inspection_schema["properties"].keys())
        self.assertTrue(set(inspection_schema["required"]).issubset(status))

    def test_changed_inputs_enable_fresh_generation_after_repair_exhaustion(self) -> None:
        ready = self.ready()
        bad = self.review(ready)
        bad["review"]["scope"]["paths"] = ["src/unreviewed.py"]
        self.stage("prepare", ready, bad)
        self.stage("prepare", ready, bad)
        _, unchanged = self.event("recover")
        self.assertNotIn("invocation_file", unchanged)
        (self.repo / "src/app.py").write_text("print('new generation')\n")
        _, renewed = self.event("recover")
        self.assertIn("invocation_file", renewed)
        self.assertEqual(renewed["obligations"][0]["attempt_count"], 1)
        self.assertEqual(renewed["obligations"][0]["semantic_repairs"], 0)
        result, _ = self.stage("prepare", renewed, self.review(renewed))
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
