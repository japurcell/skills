#!/usr/bin/env python3
"""Bounded safe reports through public generated security entrypoints."""
from __future__ import annotations
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("merge_fixture", ROOT / "scripts/test-scan-secrets-merge.py")
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)

class SecurityReportingTests(unittest.TestCase):
    git = fixture.MergeScannerTests.git

    def setUp(self):
        fixture.MergeScannerTests.setUp(self)
        for key in ("SKIP_TOOL_GUARD", "TOOL_GUARD_ALLOWLIST", "SKIP_SECRETS_SCAN", "SECRETS_ALLOWLIST"):
            self.env.pop(key, None)
        self.env.update(AUDIT_PASSIVE_LOG_MODE="default", GEMINI_PASSIVE_LOG_MODE="default",
                        AUDIT_LOG_MAX_BYTES="1048576", AUDIT_LOG_MAX_BACKUPS="3", AUDIT_LOCK_WAIT_MS="1000")

    def invoke(self, provider, *, mode="block", metadata=None, log_failure=False, guardian=False, value=None, tool=None, lock=False, raw_input=None):
        log_dir = self.root / (provider + mode + ("guard" if guardian else "scan"))
        log_dir.mkdir(exist_ok=True)
        self.env["HOME"] = str(self.root)
        env = {**self.env, "OBSERVABILITY_TESTING": "1", "TMPDIR": str(self.root),
               "SCAN_MODE": mode, "GUARD_MODE": mode, "SECRETS_LOG_DIR": str(log_dir),
               "AUDIT_LOG": str(log_dir / "audit.log"), "OBSERVABILITY_LOG_PATH": str(log_dir / "obs.jsonl"),
               "TOOL_GUARD_LOG_DIR": str(log_dir if provider == "gemini" else log_dir / "guard.log")}
        payload = ({"toolName": tool or "bash", "toolArgs": value or {"command": "echo safe"}, "sessionId": "test"}
                   if provider == "copilot" else {"tool_name": tool or ("run_shell_command" if provider == "gemini" else "exec_command"),
                       "tool_input": value or {"cmd": "echo safe"}, "session_id": "test"})
        payload["hook_event_name"] = {"copilot": "preToolUse", "gemini": "BeforeTool", "codex": "PreToolUse"}[provider]
        payload.update(metadata or {})
        path = log_dir / ("guard.log" if guardian else "scan.log")
        if log_failure:
            if not path.is_dir():
                path.unlink(missing_ok=True)
            path.mkdir(exist_ok=True)
        hook = (ROOT / (".codex/hooks/tool-guard.py" if provider == "codex" else f".{provider}/hooks/scripts/tool-guard.py")) if guardian else fixture.HOOKS[provider]
        lock_handle = None
        try:
            if lock:
                lock_handle = path.with_name(path.name + ".lock").open("wb")
                if os.name == "nt":
                    import msvcrt
                    lock_handle.write(b"0")
                    lock_handle.flush()
                    lock_handle.seek(0)
                    msvcrt.locking(lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            result = subprocess.run([sys.executable, "-I", "-S", "-B", str(hook)], cwd=self.repo,
                env=env, input=json.dumps(payload) if raw_input is None else raw_input, text=True, capture_output=True, timeout=12)
        finally:
            if lock_handle:
                lock_handle.close()
        self.assertEqual(result.returncode, 0, result.stderr)
        raw = path.read_bytes() if path.is_file() else b""
        rows = [json.loads(line[line.find(b"{"):]) for line in raw.splitlines()]
        return json.loads(result.stdout), rows, raw, result.stderr

    def test_scanner_outer_metadata_cannot_discard_known_findings(self):
        (self.repo / "secret.txt").write_text(fixture.FAKE_TOKEN)
        for provider in fixture.PROVIDERS:
            response, rows, raw, _ = self.invoke(provider, metadata={"sessionId": "x" * 70000, "session_id": "x" * 70000, "timestamp": "y" * 70000})
            self.assertIn("potential secrets detected", json.dumps(response))
            self.assertEqual(rows[-1]["status"], "findings")
            self.assertLessEqual(len(raw.splitlines(keepends=True)[-1]), 65536)

    def test_scanner_token_labels_are_sanitized_and_escaped_record_bounded(self):
        token = "github_pat_" + "FAKE" * 8
        path = self.repo / (token + "\x1b[31m")
        path.mkdir()
        target = path / ('"\\' * 80 + ".txt")
        target.write_text((fixture.FAKE_TOKEN + "\n") * 1001)
        for provider in fixture.PROVIDERS:
            response, rows, raw, stderr = self.invoke(provider, metadata={"sessionId": token, "session_id": token, "timestamp": token})
            self.assertIn("potential secrets detected", json.dumps(response))
            self.assertNotIn(token, raw.decode() + json.dumps(response) + stderr)
            self.assertNotIn("\\u001b", raw.decode())
            self.assertLessEqual(len(raw.splitlines(keepends=True)[-1]), 65536)
            record = rows[-1]
            self.assertEqual(len(record["findings"]), 100)
            self.assertEqual(record["omittedFindings"], 900)
            self.assertEqual(record["security_outcome"], "findings")
            self.assertEqual(record["audit_outcome"], "written")
            self.assertEqual(record["enforcement"], "deny")

    def test_guardian_token_labels_and_unknown_profile_are_safe_and_attributable(self):
        token = "github_pat_" + "FAKE" * 8
        command = "git push" + " --force origin main"
        for provider in fixture.PROVIDERS:
            response, rows, raw, _ = self.invoke(provider, guardian=True, tool=token + "\x1b[31m", value={"command": command, token: "unknown-private-body"})
            text = raw.decode() + json.dumps(response)
            self.assertNotIn(token, text)
            self.assertNotIn("unknown-private-body", text)
            self.assertLessEqual(len(raw), 16384)
            self.assertEqual(rows[-1]["route"], "strict_fallback")
            self.assertEqual(rows[-1]["profile"], "unsupported")
            self.assertRegex(rows[-1]["build"], r"^[0-9a-f]{16}$")

    def test_audit_failure_preserves_findings_and_clean_calls_fail_closed(self):
        secret = self.repo / "secret.txt"
        command = "git push" + " --force origin main"
        for guardian in (False, True):
            for provider in fixture.PROVIDERS:
                for mode in ("block", "warn"):
                    with self.subTest(guardian=guardian, provider=provider, mode=mode):
                        secret.write_text(fixture.FAKE_TOKEN)
                        response, _, _, _ = self.invoke(provider, mode=mode, guardian=guardian,
                            log_failure=True, value={"command": command})
                        text = json.dumps(response)
                        self.assertIn("security_outcome=findings", text)
                        self.assertIn("audit_outcome=failed", text)
                        self.assertIn("potential secrets detected" if not guardian else "force_push_protected_branch", text)
                        secret.unlink()
                        response, _, _, _ = self.invoke(provider, mode=mode, guardian=guardian,
                            log_failure=True, value={"command": "echo safe"})
                        text = json.dumps(response)
                        self.assertIn("security_outcome=clean", text)
                        self.assertIn("audit_outcome=failed", text)
                        if mode == "block" or guardian:
                            self.assertIn("deny", text)

    def test_partial_findings_survive_later_unsafe_candidate(self):
        (self.repo / "a-secret.txt").write_text(fixture.FAKE_TOKEN)
        (self.repo / "z-unsafe.txt").symlink_to(self.root / "outside.txt")
        for provider in fixture.PROVIDERS:
            for mode in ("block", "warn"):
                with self.subTest(provider=provider, mode=mode):
                    response, rows, _, _ = self.invoke(provider, mode=mode)
                    self.assertIn("potential secrets detected", json.dumps(response))
                    self.assertIn("scan incomplete", json.dumps(response))
                    self.assertEqual(rows[-1]["status"], "incomplete")
                    self.assertEqual(rows[-1]["security_outcome"], "findings")
                    self.assertEqual(rows[-1]["inspection_outcome"], "incomplete")
                    self.assertEqual(rows[-1]["diagnostic"]["cause"], "candidate_unsafe")
                    self.assertEqual(rows[-1]["findings"][0]["path"], "a-secret.txt")

    def test_lock_contention_preserves_positive_findings(self):
        (self.repo / "secret.txt").write_text(fixture.FAKE_TOKEN)
        command = "git push" + " --force origin main"
        for guardian in (False, True):
            for provider in fixture.PROVIDERS:
                for mode in ("block", "warn"):
                    with self.subTest(guardian=guardian, provider=provider, mode=mode):
                        response, _, _, _ = self.invoke(provider, mode=mode, guardian=guardian,
                            lock=True, value={"command": command})
                        text = json.dumps(response)
                        self.assertIn("security_outcome=findings", text)
                        self.assertIn("audit_outcome=failed", text)
                        self.assertIn("enforcement=" + ("deny" if mode == "block" else "allow"), text)

    def test_malformed_known_profile_is_strict_without_echoing_unknown_fields(self):
        token = "xoxb-" + "FAKE" * 8
        command = "git push" + " --force origin main"
        for provider in fixture.PROVIDERS:
            tool = {"copilot": "bash", "gemini": "run_shell_command", "codex": "exec_command"}[provider]
            value = {"cmd" if provider == "codex" else "command": command, token: "untrusted-body"}
            for mode in ("block", "warn"):
                response, rows, raw, _ = self.invoke(provider, mode=mode, guardian=True, tool=tool, value=value)
                self.assertNotIn(token, raw.decode() + json.dumps(response))
                self.assertNotIn("untrusted-body", raw.decode() + json.dumps(response))
                self.assertEqual(rows[-1]["profile"], "unsupported")
                self.assertEqual(rows[-1]["route"], "strict_fallback")
                self.assertIn("force_push_protected_branch", json.dumps(response))

    def test_maximum_escaped_paths_and_env_labels_keep_encoded_ceiling(self):
        parent = self.repo / "z"
        for _ in range(6):
            parent = parent / ('"\\' * 50)
        parent.mkdir(parents=True)
        (parent / "secret.txt").write_text((fixture.FAKE_TOKEN + "\n") * 1001)
        for index in range(120):
            (self.repo / (".env." + str(index) + '"\\' * 70)).write_text("safe")
        for provider in fixture.PROVIDERS:
            for mode in ("block", "warn"):
                response, rows, raw, _ = self.invoke(provider, mode=mode)
                record = rows[-1]
                self.assertEqual(record["security_outcome"], "findings")
                self.assertLessEqual(len(raw.splitlines(keepends=True)[-1]), 65536)
                self.assertLessEqual(len(json.dumps(response).encode()), 16384)
                self.assertEqual(record["omittedFindings"], 900)
                self.assertEqual(len(record["envFiles"]) + record["omittedEnvFiles"], 120)

    def test_guardian_invalid_transport_and_nonobject_have_safe_attribution(self):
        for provider in fixture.PROVIDERS:
            for raw in ("{]", "[]"):
                with self.subTest(provider=provider, raw=raw):
                    response, rows, _, _ = self.invoke(provider, guardian=True, raw_input=raw)
                    text = json.dumps(response)
                    self.assertIn("invalid hook input JSON", text)
                    self.assertIn("security_outcome=incomplete", text)
                    self.assertIn("audit_outcome=not_attempted", text)
                    self.assertIn("route=input_validation", text)
                    self.assertIn("cause=input_invalid", text)
                    self.assertIn("enforcement=deny", text)
                    self.assertRegex(text, r"build=[0-9a-f]{16}")
                    self.assertEqual(rows, [])

if __name__ == "__main__":
    unittest.main()
