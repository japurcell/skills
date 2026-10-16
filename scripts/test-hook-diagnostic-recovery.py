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

from hook_test_support import hook_entrypoint, raw_tool_envelope

ROOT = Path(__file__).resolve().parent.parent
PROVIDERS = ("codex", "copilot", "gemini")
PREFIX = "scan-secrets diagnostics (request not executed):"

def entry(provider):
    return hook_entrypoint(Path(), provider, "scan-secrets.py")

def envelope(provider, command="hooks-diagnostics-v1", **extra):
    tool = {"copilot": "bash", "codex": "exec_command", "gemini": "run_shell_command"}[provider]
    value = {"cmd": command, "login": False} if provider == "codex" else {"command": command}
    return raw_tool_envelope(provider, tool, {**value, **extra})


def registered_handlers(config, provider):
    event = {"codex": "PreToolUse", "copilot": "preToolUse", "gemini": "BeforeTool"}[provider]
    groups = config["hooks"][event]
    return groups if provider == "copilot" else [handler for group in groups for handler in group["hooks"]]


def registered_handler(config, provider, filename):
    return next(item for item in registered_handlers(config, provider)
                if filename in item.get("command", item.get("bash", "")))

def reason(response):
    return response.get("permissionDecisionReason", response.get("reason", response.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")))

class RecoveryTests(unittest.TestCase):
    def installed_launch(self, installer):
        with tempfile.TemporaryDirectory(prefix="trusted launch '") as directory:
            base = Path(directory).resolve()
            home, cwd = base / "home", base / "repository"
            home.mkdir()
            cwd.mkdir()
            env = {key: value for key, value in os.environ.items() if key not in {"PYTHONPATH", "PYTHONHOME", "SKIP_SECRETS_SCAN", "SECRETS_ALLOWLIST"}}
            env.update(HOME=str(home), USERPROFILE=str(home), CODEX_HOME=str(home / "custom-codex"), OBSERVABILITY_TESTING="1", OBSERVABILITY_LOG_PATH=str(base / "audit/log.jsonl"), AUDIT_LOG=str(base / "audit/audit.log"), AUDIT_LOCK=str(base / "audit/audit.lock"), SECRETS_LOG_DIR=str(base / "secrets"))
            (base / "guardian").mkdir()
            interpreter = base / "trusted python & '" / "python3"
            interpreter.parent.mkdir()
            interpreter.symlink_to(sys.executable)
            env["PATH"] = str(interpreter.parent) + os.pathsep + env["PATH"]
            subprocess.run(["git", "init", "-q", str(cwd)], check=True, capture_output=True)
            command = ["bash", str(ROOT / "scripts/install.sh")] if installer == "bash" else ["pwsh", "-NoProfile", "-File", str(ROOT / "scripts/install.ps1")]
            installed = subprocess.run(command, env=env, capture_output=True, timeout=90)
            self.assertEqual(installed.returncode, 0, installed.stderr)
            paths = {"codex": ".codex/hooks.json", "copilot": ".copilot/hooks/hooks.json", "gemini": ".gemini/settings.json"}
            configs = {provider: json.loads((home / path).read_bytes()) for provider, path in paths.items()}
            for provider in PROVIDERS:
                for helper in ("scan_types", "scan_reporting", "scan_allowlist", "scan_stream",
                               "scan_git", "scan_native_file", "scan_audit", "scan_engine"):
                    relative = entry(provider).parent / "helpers" / (helper + ".py")
                    installed_helper = home / relative
                    self.assertEqual(installed_helper.read_bytes(), (ROOT / relative).read_bytes(),
                                     (installer, provider, helper))
                    if os.name == "posix":
                        self.assertTrue(os.access(installed_helper, os.X_OK), (installer, provider, helper))
            sentinel = base / "executed"
            hostile = base / "hostile"
            hostile.mkdir()
            (hostile / "sitecustomize.py").write_text("from pathlib import Path\nPath(" + repr(str(sentinel)) + ").write_text('startup')\n")
            for executable in ("python", "python3", "py"):
                target = hostile / executable
                target.write_text("#!/bin/sh\nprintf replaced > \"" + str(sentinel) + "\"\nexit 97\n")
                target.chmod(0o755)
            for attack in ("startup", "path"):
                attack_env = {**env, "PYTHONPATH": str(hostile)}
                if attack == "path":
                    attack_env["PATH"] = str(hostile)
                for provider, config in configs.items():
                    env["TOOL_GUARD_LOG_DIR"] = str(base / "guardian" / (provider if provider == "gemini" else provider + ".log"))
                    for filename in ("scan-secrets.py", "tool-guard.py"):
                        with self.subTest(installer=installer, attack=attack, provider=provider, hook=filename):
                            sentinel.unlink(missing_ok=True)
                            handler = registered_handler(config, provider, filename)
                            registered = handler["bash" if provider == "copilot" else "command"]
                            result = subprocess.run(["/bin/sh", "-c", registered], cwd=cwd, env={**attack_env, **handler.get("env", {})}, input=json.dumps(envelope(provider)).encode(), capture_output=True, timeout=12)
                            self.assertFalse(sentinel.exists(), (registered, attack))
                            self.assertEqual(result.returncode, 0, result.stderr)
                            response = json.loads(result.stdout)
                            if filename == "scan-secrets.py":
                                self.diagnostics(response, result, provider)
                            else:
                                self.assertNotIn(PREFIX, reason(response))
                            if provider == "copilot" and shutil.which("pwsh"):
                                powershell = subprocess.run([shutil.which("pwsh"), "-NoProfile", "-NonInteractive", "-Command", handler["powershell"]], cwd=cwd, env={**attack_env, **handler.get("env", {})}, input=json.dumps(envelope(provider)).encode(), capture_output=True, timeout=12)
                                self.assertEqual(powershell.returncode, 0, powershell.stderr)
                                self.assertFalse(sentinel.exists())
                                if filename == "scan-secrets.py":
                                    self.diagnostics(json.loads(powershell.stdout), powershell, provider)
                            ordinary = envelope(provider, "echo safe")
                            if filename == "tool-guard.py":
                                ordinary = envelope(provider, "git " + "push --force origin main")
                            checked = subprocess.run(["/bin/sh", "-c", registered], cwd=cwd, env={**env, **handler.get("env", {})}, input=json.dumps(ordinary).encode(), capture_output=True, timeout=12)
                            self.assertEqual(checked.returncode, 0, checked.stderr)
                            checked_response = json.loads(checked.stdout)
                            if filename == "tool-guard.py":
                                self.assertIn("Tool Guardian blocked", reason(checked_response))
                            else:
                                self.assertEqual(checked_response, {})
            self.assertTrue(any((base / "guardian").iterdir()))
            for provider in PROVIDERS:
                guard_log = base / "guardian" / ("gemini/guard.log" if provider == "gemini" else provider + ".log")
                self.assertIn('"rule_id":"force_push_protected_branch"', guard_log.read_text())
                self.assertIn('"audit_outcome":"written"', guard_log.read_text())
            self.assertTrue((base / "secrets/scan.log").is_file())
            self.assertTrue(all(json.loads(line)["status"] == "clean" for line in (base / "secrets/scan.log").read_text().splitlines()))
            candidate = cwd / "credential.txt"
            candidate.write_text("ghp_" + "A" * 36)
            for provider, config in configs.items():
                handler = registered_handler(config, provider, "scan-secrets.py")
                result = subprocess.run(["/bin/sh", "-c", handler["bash" if provider == "copilot" else "command"]], cwd=cwd, env={**env, **handler.get("env", {})}, input=json.dumps(envelope(provider, "echo safe")).encode(), capture_output=True, timeout=12)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("potential secrets detected", reason(json.loads(result.stdout)))
            candidate.unlink()
            for provider in PROVIDERS:
                cli = home / entry(provider).with_name("hooks-diagnostics.py")
                doctor = subprocess.run([sys.executable, "-I", "-S", "-B", str(cli), "--doctor"], cwd=cwd, env=env, capture_output=True, timeout=5)
                self.assertEqual(doctor.returncode, 0, doctor.stderr)
                registrations = json.loads(doctor.stdout)["registrations"]
                self.assertEqual(registrations["health"], "observed", registrations)
                config = configs[provider]
                handler = registered_handler(config, provider, "scan-secrets.py")
                key = "bash" if provider == "copilot" else "command"
                original = handler[key]
                handler[key] += " --doctor"
                (home / paths[provider]).write_text(json.dumps(config))
                rejected = subprocess.run([str(interpreter), "-I", "-S", "-B", str(cli), "--doctor"], cwd=cwd, env=env, capture_output=True, timeout=5)
                registrations = json.loads(rejected.stdout)["registrations"]
                self.assertGreater(registrations["missing"], 0)
                self.assertGreater(registrations["unowned"], 0)
                handler[key] = original
                (home / paths[provider]).write_text(json.dumps(config))
            repeated = subprocess.run(command, env=env, capture_output=True, timeout=90)
            self.assertEqual(repeated.returncode, 0, repeated.stderr)
            for provider, config in configs.items():
                self.assertEqual(json.loads((home / paths[provider]).read_bytes()), config)
            refused_home = base / "unsupported%home"
            refused_home.mkdir()
            (refused_home / "preserved").write_text("unchanged")
            refused_env = {**env, "HOME": str(refused_home), "USERPROFILE": str(refused_home), "CODEX_HOME": str(refused_home / "custom-codex")}
            refused_env.update(XDG_CACHE_HOME=str(base / "shell-cache"), XDG_DATA_HOME=str(base / "shell-data"), XDG_CONFIG_HOME=str(base / "shell-config"), PSModuleAnalysisCachePath=str(base / "shell-module-cache"))
            if installer != "bash":
                # PowerShell initializes its own cache before executing a script.
                subprocess.run(["pwsh", "-NoProfile", "-Command", "exit 0"], env=refused_env, check=True, capture_output=True, timeout=10)
            def fingerprint():
                return {str(path.relative_to(refused_home)): (path.stat().st_mode, path.read_bytes() if path.is_file() else None) for path in refused_home.rglob("*")}
            before = fingerprint()
            refused = subprocess.run(command, env=refused_env, capture_output=True, timeout=90)
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn(b"unsupported Windows shell characters", refused.stderr)
            self.assertEqual(fingerprint(), before)

    def test_bash_installed_commands_resist_startup_and_path_injection(self):
        self.installed_launch("bash")

    @unittest.skipUnless(shutil.which("pwsh"), "PowerShell unavailable")
    def test_powershell_installed_commands_resist_startup_and_path_injection(self):
        self.installed_launch("powershell")

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
        result = subprocess.run([sys.executable, "-I", "-S", "-B", str(script)], input=json.dumps(payload).encode(), cwd=cwd, env={**env, "SCAN_MODE": mode, "GUARD_MODE": mode}, capture_output=True, timeout=12)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout), result

    def assert_native_enforcement(self, response, provider, expected):
        if provider == "gemini":
            decision = response.get("decision", "allow")
        elif provider == "copilot":
            decision = response.get("permissionDecision", "allow")
        else:
            decision = response.get("hookSpecificOutput", {}).get("permissionDecision", "allow")
        self.assertEqual(decision, expected, response)
        if expected == "allow":
            self.assertIsNot(response.get("continue"), False, response)
            self.assertNotIn(response.get("decision"), ("deny", "block"), response)
            self.assertNotIn(response.get("permissionDecision"), ("deny", "ask"), response)
            self.assertNotIn(response.get("hookSpecificOutput", {}).get("permissionDecision"), ("deny", "ask"), response)

    def test_launch_honors_scan_mode(self):
        for provider in PROVIDERS:
            for mode, inherited, enforcement in (("block", "warn", "deny"), ("warn", "block", "allow")):
                with self.subTest(provider=provider, mode=mode), tempfile.TemporaryDirectory() as directory:
                    script, cwd, env = self.setup_fixture(directory, provider)
                    env.update(SCAN_MODE=inherited, GUARD_MODE=inherited)
                    (cwd / "credential.txt").write_text("ghp_" + "FAKE" * 9)
                    audit = Path(env["SECRETS_LOG_DIR"]) / "scan.log"
                    self.assertFalse(audit.exists())
                    response, _ = self.launch(script, cwd, env, envelope(provider, "echo safe"), mode)
                    self.assert_native_enforcement(response, provider, enforcement)
                    self.assertIn("potential secrets detected", reason(response) + response.get("systemMessage", ""))
                    rows = [json.loads(line) for line in audit.read_text().splitlines()]
                    self.assertEqual(len(rows), 1, rows)
                    self.assertEqual(rows[0]["mode"], mode)
                    self.assertEqual(rows[0]["enforcement"], enforcement)
                    self.assertEqual(rows[0]["security_outcome"], "findings")
                    self.assertEqual(rows[0]["audit_outcome"], "written")
                    self.assertEqual([finding["pattern"] for finding in rows[0]["findings"]], ["github_classic_pat"])

    def test_launch_honors_guard_mode(self):
        # This is hook input only. The protected operation is never executed.
        command = "git push" + " --force origin main"
        for provider in PROVIDERS:
            for mode, inherited, enforcement in (("block", "warn", "deny"), ("warn", "block", "allow")):
                with self.subTest(provider=provider, mode=mode), tempfile.TemporaryDirectory() as directory:
                    script, cwd, env = self.setup_fixture(directory, provider)
                    for key in ("SKIP_TOOL_GUARD", "TOOL_GUARD_ALLOWLIST"):
                        env.pop(key, None)
                    log_dir = Path(directory).resolve() / "guardian"
                    log_dir.mkdir()
                    audit = log_dir / "guard.log"
                    env.update(SCAN_MODE=inherited, GUARD_MODE=inherited,
                               TOOL_GUARD_LOG_DIR=str(log_dir if provider == "gemini" else audit))
                    self.assertFalse(audit.exists())
                    response, _ = self.launch(script.with_name("tool-guard.py"), cwd, env, envelope(provider, command), mode)
                    self.assert_native_enforcement(response, provider, enforcement)
                    self.assertIn("force_push_protected_branch", reason(response) + response.get("systemMessage", ""))
                    rows = [json.loads(line[line.find("{"):]) for line in audit.read_text().splitlines()]
                    self.assertEqual(len(rows), 1, rows)
                    self.assertEqual(rows[0]["mode"], mode)
                    self.assertEqual(rows[0]["enforcement"], enforcement)
                    self.assertEqual(rows[0]["security_outcome"], "findings")
                    self.assertEqual(rows[0]["audit_outcome"], "written")
                    self.assertEqual([threat["rule_id"] for threat in rows[0]["threats"]], ["force_push_protected_branch"])

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

    @unittest.skipUnless(hasattr(os, "O_NOFOLLOW") and os.scandir in os.supports_fd, "descriptor-relative no-follow proof requires supported OS")
    def test_recovery_redacts_fake_credential_filenames(self):
        for provider in PROVIDERS:
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as directory:
                script, cwd, env = self.setup_fixture(directory, provider)
                for size, label in enumerate(("sk-FAKE-not-a-real-key", "api-key=FAKE", "ｓｋ－ＦＡＫＥ", "ａｐｉ＿ｋｅｙ＝ＦＡＫＥ"), 1):
                    (cwd / label).write_bytes(b"x" * size)
                response, result = self.launch(script, cwd, env, envelope(provider))
                report = self.diagnostics(response, result, provider)
                self.assertEqual({record["size"]: record["label"] for record in report["repository"]["records"]},
                                 {1: "[REDACTED]", 2: "[REDACTED]", 3: "[REDACTED]", 4: "[REDACTED]"})

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
                    self.assert_native_enforcement(ordinary, provider, "deny")
                    response, result = self.launch(script, cwd, env, envelope(provider), mode)
                    report = self.diagnostics(response, result, provider)
                    states = {item["asset"]: item["state"] for item in report["assets"]["records"]}
                    self.assertEqual(states["helpers/audit.py"], "missing")
                    self.assertEqual(states["helpers/tool_guard_policy.py"], "missing")
                # Guardian retains its independent fail-closed missing-policy path.
                audit.write_bytes(audit_source)
                for mode in ("block", "warn"):
                    guardian, _ = self.launch(script.with_name("tool-guard.py"), cwd, env, envelope(provider), mode)
                    self.assertIn("internal error", reason(guardian))
                    self.assert_native_enforcement(guardian, provider, "deny")
                audit.write_text("raise RuntimeError('corrupt audit')\n")
                (script.parent / "helpers/tool_guard_policy.py").write_text("raise RuntimeError('corrupt policy')\n")
                for mode in ("block", "warn"):
                    ordinary, _ = self.launch(script, cwd, env, envelope(provider, "echo safe"), mode)
                    self.assertIn("audit helper unavailable", reason(ordinary))
                    self.assert_native_enforcement(ordinary, provider, "deny")
                    response, result = self.launch(script, cwd, env, envelope(provider), mode)
                    report = self.diagnostics(response, result, provider)
                    states = {item["asset"]: item["state"] for item in report["assets"]["records"]}
                    self.assertEqual(states["helpers/audit.py"], "drift")
                    self.assertEqual(states["helpers/tool_guard_policy.py"], "drift")
                audit.write_bytes(audit_source)
                for mode in ("block", "warn"):
                    guardian, _ = self.launch(script.with_name("tool-guard.py"), cwd, env, envelope(provider), mode)
                    self.assertIn("internal error", reason(guardian))
                    self.assert_native_enforcement(guardian, provider, "deny")
                (script.parent / "helpers/common.py").write_text("raise RuntimeError('broken common')\n")
                broken = subprocess.run([sys.executable, "-I", "-S", "-B", str(script)], cwd=cwd, env=env, input=json.dumps(envelope(provider)).encode(), capture_output=True, timeout=5)
                self.assertNotEqual(broken.returncode, 0)
                cli = subprocess.run([sys.executable, "-I", "-S", "-B", str(script.with_name("hooks-diagnostics.py"))], cwd=cwd, env=env, capture_output=True, timeout=5)
                self.assertEqual(cli.returncode, 0, cli.stderr)
                self.assertEqual(json.loads(cli.stdout)["security"]["outcome"], "not_scanned")

    def test_scanner_runtime_helper_closure_fails_closed_and_preserves_recovery(self):
        helpers = ("scan_types", "scan_reporting", "scan_allowlist", "scan_stream",
                   "scan_git", "scan_native_file", "scan_audit", "scan_engine")
        for provider in PROVIDERS:
            with tempfile.TemporaryDirectory() as directory:
                script, cwd, env = self.setup_fixture(directory, provider)
                for helper in helpers:
                    path = script.parent / "helpers" / (helper + ".py")
                    original = path.read_bytes()
                    for state in ("missing", "drift"):
                        if state == "missing":
                            path.unlink()
                        else:
                            path.write_text("raise RuntimeError('fixture corrupt helper')\n")
                        for mode in ("block", "warn"):
                            with self.subTest(provider=provider, helper=helper, state=state, mode=mode):
                                ordinary, result = self.launch(script, cwd, env, envelope(provider, "echo safe"), mode)
                                self.assertEqual(result.returncode, 0)
                                self.assertIn("scanner helper unavailable", reason(ordinary))
                                self.assert_native_enforcement(ordinary, provider, "deny")
                                response, result = self.launch(script, cwd, env, envelope(provider), mode)
                                report = self.diagnostics(response, result, provider)
                                states = {item["asset"]: item["state"] for item in report["assets"]["records"]}
                                self.assertEqual(states["helpers/" + helper + ".py"], state)
                        path.write_bytes(original)

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

    def test_codex_documented_metadata_keeps_exact_diagnostic_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            script, cwd, env = self.setup_fixture(directory, "codex")
            env["PATH"] = str(Path(directory) / "no-executables")
            metadata = {"model": "gpt-6", "permission_mode": "default", "transcript_path": None, "turn_id": "turn-123"}
            for mode in ("default", "acceptEdits", "plan", "dontAsk", "bypassPermissions"):
                payload = {**envelope("codex"), **metadata, "permission_mode": mode}
                response, result = self.launch(script, cwd, env, payload)
                self.diagnostics(response, result, "codex")
            for command, expected in (("echo safe", "allow"), ("git push" + " --force origin main", "deny")):
                payload = {**envelope("codex", command), **metadata}
                response, _ = self.launch(script.with_name("tool-guard.py"), cwd, env, payload)
                self.assert_native_enforcement(response, "codex", expected)
                if expected == "deny":
                    self.assertIn("Tool Guardian blocked", reason(response))
            for invalid in ({"model": []}, {"turn_id": False}, {"permission_mode": "unknown"}, {"transcript_path": 1}, {"model": "x" * 257}):
                payload = {**envelope("codex"), **metadata, **invalid}
                response, _ = self.launch(script, cwd, env, payload)
                self.assertIn("git_unavailable", reason(response))
                self.assertNotIn(PREFIX, reason(response))
            for extra in ({"cmd": "hooks-diagnostics-v1 --doctor"}, {"login": True}, {"unknown": False}, {"max_output_tokens": True}):
                payload = {**envelope("codex", **extra), **metadata}
                response, _ = self.launch(script, cwd, env, payload)
                self.assertIn("git_unavailable", reason(response))
                self.assertNotIn(PREFIX, reason(response))

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
