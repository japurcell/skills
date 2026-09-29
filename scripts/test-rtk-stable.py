#!/usr/bin/env python3
"""Public CLI checks for stable RTK setup and migration in isolated homes."""
from __future__ import annotations
import os
import hashlib
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "scripts/configure-rtk.py"

class StableRtkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="rtk-stable-")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name).resolve()
        self.env = {**os.environ, "HOME": str(self.home), "USERPROFILE": str(self.home),
                    "APPDATA": str(self.home / "AppData/Roaming"), "PYTHONDONTWRITEBYTECODE": "1"}
        self.env.pop("RTK_SUPPRESS_HOOK_WARNING", None)
        binary_dir = self.home / "bin"
        binary_dir.mkdir()
        binary = binary_dir / ("rtk.cmd" if os.name == "nt" else "rtk")
        binary.write_text("@echo off\r\necho rtk 0.50.0\r\n" if os.name == "nt" else "#!/bin/sh\nprintf 'rtk 0.50.0\\n'\n")
        binary.chmod(0o755)
        self.env["PATH"] = str(binary_dir) + os.pathsep + self.env.get("PATH", "")

    def run_helper(self, *args):
        return subprocess.run([sys.executable, str(HELPER), "--home", str(self.home), *args],
                              env=self.env, capture_output=True, text=True, timeout=20)

    def config(self, platform="linux"):
        paths = {"linux": ".config/rtk/config.toml", "darwin": "Library/Application Support/rtk/config.toml",
                 "win32": "AppData/Roaming/rtk/config.toml"}
        return self.home / paths[platform]

    def test_changes_only_warning_setting_and_backs_up_original(self):
        path = self.config()
        path.parent.mkdir(parents=True)
        original = b'# personal settings\n[hooks] # hook preferences\nsuppress_hook_warning = false # retain comment\nexclude_commands = ["git rebase"]\n[display]\ncolors = false\n'
        path.write_bytes(original)
        result = self.run_helper("--platform", "linux")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(path.read_bytes(), original.replace(b"= false #", b"= true #"))
        self.assertEqual(path.with_suffix(".toml.bak").read_bytes(), original)
        if os.name != "nt":
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(path.with_suffix(".toml.bak").stat().st_mode), 0o600)
        before = path.stat().st_mtime_ns
        result = self.run_helper("--platform", "linux")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(path.stat().st_mtime_ns, before)
        self.assertEqual(path.with_suffix(".toml.bak").read_bytes(), original)

    def test_config_locations_and_read_only_preflight(self):
        for platform in ("linux", "darwin", "win32"):
            with self.subTest(platform=platform):
                result = self.run_helper("--platform", platform, "--check")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertFalse(self.config(platform).exists())
                result = self.run_helper("--platform", platform)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(tomllib.loads(self.config(platform).read_text()), {"hooks": {"suppress_hook_warning": True}})

    def test_malformed_and_ambiguous_config_remain_untouched(self):
        path = self.config()
        path.parent.mkdir(parents=True)
        for content in ('[hooks]\nsuppress_hook_warning = nope\n',
                        '[hooks]\nsuppress_hook_warning = "false"\n',
                        'hooks = { suppress_hook_warning = false }\n',
                        'hooks.suppress_hook_warning = false\n',
                        '[hooks]\nsuppress_hook_warning = false\nsuppress_hook_warning = true\n'):
            with self.subTest(content=content):
                path.write_text(content)
                result = self.run_helper("--platform", "linux")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(path.read_text(), content)
                self.assertFalse(path.with_suffix(".toml.bak").exists())

    def test_preserves_multiline_strings_and_crlf(self):
        path = self.config()
        path.parent.mkdir(parents=True)
        content = b'text = """\r\n[hooks]\r\nsuppress_hook_warning = false\r\n"""\r\n[hooks]\r\n# preserve me\r\n'
        path.write_bytes(content)
        result = self.run_helper("--platform", "linux")
        self.assertEqual(result.returncode, 0, result.stderr)
        expected = tomllib.loads(content.decode())
        expected["hooks"]["suppress_hook_warning"] = True
        self.assertEqual(tomllib.loads(path.read_text()), expected)
        self.assertEqual(path.with_suffix(".toml.bak").read_bytes(), content)

    def test_correct_inline_configuration_is_byte_identical(self):
        path = self.config()
        path.parent.mkdir(parents=True)
        content = b'hooks = { suppress_hook_warning = true } # keep layout\n'
        path.write_bytes(content)
        before = path.stat().st_mtime_ns
        result = self.run_helper("--platform", "linux")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(path.read_bytes(), content)
        self.assertEqual(path.stat().st_mtime_ns, before)
        self.assertFalse(path.with_suffix(".toml.bak").exists())

    def test_explicit_stable_command_keeps_output_diagnostics_and_exit(self):
        real_rtk = shutil.which("rtk")
        if not real_rtk:
            self.skipTest("stable RTK is not installed")
        self.env["PATH"] = os.environ.get("PATH", "")
        result = self.run_helper("--platform", sys.platform)
        self.assertEqual(result.returncode, 0, result.stderr)
        version = subprocess.run(["rtk", "--version"], env=self.env, capture_output=True, text=True)
        self.assertEqual(version.returncode, 0)
        self.assertRegex(version.stdout, r"rtk \d+\.\d+\.\d+")
        self.assertNotIn("No hook installed", version.stderr)
        missing = subprocess.run(["rtk", "read", str(self.home / "absent-file")],
                                 env=self.env, capture_output=True, text=True)
        self.assertNotEqual(missing.returncode, 0)
        self.assertEqual(missing.stdout, "")
        self.assertIn("absent-file", missing.stderr)
        self.assertNotIn("No hook installed", missing.stderr)

    def test_version_preflight_stops_before_any_destination_mutation(self):
        binary_dir = self.home / "bin"
        (binary_dir / ("rtk.cmd" if os.name == "nt" else "rtk")).unlink()
        self.env["PATH"] = str(binary_dir)
        cases = (None, "rtk 0.49.9", "rtk 0.50.0-rc.451", "some other tool 2.0.0")
        for version in cases:
            with self.subTest(version=version):
                if version is not None:
                    script = binary_dir / ("rtk.cmd" if os.name == "nt" else "rtk")
                    script.write_text(("@echo off\r\necho " + version + "\r\n") if os.name == "nt" else ("#!/bin/sh\nprintf '%s\\n' '" + version + "'\n"))
                    script.chmod(0o755)
                result = self.run_helper("--platform", "linux")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("0.50.0", result.stderr)
                self.assertFalse(self.config().exists())
                self.assertFalse((self.home / ".agents").exists())

    def test_existing_backup_is_never_overwritten(self):
        path = self.config()
        path.parent.mkdir(parents=True)
        path.write_text("[hooks]\nsuppress_hook_warning = false\n")
        backup = path.with_suffix(".toml.bak")
        backup.write_text("older backup\n")
        result = self.run_helper("--platform", "linux")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(path.read_text(), "[hooks]\nsuppress_hook_warning = false\n")
        self.assertEqual(backup.read_text(), "older backup\n")

    def test_linked_destination_is_not_followed(self):
        if os.name == "nt":
            self.skipTest("symlink creation may require Windows privilege")
        target = self.home / "personal.toml"
        target.write_text("[hooks]\nsuppress_hook_warning = false\n")
        path = self.config()
        path.parent.mkdir(parents=True)
        path.symlink_to(target)
        result = self.run_helper("--platform", "linux")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(target.read_text(), "[hooks]\nsuppress_hook_warning = false\n")
        self.assertTrue(path.is_symlink())

    def test_retirement_removes_only_verified_owned_files(self):
        changed = self.home / ".gemini/hooks/scripts/rtk-agent-launcher.py"
        changed.parent.mkdir(parents=True)
        changed.write_text("personal file\n")
        bundle = self.home / ".agents/rtk/dev-0.50.0-rc.451"
        bundle.mkdir(parents=True)
        binary = bundle / "rtk"
        binary.write_bytes(b"receipt-owned-test-binary")
        (bundle / "receipt.json").write_text(json.dumps({
            "tag": "dev-0.50.0-rc.451",
            "asset": "rtk-aarch64-apple-darwin.tar.gz",
            "asset_sha256": "05a32507b07dc38bca835808deb8f32bd182446e8adc90b00209deda0404d321",
            "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        }))
        result = self.run_helper("--platform", "linux", "--check")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_helper("--platform", "linux")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(bundle.exists(), result.stderr)
        self.assertEqual(changed.read_text(), "personal file\n")
        self.assertIn("manual review", result.stderr)
        bundle.mkdir()
        binary = bundle / "rtk"
        binary.write_bytes(b"modified binary")
        (bundle / "receipt.json").write_text(json.dumps({
            "tag": "dev-0.50.0-rc.451", "asset": "unknown asset",
            "asset_sha256": "05a32507b07dc38bca835808deb8f32bd182446e8adc90b00209deda0404d321",
            "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        }))
        result = self.run_helper("--platform", "linux")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(bundle.exists())
        self.assertIn("manual review", result.stderr)

    def test_installers_apply_config_before_copying(self):
        commands = []
        if os.name != "nt":
            commands.append([shutil.which("bash"), str(ROOT / "scripts/install.sh")])
        if shutil.which("pwsh"):
            commands.append([shutil.which("pwsh"), "-NoProfile", "-File", str(ROOT / "scripts/install.ps1")])
        self.assertTrue(commands, "No installer shell available")
        for index, command in enumerate(commands):
            with self.subTest(installer=command[0]):
                home = self.home / str(index)
                home.mkdir()
                env = {**self.env, "HOME": str(home), "USERPROFILE": str(home), "APPDATA": str(home / "AppData/Roaming")}
                env.pop("CODEX_HOME", None)
                result = subprocess.run(command, env=env, text=True, capture_output=True, timeout=120)
                self.assertEqual(result.returncode, 0, result.stderr)
                relative = {"darwin": "Library/Application Support/rtk/config.toml", "win32": "AppData/Roaming/rtk/config.toml"}.get(sys.platform, ".config/rtk/config.toml")
                path = home / relative
                self.assertTrue(path.is_file(), result.stdout)
                self.assertTrue(tomllib.loads(path.read_text())["hooks"]["suppress_hook_warning"])
                self.assertTrue((home / ".copilot/hooks/scripts/rtk-hook-copilot.py").is_file())
                self.assertTrue((home / ".gemini/hooks/scripts/rtk-hook-gemini.py").is_file())

    def test_installers_reject_old_rtk_before_installed_file_changes(self):
        binary = self.home / "bin" / ("rtk.cmd" if os.name == "nt" else "rtk")
        binary.write_text("@echo off\r\necho rtk 0.49.9\r\n" if os.name == "nt" else "#!/bin/sh\nprintf 'rtk 0.49.9\\n'\n")
        commands = []
        if os.name != "nt":
            commands.append([shutil.which("bash"), str(ROOT / "scripts/install.sh")])
        if shutil.which("pwsh"):
            commands.append([shutil.which("pwsh"), "-NoProfile", "-File", str(ROOT / "scripts/install.ps1")])
        for index, command in enumerate(commands):
            with self.subTest(installer=command[0]):
                home = self.home / f"old-{index}"
                home.mkdir()
                env = {**self.env, "HOME": str(home), "USERPROFILE": str(home),
                       "APPDATA": str(home / "AppData/Roaming")}
                result = subprocess.run(command, env=env, text=True, capture_output=True, timeout=30)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("0.50.0", result.stderr)
                for destination in (".agents", ".codex", ".copilot", ".gemini",
                                    "Library/Application Support/rtk/config.toml", ".config/rtk/config.toml",
                                    "AppData/Roaming/rtk/config.toml"):
                    self.assertFalse((home / destination).exists(), destination)

if __name__ == "__main__":
    unittest.main()
