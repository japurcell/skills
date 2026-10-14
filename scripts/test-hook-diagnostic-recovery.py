#!/usr/bin/env python3
"""Public scanner recovery workflow; source hooks do not prove host dispatch."""
from __future__ import annotations
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
PROVIDERS = ("codex", "copilot", "gemini")
PREFIX = "scan-secrets diagnostics (request not executed):"

def entry(provider):
    return Path(".codex/hooks/scan-secrets.py" if provider == "codex" else f".{provider}/hooks/scripts/scan-secrets.py")

def envelope(provider, command="hooks-diagnostics-v1", **extra):
    if provider == "copilot":
        return {"hook_event_name": "preToolUse", "toolName": "bash", "toolArgs": {"command": command, **extra}}
    return {"hook_event_name": "PreToolUse" if provider == "codex" else "BeforeTool", "tool_name": "exec_command" if provider == "codex" else "run_shell_command", "tool_input": {**({"cmd": command, "login": False} if provider == "codex" else {"command": command}), **extra}}

def reason(response):
    return response.get("permissionDecisionReason", response.get("reason", response.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")))

class RecoveryTests(unittest.TestCase):
    def test_import_does_not_consume_open_stdin(self):
        for provider in PROVIDERS:
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as directory:
                script, cwd, env = self.setup_fixture(directory, provider)
                code = "import runpy; runpy.run_path(" + repr(str(script)) + "); print('loaded')"
                with subprocess.Popen([sys.executable, "-I", "-S", "-B", "-c", code], cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                    process.wait(timeout=2)
                    self.assertEqual(process.returncode, 0, process.stderr.read())
                    self.assertEqual(process.stdout.read(), b"loaded\n")

    def setup_fixture(self, directory, provider):
        base = Path(directory).resolve()
        home, cwd = base / "home", base / "repository"
        cwd.mkdir()
        script = home / entry(provider)
        shutil.copytree((ROOT / entry(provider)).parent, script.parent)
        subprocess.run(["git", "init", "-q", str(cwd)], check=True, capture_output=True)
        env = {key: value for key, value in os.environ.items() if key not in {"SKIP_SECRETS_SCAN", "SECRETS_ALLOWLIST", "PYTHONPATH", "GEMINI_PROJECT_DIR"}}
        env.update(HOME=str(home), USERPROFILE=str(home), OBSERVABILITY_TESTING="1", OBSERVABILITY_LOG_PATH=str(base / "audit/log.jsonl"), AUDIT_LOG=str(base / "audit/audit.log"), AUDIT_LOCK=str(base / "audit/audit.lock"), SECRETS_LOG_DIR=str(base / "secrets"))
        return script, cwd, env

    def launch(self, script, cwd, env, payload, mode="block"):
        result = subprocess.run([sys.executable, "-I", "-S", "-B", str(script)], input=json.dumps(payload).encode(), cwd=cwd, env={**env, "SCAN_MODE": mode}, capture_output=True, timeout=12)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout), result

    def diagnostics(self, response, result, provider):
        if provider == "gemini":
            self.assertEqual(response.get("decision"), "deny", response)
        else:
            self.assertEqual(response.get("hookSpecificOutput", {}).get("permissionDecision"), "deny", response)
        self.assertTrue(reason(response).startswith(PREFIX), response)
        self.assertLessEqual(len(result.stdout), 16384)
        report = json.loads(reason(response)[len(PREFIX):])
        self.assertEqual(report["action"], "diagnostics")
        self.assertEqual(report["security_outcome"], "not_scanned")
        self.assertEqual(report["enforcement"], "deny")
        self.assertEqual(report["audit_outcome"], "not_attempted")
        return report

    def test_overflow_failure_preserves_deny_only_diagnostics(self):
        for provider in PROVIDERS:
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as directory:
                script, cwd, env = self.setup_fixture(directory, provider)
                (cwd / "overflow.txt").write_bytes(b"a" * (8388608 + 1))
                ordinary, _ = self.launch(script, cwd, env, envelope(provider, "echo safe"))
                self.assertIn("scan incomplete", reason(ordinary))
                for mode in ("block", "warn"):
                    response, result = self.launch(script, cwd, env, envelope(provider), mode)
                    report = self.diagnostics(response, result, provider)
                    self.assertEqual(report["repository"]["records"][0]["size"], 8388609)

    def test_helper_failures_preserve_report_and_common_needs_human_cli(self):
        for provider in PROVIDERS:
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as directory:
                script, cwd, env = self.setup_fixture(directory, provider)
                audit = script.parent / "helpers/audit.py"
                audit_source = audit.read_bytes()
                audit.unlink()
                (script.parent / "helpers/tool_guard_policy.py").unlink()
                for mode in ("block", "warn"):
                    ordinary, _ = self.launch(script, cwd, env, envelope(provider, "echo safe"), mode)
                    self.assertIn("audit helper unavailable", reason(ordinary))
                    response, result = self.launch(script, cwd, env, envelope(provider), mode)
                    report = self.diagnostics(response, result, provider)
                    states = {item["asset"]: item["state"] for item in report["assets"]["records"]}
                    self.assertEqual(states["helpers/audit.py"], "missing")
                    self.assertEqual(states["helpers/tool_guard_policy.py"], "missing")
                # Guardian retains its independent fail-closed missing-policy path.
                audit.write_bytes(audit_source)
                guardian, _ = self.launch(script.with_name("tool-guard.py"), cwd, env, envelope(provider), "warn")
                self.assertIn("internal error", reason(guardian))
                audit.write_text("raise RuntimeError('corrupt audit')\n")
                (script.parent / "helpers/tool_guard_policy.py").write_text("raise RuntimeError('corrupt policy')\n")
                ordinary, _ = self.launch(script, cwd, env, envelope(provider, "echo safe"), "warn")
                self.assertIn("audit helper unavailable", reason(ordinary))
                response, result = self.launch(script, cwd, env, envelope(provider), "warn")
                report = self.diagnostics(response, result, provider)
                states = {item["asset"]: item["state"] for item in report["assets"]["records"]}
                self.assertEqual(states["helpers/audit.py"], "drift")
                self.assertEqual(states["helpers/tool_guard_policy.py"], "drift")
                (script.parent / "helpers/common.py").write_text("raise RuntimeError('broken common')\n")
                broken = subprocess.run([sys.executable, "-I", "-S", "-B", str(script)], cwd=cwd, env=env, input=json.dumps(envelope(provider)).encode(), capture_output=True, timeout=5)
                self.assertNotEqual(broken.returncode, 0)
                cli = subprocess.run([sys.executable, "-I", "-S", "-B", str(script.with_name("hooks-diagnostics.py"))], cwd=cwd, env=env, capture_output=True, timeout=5)
                self.assertEqual(cli.returncode, 0, cli.stderr)
                self.assertEqual(json.loads(cli.stdout)["security"]["outcome"], "not_scanned")

    def test_git_audit_unsafe_candidate_failure_does_not_block_recovery(self):
        for provider in PROVIDERS:
            for fault in ("git", "audit", "scan_log", "unsafe"):
                with self.subTest(provider=provider, fault=fault), tempfile.TemporaryDirectory() as directory:
                    script, cwd, env = self.setup_fixture(directory, provider)
                    (cwd / "safe.txt").write_text("safe")
                    if fault == "git":
                        env["PATH"] = str(Path(directory) / "no-executables")
                    elif fault in {"audit", "scan_log"}:
                        blocked = Path(directory) / "blocked-log"
                        blocked.write_text("not a directory")
                        env["AUDIT_LOG" if fault == "audit" else "SECRETS_LOG_DIR"] = str(blocked / "secrets")
                    else:
                        (cwd / "unsafe.txt").symlink_to(Path(directory) / "outside")
                    ordinary, _ = self.launch(script, cwd, env, envelope(provider, "echo safe"))
                    self.assertIn("scan incomplete", reason(ordinary))
                    for mode in ("block", "warn"):
                        response, result = self.launch(script, cwd, env, envelope(provider), mode)
                        report = self.diagnostics(response, result, provider)
                        self.assertEqual(report["audit"]["outcome"], "not_attempted")

    def test_marker_has_no_executable_or_import_authority(self):
        for provider in PROVIDERS:
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as directory:
                script, cwd, env = self.setup_fixture(directory, provider)
                sentinel = Path(directory) / "executed"
                hostile = "from pathlib import Path\nPath(" + repr(str(sentinel)) + ").write_text('bad')\nraise RuntimeError('hostile import')\n"
                for name in ("json.py", "sitecustomize.py", "os.py"):
                    (cwd / name).write_text(hostile)
                marker = cwd / "hooks-diagnostics-v1"
                marker.write_text("#!/bin/sh\nprintf bad > " + str(sentinel) + "\n")
                marker.chmod(0o755)
                git = cwd / "git"
                git.write_bytes(marker.read_bytes())
                git.chmod(0o755)
                env.update(PATH=str(cwd), PYTHONPATH=str(cwd), BASH_ENV=str(cwd / "startup"))
                (cwd / "startup").write_bytes(marker.read_bytes())
                token = "ghp_" + "A" * 36
                (cwd / (token + ".txt")).write_bytes(b"candidate body\0" + token.encode())
                payload = envelope(provider)
                arbitrary = Path(directory) / "payload-only"
                arbitrary.mkdir()
                (arbitrary / "must-not-be-inventoried").touch()
                payload["cwd"] = str(arbitrary)
                response, result = self.launch(script, cwd, env, payload)
                report = self.diagnostics(response, result, provider)
                self.assertEqual(report["repository"]["repository_location"], "unverified")
                self.assertNotIn(token.encode(), result.stdout)
                self.assertNotIn(b"candidate body", result.stdout)
                self.assertNotIn(b"must-not-be-inventoried", result.stdout)
                self.assertFalse(sentinel.exists())

    def test_spoofed_extended_profiles_follow_ordinary_scan(self):
        commands = (" hooks-diagnostics-v1", "hooks-diagnostics-v1 ", "./hooks-diagnostics-v1", "'hooks-diagnostics-v1'", "hooks-diagnostics-v1 --doctor", "hooks-diagnostics-v1; echo unsafe", "$(hooks-diagnostics-v1)", "env hooks-diagnostics-v1", "hooks-diagnostics-v１")
        for provider in PROVIDERS:
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as directory:
                script, cwd, env = self.setup_fixture(directory, provider)
                env["PATH"] = str(Path(directory) / "no-executables")
                payloads = [envelope(provider, value) for value in commands]
                for extra in ({"workdir": "."}, {"shell": "/bin/sh"}, {"env": {}}, {"sandbox_permissions": "require_escalated"}, {"unknown": False}):
                    payloads.append(envelope(provider, **extra))
                if provider == "codex":
                    for extra in ({"login": True}, {"max_output_tokens": True}, {"yield_time_ms": -1}, {"yield_time_ms": 2147483648}):
                        payloads.append(envelope(provider, **extra))
                    missing_login = envelope(provider)
                    del missing_login["tool_input"]["login"]
                    payloads.append(missing_login)
                wrong_event = envelope(provider)
                wrong_event["hook_event_name"] = "PreToolUse" if provider != "codex" else "Stop"
                payloads.append(wrong_event)
                wrong_tool = envelope(provider)
                wrong_tool["toolName" if provider == "copilot" else "tool_name"] = "Bash"
                payloads.append(wrong_tool)
                malformed_tool = envelope(provider)
                malformed_tool["toolName" if provider == "copilot" else "tool_name"] = []
                payloads.append(malformed_tool)
                unknown_outer = envelope(provider)
                unknown_outer["unknown"] = "anything"
                payloads.append(unknown_outer)
                for payload in payloads:
                    response, _ = self.launch(script, cwd, env, payload)
                    self.assertIn("git_unavailable", reason(response), payload)
                    self.assertNotIn(PREFIX, reason(response))
                if provider == "codex":
                    for tool in ("exec_command", "functions.exec_command"):
                        payload = envelope(provider, max_output_tokens=0, yield_time_ms=2147483647)
                        payload["tool_name"] = tool
                        response, result = self.launch(script, cwd, env, payload)
                        self.diagnostics(response, result, provider)
                elif provider == "copilot":
                    payload = envelope(provider)
                    del payload["hook_event_name"]
                    response, result = self.launch(script, cwd, env, payload)
                    self.diagnostics(response, result, provider)

    def test_guardian_still_inspects_marker_and_appended_operations(self):
        dangerous = "".join(map(chr, (103, 105, 116, 32, 112, 117, 115, 104, 32, 45, 45, 102, 111, 114, 99, 101, 32, 111, 114, 105, 103, 105, 110, 32, 109, 97, 105, 110)))
        for provider in PROVIDERS:
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as directory:
                script, cwd, env = self.setup_fixture(directory, provider)
                response, _ = self.launch(script.with_name("tool-guard.py"), cwd, env, envelope(provider, "hooks-diagnostics-v1; " + dangerous))
                self.assertIn("Tool Guardian blocked", reason(response))
                self.assertNotIn(PREFIX, reason(response))

    def test_native_envelope_metadata_is_bounded_and_inert(self):
        for provider in PROVIDERS:
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as directory:
                script, cwd, env = self.setup_fixture(directory, provider)
                payload = envelope(provider)
                payload["cwd"] = str(cwd)
                if provider == "copilot":
                    payload.update(sessionId="test-session", timestamp=1791936000000)
                else:
                    payload.update(session_id="test-session", timestamp="2026-10-14T00:00:00Z", transcript_path="/unopened/transcript", tool_use_id="test-call")
                response, result = self.launch(script, cwd, env, payload)
                report = self.diagnostics(response, result, provider)
                self.assertEqual(report["repository"]["repository_location"], "process_cwd")
                env["PATH"] = str(Path(directory) / "no-executables")
                for key, value in (("cwd", "x" * 8193), ("timestamp", True)):
                    response, _ = self.launch(script, cwd, env, {**payload, key: value})
                    self.assertIn("git_unavailable", reason(response))

    def test_native_wrapper_bounds_and_hostile_label_redaction(self):
        for provider in PROVIDERS:
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as directory:
                script, cwd, env = self.setup_fixture(directory, provider)
                for index in range(300):
                    (cwd / (str(index) + "\\\"" * 50 + "é" * 30)).write_bytes(b"x" * (index + 1))
                token = "github_pat_" + "A" * 25
                (cwd / ("x" * 170 + token)).write_bytes(b"x" * 900)
                response, result = self.launch(script, cwd, env, envelope(provider))
                report = self.diagnostics(response, result, provider)
                self.assertTrue(report["response_truncated"])
                self.assertEqual(report["repository"]["records"][0]["size"], 900)
                self.assertGreater(report["repository"]["records_omitted"], 0)
                self.assertNotIn(token.encode(), result.stdout)

    def test_repair_retry_requires_real_scan(self):
        for provider in PROVIDERS:
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as directory:
                script, cwd, env = self.setup_fixture(directory, provider)
                candidate = cwd / "artifact.txt"
                candidate.write_bytes(b"x" * 8388609)
                response, _ = self.launch(script, cwd, env, envelope(provider, "echo safe"))
                self.assertIn("scan incomplete", reason(response))
                response, result = self.launch(script, cwd, env, envelope(provider))
                self.diagnostics(response, result, provider)
                candidate.write_text("safe repaired artifact")
                response, _ = self.launch(script, cwd, env, envelope(provider, "echo safe"))
                self.assertEqual(response, {})
                candidate.write_text("ghp_" + "A" * 36)
                response, _ = self.launch(script, cwd, env, envelope(provider, "echo safe"))
                self.assertIn("potential secrets detected", reason(response))
                rows = [json.loads(line) for line in (Path(env["SECRETS_LOG_DIR"]) / "scan.log").read_text().splitlines()]
                self.assertEqual(rows[-1]["status"], "findings")

if __name__ == "__main__":
    unittest.main()
