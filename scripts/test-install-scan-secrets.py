#!/usr/bin/env python3
"""Public installed scanner and installer contract checks."""
import json
import os
import hashlib
import shutil
import signal
import time
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parent.parent
PYTHON = str(Path(sys.executable).resolve())

class InstalledScannerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="installed scanner ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.home = self.root / "home"
        self.home.mkdir()
        self.destination = self.root / "private runtime"
        self.environment = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home),
            APPDATA=str(self.home / "roaming"), LOCALAPPDATA=str(self.home / "local"),
            XDG_DATA_HOME=str(self.home / "data"), XDG_CONFIG_HOME=str(self.home / "config"),
            XDG_CACHE_HOME=str(self.root / "cache"), POWERSHELL_TELEMETRY_OPTOUT="1")
        self.environment.pop("CODEX_HOME", None)
        self.environment.pop("INSTALL_FOREST_SERVICE_SKILLS", None)

    def invoke(self, arguments, *, timeout=30, **kwargs):
        return subprocess.run(arguments, capture_output=True, text=True, env=self.environment, timeout=timeout, **kwargs)

    def install(self, *arguments, source=SOURCE):
        return self.invoke([PYTHON, "-I", "-S", "-B", str(SOURCE / "scripts/install-scan-secrets.py"), "install", "--source-dir", str(source), "--destination", str(self.destination), "--json", *arguments])

    def command(self, *arguments, powershell=False):
        command = [str(self.destination / "scan-secrets")]
        if powershell:
            self.assertIsNotNone(shutil.which("pwsh"), "PowerShell is a required test prerequisite")
            command = ["pwsh", "-NoProfile", "-File", str(self.destination / "scan-secrets.ps1")]
        return self.invoke([*command, *arguments])

    def copy_source(self):
        source = self.root / "source checkout"
        shutil.copytree(SOURCE / "hooks", source / "hooks", ignore=shutil.ignore_patterns("__pycache__"))
        (source / "scripts").mkdir()
        for name in ("scan-secrets.py", "scan_install_windows.py"):
            shutil.copy2(SOURCE / "scripts" / name, source / "scripts" / name)
        return source

    def fingerprint(self, root):
        return [(str(path.relative_to(root)), path.lstat().st_mode, hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None)
                for path in sorted(root.rglob("*"))]

    def test_installed_roundtrip_without_source_or_provider_trees(self):
        source = self.copy_source()
        self.assertEqual(self.install(source=source).returncode, 0)
        manifest = json.loads((self.destination / "installation.json").read_text())
        self.assertEqual(len(manifest["files"]), 13)
        self.assertEqual(manifest["interpreter"], PYTHON)
        self.assertEqual(Path(manifest["runtime"]), self.destination / "hooks/runtime")
        shutil.rmtree(source)
        hostile = self.root / "host modules"
        hostile.mkdir()
        marker = self.root / "ambient-startup-ran"
        (hostile / "sitecustomize.py").write_text(f"from pathlib import Path; Path({str(marker)!r}).touch()")
        self.environment["PYTHONPATH"] = str(hostile)
        repository = self.root / "repository ; ' $(touch NEVER)"
        repository.mkdir()
        self.assertEqual(self.invoke(["git", "init", "-q", str(repository)]).returncode, 0)
        (repository / "notes.txt").write_text("ordinary text\n")
        for powershell in (False, True):
            for arguments in (("--help",), ("--version",), ("help", "check"), ("help", "status")):
                result = self.command(*arguments, powershell=powershell)
                self.assertEqual(result.returncode, 0, result.stderr)
            result = self.command("check", "--repo", str(repository), "--json", powershell=powershell)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertEqual(json.loads(result.stdout)["outcome"], "complete_clean")
            status = self.command("status", "--repo", str(repository), "--json", powershell=powershell)
            self.assertEqual(status.returncode, 0, status.stderr)
            self.assertEqual(json.loads(status.stdout)["last_scan"]["outcome"], "complete_clean")
        (repository / "notes.txt").write_text("token = ghp_" + "A" * 36 + "\n")
        finding = self.command("check", "--repo", str(repository), "--json")
        self.assertEqual(finding.returncode, 1, finding.stderr + finding.stdout)
        self.assertNotIn("A" * 36, finding.stdout + finding.stderr)
        (self.destination / "hooks/runtime/scan_engine.py").unlink()
        incomplete = self.command("check", "--repo", str(repository), "--json")
        self.assertEqual(incomplete.returncode, 2)
        self.assertEqual(json.loads(incomplete.stdout)["outcome"], "incomplete")
        self.assertFalse(marker.exists())
        self.assertEqual(list(self.destination.rglob("__pycache__")), [])
        self.assertFalse((self.root / "NEVER").exists())

    def test_dry_run_and_parser_have_no_writes(self):
        before = self.fingerprint(self.root)
        result = self.install("--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["outcome"], "validated")
        self.assertEqual(before, self.fingerprint(self.root))
        for arguments, code in (([], 0), (["--help"], 0), (["--version"], 0), (["help", "install"], 0), (["install", "--dest", "PRIVATE-CREDENTIAL", "--json"], 3), (["--wat", "PRIVATE-CREDENTIAL", "--json"], 3)):
            result = self.invoke([PYTHON, "-I", "-S", "-B", str(SOURCE / "scripts/install-scan-secrets.py"), *arguments])
            self.assertEqual(result.returncode, code, result.stderr)
            self.assertNotIn("PRIVATE-CREDENTIAL", result.stdout + result.stderr)
            if "--json" in arguments:
                self.assertEqual(json.loads(result.stdout)["reason"], "invalid_arguments")
        self.assertEqual(before, self.fingerprint(self.root))

    def test_exact_missing_or_corrupt_assets_preserve_existing_install(self):
        self.assertEqual(self.install().returncode, 0)
        before = self.fingerprint(self.destination)
        source = self.copy_source()
        for relative in ("scripts/scan-secrets.py", "hooks/runtime/scan_status.py", "hooks/runtime/scan_native_file.py", "hooks/runtime/scan_engine.py", "scripts/scan_install_windows.py"):
            path = source / relative
            raw = path.read_bytes()
            for corruption in (None, b"invalid syntax !"):
                if corruption is None:
                    path.unlink()
                else:
                    path.write_bytes(corruption)
                result = self.install(source=source)
                self.assertEqual(result.returncode, 2, relative)
                self.assertEqual(json.loads(result.stdout)["reason"], "source_assets_invalid")
                self.assertEqual(before, self.fingerprint(self.destination))
                path.write_bytes(raw)

    def test_idempotent_reinstall_and_interrupted_promotion_recovery(self):
        self.assertEqual(self.install().returncode, 0)
        before = self.fingerprint(self.destination)
        self.assertEqual(self.install().returncode, 0)
        self.assertEqual(before, self.fingerprint(self.destination))
        previous = self.destination.with_name(self.destination.name + ".previous")
        self.destination.rename(previous)
        dry_run = self.install("--dry-run")
        self.assertEqual(dry_run.returncode, 0)
        self.assertFalse(self.destination.exists())
        self.assertTrue(previous.exists())
        self.assertEqual(self.install().returncode, 0)
        self.assertEqual(before, self.fingerprint(self.destination))
        self.assertFalse(previous.exists())

    def test_actual_promotion_failure_and_cancellation_restore_old_bundle(self):
        self.assertEqual(self.install().returncode, 0)
        before = self.fingerprint(self.destination)
        for mode, expected in (("failure", 2), ("interrupt", 130), ("kill", -signal.SIGKILL)):
            marker = self.root / (mode + "-activated")
            wrapper = self.root / "fault-boundary.py"
            wrapper.write_text("""import os, runpy, signal, sys, time
from pathlib import Path
helper, destination, marker, mode = sys.argv[1:]
sys.argv = [helper, 'install', '--destination', destination, '--json']
activated = False
def fault(event, arguments):
    global activated
    if event == 'os.rename' and not activated and '.scan-secrets-stage-' in str(arguments[0]) and str(Path(arguments[1]).absolute()) == destination:
        assert Path(destination + '.previous').is_dir()
        activated = True
        Path(marker).write_text('promotion reached')
        if mode == 'failure':
            raise OSError('PRIVATE-CREDENTIAL')
        if mode == 'interrupt':
            os.kill(os.getpid(), signal.SIGINT)
        while True:
            time.sleep(0.05)
sys.addaudithook(fault)
runpy.run_path(helper, run_name='__main__')
""")
            arguments = [PYTHON, "-I", "-S", "-B", str(wrapper), str(SOURCE / "scripts/install-scan-secrets.py"), str(self.destination), str(marker), mode]
            if mode == "kill":
                process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=self.environment)
                try:
                    deadline = time.monotonic() + 10
                    while not marker.exists() and time.monotonic() < deadline and process.poll() is None:
                        time.sleep(0.01)
                    self.assertTrue(marker.exists(), "hard-kill boundary did not activate")
                    concurrent = self.install()
                    self.assertEqual(json.loads(concurrent.stdout)["reason"], "installation_busy")
                    process.kill()
                    stdout, stderr = process.communicate(timeout=5)
                    self.assertEqual(process.returncode, expected)
                    self.assertEqual(self.install().returncode, 0, "kernel lock release and explicit recovery failed")
                finally:
                    if process.poll() is None:
                        process.kill()
                    process.communicate(timeout=5)
            else:
                result = self.invoke(arguments)
                self.assertEqual(result.returncode, expected, result.stderr)
                self.assertNotIn("PRIVATE-CREDENTIAL", result.stdout + result.stderr)
                self.assertEqual(json.loads(result.stdout)["outcome"], "incomplete")
            self.assertTrue(marker.exists(), "promotion failure boundary did not activate")
            self.assertEqual(before, self.fingerprint(self.destination))
            self.assertEqual(self.command("--version").returncode, 0)

    def test_real_main_installers_deliver_usable_neutral_bundle(self):
        source = self.root / "main source"
        shutil.copytree(SOURCE, source, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        for command in (["bash", str(source / "scripts/install.sh")], ["pwsh", "-NoProfile", "-File", str(source / "scripts/install.ps1")]):
            result = self.invoke(command, timeout=120)
            self.assertEqual(result.returncode, 0, result.stderr)
            installed = self.home / ".local/lib/scan-secrets"
            manifest = json.loads((installed / "installation.json").read_text())
            self.assertEqual(len(manifest["files"]), 13)
            hidden = source.with_name("source unavailable")
            source.rename(hidden)
            try:
                version = self.invoke([str(installed / "scan-secrets"), "--version"])
                self.assertEqual(version.returncode, 0, version.stderr)
            finally:
                hidden.rename(source)

    def test_held_parent_prevents_ancestor_substitution_writes(self):
        parent = self.root / "install parent"
        parent.mkdir()
        self.destination = parent / "runtime"
        self.assertEqual(self.install().returncode, 0)
        external = self.root / "external directory"
        external.mkdir()
        (external / "owner-file").write_text("external original")
        before = self.fingerprint(external)
        marker = self.root / "ancestor-swap-activated"
        moved = self.root / "held-parent"
        wrapper = self.root / "ancestor-fault.py"
        wrapper.write_text("""import runpy, sys
from pathlib import Path
helper, parent, moved, external, marker, destination = sys.argv[1:]
sys.argv = [helper, 'install', '--destination', destination, '--json']
activated = False
def fault(event, arguments):
    global activated
    if event == 'tempfile.mkdtemp' and not activated:
        activated = True
        Path(parent).rename(moved)
        Path(parent).symlink_to(external, target_is_directory=True)
        Path(marker).write_text('swapped')
sys.addaudithook(fault)
runpy.run_path(helper, run_name='__main__')
""")
        result = self.invoke([PYTHON, "-I", "-S", "-B", str(wrapper), str(SOURCE / "scripts/install-scan-secrets.py"), str(parent), str(moved), str(external), str(marker), str(self.destination)])
        self.assertTrue(marker.exists(), "ancestor substitution did not activate")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(json.loads(result.stdout)["reason"], "unsafe_destination")
        self.assertEqual(before, self.fingerprint(external))
        self.assertTrue((moved / "runtime/installation.json").is_file())

    def test_open_stdin_and_broken_output_are_bounded(self):
        self.assertEqual(self.install().returncode, 0)
        for arguments in (("--help",), ("--version",), ("status", "--repo", str(self.home), "--json")):
            process = subprocess.Popen([str(self.destination / "scan-secrets"), *arguments], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.environment)
            try:
                self.assertEqual(process.wait(timeout=5), 0)
                self.assertNotIn(b"Traceback", process.stderr.read())
            finally:
                process.stdin.close()
                process.stdout.close()
                process.stderr.close()
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=5)
        read, write = os.pipe()
        os.close(read)
        process = subprocess.Popen([str(self.destination / "scan-secrets"), "--help"], stdout=write, stderr=subprocess.PIPE, env=self.environment)
        os.close(write)
        stderr = process.communicate(timeout=5)[1]
        self.assertEqual(process.returncode, 2)
        self.assertNotIn(b"Traceback", stderr)

    def test_nonregular_and_oversized_source_assets_fail_without_waiting(self):
        source = self.copy_source()
        status = source / "hooks/runtime/scan_status.py"
        status.unlink()
        os.mkfifo(status)
        result = self.install(source=source)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["reason"], "source_assets_invalid")
        self.assertFalse(self.destination.exists())
        status.unlink()
        status.write_bytes(b"#" * 1048577)
        result = self.install(source=source)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["reason"], "source_assets_invalid")
        self.assertFalse(self.destination.exists())

    def test_publicly_writable_parent_fails_preflight_without_changes(self):
        parent = self.root / "writable parent"
        parent.mkdir(mode=0o777)
        parent.chmod(0o777)
        self.destination = parent / "runtime"
        before = self.fingerprint(parent)
        for arguments in (("--dry-run",), ()):
            result = self.install(*arguments)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["reason"], "unsafe_destination")
            self.assertEqual(before, self.fingerprint(parent))

    def test_writable_ancestor_above_private_parent_is_rejected(self):
        ancestor = self.root / "writable ancestor"
        ancestor.mkdir()
        ancestor.chmod(0o777)
        parent = ancestor / "private parent"
        parent.mkdir(mode=0o700)
        self.destination = parent / "runtime"
        before = self.fingerprint(ancestor)
        result = self.install("--dry-run")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["reason"], "unsafe_destination")
        self.assertEqual(before, self.fingerprint(ancestor))

    def test_root_sticky_temporary_ancestor_with_private_child_is_supported(self):
        with tempfile.TemporaryDirectory(prefix="t3c-sticky-", dir="/tmp") as temporary:
            self.destination = Path(temporary).resolve() / "runtime"
            self.assertEqual(self.install().returncode, 0)
            self.assertEqual(self.command("--version").returncode, 0)

    def test_compatible_native_helper_update_installs_and_runs(self):
        source = self.copy_source()
        helper = source / "hooks/runtime/scan_native_file.py"
        helper.write_bytes(helper.read_bytes() + b"\n# Compatible canonical helper maintenance.\n")
        result = self.install(source=source)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        delivered = self.destination / "hooks/runtime/scan_native_file.py"
        self.assertEqual(delivered.read_bytes(), helper.read_bytes())
        manifest = json.loads((self.destination / "installation.json").read_text())
        self.assertEqual(manifest["files"]["hooks/runtime/scan_native_file.py"], hashlib.sha256(helper.read_bytes()).hexdigest())
        shutil.rmtree(source)
        repository = self.root / "updated native repository"
        repository.mkdir()
        self.assertEqual(self.invoke(["git", "init", "-q", str(repository)]).returncode, 0)
        (repository / "notes.txt").write_text("ordinary updated text\n")
        self.assertEqual(self.command("check", "--repo", str(repository), "--json").returncode, 0)
        self.assertEqual(self.command("status", "--repo", str(repository), "--json").returncode, 0)

    def test_unsupported_native_handle_api_preserves_existing_bundle(self):
        self.assertEqual(self.install().returncode, 0)
        before = self.fingerprint(self.destination)
        source = self.copy_source()
        (source / "hooks/runtime/scan_native_file.py").write_text("class WindowsDirectoryHandles:\n    def __init__(self, resources): pass\n")
        result = self.install(source=source)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["reason"], "source_assets_invalid")
        self.assertEqual(before, self.fingerprint(self.destination))

    def expand_source_closure(self, count):
        source = self.copy_source()
        extra = ["scan_extra_" + str(index) for index in range(count)]
        cli = source / "hooks/runtime/scan_cli.py"
        cli.write_text(cli.read_text().replace("MODULES = (", "MODULES = (" + "".join(repr(name) + ", " for name in extra), 1))
        for name in extra:
            (source / "hooks/runtime" / (name + ".py")).write_text("# Compatible optional checkpoint module.\n")
        return source

    def test_oversized_or_reserved_closure_fails_before_first_install(self):
        source = self.expand_source_closure(46)
        before = self.fingerprint(self.root)
        result = self.install(source=source)
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertEqual(json.loads(result.stdout)["reason"], "source_assets_invalid")
        self.assertEqual(before, self.fingerprint(self.root))
        shutil.rmtree(source)
        for name in ("scan_cli", "scan_status", "scan_CLI", "scan_STATUS"):
            source = self.copy_source()
            cli = source / "hooks/runtime/scan_cli.py"
            cli.write_text(cli.read_text().replace("MODULES = (", "MODULES = (" + repr(name) + ", ", 1))
            before = self.fingerprint(self.root)
            result = self.install(source=source)
            self.assertEqual(result.returncode, 2, name)
            self.assertEqual(json.loads(result.stdout)["reason"], "source_assets_invalid")
            self.assertEqual(before, self.fingerprint(self.root))
            shutil.rmtree(source)

    def test_largest_supported_closure_installs_reinstalls_and_checks(self):
        source = self.expand_source_closure(45)
        result = self.install(source=source)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["asset_count"], 58)
        self.assertEqual(len(list(self.destination.rglob("*"))), 64)
        before = self.fingerprint(self.destination)
        self.assertEqual(self.install(source=source).returncode, 0)
        self.assertEqual(before, self.fingerprint(self.destination))
        shutil.rmtree(source)
        repository = self.root / "large closure repository"
        repository.mkdir()
        self.assertEqual(self.invoke(["git", "init", "-q", str(repository)]).returncode, 0)
        (repository / "notes.txt").write_text("ordinary expanded checkpoint\n")
        result = self.command("check", "--repo", str(repository), "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["outcome"], "complete_clean")

    def test_casefolded_module_collision_fails_before_any_mutation(self):
        for first, second in (("scan_extra_0", "scan_EXTRA_0"), ("scan_caf\u00e9", "scan_cafe\u0301")):
            source = self.expand_source_closure(2)
            cli = source / "hooks/runtime/scan_cli.py"
            raw = cli.read_text().replace("'scan_extra_0'", repr(first), 1).replace("'scan_extra_1'", repr(second), 1)
            cli.write_text(raw)
            for name in (first, second):
                (source / "hooks/runtime" / (name + ".py")).write_text("# Compatible optional checkpoint module.\n")
            before = self.fingerprint(self.root)
            result = self.install(source=source)
            self.assertEqual(result.returncode, 2, result.stdout)
            self.assertEqual(json.loads(result.stdout)["reason"], "source_assets_invalid")
            self.assertEqual(before, self.fingerprint(self.root))
            shutil.rmtree(source)

    def test_unowned_destination_and_backup_are_never_deleted(self):
        for location in (self.destination, self.destination.with_name(self.destination.name + ".previous")):
            location.mkdir(mode=0o700)
            owner_file = location / "owner-notes.txt"
            owner_file.write_bytes(b"unrelated owner bytes")
            owner_file.chmod(0o600)
            before = self.fingerprint(location)
            result = self.install()
            self.assertEqual(result.returncode, 2)
            self.assertEqual(before, self.fingerprint(location))
            shutil.rmtree(location)

    def test_linked_and_hardlinked_destinations_preserve_external_files(self):
        self.assertEqual(self.install().returncode, 0)
        external = self.root / "external"
        external.write_bytes(b"external bytes")
        original = (external.read_bytes(), external.stat().st_mode)
        entry = self.destination / "scan-secrets"
        entry.unlink()
        os.link(external, entry)
        self.assertEqual(self.install().returncode, 2)
        self.assertEqual(original, (external.read_bytes(), external.stat().st_mode))
        entry.unlink()
        entry.symlink_to(external)
        self.assertEqual(self.install().returncode, 2)
        self.assertEqual(original, (external.read_bytes(), external.stat().st_mode))
        entry.unlink()
        shutil.rmtree(self.destination)
        self.destination.symlink_to(self.home, target_is_directory=True)
        before = self.fingerprint(self.home)
        self.assertEqual(self.install().returncode, 2)
        self.assertEqual(before, self.fingerprint(self.home))

    def test_real_main_installers_preflight_missing_status_before_mutation(self):
        self.assertIsNotNone(shutil.which("pwsh"), "PowerShell is required")
        source = self.root / "complete source"
        shutil.copytree(SOURCE, source, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        (source / "hooks/runtime/scan_status.py").unlink()
        # Startup files are preinitialized so PowerShell startup is outside the fingerprint.
        self.invoke(["pwsh", "-NoProfile", "-Command", "exit 0"])
        before = self.fingerprint(self.home)
        for command in (["bash", str(source / "scripts/install.sh")], ["pwsh", "-NoProfile", "-File", str(source / "scripts/install.ps1")]):
            result = self.invoke(command)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source_assets_invalid", result.stderr)
            self.assertEqual(before, self.fingerprint(self.home))

    def test_install_delivers_independent_help(self):
        with tempfile.TemporaryDirectory(prefix="installed scanner ") as temporary:
            root = Path(temporary).resolve()
            destination = root / "private runtime"
            result = subprocess.run([PYTHON, "-I", "-S", "-B", str(SOURCE / "scripts/install-scan-secrets.py"), "install", "--destination", str(destination), "--json"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["outcome"], "installed")
            help_result = subprocess.run([str(destination / "scan-secrets"), "--help"], capture_output=True, text=True)
            self.assertEqual(help_result.returncode, 0, help_result.stderr)
            self.assertIn("check", help_result.stdout)

if __name__ == "__main__":
    unittest.main()
