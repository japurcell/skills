#!/usr/bin/env python3
"""Public-envelope tests for explicit RTK command rewriting."""

from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = {
    "copilot": ROOT / ".copilot/hooks/scripts/rtk-explicit-copilot.py",
    "gemini": ROOT / ".gemini/hooks/scripts/rtk-explicit-gemini.py",
    "codex": ROOT / ".codex/hooks/rtk-explicit-codex.py",
}


class ExplicitRtkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        binary = self.home / ".agents/rtk/dev-0.50.0-rc.451/rtk"
        binary.parent.mkdir(parents=True)
        binary.write_text("#!/bin/sh\nexit 0\n")
        binary.chmod(0o755)
        (binary.parent / "receipt.json").write_text(json.dumps({
            "tag": "dev-0.50.0-rc.451",
            "asset_sha256": "05a32507b07dc38bca835808deb8f32bd182446e8adc90b00209deda0404d321",
            "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        }))

    def run_hook(self, provider: str, command: str, *, tool: str | None = None) -> dict:
        if provider == "copilot":
            payload = {"toolName": tool or "bash", "toolArgs": {"command": command, "description": "keep"}}
        elif provider == "gemini":
            payload = {"hook_event_name": "BeforeTool", "tool_name": tool or "run_shell_command", "tool_input": {"command": command, "description": "keep"}}
        else:
            payload = {"hook_event_name": "PreToolUse", "tool_name": tool or "Bash", "tool_input": {"command": command, "description": "keep"}}
        result = subprocess.run(
            [sys.executable, str(SCRIPTS[provider])], input=json.dumps(payload), text=True,
            capture_output=True, env=os.environ | {"HOME": str(self.home)}, check=True,
        )
        return json.loads(result.stdout)

    def test_rewrites_explicit_command_and_preserves_chain(self) -> None:
        for provider in SCRIPTS:
            with self.subTest(provider=provider):
                output = self.run_hook(provider, "rtk read 'a b' && rtk --version")
                if provider == "copilot":
                    args = output["modifiedArgs"]
                else:
                    key = "tool_input" if provider == "gemini" else "updatedInput"
                    args = output["hookSpecificOutput"][key]
                self.assertEqual(args["description"], "keep")
                self.assertIn("rtk-agent-launcher.py", args["command"])
                self.assertEqual(args["command"].count("rtk-agent-launcher.py"), 2)
                self.assertIn("'a b' &&", args["command"])

    def test_quoted_prose_and_unsafe_syntax_are_unchanged(self) -> None:
        for provider in SCRIPTS:
            for command in ("echo 'rtk read file'", "rtk read file | cat", "echo $(rtk read file)"):
                with self.subTest(provider=provider, command=command):
                    self.assertEqual(self.run_hook(provider, command), {})

    def test_powershell_call_operator_rewrites_executable_path(self) -> None:
        binary = self.home / ".agents/rtk/dev-0.50.0-rc.451/rtk.exe"
        binary.write_bytes(b"fake Windows executable")
        (binary.parent / "receipt.json").write_text(json.dumps({
            "tag": "dev-0.50.0-rc.451",
            "asset_sha256": "636262ec8341455c09a3826329f90c92a57e2ef64d8761511eb123f1b84642d7",
            "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        }))
        output = self.run_hook("copilot", "& 'C:\\Tools\\rtk.exe' --version; Write-Output done", tool="powershell")
        self.assertIn("rtk-agent-launcher.py", output["modifiedArgs"]["command"])
        self.assertIn("; Write-Output done", output["modifiedArgs"]["command"])

    def test_missing_verified_binary_is_unchanged(self) -> None:
        (self.home / ".agents/rtk/dev-0.50.0-rc.451/rtk").unlink()
        self.assertEqual(self.run_hook("codex", "rtk read file"), {})

    def test_tampered_binary_is_unchanged(self) -> None:
        binary = self.home / ".agents/rtk/dev-0.50.0-rc.451/rtk"
        binary.write_text("#!/bin/sh\nexit 8\n")
        self.assertEqual(self.run_hook("codex", "rtk read file"), {})

    def test_launcher_preserves_streams_exit_and_child_scope(self) -> None:
        binary = self.home / ".agents/rtk/dev-0.50.0-rc.451/rtk"
        binary.write_text("#!/bin/sh\nprintf 'out:%s:%s\\n' \"$RTK_SUPPRESS_HOOK_WARNING\" \"$1\"\nprintf 'outdated-hook warning\\n' >&2\nexit 7\n")
        (binary.parent / "receipt.json").write_text(json.dumps({
            "tag": "dev-0.50.0-rc.451",
            "asset_sha256": "05a32507b07dc38bca835808deb8f32bd182446e8adc90b00209deda0404d321",
            "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        }))
        launcher = ROOT / ".codex/hooks/rtk-agent-launcher.py"
        result = subprocess.run([sys.executable, str(launcher), "argument"], text=True,
                                capture_output=True, env=os.environ | {"HOME": str(self.home)})
        self.assertEqual(result.returncode, 7)
        self.assertEqual(result.stdout, "out:1:argument\n")
        self.assertEqual(result.stderr, "outdated-hook warning\n")
        self.assertNotIn("RTK_SUPPRESS_HOOK_WARNING", os.environ)

    def test_installer_rejects_unpublished_archive(self) -> None:
        archive = self.home / "unpublished.tar.gz"
        archive.write_bytes(b"fake")
        other_home = self.home / "other"
        other_home.mkdir()
        result = subprocess.run([sys.executable, str(ROOT / "scripts/install-rtk-prerelease.py"),
                                 "--home", str(other_home), "--archive", str(archive),
                                 "--platform", "darwin-arm64"], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checksum mismatch", result.stderr)
        self.assertFalse((other_home / ".agents/rtk/dev-0.50.0-rc.451/receipt.json").exists())

    def test_provider_registrations_keep_automatic_forwarders(self) -> None:
        copilot = json.loads((ROOT / ".copilot/hooks/rtk-rewrite.json").read_text())
        for event in ("preToolUse", "PreToolUse"):
            commands = [entry["bash"] for entry in copilot["hooks"][event]]
            self.assertTrue(commands[0].endswith("rtk-hook-copilot.py"))
            self.assertTrue(commands[1].endswith("rtk-explicit-copilot.py"))
            self.assertIn("powershell", copilot["hooks"][event][1])
        gemini = json.loads((ROOT / ".gemini/global-settings.json").read_text())
        shell_group = next(group for group in gemini["hooks"]["BeforeTool"] if group.get("matcher") == "run_shell_command")
        self.assertTrue(shell_group["hooks"][0]["command"].endswith('rtk-hook-gemini.py"'))
        self.assertTrue(shell_group["hooks"][1]["command"].endswith('rtk-explicit-gemini.py"'))
        codex = json.loads((ROOT / ".codex/global-hooks.json").read_text())
        self.assertEqual(codex["hooks"]["PreToolUse"][0]["matcher"], "Bash")
        self.assertTrue(codex["hooks"]["PreToolUse"][0]["hooks"][0]["command"].endswith("rtk-explicit-codex.py"))


if __name__ == "__main__":
    unittest.main()
