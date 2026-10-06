#!/usr/bin/env python3
"""Offline native envelopes at public subprocess seams, never certification."""
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

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("adapter_lifecycle_fixture", ROOT / "scripts/test-agent-brain-lifecycle.py")
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
compat_spec = importlib.util.spec_from_file_location("adapter_source_fixture", ROOT / "scripts/test-agent-brain-compatibility.py")
compat = importlib.util.module_from_spec(compat_spec)
compat_spec.loader.exec_module(compat)
publication = compat.publication_fixture


class AdapterTests(fixture.LifecycleTests):
    # Reuse setup and public helpers, not inherited common-protocol test cases.
    def setUp(self):
        super().setUp()
        self.bundle = self.repo / "bundle"
        shutil.copytree(ROOT / "skills/agent-brain", self.bundle, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        self.adapter = self.bundle / "assets/adapters/codex.py"

    def native(self, provider="codex", mode="cli", deadline=5):
        self.provider = provider
        self.adapter = self.bundle / ("assets/adapters/" + provider + ".py")
        self.config["providers"]["fixture"].update(kind="native", adapter_version="native-1")
        self.save_config()
        permissions = self.repo / "permissions.json"
        permissions.write_text('{"mode":"offline"}')
        lifecycle = self.repo / "native-hooks.json"
        lifecycle.write_text('{"unrelated":{"preserved":true},"hooks":{}}')
        events = {
            "codex": ["SessionStart", "UserPromptSubmit", "PreToolUse", "PreCompact", "SubagentStart", "SubagentStop", "Stop"],
            "copilot": ["sessionStart", "userPromptTransformed", "preToolUse", "preCompact", "subagentStart", "subagentStop", "agentStop"],
            "gemini": ["SessionStart", "BeforeAgent", "BeforeTool", "BeforeModel", "AfterAgent", "PreCompress"],
        }[provider]
        files = [(p.relative_to(self.bundle).as_posix(), fixture.sha(p)) for p in sorted((self.bundle / "scripts").rglob("*.py"))]
        self.support = {
            "schema_version": 1, "kind": "native", "status": "offline_fixture", "repository_id": self.repository_id,
            "repository_root": str(self.repo), "worktree_root": str(self.repo), "platform": sys.platform,
            "filesystem_id": str(self.repo.stat().st_dev), "events": fixture.EVENTS, "core_version": fixture.VERSION,
            "adapter_version": "native-1", "certification_id": self.cert,
            "provider": provider, "provider_version": "offline-build-1", "entry_mode": mode,
            "native_events": events, "adapter_path": self.adapter.relative_to(self.repo).as_posix(),
            "adapter_revision": fixture.sha(self.adapter), "bundle_path": "bundle",
            "bundle_revision": hashlib.sha256(json.dumps(files, separators=(",", ":")).encode()).hexdigest(),
            "permissions": {"path": "permissions.json", "revision": fixture.sha(permissions)},
            "lifecycle_config": {"path": "native-hooks.json", "revision": fixture.sha(lifecycle)},
            "native_deadline_seconds": deadline, "immediate_model_boundary": True, "child_delivery": True,
            "evidence": "offline_translation_only",
            "scope": {"paths": ["src/app.py"]},
        }
        self.save_support()
        self.registration = {"schema_version": 1, "integration_id": "fixture", "config_path": ".agents/context/config.json",
            "bundle_path": "bundle", "provider": provider, "provider_version": "offline-build-1", "entry_mode": mode}
        self.registration_path = self.config_path.parent / "native-registration.json"
        self.registration_path.write_text(json.dumps(self.registration))

    def save_support(self):
        (self.config_path.parent / "fixture.json").write_text(json.dumps(self.support))

    def payload(self, event, **fields):
        value = {"cwd": str(self.repo), "sessionId" if self.provider == "copilot" else "session_id": "conversation"}
        value.update(fields)
        return value

    def adapter_event(self, event, **fields):
        return self.process(self.adapter, "--event", event, payload=self.payload(event, **fields))

    def run_foreground(self, envelope, classification=None, objective=None):
        text = json.dumps(envelope)
        # The native response supplies an exact issued path. No synthesized
        # normalized event is injected by the harness.
        import re
        match = re.search(r"(/[^\s\"\\]+/foreground/[^\s\"\\]+\.json)", text)
        self.assertIsNotNone(match, text)
        return self.process(self.bundle / "scripts/native-integration.py", "foreground", "--invocation-file", match[1],
            *(["--classification", classification] if classification else []),
            *(["--objective", objective] if objective else []))

    def native_ready(self):
        self.adapter_event("SessionStart", source="startup")
        _, stopped = self.adapter_event("Stop")
        result, ready = self.run_foreground(stopped, "ready_to_complete")
        self.assertEqual(result.returncode, 0, (ready, result.stderr))
        return ready

    sources = compat.CompatibilityTests.sources
    annotation = compat.CompatibilityTests.annotation
    proposal = compat.CompatibilityTests.proposal
    summary_text = compat.CompatibilityTests.summary_text
    evidence = compat.CompatibilityTests.evidence
    tip = publication.PublicationTests.tip
    interrupted = publication.PublicationTests.interrupted

    def native_gate(self, provider, event, **fields):
        if provider == "copilot":
            helpers = self.repo / ".github/hooks/scripts/helpers"
            if not helpers.exists(): shutil.copytree(ROOT / ".github/hooks/scripts/helpers", helpers)
            script = ROOT / ".github/hooks/scripts/inject-auto-ingest-context.py"
        else:
            script = ROOT / ".gemini/hooks/scripts/inject-auto-ingest-context.py"
        home = self.repo / "disposable-home"
        home.mkdir(exist_ok=True)
        payload = self.payload(event, hook_event_name=event, **fields)
        result = subprocess.run([sys.executable, str(script)], cwd=self.repo, input=json.dumps(payload), text=True,
            capture_output=True, timeout=5, env=dict(os.environ, HOME=str(home), AUDIT_LOG=str(home / "audit.log"), PYTHONDONTWRITEBYTECODE="1"))
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_provider_start_resume_scope_and_completion_foreground(self):
        for provider, start, scope, stop in (("codex", "SessionStart", "PreToolUse", "Stop"),
                ("copilot", "sessionStart", "preToolUse", "agentStop"), ("gemini", "SessionStart", "BeforeTool", "AfterAgent")):
            with self.subTest(provider=provider):
                self.native(provider)
                result, context = self.adapter_event(start, source="startup")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Read current guidance before concluding.", json.dumps(context))
                result, restored = self.adapter_event(start, source="resume")
                self.assertIn("Read current guidance before concluding.", json.dumps(restored), result.stderr)
                _, allowed = self.adapter_event(scope, **{"toolArgs" if provider == "copilot" else "tool_input": {"path": "src/app.py"}})
                self.assertNotIn("deny", json.dumps(allowed))
                _, blocked = self.adapter_event(stop)
                self.assertIn("foreground", json.dumps(blocked))
                _, status = self.cli("status")
                self.assertEqual(status["work_sessions"][0]["obligations"], [])
                result, ready = self.run_foreground(blocked, "ready_to_complete")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(ready["obligations"][0]["attempt_count"], 1)
                self.assertEqual(ready["next_action"]["kind"], "learn")
                # Clean one disposable integration before trying the next.
                shutil.rmtree(self.repo / ".agents/context/state")

    def test_staggered_json_and_split_utf8_finish_before_pipe_eof(self):
        self.native()
        raw = json.dumps(self.payload("SessionStart", source="startup", prompt="café"), ensure_ascii=False).encode("utf-8")
        split = raw.index(b"\xc3") + 1
        process = subprocess.Popen([sys.executable, str(self.adapter), "--event", "SessionStart"], cwd=self.repo,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            time.sleep(0.3)
            process.stdin.write(raw[:split]); process.stdin.flush()
            time.sleep(0.3)
            process.stdin.write(raw[split:]); process.stdin.flush()
            process.wait(timeout=2)
            self.assertIsNone(process.stdin.closed if process.stdin.closed else None)
            process.stdin.close(); process.stdin = None
            stdout, stderr = process.communicate(timeout=1)
            self.assertIn("Read current guidance", json.dumps(json.loads(stdout)), stderr)
        finally:
            if process.poll() is None:
                process.kill()
            if process.stdin:
                process.stdin.close(); process.stdin = None
            process.communicate(timeout=2)

    def test_copilot_preserves_original_transformed_prompt(self):
        self.native("copilot")
        self.adapter_event("sessionStart", source="startup")
        original = "Please implement the user's original task."
        for valid in (True, False):
            if not valid:
                self.registration["provider_version"] = "other-build"
                self.registration_path.write_text(json.dumps(self.registration))
            result, response = self.adapter_event("userPromptTransformed", transformedPrompt=original, prompt="raw")
            self.assertEqual(result.returncode, 0)
            self.assertTrue(response["modifiedTransformedPrompt"].startswith(original + "\n\n"))

    def test_binding_changes_reject_before_state(self):
        for field, value in (("entry_mode", "desktop"), ("provider_version", "different"), ("bundle_path", "wrong")):
            self.native()
            self.registration[field] = value
            self.registration_path.write_text(json.dumps(self.registration))
            _, response = self.adapter_event("PreToolUse", tool_input={})
            self.assertEqual(response["hookSpecificOutput"]["permissionDecision"], "deny")
            self.assertFalse((self.repo / ".agents/context/state").exists())

    def test_support_identity_and_permission_configuration_pins_reject_before_state(self):
        for field, replacement in (("schema_version", 2), ("core_version", "unknown-core"),
                ("certification_id", "00000000-0000-4000-8000-000000000001"), ("repository_root", "/unmatched"),
                ("native_events", []), ("adapter_revision", "0" * 64)):
            self.native()
            self.support[field] = replacement
            self.save_support()
            _, rejected = self.adapter_event("SessionStart", source="startup")
            self.assertIn("NATIVE_UNSUPPORTED", json.dumps(rejected))
            self.assertFalse((self.repo / ".agents/context/state").exists())
        for path in ("permissions.json", "native-hooks.json"):
            self.native()
            (self.repo / path).write_text('{"changed":true}')
            _, rejected = self.adapter_event("SessionStart", source="startup")
            self.assertIn("NATIVE_UNSUPPORTED", json.dumps(rejected))
            self.assertFalse((self.repo / ".agents/context/state").exists())
        self.native()
        support_path = self.config_path.parent / "fixture.json"
        support_path.write_bytes(b"x" * (1024 * 1024 + 1))
        _, rejected = self.adapter_event("PreToolUse", tool_input={})
        self.assertEqual(rejected["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertFalse((self.repo / ".agents/context/state").exists())
        if hasattr(os, "mkfifo"):
            support_path.unlink()
            os.mkfifo(support_path)
            _, rejected = self.adapter_event("PreToolUse", tool_input={})
            self.assertEqual(rejected["hookSpecificOutput"]["permissionDecision"], "deny")
            self.assertFalse((self.repo / ".agents/context/state").exists())

    def test_linked_bundle_directory_rejects_before_pinned_code_execution(self):
        script = self.bundle / "scripts/native-integration.py"
        script.write_text(script.read_text().replace("from agent_brain.native import main",
            "from pathlib import Path\nPath('untrusted-code-ran.txt').write_text('unexpected')\nfrom agent_brain.native import main"))
        self.native()
        destination = self.repo / "linked-scripts"
        (self.bundle / "scripts").rename(destination)
        (self.bundle / "scripts").symlink_to(destination, target_is_directory=True)
        _, rejected = self.adapter_event("SessionStart", source="startup")
        self.assertIn("NATIVE_UNSUPPORTED", json.dumps(rejected))
        self.assertFalse((self.repo / "untrusted-code-ran.txt").exists())
        self.assertFalse((self.repo / ".agents/context/state").exists())

    def test_duplicate_nonfinite_trailing_invalid_utf8_and_partial(self):
        self.native(deadline=0.5)
        for raw in (b'{"cwd":1,"cwd":2}', b'{"cwd":NaN}', b'{"cwd":Infinity}', b'{}{}', b'{"cwd":"\xff"}', b'{"cwd":'):
            result = subprocess.run([sys.executable, str(self.adapter), "--event", "PreToolUse"], cwd=self.repo,
                input=raw, capture_output=True, timeout=1)
            self.assertEqual(json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")
            self.assertFalse((self.repo / ".agents/context/state").exists())

    def test_internal_watchdog_below_tighter_native_deadline(self):
        self.native(deadline=0.4)
        process = subprocess.Popen([sys.executable, str(self.adapter), "--event", "PreToolUse"], cwd=self.repo,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        started = time.monotonic()
        try:
            process.stdin.write(b'{"cwd":'); process.stdin.flush()
            process.wait(timeout=1)
            self.assertLess(time.monotonic() - started, 0.6)
            process.stdin.close(); process.stdin = None
            stdout, stderr = process.communicate(timeout=1)
            self.assertIn("INTERNAL_WATCHDOG_INCOMPLETE", stdout.decode())
            self.assertIn("provider timeout behavior remain unverified", stderr.decode())
        finally:
            if process.poll() is None: process.kill()
            if process.stdin: process.stdin.close(); process.stdin = None
            process.communicate(timeout=2)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "POSIX special-file fixture")
    def test_registration_fifo_rejected_without_callback_effects(self):
        path = self.config_path.parent / "native-registration.json"
        os.mkfifo(path)
        started = time.monotonic()
        result, response = self.process(self.adapter, "--event", "PreToolUse", payload={"cwd": str(self.repo)})
        self.assertLess(time.monotonic() - started, 0.5)
        self.assertEqual(response["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertFalse((self.repo / ".agents/context/state").exists())

    def test_gate_failed_output_never_creates_tool_authority(self):
        self.native()
        bridge = self.bundle / "scripts/integration-bridge.py"
        process = subprocess.Popen([sys.executable, str(bridge), "--json", "--native-gate"], cwd=self.repo,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.stdout.close(); process.stdout = None
        _, errors = process.communicate(json.dumps(self.payload("SessionStart", hook_event_name="SessionStart", source="startup")).encode(), timeout=3)
        self.assertNotEqual(process.returncode, 0)
        _, denied = self.adapter_event("PreToolUse", tool_input={"path": "src/app.py"})
        self.assertEqual(denied["hookSpecificOutput"]["permissionDecision"], "deny")
        process = subprocess.Popen([sys.executable, str(self.adapter), "--event", "SessionStart"], cwd=self.repo,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.stdout.close(); process.stdout = None
        process.communicate(json.dumps(self.payload("SessionStart", source="startup")).encode(), timeout=3)
        _, denied = self.adapter_event("PreToolUse", tool_input={"path": "src/app.py"})
        self.assertEqual(denied["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_compaction_and_validated_immediate_model_boundary(self):
        for provider in ("codex", "copilot", "gemini"):
            self.native(provider)
            start = "sessionStart" if provider == "copilot" else "SessionStart"
            self.adapter_event(start, source="startup")
            advisory = {"codex": "PreCompact", "copilot": "preCompact", "gemini": "PreCompress"}[provider]
            _, output = self.adapter_event(advisory, trigger="auto")
            if provider == "copilot": self.assertEqual(output, {})
            elif provider == "gemini": self.assertEqual(set(output), {"systemMessage"})
            _, status = self.cli("status")
            self.assertFalse(status["work_sessions"][0]["agents"][0]["delivery_complete"])
            if provider == "codex":
                _, restored = self.adapter_event("SessionStart", source="compact")
            elif provider == "copilot":
                _, restored = self.adapter_event("userPromptTransformed", transformedPrompt="Keep working.")
            else:
                _, restored = self.adapter_event("BeforeModel", llm_request={"model": "offline-model", "messages": [{"role": "user", "content": "Keep working."}], "config": {}})
                self.assertEqual(restored["hookSpecificOutput"]["llm_request"]["messages"][0], {"role": "user", "content": "Keep working."})
            self.assertIn("Read current guidance", json.dumps(restored))
            shutil.rmtree(self.repo / ".agents/context/state")

    def test_unverified_compaction_model_child_and_vscode_are_unsupported(self):
        self.native()
        self.adapter_event("SessionStart", source="startup")
        self.support["immediate_model_boundary"] = False
        self.save_support()
        _, response = self.adapter_event("SessionStart", source="compact")
        self.assertIn("NATIVE_UNSUPPORTED", json.dumps(response))
        self.support["child_delivery"] = False
        self.save_support()
        _, response = self.adapter_event("SubagentStart", agent_id="child", agent_type="custom")
        self.assertIn("NATIVE_UNSUPPORTED", json.dumps(response))
        self.registration["entry_mode"] = "vscode"
        self.registration_path.write_text(json.dumps(self.registration))
        _, response = self.adapter_event("PreToolUse", tool_input={})
        self.assertEqual(response["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_child_context_and_stop_require_scoped_foreground_review(self):
        for provider in ("codex", "copilot"):
            self.native(provider)
            self.adapter_event("sessionStart" if provider == "copilot" else "SessionStart", source="startup")
            start = "subagentStart" if provider == "copilot" else "SubagentStart"
            stop = "subagentStop" if provider == "copilot" else "SubagentStop"
            fields = {"agentName": "review-child", "agentType": "custom"} if provider == "copilot" else {"agent_id": "review-child", "agent_type": "custom"}
            _, output = self.adapter_event(start, **fields)
            self.assertIn("Read current guidance", json.dumps(output))
            _, parent_checkpoint = self.adapter_event("agentStop" if provider == "copilot" else "Stop")
            code, parent_waiting = self.run_foreground(parent_checkpoint, "awaiting_user")
            self.assertEqual(code.returncode, 0, (parent_waiting, code.stderr))
            _, released_parent = self.adapter_event("agentStop" if provider == "copilot" else "Stop")
            self.assertNotIn("block", json.dumps(released_parent))
            _, stopped = self.adapter_event(stop, **fields)
            self.assertIn("foreground", json.dumps(stopped))
            result, ready = self.run_foreground(stopped, "ready_to_complete")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(ready["obligations"][0]["kind"], "child_review")
            self.assertEqual(ready["obligations"][0]["attempt_count"], 1)
            shutil.rmtree(self.repo / ".agents/context/state")

    def test_copilot_general_purpose_child_cannot_register(self):
        self.native("copilot")
        self.adapter_event("sessionStart", source="startup")
        _, result = self.adapter_event("subagentStart", agentName="general-purpose", agentId="child")
        self.assertIn("NATIVE_UNSUPPORTED", json.dumps(result))
        _, status = self.cli("status")
        self.assertEqual(len(status["work_sessions"][0]["agents"]), 1)

    def test_pause_cancel_are_explicit_issued_foreground_controls(self):
        import re
        for control, expected in (("pause", "paused"), ("cancel", "cancelled")):
            self.native()
            self.adapter_event("SessionStart", source="startup")
            _, envelope = self.adapter_event("Stop")
            path = re.search(r"(/[^\s\"\\]+/foreground/[^\s\"\\]+\.json)", json.dumps(envelope))[1]
            result, data = self.process(self.bundle / "scripts/native-integration.py", "foreground", "--invocation-file", path, "--control", control)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(data["work_session_status"], expected)
            _, status = self.cli("status")
            self.assertEqual(status["work_sessions"][0]["obligations"], [])
            shutil.rmtree(self.repo / ".agents/context/state")

    def test_verified_turn_checkpoints_release_stop_without_completing_objective(self):
        import re
        for provider, stop in (("codex", "Stop"), ("copilot", "agentStop"), ("gemini", "AfterAgent")):
            for classification, control in (("active", None), ("awaiting_user", None), (None, "pause"), (None, "cancel")):
                with self.subTest(provider=provider, classification=classification, control=control):
                    self.native(provider)
                    self.adapter_event("sessionStart" if provider == "copilot" else "SessionStart", source="startup")
                    _, issued = self.adapter_event(stop)
                    path = re.search(r"(/[^\s\"\\]+/foreground/[^\s\"\\]+\.json)", json.dumps(issued))[1]
                    arguments = ["--control", control] if control else ["--classification", classification]
                    code, result = self.process(self.bundle / "scripts/native-integration.py", "foreground", "--invocation-file", path, *arguments)
                    self.assertEqual(code.returncode, 0, (result, code.stderr))
                    _, released = self.adapter_event(stop, stop_hook_active=True)
                    self.assertNotIn("block", json.dumps(released))
                    self.assertNotIn("deny", json.dumps(released))
                    _, status = self.cli("status")
                    self.assertNotEqual(status["work_sessions"][0]["work_session_status"], "completed")
                    if not control:
                        task = "userPromptTransformed" if provider == "copilot" else "BeforeAgent" if provider == "gemini" else "UserPromptSubmit"
                        self.adapter_event(task, **({"transformedPrompt": "Continue the same task."} if provider == "copilot" else {"prompt": "Continue the same task."}))
                        _, stopped = self.adapter_event(stop)
                        self.assertIn("foreground", json.dumps(stopped))
                    shutil.rmtree(self.repo / ".agents/context/state")

    def test_source_turn_release_preserves_pending_obligation_and_dependent_gate(self):
        for provider, start, stop in (("copilot", "sessionStart", "agentStop"), ("gemini", "SessionStart", "AfterAgent")):
            self.sources()
            self.native(provider)
            _, started = self.adapter_event(start, source="startup")
            self.run_foreground(started)
            _, issued = self.adapter_event(stop)
            code, result = self.run_foreground(issued, "awaiting_user")
            self.assertEqual(code.returncode, 0, (result, code.stderr))
            _, released = self.adapter_event(stop)
            self.assertNotIn("deny", json.dumps(released))
            self.assertNotIn("block", json.dumps(released))
            legacy = self.native_gate(provider, stop)
            self.assertNotIn(legacy.get("decision"), ("deny", "block"))
            _, blocked = self.adapter_event("preToolUse" if provider == "copilot" else "BeforeTool", **{
                "toolArgs" if provider == "copilot" else "tool_input": {"path": "src/app.py"}})
            self.assertIn("deny", json.dumps(blocked))
            _, status = self.cli("status")
            self.assertEqual(len(status["work_sessions"][0]["obligations"]), 1)
            self.assertNotEqual(status["work_sessions"][0]["obligations"][0]["status"], "completed")
            old_obligation = status["work_sessions"][0]["obligations"][0]
            import re
            path = re.search(r"(/[^\s\"\\]+/foreground/[^\s\"\\]+\.json)", json.dumps(issued))[1]
            code, paused = self.process(self.bundle / "scripts/native-integration.py", "foreground", "--invocation-file", path, "--control", "pause")
            self.assertEqual(code.returncode, 0, (paused, code.stderr))
            task = "userPromptTransformed" if provider == "copilot" else "BeforeAgent"
            _, resume_intent = self.adapter_event(task, **({"transformedPrompt": "Resume my paused task."} if provider == "copilot" else {"prompt": "Resume my paused task."}))
            code, resumed = self.run_foreground(resume_intent, objective="resume")
            self.assertEqual(code.returncode, 0, (resumed, code.stderr))
            self.assertEqual(resumed["identities"]["task_id"], paused["identities"]["task_id"])
            self.assertEqual(resumed["obligations"][0]["id"], old_obligation["id"])
            self.assertEqual(resumed["obligations"][0]["attempt_count"], old_obligation["attempt_count"])
            self.assertFalse(resumed["action_ready"])
            code, cancelled = self.process(self.bundle / "scripts/native-integration.py", "foreground", "--invocation-file", path, "--control", "cancel")
            self.assertEqual(code.returncode, 0, (cancelled, code.stderr))
            task = "userPromptTransformed" if provider == "copilot" else "BeforeAgent"
            _, intent = self.adapter_event(task, **({"transformedPrompt": "Independent task."} if provider == "copilot" else {"prompt": "Independent task."}))
            code, next_task = self.run_foreground(intent, objective="new")
            self.assertEqual(code.returncode, 0, (next_task, code.stderr))
            self.assertFalse(next_task["action_ready"])
            _, status = self.cli("status")
            old = next(s for s in status["work_sessions"] if s["work_session_status"] == "cancelled")
            self.assertEqual(old["obligations"][0]["id"], old_obligation["id"])
            self.assertEqual(old["obligations"][0]["attempt_count"], old_obligation["attempt_count"])
            shutil.rmtree(self.repo / ".agents/context/state")
            shutil.rmtree(self.repo / "tools")
            shutil.rmtree(self.repo / ".agents/sources")
            shutil.rmtree(self.repo / ".agents/memory")
            shutil.rmtree(self.repo / ".agents/skills")

            self.config["knowledge_roots"] = [{"path": "guidance", "ownership": "agent_brain"}]

    def test_new_objective_after_stopped_task_requires_issued_intent_and_keeps_old_stopped(self):
        import re
        for provider, start, stop, task in (("codex", "SessionStart", "Stop", "UserPromptSubmit"),
                ("copilot", "sessionStart", "agentStop", "userPromptTransformed"),
                ("gemini", "SessionStart", "AfterAgent", "BeforeAgent")):
            for control, stopped_status in (("pause", "paused"), ("cancel", "cancelled")):
                self.native(provider)
                self.adapter_event(start, source="startup")
                _, issued = self.adapter_event(stop)
                path = re.search(r"(/[^\s\"\\]+/foreground/[^\s\"\\]+\.json)", json.dumps(issued))[1]
                code, stopped = self.process(self.bundle / "scripts/native-integration.py", "foreground", "--invocation-file", path, "--control", control)
                self.assertEqual(code.returncode, 0, (stopped, code.stderr))
                fields = {"transformedPrompt": "Start independent work."} if provider == "copilot" else {"prompt": "Start independent work."}
                _, intent = self.adapter_event(task, **fields)
                self.assertIn("--objective new", json.dumps(intent))
                code, missing = self.run_foreground(intent)
                self.assertEqual(code.returncode, 2)
                self.assertEqual(missing["error"]["code"], "OBJECTIVE_INTENT_REQUIRED")
                code, retained = self.run_foreground(intent, objective="retain_stopped")
                self.assertEqual(code.returncode, 0, (retained, code.stderr))
                self.assertEqual(retained["work_session_status"], stopped_status)
                _, released = self.adapter_event(stop)
                self.assertNotIn("block", json.dumps(released))
                self.assertNotIn("deny", json.dumps(released))
                code, resumed = self.run_foreground(intent, objective="resume")
                if control == "pause":
                    self.assertEqual(code.returncode, 0, (resumed, code.stderr))
                    self.assertEqual(resumed["identities"]["task_id"], stopped["identities"]["task_id"])
                    self.assertEqual(resumed["work_session_status"], "active")
                    # Stop it again so the same issued intent can choose new.
                    code, stopped = self.process(self.bundle / "scripts/native-integration.py", "foreground", "--invocation-file", path, "--control", control)
                    self.assertEqual(code.returncode, 0, (stopped, code.stderr))
                else:
                    self.assertEqual(code.returncode, 2)
                    self.assertEqual(resumed["error"]["code"], "OBJECTIVE_RESUME_INVALID")
                code, new = self.run_foreground(intent, objective="new")
                self.assertEqual(code.returncode, 0, (new, code.stderr))
                self.assertIn("Read current guidance", json.dumps(new))
                _, status = self.cli("status")
                self.assertEqual(sorted(s["work_session_status"] for s in status["work_sessions"]), sorted(["active", stopped_status]))
                self.adapter_event(task, **fields)
                _, status = self.cli("status")
                self.assertEqual(len(status["work_sessions"]), 2)
                _, final_checkpoint = self.adapter_event(stop)
                self.assertIn("foreground", json.dumps(final_checkpoint))
                shutil.rmtree(self.repo / ".agents/context/state")

    def test_native_source_gates_join_one_verified_obligation_without_private_payload(self):
        for provider, start, stop in (("copilot", "sessionStart", "agentStop"), ("gemini", "SessionStart", "AfterAgent")):
            with self.subTest(provider=provider):
                self.sources()
                self.engine.write_text(self.engine.read_text().replace('if __name__ == "__main__":',
                    "Path('scanner-ran.txt').write_text('scanner')\n\nif __name__ == \"__main__\":"))
                self.config["source_ingestion"]["engine_revision"] = fixture.sha(self.engine)
                self.native(provider)
                manifest_before = self.manifest.read_bytes()
                _, startup = self.adapter_event(start, source="startup")
                self.assertEqual(self.manifest.read_bytes(), manifest_before)
                self.assertFalse((self.summaries / "colors-md.summary.md").exists())
                import re, shlex
                path = re.search(r"(/[^\s\"\\]+/foreground/[^\s\"\\]+\.json)", json.dumps(startup))[1]
                command = shlex.join([sys.executable, str(self.bundle / "scripts/native-integration.py"), "foreground", "--invocation-file", path])
                tool_event = "preToolUse" if provider == "copilot" else "BeforeTool"
                tool_field = "toolArgs" if provider == "copilot" else "tool_input"
                _, admitted = self.adapter_event(tool_event, **{tool_field: {"command": command}})
                self.assertNotIn("deny", json.dumps(admitted))
                _, rejected = self.adapter_event(tool_event, **{tool_field: {"command": command + "; extra-command"}})
                self.assertIn("deny", json.dumps(rejected))
                self.assertEqual(self.manifest.read_bytes(), manifest_before)
                _, ready = self.run_foreground(startup)
                stage_command = shlex.join([sys.executable, str(self.bundle / "scripts/agent-brain.py"), "learn", "start", "--invocation-file", ready["invocation_file"], "--json"])
                _, admitted = self.adapter_event(tool_event, **{tool_field: {"command": stage_command}})
                self.assertNotIn("deny", json.dumps(admitted))
                for suffix in (" --input \"$(printf harmless-public-probe)\"", " --input \"`printf harmless-public-probe`\"",
                        " && extra-command", " --json", " --unknown", " --input", " --input --json",
                        " --invocation-file " + shlex.quote(ready["invocation_file"]), " --config other.json"):
                    _, rejected = self.adapter_event(tool_event, **{tool_field: {"command": stage_command + suffix}})
                    self.assertIn("deny", json.dumps(rejected), suffix)
                for accepted in (stage_command + " --input 'literal path.json'",
                        stage_command + ' --input "literal path.json"',
                        stage_command + " --config " + shlex.quote(str(self.repo / ".agents/context/config.json"))):
                    _, admitted = self.adapter_event(tool_event, **{tool_field: {"command": accepted}})
                    self.assertNotIn("deny", json.dumps(admitted), accepted)
                for rejected_command in (stage_command.replace(" learn start ", " dream start "),
                        stage_command.replace(ready["invocation_file"], str(self.repo / "missing-handle.json")),
                        stage_command.replace(" learn start ", " learn unsupported ")):
                    _, rejected = self.adapter_event(tool_event, **{tool_field: {"command": rejected_command}})
                    self.assertIn("deny", json.dumps(rejected))
                first = ready["obligations"][0]["id"]
                _, blocked = self.adapter_event(stop)
                joined = self.native_gate(provider, stop)
                self.assertIn("joined", json.dumps(joined))
                self.assertIn("foreground", json.dumps(joined))
                _, status = self.cli("status")
                self.assertEqual(len(status["work_sessions"][0]["obligations"]), 1)
                self.assertEqual(status["work_sessions"][0]["obligations"][0]["id"], first)
                _, ready = self.run_foreground(blocked, "ready_to_complete")
                payload = self.proposal(ready)
                for operation in ("prepare", "publish", "complete"):
                    code, final = self.stage(operation, ready, payload if operation == "prepare" else None)
                    self.assertEqual(code.returncode, 0, (operation, final, code.stderr))
                self.assertEqual(final["work_session_status"], "completed")
                self.assertEqual(final["obligations"][0]["id"], first)
                self.assertIn("cobalt", (self.repo / "guidance/colors.md").read_text())
                scanner_marker = self.repo / "scanner-ran.txt"
                scanner_marker.unlink(missing_ok=True)
                passed = self.native_gate(provider, stop)
                self.assertNotIn(passed.get("decision"), ("block", "deny"))
                self.assertFalse(scanner_marker.exists(), "nested native gate launched the scanner")
                _, permitted = self.adapter_event("preToolUse" if provider == "copilot" else "BeforeTool", **{
                    "toolArgs" if provider == "copilot" else "tool_input": {"path": "src/app.py"}})
                self.assertNotIn("deny", json.dumps(permitted))
                self.assertFalse(scanner_marker.exists(), "native tool callback launched the scanner")
                (self.raw / "new-source.md").write_text("New controlling input.\n")
                _, drift = self.adapter_event("preToolUse" if provider == "copilot" else "BeforeTool", **{
                    "toolArgs" if provider == "copilot" else "tool_input": {"path": "src/app.py"}})
                self.assertIn("deny", json.dumps(drift))
                self.assertIn("foreground", json.dumps(drift))
                self.assertFalse(scanner_marker.exists(), "source drift callback launched the scanner")
                _, status = self.cli("status")
                self.assertEqual(status["work_sessions"][0]["obligations"][0]["attempt_count"], 1)
                # Reset only this disposable scenario; never weaken a check.
                shutil.rmtree(self.repo / ".agents/context/state")
                shutil.rmtree(self.repo / "tools")
                shutil.rmtree(self.repo / ".agents/sources")
                shutil.rmtree(self.repo / ".agents/memory")
                shutil.rmtree(self.repo / ".agents/skills")
                (self.repo / "guidance/colors.md").unlink()
                self.config["knowledge_roots"] = [{"path": "guidance", "ownership": "agent_brain"}]

    def test_recovery_checks_are_foreground_and_duplicates_preserve_attempts(self):
        checker = self.repo / "delayed-check.py"
        marker = self.repo / "checked.txt"
        checker.write_text("import time\nfrom pathlib import Path\ntime.sleep(0.5)\nPath('checked.txt').write_text('checked')\n")
        self.config["checks"] = {"required": ["guidance", "review_sources", "delayed"],
            "trusted": [{"id": "delayed", "argv": [sys.executable, str(checker)], "timeout_seconds": 3}]}
        self.native()
        ready = self.native_ready()
        payload = self.tip(ready)
        code, prepared = self.stage("prepare", ready, payload)
        self.assertEqual(code.returncode, 0, prepared)
        self.interrupted(ready, "after_intent")
        marker.unlink(missing_ok=True)
        for index in range(3):
            _, deferred = self.adapter_event("SessionStart", source="resume")
            self.assertIn("foreground", json.dumps(deferred))
            self.assertFalse(marker.exists())
            self.assertFalse((self.repo / "guidance/tip.md").exists())
            _, status = self.cli("status")
            self.assertEqual(status["work_sessions"][0]["obligations"][0]["attempt_count"], 1)
        started = time.monotonic()
        code, recovered = self.run_foreground(deferred)
        self.assertEqual(code.returncode, 0, (recovered, code.stderr))
        self.assertGreater(time.monotonic() - started, 0.45)
        self.assertEqual(recovered["publication_recovery"]["status"], "completed")
        self.assertTrue(marker.exists())
        self.assertTrue((self.repo / "guidance/tip.md").exists())
        _, status = self.cli("status")
        self.assertEqual(status["work_sessions"][0]["obligations"][0]["attempt_count"], 2)

    def test_recovery_on_new_task_settles_exact_previous_output_identity(self):
        self.native()
        ready = self.native_ready()
        payload = self.tip(ready)
        code, prepared = self.stage("prepare", ready, payload)
        self.assertEqual(code.returncode, 0, prepared)
        self.interrupted(ready, "after_intent")
        _, deferred = self.adapter_event("SessionStart", source="startup", session_id="new-conversation")
        code, recovered = self.run_foreground(deferred)
        self.assertEqual(code.returncode, 0, (recovered, code.stderr))
        self.assertEqual(recovered["publication_recovery"]["status"], "completed")
        self.assertNotEqual(recovered["identities"]["task_id"], ready["identities"]["task_id"])
        self.assertFalse((self.repo / ".agents/context/state/output-pending.json").exists())
        _, status = self.cli("status")
        self.assertEqual(sorted(s["work_session_status"] for s in status["work_sessions"]), ["active", "completed"])

    def test_turn_release_retains_pending_publication_and_checked_attempt(self):
        for provider, start, stop in (("codex", "SessionStart", "Stop"), ("copilot", "sessionStart", "agentStop"), ("gemini", "SessionStart", "AfterAgent")):
            self.native(provider)
            self.adapter_event(start, source="startup")
            _, checkpoint = self.adapter_event(stop)
            code, ready = self.run_foreground(checkpoint, "ready_to_complete")
            self.assertEqual(code.returncode, 0, (ready, code.stderr))
            code, _ = self.stage("prepare", ready, self.tip(ready))
            self.assertEqual(code.returncode, 0)
            self.interrupted(ready, "after_intent")
            journal = self.config_path.parent / "state/publication.json"
            before = journal.read_bytes()
            _, issued = self.adapter_event(stop)
            code, result = self.run_foreground(issued, "awaiting_user")
            self.assertIn(code.returncode, (0, 1), (result, code.stderr))
            _, released = self.adapter_event(stop)
            self.assertNotIn("block", json.dumps(released))
            self.assertNotIn("deny", json.dumps(released))
            self.assertEqual(journal.read_bytes(), before)
            self.assertFalse((self.repo / "guidance/tip.md").exists())
            _, status = self.cli("status")
            obligation = status["work_sessions"][0]["obligations"][0]
            self.assertNotEqual(obligation["status"], "completed")
            self.assertEqual(obligation["attempt_count"], 1)
            shutil.rmtree(self.repo / ".agents/context/state")
            shutil.rmtree(self.repo / ".agents/context/history")

    def test_duplicate_stop_reissues_expired_ticket_without_spending_attempt(self):
        self.config["limits"] = {"lease_seconds": 0.3}
        self.native()
        self.adapter_event("SessionStart", source="startup")
        _, first = self.adapter_event("Stop")
        time.sleep(0.35)
        _, renewed = self.adapter_event("Stop")
        self.assertNotEqual(first, renewed)
        _, status = self.cli("status")
        self.assertEqual(status["work_sessions"][0]["obligations"], [])
        code, ready = self.run_foreground(renewed, "ready_to_complete")
        self.assertEqual(code.returncode, 0, (ready, code.stderr))
        self.assertEqual(ready["obligations"][0]["attempt_count"], 1)

    def test_new_completed_objective_in_same_native_conversation_gets_current_context(self):
        self.native()
        ready = self.native_ready()
        review = self.review(ready)
        for operation in ("prepare", "complete"):
            code, result = self.stage(operation, ready, review)
            self.assertEqual(code.returncode, 0, (result, code.stderr))
        _, task = self.adapter_event("UserPromptSubmit", prompt="Begin another objective.", turn_id="turn-two")
        self.assertIn("Read current guidance", json.dumps(task))
        _, status = self.cli("status")
        self.assertEqual(sorted(s["work_session_status"] for s in status["work_sessions"]), ["active", "completed"])
        self.assertEqual(len({s["task_id"] for s in status["work_sessions"]}), 2)
        self.adapter_event("UserPromptSubmit", prompt="Clarify the same objective.", turn_id="turn-three")
        _, status = self.cli("status")
        self.assertEqual(len(status["work_sessions"]), 2)

    def test_standalone_unconfigured_native_envelopes(self):
        for provider, event, expected in (
            ("codex", "PreToolUse", {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "agent-brain: NATIVE_UNSUPPORTED"}}),
            ("copilot", "preToolUse", {"permissionDecision": "deny", "permissionDecisionReason": "agent-brain: NATIVE_UNSUPPORTED"}),
            ("gemini", "BeforeTool", {"decision": "deny", "reason": "agent-brain: NATIVE_UNSUPPORTED"}),
        ):
            with self.subTest(provider=provider):
                path = self.repo / (provider + ".py")
                shutil.copy(self.bundle / ("assets/adapters/" + provider + ".py"), path)
                result, data = self.process(path, "--event", event, payload={"cwd": str(self.repo)})
                self.assertEqual(result.returncode, 0)
                self.assertEqual(data, expected)
                self.assertNotIn("cwd", result.stderr)

    def test_all_repository_entrypoints_copy_without_peer_imports(self):
        entries = ((".codex/hooks/agent-brain.py", "codex", "PreToolUse"),
            (".copilot/hooks/scripts/agent-brain.py", "copilot", "preToolUse"),
            (".github/hooks/scripts/agent-brain.py", "copilot", "preToolUse"),
            (".gemini/hooks/scripts/agent-brain.py", "gemini", "BeforeTool"))
        for relative, provider, event in entries:
            self.native(provider)
            copied = self.repo / "entrypoint.py"
            shutil.copy(ROOT / relative, copied)
            # Copied entrypoints are pinned by their own exact location.
            self.support.update(adapter_path="entrypoint.py", adapter_revision=fixture.sha(copied))
            self.save_support()
            result, context = self.process(copied, "--event", "sessionStart" if provider == "copilot" else "SessionStart",
                payload=self.payload(event, source="startup"))
            self.assertIn("Read current guidance", json.dumps(context), result.stderr)
            result, response = self.process(copied, "--event", event,
                payload=self.payload(event, **{"toolArgs" if provider == "copilot" else "tool_input": {"path": "src/app.py"}}))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("deny", json.dumps(response))
            self.assertEqual(json.loads((self.repo / "native-hooks.json").read_text())["unrelated"], {"preserved": True})
            shutil.rmtree(self.repo / ".agents/context/state")

    def test_closed_foreground_ticket_retention_preserves_unresolved_ticket(self):
        import re
        self.config["maintenance"] = {"enabled": True, "retention_days": 30}
        self.native()
        state = self.config_path.parent / "state"
        state.mkdir()
        clock = state / "fixture-clock.json"
        clock.write_text('{"utc":"2026-10-01T00:00:00Z"}')
        self.adapter_event("SessionStart", source="startup")
        _, stopped = self.adapter_event("Stop")
        ticket = Path(re.search(r"(/[^\s\"\\]+/foreground/[^\s\"\\]+\.json)", json.dumps(stopped))[1])
        code, ready = self.run_foreground(stopped, "ready_to_complete")
        self.assertEqual(code.returncode, 0, (ready, code.stderr))
        reviewed = self.review(dict(ready, obligations=[item for item in ready["obligations"] if item["kind"] == "learn"]))
        for operation in ("prepare", "complete"):
            code, result = self.stage(operation, ready, reviewed)
            self.assertEqual(code.returncode, 0, (result, code.stderr))
        code, dream = self.run_foreground(stopped, "ready_to_complete")
        self.assertEqual(code.returncode, 0, (dream, code.stderr))
        assigned = next(item for item in dream["obligations"] if item["kind"] == "dream")
        reviewed = self.review(dict(dream, obligations=[assigned]))
        reviewed["dispositions"] = [{"id": identity, "revision": revision, "disposition": "reviewed",
            "factual_verification": "uncertain", "note": "Reviewed current guidance while retaining uncertainty."}
            for identity, revision in assigned["batch"]["targets"].items()]
        for operation in ("prepare", "complete"):
            code, result = self.cli("dream", operation, "--invocation-file", dream["invocation_file"], "--input", "-", payload=reviewed)
            self.assertEqual(code.returncode, 0, (result, code.stderr))
        clock.write_text('{"utc":"2026-10-30T00:00:00Z"}')
        _, pending = self.adapter_event("Stop", session_id="unresolved")
        pending_ticket = Path(re.search(r"(/[^\s\"\\]+/foreground/[^\s\"\\]+\.json)", json.dumps(pending))[1])
        self.adapter_event("SessionStart", session_id="next", source="startup")
        self.assertTrue(ticket.exists())
        clock.write_text('{"utc":"2026-10-31T00:00:00Z"}')
        self.adapter_event("SessionStart", session_id="next", source="resume")
        self.assertFalse(ticket.exists())
        self.assertTrue(pending_ticket.exists())
        _, status = self.cli("status")
        self.assertGreaterEqual(status["native_foreground"]["pending"], 1)
        self.assertEqual(status["maintenance"]["cleanup"]["pending_files"], [])


# Avoid rerunning inherited tests through unittest's subclass discovery.
for name in tuple(vars(fixture.LifecycleTests)):
    if name.startswith("test_") and name not in vars(AdapterTests):
        setattr(AdapterTests, name, None)

if __name__ == "__main__":
    unittest.main()
