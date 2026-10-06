#!/usr/bin/env python3
"""Public offline source/legacy joins. No native host or semantic model runs."""
from __future__ import annotations

import importlib.util
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("lifecycle_fixture", ROOT / "scripts/test-agent-brain-lifecycle.py")
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
sha = fixture.sha
publication_spec = importlib.util.spec_from_file_location("publication_fixture", ROOT / "scripts/test-agent-brain-publication.py")
publication_fixture = importlib.util.module_from_spec(publication_spec)
publication_spec.loader.exec_module(publication_fixture)


class CompatibilityTests(unittest.TestCase):
    setUp = fixture.LifecycleTests.setUp
    save_config = fixture.LifecycleTests.save_config
    process = fixture.LifecycleTests.process
    event = fixture.LifecycleTests.event
    cli = fixture.LifecycleTests.cli
    ready = fixture.LifecycleTests.ready
    review = fixture.LifecycleTests.review
    stage = fixture.LifecycleTests.stage
    interrupted = publication_fixture.PublicationTests.interrupted

    def review(self, ready):
        learn = next(item for item in ready["obligations"] if item["kind"] == "learn")
        return fixture.LifecycleTests.review(self, dict(ready, obligations=[learn]))

    def sources(self):
        shutil.copytree(ROOT / "skills/agent-brain", self.repo / "tools/agent-brain")
        self.engine = self.repo / "tools/auto-ingest-engine.py"
        shutil.copyfile(ROOT / "hooks/families/auto_ingest_engine.py", self.engine)
        bridge = self.repo / "tools/agent-brain/scripts/integration-bridge.py"
        self.config["source_ingestion"] = {"enabled": True,
            "engine_path": "tools/auto-ingest-engine.py", "engine_revision": sha(self.engine),
            "bridge_path": "tools/agent-brain/scripts/integration-bridge.py", "bridge_revision": sha(bridge)}
        self.config["knowledge_roots"].append({"path": ".agents/memory/sources", "ownership": "agent_brain"})
        self.color_id = str(uuid.uuid5(uuid.UUID(self.repository_id), "colors-fact"))
        self.save_config()
        self.raw = self.repo / ".agents/sources"
        self.raw.mkdir(parents=True)
        self.summaries = self.repo / ".agents/memory/sources"
        self.summaries.mkdir(parents=True)
        self.manifest = self.summaries / "source-ingest-manifest.json"
        self.manifest.write_text('{"version":1,"entries":[]}')
        skill = self.repo / ".agents/skills/ingest-source/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("# Focused ingestion\nProcess every blocking entry once, then refresh knowledge.\n")
        (self.raw / "colors.md").write_text("The approved accent color is cobalt.\n")

    def annotation(self, identity, name):
        fields = {"schema_version": 1, "id": identity,
            "kind": "fact", "status": "established", "applies": {"paths": ["src/app.py"]},
            "evidence": {"sources": [{"source": ".agents/sources/" + name, "revision": sha(self.raw / name)}],
                "verification_note": "Read the accent fact from the complete controlling source.",
                "verified_at": "2026-10-06"}}
        if hasattr(self, "required_id") and identity == self.color_id:
            fields["requires"] = [{"id": self.required_id, "loading_mode": "whole"}]
        return '<!-- agent-brain ' + json.dumps(fields) + ' -->\n'

    def proposal(self, ready, name="colors.md", fact="The approved accent color is cobalt.", orphans=()):
        summary = self.summaries / (name.replace(".", "-") + ".summary.md")
        summary_id = str(uuid.uuid5(uuid.UUID(self.repository_id), "summary:" + name))
        after_summary = self.summary_text(name, fact)
        after_fact = "# Colors\n" + self.annotation(self.color_id, name) + fact + "\n"
        payload = self.evidence(ready, (), orphans)
        payload["outcome"] = "changed"
        source = {"path": ".agents/sources/" + name, "revision": sha(self.raw / name), "note": "Read the complete accent-color source."}
        payload["review"]["sources"].append(source)
        payload["source_ingestion"]["entries"] = [{"source_path": name, "source_revision": sha(self.raw / name),
            "summary_revision": hashlib.sha256(after_summary.encode()).hexdigest(), "knowledge_ids": [self.color_id],
            "note": "Integrated the controlling accent fact into qualified summary and Colors guidance."}]
        changes = []
        claims = []
        for path, content, identity in ((summary, after_summary, summary_id), (self.repo / "guidance/colors.md", after_fact, self.color_id)):
            before = path.read_text() if path.exists() else None
            changes.append({"path": path.relative_to(self.repo).as_posix(), "base_revision": sha(path) if before is not None else None, "content": content})
            action = "correct" if before and "<!-- agent-brain " in before else "add"
            evidence = {"verified_at": "2026-10-06", "result": "verified", "source": source}
            if action == "correct":
                evidence.update(basis="error", basis_note="The changed controlling source supplies the replacement accent fact.")
            claims.append({"id": identity, "type": "fact", "action": action, "scope": {"paths": ["src/app.py"]}, "evidence": evidence})
        payload["proposal"] = {"base_input_revision": ready["input_revision"], "rationale": "Retain verified source facts with exact provenance.", "changes": changes, "claims": claims}
        return payload

    def ingest(self, name="colors.md", fact="The approved accent color is cobalt.", orphans=()):
        code, ready = self.event("recover")
        self.assertEqual(code.returncode, 0, (ready, code.stderr))
        payload = self.proposal(ready, name, fact, orphans)
        for operation in ("prepare", "publish", "complete"):
            code, result = self.stage(operation, ready, payload if operation == "prepare" else None)
            self.assertEqual(code.returncode, 0, (operation, result, code.stderr))
        return result

    def summary_text(self, name, fact):
        return ('---\ntype: Source Summary\ndescription: Verified accent-color source facts.\n'
            'sources:\n  - resource: "../../sources/' + name + '"\nstatus: current\n---\n# Colors\n' +
            self.annotation(str(uuid.uuid5(uuid.UUID(self.repository_id), "summary:" + name)), name) + fact + '\n')

    def evidence(self, ready, names=("colors.md",), orphans=()):
        review = self.review(ready)
        review["source_ingestion"] = {"entries": [], "orphans": []}
        for name in names:
            summary = self.summaries / (name.replace(".", "-") + ".summary.md")
            review["source_ingestion"]["entries"].append({"source_path": name,
                "source_revision": sha(self.raw / name), "summary_revision": sha(summary),
                "knowledge_ids": [self.color_id], "note": "Read the complete source and integrated its accent fact into Colors guidance."})
        for name in orphans:
            summary = self.summaries / (name.replace(".", "-") + ".summary.md")
            review["source_ingestion"]["orphans"].append({"source_path": name,
                "summary_revision": sha(summary), "disposition": "retained",
                "note": "Reviewed the orphan and retained its qualified provenance after source removal."})
        return review

    def test_pending_sources_are_foreground_work_and_scanner_alone_cannot_complete(self):
        self.sources()
        ready = self.ready()
        code, package = self.stage("start", ready)
        self.assertEqual(code.returncode, 0, code.stderr)
        self.assertEqual(package["work_package"]["source_ingestion"]["blocking"][0]["source_path"], "colors.md")
        code, failed = self.stage("prepare", ready, self.review(ready))
        self.assertEqual(code.returncode, 1)
        self.assertEqual(failed["error"]["code"], "SOURCE_INGESTION_PENDING")
        self.assertEqual((self.raw / "colors.md").read_text(), "The approved accent color is cobalt.\n")

    def test_artifacts_current_evidence_and_three_gates_join_one_pass(self):
        self.sources()
        ready = self.ready()
        first_id = ready["obligations"][0]["id"]
        for gate in ("github", "gemini"):
            self.assertIn("joined", json.dumps(self.gate(gate)))
        _, status = self.cli("status")
        self.assertEqual(len(status["work_sessions"][0]["obligations"]), 1)
        self.assertEqual(status["work_sessions"][0]["obligations"][0]["id"], first_id)
        result = self.ingest()
        self.assertEqual(result["obligations"][0]["id"], first_id)
        self.assertEqual(result["work_session_status"], "completed")
        self.assertEqual((self.repo / "guidance/colors.md").read_text(), "# Colors\n" + self.annotation(self.color_id, "colors.md") + "The approved accent color is cobalt.\n")
        self.assertEqual((self.summaries / "colors-md.summary.md").read_text(), self.summary_text("colors.md", "The approved accent color is cobalt."))
        self.assertEqual(self.gate("github")["decision"], "allow")
        self.assertNotIn("deny", json.dumps(self.gate("gemini")))
        journal = json.loads((self.repo / result["publication"]["history_path"]).read_text())
        self.assertEqual({item["path"] for item in journal["changes"]}, {"guidance/colors.md", ".agents/memory/sources/colors-md.summary.md"})
        self.assertIsNone(next(item for item in journal["changes"] if item["path"] == "guidance/colors.md")["before"])
        self.assertIn("status: draft", next(item for item in journal["changes"] if item["path"].endswith(".summary.md"))["before"])

    def gate(self, name, **event_fields):
        self.sequence += 1
        event = {"schema_version": 1, "event_id": f"legacy-{self.sequence}", "event": "checkpoint",
            "classification": "ready_to_complete",
            "integration": {"id": "fixture", "core_version": fixture.VERSION, "adapter_version": "fixture-1",
                "certification_id": self.cert, "config_revision": sha(self.config_path)},
            "binding": {"repository_root": str(self.repo), "worktree_root": str(self.repo),
                "provider_session_id": "conversation", "provider_task_id": "objective", "provider_agent_id": "parent"},
            "scope": {"paths": ["src/app.py"]}}
        event.update(event_fields)
        if name == "github":
            helpers = self.repo / ".github/hooks/scripts/helpers"
            if not helpers.exists():
                shutil.copytree(ROOT / ".github/hooks/scripts/helpers", helpers)
            script = ROOT / ".github/hooks/scripts/inject-auto-ingest-context.py"
            event_name = "agentStop"
        else:
            script = ROOT / ".gemini/hooks/scripts/inject-auto-ingest-context.py"
            event_name = "AfterAgent"
        home = self.repo / ".agents/context/state/hook-home"
        home.mkdir(parents=True, exist_ok=True)
        result = subprocess.run([sys.executable, str(script)], cwd=self.repo,
            input=json.dumps({"cwd": str(self.repo), "hook_event_name": event_name, "agent_brain_event": event}),
            text=True, capture_output=True, timeout=8,
            env=os.environ | {"HOME": str(home), "AUDIT_LOG": str(home / "audit.log")})
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_changed_renamed_removed_sources_keep_orphans_separate(self):
        self.sources()
        self.ready()
        self.ingest()
        (self.raw / "colors.md").write_text("The approved accent color is amber.\n")
        _, changed = self.event("recover")
        _, package = self.stage("start", changed)
        self.assertEqual(package["work_package"]["source_ingestion"]["blocking"][0]["state"], "stale")
        self.ingest(fact="The approved accent color is amber.")
        (self.raw / "colors.md").rename(self.raw / "palette.md")
        _, renamed = self.event("recover")
        _, package = self.stage("start", renamed)
        self.assertEqual([entry["source_path"] for entry in package["work_package"]["source_ingestion"]["blocking"]], ["palette.md"])
        self.assertEqual(package["work_package"]["source_ingestion"]["orphans"][0]["source_path"], "colors.md")
        self.ingest("palette.md", "The approved accent color is amber.", ("colors.md",))
        (self.raw / "palette.md").unlink()
        _, removed = self.event("recover")
        _, removed = self.event("checkpoint", classification="ready_to_complete")
        payload = self.evidence(removed, (), ("colors.md", "palette.md"))
        for op in ("prepare", "complete"):
            code, result = self.stage(op, removed, payload)
            self.assertEqual(code.returncode, 0, (code.stderr, result))
        self.assertEqual(result["work_session_status"], "completed")

    def test_manifest_assertion_alone_does_not_settle_semantic_integration(self):
        self.sources()
        self.ready()
        summary = self.summaries / "colors-md.summary.md"
        summary.write_text(self.summary_text("colors.md", "The approved accent color is cobalt."))
        (self.repo / "guidance/colors.md").write_text("# Colors\nThe approved accent color is cobalt.\n")
        _, current = self.event("recover")
        self.assertEqual(current["error"]["code"], "SOURCE_UNJOURNALED_CHANGE")
        self.assertFalse(list((self.config_path.parent / "history").glob("*.json")))
        self.assertEqual(summary.read_text(), self.summary_text("colors.md", "The approved accent color is cobalt."))

    def test_new_task_cannot_launder_unjournaled_prior_source_work(self):
        self.sources()
        self.event("startup")
        summary = self.summaries / "colors-md.summary.md"
        summary.write_text(self.summary_text("colors.md", "The approved accent color is cobalt."))
        fact = "# Colors\n" + self.annotation(self.color_id, "colors.md") + "The approved accent color is cobalt.\n"
        (self.repo / "guidance/colors.md").write_text(fact)
        self.assertEqual(self.event("recover")[1]["error"]["code"], "SOURCE_UNJOURNALED_CHANGE")
        result, different = self.event("startup", task="different")
        self.assertEqual(result.returncode, 1, different)
        self.assertEqual(different["error"]["code"], "SOURCE_UNJOURNALED_CHANGE")
        self.assertEqual(summary.read_text(), self.summary_text("colors.md", "The approved accent color is cobalt."))
        self.assertEqual((self.repo / "guidance/colors.md").read_text(), fact)
        self.assertFalse(list((self.config_path.parent / "history").glob("*.json")))
        (self.repo / "src/other.py").write_text("print('independent')\n")
        result, unrelated = self.event("startup", task="unrelated", scope={"paths": ["src/other.py"]})
        self.assertEqual(result.returncode, 0, (unrelated, result.stderr))
        self.assertNotIn(self.color_id, [unit["id"] for unit in unrelated["delivery"]["units"]])

    def test_new_task_retains_clean_prior_source_work_and_canceled_work_is_not_restarted(self):
        self.sources()
        initial = self.event("startup")[1]
        result, blocked = self.event("startup", task="different")
        self.assertEqual(result.returncode, 1, blocked)
        self.assertEqual(blocked["error"]["code"], "SOURCE_PRIOR_WORK_PENDING")
        self.event("cancel")
        result, replacement = self.event("startup", task="replacement")
        self.assertEqual(result.returncode, 0, (replacement, result.stderr))
        self.assertFalse(replacement["action_ready"])
        self.assertEqual(replacement["next_action"]["kind"], "learn")
        _, status = self.cli("status")
        old = next(item for item in status["work_sessions"] if item["work_session_id"] == initial["identities"]["work_session_id"])
        self.assertEqual(old["work_session_status"], "cancelled")
        result, current = self.event("recover", task="replacement")
        self.assertEqual(result.returncode, 0, (current, result.stderr))
        payload = self.proposal(current)
        for operation in ("prepare", "publish", "complete"):
            result, completed = self.stage(operation, current, payload if operation == "prepare" else None)
            self.assertEqual(result.returncode, 0, (completed, result.stderr))
        result, later = self.event("startup", task="later")
        self.assertEqual(result.returncode, 0, (later, result.stderr))
        self.assertNotIn("source_work", later)

    def test_missing_ingest_access_and_expected_manifest_remain_incomplete(self):
        for damage in ("skill", "missing_manifest", "damaged_manifest"):
            with self.subTest(damage=damage):
                self.setUp()
                self.sources()
                ready = self.ready()
                if damage == "skill":
                    (self.repo / ".agents/skills/ingest-source/SKILL.md").unlink()
                    _, ready = self.event("recover")
                    code, failed = self.stage("prepare", ready, self.review(ready))
                    self.assertEqual(failed["error"]["code"], "SOURCE_INGESTION_UNAVAILABLE")
                else:
                    if damage == "missing_manifest":
                        self.manifest.unlink()
                    else:
                        self.manifest.write_text("{broken")
                    code, failed = self.event("recover")
                    self.assertEqual(failed["error"]["code"], "SOURCE_INGESTION_UNAVAILABLE")
                self.assertNotEqual(code.returncode, 0)
                _, status = self.cli("status")
                if damage == "skill":
                    self.assertNotEqual(status["work_sessions"][0]["work_session_status"], "completed")
                else:
                    self.assertEqual(status["state_status"], "unavailable")
                    self.assertEqual(status["work_session_status"], "incomplete")
                    self.assertEqual(status["pending_work"], "unknown")

    def test_no_source_repository_and_inactive_legacy_keep_existing_flow(self):
        ready = self.ready()
        for op in ("prepare", "complete"):
            code, completed = self.stage(op, ready, self.review(ready))
            self.assertEqual(code.returncode, 0, code.stderr)
        self.assertEqual(completed["work_session_status"], "completed")
        for path, stage in (("update-agent-docs", "learn"), ("clean-agent-docs", "dream")):
            text = (ROOT / f".agents/skills/{path}/SKILL.md").read_text()
            self.assertIn("## Agent-brain compatibility", text)
            self.assertIn(stage, text)
            self.assertIn("unactivated", text)
            self.assertIn("## Workflow", text)

    def test_enabled_empty_source_repository_needs_no_focused_skill(self):
        self.sources()
        (self.raw / "colors.md").unlink()
        (self.repo / ".agents/skills/ingest-source/SKILL.md").unlink()
        ready = self.ready()
        self.assertNotIn("source_work", ready)
        for operation in ("prepare", "complete"):
            result, completed = self.stage(operation, ready, self.review(ready))
            self.assertEqual(result.returncode, 0, (completed, result.stderr))
        self.assertEqual(completed["work_session_status"], "completed")

    def test_external_policy_revision_restores_context_without_becoming_source_write(self):
        self.sources()
        self.config["knowledge_roots"][0]["ownership"] = "read_only"
        self.save_config()
        initial = self.event("startup")[1]
        (self.repo / "guidance/policy.md").write_text("# Policy\nRead current guidance and preserve user-approved exceptions.\n")
        result, current = self.event("recover")
        self.assertEqual(result.returncode, 0, (current, result.stderr))
        self.assertFalse(current["action_ready"])
        self.assertEqual(current["obligations"][0]["id"], initial["obligations"][0]["id"])
        self.assertIn("preserve user-approved exceptions", current["delivery"]["artifacts"][0]["content"])

    def test_publication_cannot_mutate_raw_sources_even_with_broad_owned_root(self):
        self.sources()
        self.config["knowledge_roots"] = [{"path": "guidance", "ownership": "agent_brain"}, {"path": ".agents", "ownership": "agent_brain"}]
        self.save_config()
        current = self.ready()
        payload = self.proposal(current)
        raw = self.raw / "colors.md"
        before = raw.read_bytes()
        payload["proposal"]["changes"].append({"path": ".agents/sources/colors.md", "base_revision": sha(raw), "content": "Altered immutable input.\n"})
        result, failed = self.stage("prepare", current, payload)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(failed["error"]["code"], "RAW_SOURCE_IMMUTABLE")
        self.assertEqual(raw.read_bytes(), before)
        self.assertFalse(list((self.config_path.parent / "history").glob("*.json")))

    def test_interrupted_join_remains_one_pending_obligation(self):
        self.sources()
        ready = self.ready()
        self.gate("github", stage_generated=ready["attempt_id"])
        _, status = self.cli("status")
        self.assertEqual(len(status["work_sessions"][0]["obligations"]), 1)
        self.assertNotEqual(status["work_sessions"][0]["work_session_status"], "completed")
        self.assertEqual(status["work_sessions"][0]["obligations"][0]["attempt_count"], 1)

    def test_early_source_learning_blocks_action_without_finishing_objective(self):
        self.sources()
        self.required_id = str(uuid.uuid5(uuid.UUID(self.repository_id), "required-qualification"))
        qualification = "# Required qualification\n<!-- agent-brain " + json.dumps({"schema_version": 1,
            "id": self.required_id, "kind": "fact", "status": "established", "applies": {"paths": ["other.py"]}}) + " -->\nUse the approved color only on readable backgrounds.\n"
        (self.repo / "guidance/qualification.md").write_text(qualification)
        code, startup = self.event("startup")
        self.assertEqual(code.returncode, 0, code.stderr)
        self.assertEqual(startup["checkpoint"], "active")
        self.assertFalse(startup["action_ready"])
        self.assertEqual(startup["next_action"]["kind"], "learn")
        self.assertNotIn(self.required_id, [unit["id"] for unit in startup["delivery"]["units"]])
        completed = self.ingest()
        self.assertEqual(completed["work_session_status"], "active")
        self.assertTrue(completed["action_ready"])
        self.assertTrue(completed["delivery"]["complete"])
        self.assertIn(self.required_id, [unit["id"] for unit in completed["delivery"]["units"]])
        self.assertIn(qualification, [artifact["content"] for artifact in completed["delivery"]["artifacts"]])
        _, delivered = self.event("task")
        self.assertTrue(delivered["action_ready"])
        _, final = self.event("checkpoint", classification="ready_to_complete")
        self.assertIn("invocation_file", final)
        self.assertEqual(final["obligations"][0]["id"], startup["obligations"][0]["id"])
        self.assertEqual(final["work_session_status"], "ready_to_complete")

    def test_linked_summary_parent_is_rejected_before_any_scanner_effect(self):
        self.sources()
        protected = self.repo / "protected-memory"
        (self.repo / ".agents/memory").rename(protected)
        (self.repo / ".agents/memory").symlink_to(protected, target_is_directory=True)
        before = (protected / "sources/source-ingest-manifest.json").read_bytes()
        result, failed = self.process(self.engine, "--repository-root", str(self.repo), "--reconcile", "--json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("error", failed)
        self.assertEqual((protected / "sources/source-ingest-manifest.json").read_bytes(), before)
        self.assertEqual(sorted(path.name for path in (protected / "sources").iterdir()), ["source-ingest-manifest.json"])
        self.assertEqual((self.raw / "colors.md").read_text(), "The approved accent color is cobalt.\n")

    def test_read_only_recall_exposes_source_gap_without_initializing_state(self):
        self.sources()
        before = self.manifest.read_bytes()
        result, recalled = self.cli("recall", "--path", "src/app.py")
        self.assertEqual(result.returncode, 1)
        self.assertFalse(recalled["complete"])
        self.assertIn("SOURCE_INGESTION_PENDING", [gap["code"] for gap in recalled["gaps"]])
        self.assertEqual(self.manifest.read_bytes(), before)
        self.assertFalse((self.repo / ".agents/context/state").exists())

    def test_new_source_during_foreground_checks_invalidates_prior_review(self):
        self.sources()
        self.ready()
        self.ingest()
        self.config["checks"]["required"].append("foreground")
        self.config["checks"]["trusted"] = [{"id": "foreground", "argv": [sys.executable, "-c",
            "from pathlib import Path; import time; Path('check-started').write_text('started'); time.sleep(0.4)"], "timeout_seconds": 2}]
        self.save_config()
        (self.raw / "colors.md").write_text("The approved accent color is cobalt.\nThis repeats the existing qualification.\n")
        _, current = self.event("recover")
        with subprocess.Popen([sys.executable, str(fixture.CLI), "learn", "prepare", "--invocation-file", current["invocation_file"], "--input", "-", "--json"],
                cwd=self.repo, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            process.stdin.write(json.dumps(self.evidence(current)))
            process.stdin.close()
            process.stdin = None
            deadline = time.monotonic() + 3
            while not (self.repo / "check-started").exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue((self.repo / "check-started").exists())
            (self.raw / "contrast.md").write_text("Body text requires strong contrast.\n")
            stdout, stderr = process.communicate(timeout=4)
        self.assertEqual(process.returncode, 1, stderr)
        self.assertEqual(json.loads(stdout)["error"]["code"], "INPUTS_STALE")
        _, renewed = self.event("recover")
        self.assertEqual(renewed["obligations"][0]["id"], current["obligations"][0]["id"])
        _, package = self.stage("start", renewed)
        self.assertEqual([entry["source_path"] for entry in package["work_package"]["source_ingestion"]["blocking"]], ["colors.md", "contrast.md"])

    def test_caller_assertion_without_integrated_source_notes_is_rejected(self):
        self.sources()
        current = self.ready()
        payload = self.proposal(current)
        content = payload["proposal"]["changes"][1]["content"]
        fields = json.loads(content.split('<!-- agent-brain ', 1)[1].split(' -->', 1)[0])
        fields.pop("evidence")
        payload["proposal"]["changes"][1]["content"] = "# Colors\n<!-- agent-brain " + json.dumps(fields) + " -->\nThe approved accent color is cobalt.\n"
        result, failed = self.stage("prepare", current, payload)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(failed["error"]["code"], "EVIDENCE_REQUIRED")
        self.assertFalse(self.gate("github")["decision"] == "allow")

    def test_modified_engine_revision_and_missing_foreground_event_cannot_join(self):
        self.sources()
        self.engine.write_text(self.engine.read_text() + "\n# Unreviewed edit\n")
        result, failed = self.event("startup")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(failed["error"]["code"], "SOURCE_INGESTION_UNAVAILABLE")
        self.assertFalse((self.repo / ".agents/context/state").exists())

    def test_windows_lock_branch_runs_at_public_engine_process(self):
        self.sources()
        program = ("import sys, types, runpy; from pathlib import Path; "
            "sys.modules['fcntl']=None; win=types.ModuleType('msvcrt'); win.LK_NBLCK=1; win.LK_UNLCK=2; "
            "win.locking=lambda fd, mode, count: Path('lock-events').write_text((Path('lock-events').read_text() if Path('lock-events').exists() else '')+str(mode)+'\\n'); "
            "sys.modules['msvcrt']=win; sys.argv=[sys.argv[1], '--repository-root', sys.argv[2], '--reconcile', '--json']; "
            "runpy.run_path(sys.argv[0],run_name='__main__')")
        # A controlled platform module stands in for native Windows. The test
        # invokes the full canonical engine entrypoint and asserts effects.
        result = subprocess.run([sys.executable, "-c", program, str(self.engine), str(self.repo)],
            cwd=self.repo, text=True, capture_output=True, timeout=3)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.repo / "lock-events").read_text(), "1\n2\n")
        self.assertEqual(json.loads(result.stdout)["blocking"][0]["source_path"], "colors.md")

    def test_malformed_expected_manifest_is_preserved_before_scaffold_or_lock(self):
        malformed = ('{"version":1,"entries":[],"entries":[]}', '{"version":true,"entries":[]}',
            '{"version":1,"entries":[],"extra":NaN}', '{"version":1,"entries":[],"extra":1e999}',
            '{"version":1,"entries":[{"source_path":"../escape"}]}',
            '{"version":1,"entries":[{"source_path":"colors.md","summary_path":42}]}',
            '{"version":1,"entries":[{"source_path":"colors.md","size":true}]}')
        for damaged in malformed:
            with self.subTest(damaged=damaged):
                self.setUp()
                self.sources()
                self.manifest.write_text(damaged)
                result, failed = self.process(self.engine, "--repository-root", str(self.repo), "--reconcile", "--json")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("error", failed)
                self.assertEqual(self.manifest.read_text(), damaged)
                self.assertFalse((self.summaries / "colors-md.summary.md").exists())
                self.assertFalse(self.manifest.with_suffix(".expected").exists())
                self.assertFalse(self.manifest.with_suffix(".json.lock").exists())

    def test_preexisting_qualified_facts_allow_checked_no_change_for_source_drift(self):
        self.sources()
        self.ready()
        self.ingest()
        summary = self.summaries / "colors-md.summary.md"
        knowledge = self.repo / "guidance/colors.md"
        before = (summary.read_bytes(), knowledge.read_bytes())
        journals = sorted(path.name for path in (self.config_path.parent / "history").glob("*.json"))
        (self.raw / "colors.md").write_text("The approved accent color is cobalt.\nThe same approved color applies.\n")
        _, current = self.event("recover")
        _, current = self.event("checkpoint", classification="ready_to_complete")
        payload = self.evidence(current)
        for operation in ("prepare", "complete"):
            result, completed = self.stage(operation, current, payload)
            self.assertEqual(result.returncode, 0, (completed, result.stderr))
        self.assertEqual(completed["stage_outcome"], "no_change")
        self.assertEqual(completed["work_session_status"], "completed")
        self.assertEqual((summary.read_bytes(), knowledge.read_bytes()), before)
        self.assertEqual(sorted(path.name for path in (self.config_path.parent / "history").glob("*.json")), journals)
        self.assertEqual(json.loads(self.manifest.read_text())["entries"][0]["state"], "active")

    def test_interrupted_source_publication_restores_exact_before_images_after_drift(self):
        self.sources()
        ready = self.ready()
        scaffold = (self.summaries / "colors-md.summary.md").read_bytes()
        payload = self.proposal(ready)
        result, prepared = self.stage("prepare", ready, payload)
        self.assertEqual(result.returncode, 0, (prepared, result.stderr))
        self.interrupted(ready, "between_replacements")
        (self.raw / "colors.md").write_text("The approved accent color is amber.\n")
        result, recovered = self.event("recover")
        self.assertEqual(result.returncode, 0, (recovered, result.stderr))
        self.assertEqual((self.summaries / "colors-md.summary.md").read_bytes(), scaffold)
        self.assertFalse((self.repo / "guidance/colors.md").exists())
        self.assertFalse(recovered["action_ready"])
        self.assertEqual(recovered["obligations"][0]["id"], ready["obligations"][0]["id"])
        journal = json.loads((self.repo / prepared["publication"]["history_path"]).read_text())
        self.assertEqual(journal["status"], "reversed")
        self.assertEqual(next(item for item in journal["changes"] if item["path"].endswith(".summary.md"))["before"].encode(), scaffold)
        self.assertEqual(self.ingest(fact="The approved accent color is amber.")["work_session_status"], "completed")

    def test_checked_source_learn_then_assigned_dream_needs_no_recursive_ingest(self):
        self.sources()
        self.config.pop("maintenance")
        self.save_config()
        self.ready()
        learned = self.ingest()
        self.assertEqual(learned["work_session_status"], "ready_to_complete")
        result, current = self.event("recover")
        self.assertEqual(result.returncode, 0, (current, result.stderr))
        self.assertEqual(current["next_action"]["kind"], "dream")
        dream = next(item for item in current["obligations"] if item["kind"] == "dream")
        payload = {"schema_version": 1, "outcome": "no_change", "review": {
            "scope": dream["scope"], "guidance": [{key: unit[key] for key in ("id", "content_revision", "input_revision")} for unit in current["delivery"]["units"]],
            "sources": [{"path": "guidance/policy.md", "revision": sha(self.repo / "guidance/policy.md"), "note": "Reviewed the controlling policy."}],
            "note": "Reviewed the complete assigned batch and kept its qualified source facts."},
            "dispositions": [{"id": identity, "revision": revision, "disposition": "reviewed", "factual_verification": "uncertain",
                "note": "Retained the established qualification without new factual verification."} for identity, revision in dream["batch"]["targets"].items()]}
        for operation in ("prepare", "complete"):
            result, completed = self.cli("dream", operation, "--invocation-file", current["invocation_file"], "--input", "-", payload=payload)
            self.assertEqual(result.returncode, 0, (completed, result.stderr))
        self.assertEqual(completed["work_session_status"], "completed")
        (self.raw / "colors.md").write_text("The approved accent color is amber.\n")
        result, drifted = self.event("recover")
        self.assertEqual(result.returncode, 0, (drifted, result.stderr))
        self.assertFalse(drifted["action_ready"])
        self.assertEqual(drifted["next_action"]["kind"], "learn")


if __name__ == "__main__":
    unittest.main()
