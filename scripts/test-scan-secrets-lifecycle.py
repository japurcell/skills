#!/usr/bin/env python3
"""Generated status adapters through their public process boundary."""
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
        self.env.update(PATH=str(Path(sys.executable).parent) + os.pathsep + self.env.get("PATH", ""), HOME=str(self.home), USERPROFILE=str(self.home), CODEX_HOME=str(self.home / ".codex"), XDG_DATA_HOME=str(self.base / "data"), XDG_CONFIG_HOME=str(self.base / "config"), XDG_CACHE_HOME=str(self.base / "cache"), APPDATA=str(self.base / "appdata"), LOCALAPPDATA=str(self.base / "local"), GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
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

    def installed_assets(self, installer, *, upgrade=False, fault=False):
        if upgrade:
            fixtures = ROOT / "scripts/fixtures/provider-hooks-pre-status"
            paths = {"codex": ".codex/hooks.json", "copilot": ".copilot/hooks/hooks.json", "gemini": ".gemini/settings.json"}
            for provider, relative in paths.items():
                config = json.loads((fixtures / (provider + ".json")).read_bytes())
                config["userSetting"] = {"nested": {"keep": True}}
                if provider == "gemini":
                    config["hooks"]["disabled"] = ["scan-secrets", "user-validator"]
                    config["general"]["custom"] = {"keep": True}
                if provider == "copilot":
                    config["disableAllHooks"] = True
                target = self.home / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(config))
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
        if fault:
            injection = self.base / "filesystem-fault"
            injection.mkdir()
            injection.joinpath("sitecustomize.py").write_text("import os\noriginal = os.replace\ndef fail(source, destination, *args, **kwargs):\n    if str(destination).endswith('/.gemini/settings.json'):\n        raise OSError('injected configuration promotion failure')\n    return original(source, destination, *args, **kwargs)\nos.replace = fail\n")
            failed = subprocess.run(command, env={**env, "PYTHONPATH": str(injection)}, capture_output=True, timeout=90)
            self.assertEqual(failed.returncode, 1, failed.stdout + failed.stderr)
            self.assertIn(b"injected configuration promotion failure", failed.stderr)
            # Copilot is already migrated, with its exact deployed asset. The
            # other configs remain recognizable and the same install can retry.
            config = json.loads((self.home / ".copilot/hooks/hooks.json").read_bytes())
            status = next(h for h in config["hooks"]["agentStop"] if "scan-status.py" in h.get("bash", ""))
            import shlex
            result = subprocess.run(shlex.split(status["bash"]), input=b'{"hook_event_name":"agentStop"}', env=env, cwd=self.repo, capture_output=True, timeout=2)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(b"not scanned", result.stdout)
        installed = subprocess.run(command, env=env, capture_output=True, timeout=90)
        self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
        if upgrade:
            before = {relative: (self.home / relative).read_bytes() for relative in paths.values()}
            backups = {relative: (self.home / (relative + ".bak")).read_bytes() for relative in paths.values()}
            repeated = subprocess.run(command, env=env, capture_output=True, timeout=90)
            self.assertEqual(repeated.returncode, 0, repeated.stdout + repeated.stderr)
            self.assertEqual({relative: (self.home / relative).read_bytes() for relative in paths.values()}, before)
            self.assertEqual({relative: (self.home / (relative + ".bak")).read_bytes() for relative in paths.values()}, backups)
            for provider, relative in paths.items():
                self.assertEqual(json.loads((self.home / relative).read_bytes())["userSetting"], {"nested": {"keep": True}})
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

    def merge_provider(self, provider, config, *, template=None):
        relative = {"codex": ".codex/hooks.json", "copilot": ".copilot/hooks/hooks.json", "gemini": ".gemini/settings.json"}[provider]
        destination = self.home / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        raw = (json.dumps(config) + "\n").encode()
        destination.write_bytes(raw)
        asset = self.adapter(provider, home=self.home)
        asset.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.adapter(provider), asset)
        template = template or ROOT / {"codex": ".codex/global-hooks.json", "copilot": ".copilot/hooks/hooks.json", "gemini": ".gemini/global-settings.json"}[provider]
        command = [sys.executable, "-B", str(ROOT / ("scripts/install-codex-hooks.py" if provider == "codex" else "scripts/install-provider-hooks.py")), "--template", str(template), "--destination", str(destination)]
        if provider != "codex":
            command += ["--provider", provider, "--home", str(self.home)]
        process = subprocess.run(command, env=self.env, capture_output=True, timeout=5)
        return process, destination, raw, command

    def test_powershell_real_old_install_upgrade_is_idempotent(self):
        self.installed_assets("powershell", upgrade=True)

    def test_ordered_install_failure_recovers_with_deployed_status_assets(self):
        self.installed_assets("bash", upgrade=True, fault=True)

    def test_pinned_old_interpreters_and_removed_events_migrate_to_working_status(self):
        import shlex
        self.install()
        for provider in ENTRIES:
            config = json.loads((ROOT / "scripts/fixtures/provider-hooks-pre-status" / (provider + ".json")).read_bytes())
            event = {"codex": "Stop", "copilot": "sessionEnd", "gemini": "SessionEnd"}[provider]
            directory = self.adapter(provider, home=self.home).parent
            operands = [str(self.base / "removed python"), "-I", "-S", "-B", str(directory / "scan-secrets.py")]
            scanner = {"type": "command"}
            if provider == "copilot":
                scanner.update(bash=shlex.join(operands), powershell="& " + " ".join("'" + value.replace("'", "''") + "'" for value in operands))
                config["hooks"][event] = [scanner]
            else:
                scanner["command"] = shlex.join(operands)
                if provider == "codex":
                    scanner["commandWindows"] = f'"{operands[0]}" -I -S -B "{operands[-1]}"'
                config["hooks"][event] = [{"hooks": [scanner]}]
            replacement = None
            if provider != "codex":
                original = ROOT / (".copilot/hooks/hooks.json" if provider == "copilot" else ".gemini/global-settings.json")
                template = json.loads(original.read_bytes())
                template["hooks"].pop(event)
                replacement = self.base / (provider + "-without-session-end.json")
                replacement.write_text(json.dumps(template))
            result, destination, raw, command = self.merge_provider(provider, config, template=replacement)
            self.assertEqual(result.returncode, 0, result.stderr)
            merged = json.loads(destination.read_bytes())
            status_event = {"codex": "Stop", "copilot": "agentStop", "gemini": "AfterAgent"}[provider]
            handlers = [h for entry in merged["hooks"][status_event] for h in ([entry] if provider == "copilot" else entry["hooks"])]
            status = next(h for h in handlers if "scan-status.py" in h.get("bash" if provider == "copilot" else "command", ""))
            executed = subprocess.run(shlex.split(status["bash" if provider == "copilot" else "command"]), input=json.dumps({"hook_event_name": status_event}).encode(), env=self.env, cwd=self.repo, capture_output=True, timeout=2)
            self.assertEqual(executed.returncode, 0, executed.stderr)
            self.assertIn(b"not scanned", executed.stdout)
            self.assertEqual(destination.with_name(destination.name + ".bak").read_bytes(), raw)

    def test_missing_status_asset_refuses_activation_then_recovers(self):
        for provider in ENTRIES:
            config = json.loads((ROOT / "scripts/fixtures/provider-hooks-pre-status" / (provider + ".json")).read_bytes())
            first, destination, raw, command = self.merge_provider(provider, config)
            self.assertEqual(first.returncode, 0, first.stderr)
            destination.write_bytes(raw)
            asset = self.adapter(provider, home=self.home)
            asset.unlink()
            failed = subprocess.run(command, env=self.env, capture_output=True, timeout=5)
            self.assertEqual(failed.returncode, 1, failed.stderr)
            self.assertEqual(destination.read_bytes(), raw)
            shutil.copy2(self.adapter(provider), asset)
            recovered = subprocess.run(command, env=self.env, capture_output=True, timeout=5)
            self.assertEqual(recovered.returncode, 0, recovered.stderr)
            self.assertIn("scan-status.py", destination.read_text())

    def test_config_hard_links_repair_without_external_mode_or_byte_changes(self):
        for provider in ENTRIES:
            config = json.loads((ROOT / "scripts/fixtures/provider-hooks-pre-status" / (provider + ".json")).read_bytes())
            first, destination, raw, command = self.merge_provider(provider, config)
            self.assertEqual(first.returncode, 0, first.stderr)
            previous = destination.read_bytes()
            external = self.base / (provider + "-external.json")
            external.write_bytes(previous); external.chmod(0o644)
            destination.unlink(); os.link(external, destination)
            result = subprocess.run(command, env=self.env, capture_output=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotEqual(destination.stat().st_ino, external.stat().st_ino)
            self.assertEqual(external.read_bytes(), previous)
            self.assertEqual(external.stat().st_mode & 0o777, 0o644)

    def test_mixed_owned_command_pairs_refuse_without_losing_user_behavior(self):
        for handler in (
            {"command": "python3 ~/.codex/hooks/scan-secrets.py", "commandWindows": "echo user"},
            {"command": "echo user", "commandWindows": 'py -3 "%USERPROFILE%\\.codex\\hooks\\scan-secrets.py"'},
            {"commandWindows": 'py -3 "%USERPROFILE%\\.codex\\hooks\\scan-secrets.py"'},
        ):
            config = {"hooks": {"PreToolUse": [{"hooks": [handler]}]}}
            result, destination, raw, command = self.merge_provider("codex", config)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(b"Ambiguous", result.stderr)
            self.assertEqual(destination.read_bytes(), raw)

    def test_codex_linked_ancestor_refuses_before_external_mutation(self):
        external = self.base / "external"
        (external / "nested").mkdir(parents=True)
        destination = external / "nested/hooks.json"
        destination.write_text('{"custom":"keep"}')
        (self.home / ".codex").symlink_to(external, target_is_directory=True)
        before = {str(path.relative_to(external)): path.read_bytes() for path in external.rglob("*") if path.is_file()}
        result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/install-codex-hooks.py"), "--template", str(ROOT / ".codex/global-hooks.json"), "--destination", str(self.home / ".codex/nested/hooks.json")], env=self.env, capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn(b"linked", result.stderr)
        after = {str(path.relative_to(external)): path.read_bytes() for path in external.rglob("*") if path.is_file()}
        self.assertEqual(after, before)

    def test_provider_migration_cooperating_lock_preserves_config(self):
        config = json.loads((ROOT / "scripts/fixtures/provider-hooks-pre-status/codex.json").read_bytes())
        result, destination, raw, command = self.merge_provider("codex", config)
        self.assertEqual(result.returncode, 0, result.stderr)
        before = destination.read_bytes()
        lock = destination.with_name(destination.name + ".install-lock")
        with lock.open("a+b") as stream:
            lock.chmod(0o600)
            if os.name == "nt":
                import msvcrt
                stream.write(b"0"); stream.flush(); stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            refused = subprocess.run(command, env=self.env, capture_output=True, timeout=5)
            self.assertEqual(refused.returncode, 1, refused.stderr)
            self.assertIn(b"busy", refused.stderr)
            self.assertEqual(destination.read_bytes(), before)
        recovered = subprocess.run(command, env=self.env, capture_output=True, timeout=5)
        self.assertEqual(recovered.returncode, 0, recovered.stderr)
        self.assertEqual(destination.read_bytes(), before)

    def test_unrelated_template_status_basename_keeps_its_command(self):
        config = json.loads((ROOT / "scripts/fixtures/provider-hooks-pre-status/copilot.json").read_bytes())
        first, destination, raw, command = self.merge_provider("copilot", config)
        self.assertEqual(first.returncode, 0, first.stderr)
        custom = {"type": "command", "bash": "python3 /user/scan-status.py", "powershell": "python C:/user/scan-status.py"}
        template = json.loads((ROOT / ".copilot/hooks/hooks.json").read_bytes())
        template["hooks"]["agentStop"].append(custom)
        path = self.base / "custom-template.json"
        path.write_text(json.dumps(template))
        command[command.index("--template") + 1] = str(path)
        result = subprocess.run(command, env=self.env, capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(custom, json.loads(destination.read_bytes())["hooks"]["agentStop"])
        self.assertIn("scan-status.py", destination.read_text())

    def test_plain_echo_of_owned_path_preserves_user_data_behavior(self):
        config = json.loads((ROOT / "scripts/fixtures/provider-hooks-pre-status/codex.json").read_bytes())
        custom = {"type": "command", "command": "echo ~/.codex/hooks/load-required-skills.py"}
        config["hooks"]["SessionStart"][0]["hooks"].insert(0, custom)
        result, destination, raw, command = self.merge_provider("codex", config)
        self.assertEqual(result.returncode, 0, result.stderr)
        merged = json.loads(destination.read_bytes())
        self.assertIn(custom, merged["hooks"]["SessionStart"][0]["hooks"])
        self.assertIn("scan-status.py", destination.read_text())

    def test_echo_shell_substitutions_and_sinks_keep_ambiguous_refusal(self):
        path = "~/.codex/hooks/scan-secrets.py"
        for command in (
            f"echo $(python3 {path})",
            f"echo `python3 {path}`",
            f"echo {path}; python3 {path}",
            f"echo {path} | sh",
            f"echo {path} > user-output.txt",
            f"exec echo {path}",
        ):
            config = {"hooks": {"PreToolUse": [{"hooks": [{"type": "command", "command": command}]}]}}
            result, destination, raw, invocation = self.merge_provider("codex", config)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(b"Ambiguous", result.stderr)
            self.assertEqual(destination.read_bytes(), raw)

    def test_powershell_parenthesized_execution_keeps_ambiguous_refusal(self):
        path = self.adapter("copilot", home=self.home).with_name("scan-secrets.py")
        handler = {"type": "command", "bash": "echo user", "powershell": f"echo (python '{path}')"}
        config = {"hooks": {"preToolUse": [handler]}}
        result, destination, raw, command = self.merge_provider("copilot", config)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn(b"Ambiguous", result.stderr)
        self.assertEqual(destination.read_bytes(), raw)

    def test_fifo_configurations_refuse_promptly_and_keep_regular_upgrade_available(self):
        import stat
        for provider in ENTRIES:
            with self.subTest(provider=provider):
                config = json.loads((ROOT / "scripts/fixtures/provider-hooks-pre-status" / (provider + ".json")).read_bytes())
                first, destination, raw, command = self.merge_provider(provider, config)
                self.assertEqual(first.returncode, 0, first.stderr)
                backup = destination.with_name(destination.name + ".bak").read_bytes()
                destination.unlink(); os.mkfifo(destination, 0o600)
                try:
                    result = subprocess.run(command, env=self.env, capture_output=True, timeout=1)
                except subprocess.TimeoutExpired:
                    self.fail("Public provider migration blocked on a FIFO configuration")
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertTrue(stat.S_ISFIFO(destination.lstat().st_mode))
                self.assertEqual(destination.with_name(destination.name + ".bak").read_bytes(), backup)
                destination.unlink(); destination.write_bytes(raw)
                recovered = subprocess.run(command, env=self.env, capture_output=True, timeout=5)
                self.assertEqual(recovered.returncode, 0, recovered.stderr)
                self.assertIn("scan-status.py", destination.read_text())

    def test_fifo_migration_lock_refuses_without_mutation(self):
        import stat
        config = json.loads((ROOT / "scripts/fixtures/provider-hooks-pre-status/codex.json").read_bytes())
        first, destination, raw, command = self.merge_provider("codex", config)
        self.assertEqual(first.returncode, 0, first.stderr)
        before = destination.read_bytes()
        lock = destination.with_name(destination.name + ".install-lock")
        lock.unlink(); os.mkfifo(lock, 0o600)
        result = subprocess.run(command, env=self.env, capture_output=True, timeout=1)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertTrue(stat.S_ISFIFO(lock.lstat().st_mode))
        self.assertEqual(destination.read_bytes(), before)
        lock.unlink()
        recovered = subprocess.run(command, env=self.env, capture_output=True, timeout=5)
        self.assertEqual(recovered.returncode, 0, recovered.stderr)

    def test_codex_duplicate_configuration_keys_refuse_without_rewriting(self):
        config = json.loads((ROOT / "scripts/fixtures/provider-hooks-pre-status/codex.json").read_bytes())
        first, destination, original, command = self.merge_provider("codex", config)
        self.assertEqual(first.returncode, 0, first.stderr)
        raw = b'{"hooks":{},"hooks":{"Stop":[{"hooks":[{"command":"echo user"}]}]}}'
        destination.write_bytes(raw)
        result = subprocess.run(command, env=self.env, capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(destination.read_bytes(), raw)

    def test_extra_executable_override_refuses_migration_without_mutation(self):
        config = json.loads((ROOT / "scripts/fixtures/provider-hooks-pre-status/copilot.json").read_bytes())
        scanner = config["hooks"]["preToolUse"][-1]
        scanner["command"] = "user executable must survive"
        result, destination, raw, command = self.merge_provider("copilot", config)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn(b"Ambiguous", result.stderr)
        self.assertEqual(destination.read_bytes(), raw)
        self.assertFalse(destination.with_name(destination.name + ".bak").exists())

    def test_exact_old_templates_upgrade_and_registered_status_executes(self):
        import hashlib
        self.install()
        fixture_root = ROOT / "scripts/fixtures/provider-hooks-pre-status"
        provenance = json.loads((fixture_root / "provenance.json").read_bytes())
        for provider, event in (("codex", "Stop"), ("copilot", "agentStop"), ("gemini", "AfterAgent")):
            with self.subTest(provider=provider):
                fixture = fixture_root / (provider + ".json")
                self.assertEqual(hashlib.sha256(fixture.read_bytes()).hexdigest(), provenance[provider]["sha256"])
                config = json.loads(fixture.read_bytes())
                config["userSetting"] = {"nested": {"keep": True}}
                if provider == "copilot":
                    config["disableAllHooks"] = True
                    custom = {"type": "command", "bash": "python3 /user/.copilot/hooks/scripts/scan-secrets.py", "powershell": "python C:/user/scan-secrets.py"}
                    config["hooks"]["preToolUse"].insert(0, custom)
                else:
                    custom = {"type": "command", "command": "python3 /user/scan-secrets.py"}
                    config["hooks"]["PreToolUse" if provider == "codex" else "BeforeTool"][0]["hooks"].insert(0, custom)
                result, destination, raw, command = self.merge_provider(provider, config)
                self.assertEqual(result.returncode, 0, result.stderr)
                merged = json.loads(destination.read_bytes())
                self.assertEqual(merged["userSetting"], config["userSetting"])
                self.assertIn(custom, [handler for entries in merged["hooks"].values() for entry in entries for handler in ([entry] if provider == "copilot" else entry["hooks"])])
                if provider == "copilot":
                    self.assertIs(merged["disableAllHooks"], True)
                entries = merged["hooks"][event]
                status = [h for entry in entries for h in ([entry] if provider == "copilot" else entry["hooks"]) if "scan-status.py" in h.get("bash" if provider == "copilot" else "command", "")]
                self.assertEqual(len(status), 1)
                launch = status[0]["bash" if provider == "copilot" else "command"]
                import shlex
                args = shlex.split(launch)
                self.assertEqual(args[1:4], ["-I", "-S", "-B"])
                self.assertEqual(Path(args[-1]), self.adapter(provider, home=self.home))
                invoked = subprocess.run(args, input=json.dumps({"hook_event_name": event}).encode(), cwd=self.repo, env=self.env, capture_output=True, timeout=2)
                self.assertEqual(invoked.returncode, 0, invoked.stderr)
                rows = [json.loads(row) for row in invoked.stdout.splitlines()]
                self.assertIn("not scanned", rows[0].get("message", rows[-1].get("systemMessage", "")))
                self.assertEqual(destination.with_name(destination.name + ".bak").read_bytes(), raw)
                first = destination.read_bytes()
                repeated = subprocess.run(command, env=self.env, capture_output=True, timeout=5)
                self.assertEqual(repeated.returncode, 0, repeated.stderr)
                self.assertEqual(destination.read_bytes(), first)
                self.assertEqual(destination.with_name(destination.name + ".bak").read_bytes(), raw)

    def test_gemini_disabled_names_survive_status_upgrade(self):
        self.installed_assets("bash", upgrade=True)
        config = json.loads((self.home / ".gemini/settings.json").read_bytes())
        self.assertEqual(config["hooks"]["disabled"], ["scan-secrets", "user-validator"])
        self.assertEqual(config["general"]["custom"], {"keep": True})
        status = [handler for group in config["hooks"]["AfterAgent"] for handler in group["hooks"] if "scan-status.py" in handler.get("command", "")]
        self.assertEqual(len(status), 1)
        self.assertEqual(status[0]["name"], "scan-secrets")
        result = subprocess.run(status[0]["command"], shell=True, input=b'{"hook_event_name":"AfterAgent"}', cwd=self.repo, env=self.env, capture_output=True, timeout=2)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("last clean", json.loads(result.stdout)["systemMessage"])
        doctor = subprocess.run([sys.executable, "-I", "-S", "-B", str(self.adapter("gemini", home=self.home).with_name("hooks-diagnostics.py")), "--doctor"], cwd=self.repo, env=self.env, capture_output=True, timeout=5)
        self.assertEqual(doctor.returncode, 0, doctor.stderr)
        self.assertEqual(json.loads(doctor.stdout)["registrations"]["health"], "observed")

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
