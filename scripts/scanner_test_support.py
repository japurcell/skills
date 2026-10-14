"""Shared fixtures for public generated-scanner entrypoint tests."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from hook_test_support import hook_entrypoint, raw_tool_envelope

ROOT = Path(__file__).resolve().parent.parent
HOOKS = {provider: hook_entrypoint(ROOT, provider, "scan-secrets.py")
         for provider in ("copilot", "gemini", "codex")}
PROVIDERS = tuple(HOOKS)
FAKE_TOKEN = "gh" + "p_" + "FAKE" * 9


def scanner_tool_payload(provider: str, repo: Path, *, session_id: str | None = None) -> dict:
    """Build the scanner's existing tool-call fixture, retaining provider fields."""
    tool = {"copilot": "bash", "gemini": "run_shell_command", "codex": "exec_command"}[provider]
    payload = raw_tool_envelope(provider, tool, {"command": "git status"})
    if provider != "copilot":
        payload["cwd"] = str(repo)
    if session_id is not None:
        payload["sessionId" if provider == "copilot" else "session_id"] = session_id
    return payload


def install_fake_git(root: Path, env: dict[str, str], body: str, *,
                     real_git: str, directory: str = "bin") -> Path:
    """Install a visible per-case Python program, preserving its I/O policy."""
    fake_bin = root / directory
    fake_bin.mkdir()
    wrapper = fake_bin / "git"
    wrapper.write_text(f"#!{sys.executable}\n" + body, encoding="utf-8")
    wrapper.chmod(0o755)
    env.update(REAL_GIT=real_git, PATH=str(fake_bin) + os.pathsep + env["PATH"])
    return wrapper


class ScannerFixtureMixin:
    """Disposable Git fixture and scanner assertions; deliberately no test methods."""

    def install_fake_git(self, body: str, *, directory: str = "bin") -> Path:
        return install_fake_git(self.root, self.env, body,
                                real_git=str(self.git_path), directory=directory)

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="scan-merge-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        home = self.root / "home"
        home.mkdir()
        self.git_path = shutil.which("git")
        self.assertIsNotNone(self.git_path, "Git is required")
        self.env = {
            key: value for key, value in os.environ.items()
            if not key.startswith("GIT_")
            and key not in {"SKIP_SECRETS_SCAN", "SECRETS_ALLOWLIST"}
        }
        self.env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                         "HOME": str(home), "USERPROFILE": str(home),
                         "CODEX_HOME": str(home / ".codex"),
                         "XDG_CONFIG_HOME": str(home / ".config")})
        self.git("init", "-q", "-b", "main")

    def git(self, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [str(self.git_path), "-C", str(self.repo),
             "-c", "user.name=Scanner Merge Test",
             "-c", "user.email=scanner-merge@example.invalid",
             "-c", "commit.gpgsign=false", "-c", "core.hooksPath=" + str(self.root / "no-hooks"),
             *args],
            env=self.env, text=True, capture_output=True, timeout=10,
        )
        self.assertEqual(result.returncode, expected, f"Git fixture failed: {args!r}: {result.stderr}")
        return result

    def scan(self, provider: str, mode: str = "block", scope: str = "diff",
             *, stop: bool = False) -> tuple[dict, dict]:
        log_dir = self.root / f"logs-{provider}-{mode}-{scope}"
        log_dir.mkdir(exist_ok=True)
        env = {**self.env, "SCAN_MODE": mode, "SCAN_SCOPE": scope,
               "SECRETS_LOG_DIR": str(log_dir), "AUDIT_LOG": str(log_dir / "audit.log"),
               "OBSERVABILITY_LOG_PATH": str(log_dir / "observability.jsonl"),
               "OBSERVABILITY_TESTING": "1", "TMPDIR": str(self.root)}
        payload = scanner_tool_payload(provider, self.repo, session_id="merge-test")
        if stop:
            payload["hook_event_name"] = {
                "copilot": "agentStop", "gemini": "SessionEnd", "codex": "Stop",
            }[provider]
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-B", str(HOOKS[provider])],
            cwd=self.repo, env=env, input=json.dumps(payload), text=True, capture_output=True, timeout=12,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        response = json.loads(result.stdout)
        log_text = (log_dir / "scan.log").read_text(encoding="utf-8")
        all_output = (result.stdout + result.stderr).encode("utf-8") + b"".join(
            path.read_bytes() for path in log_dir.rglob("*") if path.is_file()
        )
        self.assertNotIn(FAKE_TOKEN.encode("ascii"), all_output,
                         "fake credential leaked through hook output or logs")
        rows = [json.loads(line) for line in log_text.splitlines()]
        self.assertTrue(rows, "scanner must record an outcome")
        return response, rows[-1]

    def assert_outcome(self, provider: str, mode: str, scope: str, status: str,
                       finding_path: str | None = None, cause: str | None = None) -> None:
        response, record = self.scan(provider, mode, scope)
        self.assertEqual(record["status"], status, record)
        self.assertEqual((record["provider"], record["mode"], record["scope"]),
                         (provider, mode, scope))
        if status == "clean":
            expected = {}
        else:
            detail = ("potential secrets detected." if status == "findings" else
                      "scan incomplete; potential secrets could not be checked.")
            if status == "incomplete":
                diagnostic = record["diagnostic"]
                self.assertEqual(record["action"], "tool scan")
                if cause is not None:
                    self.assertEqual(diagnostic["cause"], cause)
                self.assertIn(diagnostic["cause"], record["note"])
                self.assertIn(diagnostic["operation"], record["note"])
                self.assertNotIn(str(self.repo), json.dumps(response) + json.dumps(record))
                if record["security_outcome"] == "findings":
                    detail = "potential secrets detected; scan incomplete."
                detail += " " + record["note"]
            self.assertRegex(record["build"], r"^[0-9a-f]{16}$")
            detail += (f" security_outcome={record['security_outcome']}; audit_outcome=written; "
                       f"enforcement={'allow' if mode == 'warn' else 'deny'}; build={record['build']}; "
                       f"profile=pending_snapshots_v1; route=pending_scan; cause={record['cause']}.")
            reason = f"scan-secrets blocked: tool scan; {detail}"
            if mode == "warn":
                expected = {"systemMessage": f"scan-secrets warning: tool scan; {detail}"}
            elif provider == "copilot":
                expected = {"continue": True, "permissionDecision": "deny",
                            "permissionDecisionReason": reason,
                            "hookSpecificOutput": {"permissionDecision": "deny",
                                                   "permissionDecisionReason": reason}}
            elif provider == "gemini":
                expected = {"decision": "deny", "reason": reason}
            else:
                expected = {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                                   "permissionDecision": "deny",
                                                   "permissionDecisionReason": reason}}
        self.assertEqual(response, expected)
        if finding_path is not None:
            self.assertTrue(any(finding["pattern"] == "github_classic_pat"
                                and finding["severity"] == "high"
                                and finding["path"] == finding_path
                                and finding["line"] == 1
                                and finding["redactedMatch"] == "ghp_...FAKE"
                                for finding in record["findings"]), record)
