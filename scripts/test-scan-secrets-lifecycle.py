#!/usr/bin/env python3
"""Generated inactive status adapters through their public process boundary."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = {"codex": ".codex/hooks/scan-status.py", "copilot": ".copilot/hooks/scripts/scan-status.py", "gemini": ".gemini/hooks/scripts/scan-status.py"}

class LifecycleTests(unittest.TestCase):
    observed_seconds = []

    @classmethod
    def tearDownClass(cls):
        if cls.observed_seconds:
            print(f"Observed adapter maximum: {max(cls.observed_seconds):.6f}s across {len(cls.observed_seconds)} callbacks", flush=True)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="scan-lifecycle-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.home, self.repo = self.base / "home", self.base / "repo"
        self.home.mkdir(); self.repo.mkdir()
        self.env = {key: value for key, value in os.environ.items() if not key.startswith(("GIT_", "PYTHON", "SCAN_SECRETS_"))}
        self.env.update(PATH=str(Path(sys.executable).parent) + os.pathsep + self.env.get("PATH", ""), HOME=str(self.home), USERPROFILE=str(self.home), CODEX_HOME=str(self.home / ".codex"), XDG_DATA_HOME=str(self.base / "data"), LOCALAPPDATA=str(self.base / "local"), GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True, capture_output=True, env=self.env)

    def adapter(self, provider, *, home=None):
        return (home or ROOT) / ENTRIES[provider]

    def invoke(self, provider, payload=None, *, home=None, env=None):
        start = time.monotonic()
        process = subprocess.run([sys.executable, "-I", "-S", "-B", str(self.adapter(provider, home=home))], cwd=self.repo, env=env or self.env, input=json.dumps(payload or {}).encode(), capture_output=True, timeout=2)
        elapsed = time.monotonic() - start
        self.observed_seconds.append(elapsed)
        self.assertLess(elapsed, 1.0)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stderr, b"")
        self.assertLess(len(process.stdout), 512)
        rows = [json.loads(row) for row in process.stdout.splitlines()]
        self.assertTrue(rows)
        final = rows[-1]
        self.assertNotIn(final.get("decision"), ("block", "deny"))
        self.assertIsNot(final.get("continue"), False)
        message = rows[0].get("message", final.get("systemMessage", ""))
        self.assertIn("scan-secrets status:", message)
        self.assertIn("never authorizes publication", message)
        if provider == "copilot" and payload and payload.get("hook_event_name") == "agentStop":
            self.assertEqual(final, {})
            self.assertEqual(rows[0]["type"], "progress")
        else:
            self.assertEqual(len(rows), 1)
        return message

    def install(self):
        result = subprocess.run([sys.executable, "-I", "-S", "-B", str(ROOT / "scripts/install-scan-secrets.py"), "install", "--no-input", "--json"], env=self.env, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.bundle = Path(json.loads(result.stdout)["destination"])
        self.cli = self.bundle / "scripts/scan-secrets.py"

    def check(self):
        result = subprocess.run([sys.executable, "-I", "-S", "-B", str(self.cli), "check", "--json", "--no-input"], env=self.env, cwd=self.repo, capture_output=True, timeout=10)
        return result

    def test_saved_absent_stale_incomplete_and_corrupt_history_is_informational(self):
        self.install()
        for provider in ENTRIES:
            self.assertIn("not scanned", self.invoke(provider))
        (self.repo / "pending.txt").write_text("clean\n")
        self.assertEqual(self.check().returncode, 0)
        report, = (self.base / "data/scan-secrets/status").glob("*.json")
        clean = json.loads(report.read_bytes())
        for provider in ENTRIES:
            self.assertIn("last clean; scope worktree; time ", self.invoke(provider))
        clean["completed_at"] = "2001-01-01T00:00:00.000000Z"
        report.write_text(json.dumps(clean))
        for provider in ENTRIES:
            self.assertIn("time 2001-01-01", self.invoke(provider, {"stop_hook_active": True}))
        (self.repo / "unsafe").symlink_to(self.base / "missing")
        self.assertEqual(self.check().returncode, 2)
        for provider in ENTRIES:
            self.assertIn("last incomplete", self.invoke(provider))
        report.write_text("{corrupt private value}")
        for provider in ENTRIES:
            self.assertIn("unavailable", self.invoke(provider))
        report.unlink()
        report.mkdir()
        for provider in ENTRIES:
            self.assertIn("unavailable", self.invoke(provider))

    def test_open_and_malformed_input_finishes_within_outer_deadline(self):
        self.install()
        for provider in ENTRIES:
            for raw in (b"", b"{", b"{}", b"{} extra", b"{\"x\":1,\"x\":2}", b"x" * 65537):
                with self.subTest(provider=provider, raw=raw[:16]):
                    start = time.monotonic()
                    with subprocess.Popen([sys.executable, "-I", "-S", "-B", str(self.adapter(provider))], cwd=self.repo, env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                        if raw:
                            process.stdin.write(raw); process.stdin.flush()
                        process.wait(timeout=1.0)
                        elapsed = time.monotonic() - start
                        self.observed_seconds.append(elapsed)
                        self.assertLess(elapsed, 1.0)
                        process.stdin.close()
                        output = process.stdout.read()
                        self.assertEqual(process.returncode, 0, process.stderr.read())
                        self.assertIn(b"not scanned" if raw == b"{}" else b"unavailable", output)

    def test_child_faults_are_bounded_redacted_and_descendants_are_cleaned(self):
        self.install()
        original = self.cli.read_bytes()
        pidfile = self.base / "descendant.pid"
        bad = "private-unsafe-status-value"
        cases = ["raise RuntimeError(" + repr(bad) + ")", "print(" + repr(bad) + ")", "print('x' * 1000000)",
            "import time; time.sleep(10)",
            "import subprocess,sys,time; from pathlib import Path; p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(10)']); Path(" + repr(str(pidfile)) + ").write_text(str(p.pid)); time.sleep(10)",
            "import subprocess,sys; from pathlib import Path; p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(10)']); Path(" + repr(str(pidfile)) + ").write_text(str(p.pid)); print('{}')"]
        try:
            for source in cases:
                self.cli.write_text(source)
                for provider in ENTRIES:
                    with self.subTest(provider=provider, source=source[:40]):
                        pidfile.unlink(missing_ok=True)
                        message = self.invoke(provider)
                        self.assertIn("unavailable", message)
                        self.assertNotIn(bad, message)
                        if pidfile.exists():
                            pid = int(pidfile.read_text())
                            # A killed orphan can remain a zombie briefly; ps must
                            # never observe a running descendant after return.
                            observed = subprocess.run(["/bin/ps", "-o", "stat=", "-p", str(pid)], capture_output=True)
                            self.assertTrue(not observed.stdout.strip() or observed.stdout.strip().startswith(b"Z"), observed.stdout)
        finally:
            self.cli.write_bytes(original)
        self.cli.unlink()
        for provider in ENTRIES:
            self.assertIn("unavailable", self.invoke(provider))

    def test_status_never_loads_detector_git_or_ambient_executables(self):
        self.install()
        self.assertEqual(self.check().returncode, 0)
        sentinel = self.base / "executed"
        hostile = self.base / "hostile"
        hostile.mkdir()
        for name in ("git", "python", "python3", "scan-secrets"):
            command = hostile / name
            command.write_text("#!/bin/sh\nprintf unsafe > " + str(sentinel) + "\nexit 97\n")
            command.chmod(0o755)
        for path in (self.bundle / "hooks/runtime").glob("*.py"):
            if path.name not in {"scan_cli.py", "scan_status.py", "scan_native_file.py"}:
                path.write_text("from pathlib import Path\nPath(" + repr(str(sentinel)) + ").write_text('imported')\nraise RuntimeError('detector forbidden')\n")
        (hostile / "sitecustomize.py").write_text("from pathlib import Path\nPath(" + repr(str(sentinel)) + ").write_text('startup')\n")
        env = {**self.env, "PATH": str(hostile), "PYTHONPATH": str(hostile), "SCAN_SECRETS_CLI": str(hostile / "scan-secrets")}
        for provider in ENTRIES:
            self.assertIn("last clean", self.invoke(provider, env=env))
            self.assertFalse(sentinel.exists())

    def test_native_cwd_selects_its_own_linked_worktree_history(self):
        self.install()
        git = shutil.which("git")
        def command(*args):
            return subprocess.run([git, "-c", "commit.gpgsign=false", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", *args], cwd=self.repo, env=self.env, check=True, capture_output=True, timeout=10)
        (self.repo / "tracked.txt").write_text("clean\n")
        command("add", "--all")
        command("commit", "-qm", "fixture")
        self.assertEqual(self.check().returncode, 0)
        other = self.base / "linked"
        command("worktree", "add", "-qb", "other", str(other))
        (other / "pending.txt").write_text("gh" + "p_" + "A" * 36)
        checked = subprocess.run([sys.executable, "-I", "-S", "-B", str(self.cli), "check", "--json", "--no-input"], cwd=other, env=self.env, capture_output=True, timeout=10)
        self.assertEqual(checked.returncode, 1, checked.stdout + checked.stderr)
        for provider in ENTRIES:
            self.assertIn("last findings", self.invoke(provider, {"cwd": str(other)}))
            self.assertIn("last clean", self.invoke(provider, {"cwd": str(self.repo)}))
            for invalid in (None, [], 1, "relative", "bad\0path", "x" * 8193):
                self.assertIn("unavailable", self.invoke(provider, {"cwd": invalid}))

    def test_untrusted_child_display_fields_are_never_forwarded(self):
        self.install()
        unsafe = "private-unsafe-value\nrun automatic checkpoint"
        shell = {"schema": "scan_secrets_status_v1", "historical": True, "authorizes_publication": False, "outcome": "last_scan", "last_scan": {"outcome": "complete_clean", "scope": "worktree", "completed_at": "2026-10-16T00:00:00.000000Z"}}
        for key in ("outcome", "scope", "completed_at"):
            value = json.loads(json.dumps(shell))
            value["last_scan"][key] = unsafe
            self.cli.write_text("print(" + repr(json.dumps(value)) + ")\n")
            for provider in ENTRIES:
                message = self.invoke(provider)
                self.assertIn("unavailable", message)
                self.assertNotIn("private-unsafe", message)
        # A malformed or open input must not launch even the known child.
        sentinel = self.base / "child-started"
        self.cli.write_text("from pathlib import Path\nPath(" + repr(str(sentinel)) + ").touch()\n")
        for provider in ENTRIES:
            process = subprocess.run([sys.executable, "-I", "-S", "-B", str(self.adapter(provider))], cwd=self.repo, env=self.env, input=b"{", capture_output=True, timeout=2)
            self.assertEqual(process.returncode, 0)
            self.assertFalse(sentinel.exists())

    def test_closed_output_consumer_finishes_quietly_after_cleanup(self):
        self.install()
        pidfile = self.base / "closed-output-child.pid"
        self.cli.write_text("import os,time\nfrom pathlib import Path\nPath(" + repr(str(pidfile)) + ").write_text(str(os.getpid()))\ntime.sleep(10)\n")
        for provider in ENTRIES:
            pidfile.unlink(missing_ok=True)
            started = time.monotonic()
            with subprocess.Popen([sys.executable, "-I", "-S", "-B", str(self.adapter(provider))], cwd=self.repo, env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                process.stdout.close()
                process.stdin.write(b"{}"); process.stdin.close()
                process.wait(timeout=1)
                self.assertLess(time.monotonic() - started, 1)
                self.assertEqual(process.returncode, 0, process.stderr.read())
                self.assertEqual(process.stderr.read(), b"")
            self.assertTrue(pidfile.exists())
            observed = subprocess.run(["/bin/ps", "-o", "stat=", "-p", pidfile.read_text()], capture_output=True)
            self.assertFalse(observed.stdout.strip(), observed.stdout)

    def test_malformed_copilot_input_is_one_portable_json_document(self):
        for raw in (b"{", b"{} extra", b'{"hook_event_name":"Stop",', b"[]"):
            process = subprocess.run([sys.executable, "-I", "-S", "-B", str(self.adapter("copilot"))], cwd=self.repo, env=self.env, input=raw, capture_output=True, timeout=2)
            self.assertEqual(process.returncode, 0)
            final = json.loads(process.stdout)
            self.assertEqual(set(final), {"systemMessage"})
            self.assertIn("unavailable", final["systemMessage"])

    def test_copilot_cli_native_shape_uses_progress_then_one_final_result(self):
        for payload in ({"hook_event_name": "agentStop", "stop_hook_active": True}, {"sessionId": "fixture", "timestamp": 1, "cwd": str(self.repo), "transcriptPath": "fixture", "stopReason": "end_turn", "stop_hook_active": False}):
            process = subprocess.run([sys.executable, "-I", "-S", "-B", str(self.adapter("copilot"))], cwd=self.repo, env=self.env, input=json.dumps(payload).encode(), capture_output=True, timeout=2)
            self.assertEqual(process.returncode, 0)
            rows = [json.loads(row) for row in process.stdout.splitlines()]
            self.assertEqual(len(rows), 2)
            self.assertEqual(set(rows[0]), {"type", "message"})
            self.assertEqual(rows[0]["type"], "progress")
            self.assertEqual(rows[1], {})

    def test_copilot_vscode_mapping_has_one_display_only_result(self):
        result = subprocess.run([sys.executable, "-I", "-S", "-B", str(self.adapter("copilot"))], cwd=self.repo, env=self.env, input=b'{"hook_event_name":"Stop","stop_hook_active":true}', capture_output=True, timeout=2)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(len(result.stdout.splitlines()), 1)
        self.assertEqual(set(json.loads(result.stdout)), {"systemMessage"})

    def installed_assets(self, installer):
        source = self.base / "source"
        source.mkdir()
        for name in ("hooks", ".codex", ".copilot", ".gemini", ".github"):
            shutil.copytree(ROOT / name, source / name, ignore=shutil.ignore_patterns("__pycache__", "logs"))
        (source / "scripts").mkdir()
        for path in (ROOT / "scripts").iterdir():
            if path.suffix in {".py", ".sh", ".ps1"}:
                shutil.copy2(path, source / "scripts" / path.name)
        for name in ("skills/default/fixture", "skills/forest-service", "references", "agents"):
            (source / name).mkdir(parents=True)
        (source / "skills/default/fixture/SKILL.md").write_text("---\nname: fixture\n---\nFixture.\n")
        (source / "agents/fixture.md").write_text("---\nname: fixture\ndescription: Test fixture.\n---\nFixture.\n")
        command = ["bash", str(source / "scripts/install.sh")] if installer == "bash" else ["pwsh", "-NoProfile", "-File", str(source / "scripts/install.ps1")]
        env = {**self.env, "XDG_CONFIG_HOME": str(self.base / "config"), "XDG_CACHE_HOME": str(self.base / "cache"), "APPDATA": str(self.base / "appdata")}
        installed = subprocess.run(command, env=env, capture_output=True, timeout=90)
        self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
        for provider in ENTRIES:
            self.assertEqual(self.adapter(provider, home=self.home).read_bytes(), self.adapter(provider).read_bytes())
        shutil.rmtree(source)
        self.assertFalse(source.exists())
        self.cli = self.home / ".local/lib/scan-secrets/scripts/scan-secrets.py"
        installed_manifest = json.loads((self.cli.parent.parent / "installation.json").read_bytes())
        self.assertEqual(Path(installed_manifest["interpreter"]), Path(sys.executable).resolve())
        self.assertEqual(self.check().returncode, 0)
        # Installed status assets have no dependency on the provider scanner
        # helper closure. Fault those files after creating real saved history.
        for provider in ENTRIES:
            helpers = self.adapter(provider, home=self.home).parent / "helpers"
            for module in helpers.glob("scan_*.py"):
                module.write_text("raise RuntimeError('scanner helper must not start')\n")
            self.assertIn("last clean", self.invoke(provider, {"stop_hook_active": True}, home=self.home))
        self.assertFalse(source.exists())

    def test_inherited_codex_home_stays_untouched(self):
        for method in ("test_bash_installed_source_free_assets", "test_powershell_installed_source_free_assets"):
            with self.subTest(method=method):
                trap = self.base / ("ambient-codex-home-" + method)
                trap.mkdir()
                result = subprocess.run([sys.executable, "-I", "-S", "-B", str(Path(__file__).resolve()), "LifecycleTests." + method],
                    env={**os.environ, "CODEX_HOME": str(trap)}, capture_output=True, timeout=90)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(list(trap.rglob("*")), [], "installer fixture escaped its disposable Codex home")

    def test_bash_installed_source_free_assets(self):
        self.installed_assets("bash")

    def test_powershell_installed_source_free_assets(self):
        self.assertIsNotNone(shutil.which("pwsh"), "PowerShell is required for installer parity")
        self.installed_assets("powershell")

    def test_absent_runtime_and_repeated_stop_are_successful(self):
        for provider in ENTRIES:
            for active in (False, True, True):
                with self.subTest(provider=provider, active=active):
                    message = self.invoke(provider, {"stop_hook_active": active})
                    self.assertIn("unavailable", message)

if __name__ == "__main__":
    unittest.main()
