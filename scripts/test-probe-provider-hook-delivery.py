#!/usr/bin/env python3
"""Exercise the deployed hook probe through its public CLI in disposable homes."""

from __future__ import annotations

import json
import os
from pathlib import Path
import select
import stat
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parent / "probe-provider-hook-delivery.py"
EVENTS = {
    "codex": ("PreToolUse", "Stop"),
    "gemini": ("BeforeTool", "AfterTool", "AfterAgent"),
    "copilot": ("preToolUse", "postToolUse", "agentStop"),
}


class ProbeTests(unittest.TestCase):
    def cli(self, home: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            env={**os.environ, "HOME": str(home), "USERPROFILE": str(home)},
            text=True,
            capture_output=True,
            check=False,
        )

    def exercise(self, provider: str) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary) / "home"
            home.mkdir()
            paths = {
                "codex": home / ".codex/hooks.json",
                "gemini": home / ".gemini/settings.json",
                "copilot": home / ".copilot/hooks/hooks.json",
            }
            config = paths[provider]
            config.parent.mkdir(parents=True)
            original = {"userSetting": "preserve", "hooks": {"unrelated": [{"command": "echo user"}]}}
            original_bytes = (json.dumps(original, indent=4) + "\n").encode()
            config.write_bytes(original_bytes)

            prepared = self.cli(home, "prepare", "--provider", provider)
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            info = json.loads(prepared.stdout)
            self.assertEqual(Path(info["backup"]).read_bytes(), original_bytes)
            self.assertEqual(stat.S_IMODE(Path(info["marker"]).stat().st_mode), 0o600)
            self.assertEqual(json.loads(config.read_text())["userSetting"], "preserve")
            if provider == "codex":
                installed = json.loads(config.read_text(encoding="utf-8"))
                for event in EVENTS["codex"]:
                    self.assertNotIn("matcher", installed["hooks"][event][-1])

            transcript = Path(info["transcript"])
            with transcript.open("w", encoding="utf-8") as output:
                for event in EVENTS[provider]:
                    payload = {"hook_event_name": event, "session_id": "test", "cwd": str(home)}
                    if event in {"PreToolUse", "BeforeTool", "AfterTool"}:
                        payload.update(tool_name="Bash", tool_input={"command": "git status --short"})
                    if event == "AfterTool":
                        payload["tool_response"] = {}
                    if event in {"Stop", "AfterAgent"}:
                        payload["stop_hook_active"] = False
                    if event == "AfterAgent":
                        payload["prompt_response"] = "done"
                    if provider == "copilot":
                        payload = {"sessionId": "test", "cwd": str(home), "toolName": "shell", "toolArgs": {}}
                        if event == "postToolUse":
                            payload["toolResult"] = {"resultType": "success"}
                    call = subprocess.run(
                        [sys.executable, info["handler"], event],
                        input=json.dumps(payload), text=True, capture_output=True, check=False,
                    )
                    self.assertEqual(call.returncode, 0, call.stderr)
                    response = json.loads(call.stdout)
                    self.assertIsInstance(response, dict)
                    output.write(call.stdout)
            verified = self.cli(home, "verify", "--provider", provider, "--id", info["id"],
                                "--transcript", str(transcript))
            self.assertEqual(verified.returncode, 0, verified.stderr)

            cleaned = self.cli(home, "cleanup", "--provider", provider, "--id", info["id"])
            self.assertEqual(cleaned.returncode, 0, cleaned.stderr)
            self.assertEqual(config.read_bytes(), original_bytes)
            self.assertFalse(Path(info["backup"]).exists())

            concurrent = self.cli(home, "prepare", "--provider", provider)
            self.assertEqual(concurrent.returncode, 0, concurrent.stderr)
            concurrent_info = json.loads(concurrent.stdout)
            changed = json.loads(config.read_text(encoding="utf-8"))
            changed["newSetting"] = "concurrent edit"
            config.write_text(json.dumps(changed), encoding="utf-8")
            self.assertEqual(self.cli(home, "cleanup", "--provider", provider,
                                      "--id", concurrent_info["id"]).returncode, 0)
            expected = {**original, "newSetting": "concurrent edit"}
            self.assertEqual(json.loads(config.read_text(encoding="utf-8")), expected)
            concurrent_bytes = config.read_bytes()

            failed_run = self.cli(home, "prepare", "--provider", provider)
            self.assertEqual(failed_run.returncode, 0, failed_run.stderr)
            failed_info = json.loads(failed_run.stdout)
            failed_verify = self.cli(home, "verify", "--provider", provider, "--id", failed_info["id"],
                                     "--transcript", failed_info["transcript"])
            self.assertNotEqual(failed_verify.returncode, 0)
            self.assertEqual(self.cli(home, "cleanup", "--provider", provider, "--id", failed_info["id"]).returncode, 0)
            self.assertEqual(config.read_bytes(), concurrent_bytes)

    def test_codex(self) -> None:
        self.exercise("codex")

    def test_gemini(self) -> None:
        self.exercise("gemini")

    def test_copilot(self) -> None:
        self.exercise("copilot")

    def test_vscode_uses_local_command_keys_and_pascal_events(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            prepared = self.cli(home, "prepare", "--provider", "copilot", "--surface", "vscode")
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            info = json.loads(prepared.stdout)
            try:
                config = json.loads(Path(info["config"]).read_text(encoding="utf-8"))
                for event in ("PreToolUse", "PostToolUse", "Stop"):
                    entry = config["hooks"][event][-1]
                    self.assertIn("command", entry)
                    self.assertIn("windows", entry)
                    self.assertNotIn("bash", entry)
                    self.assertNotIn("powershell", entry)
            finally:
                self.assertEqual(self.cli(home, "cleanup", "--provider", "copilot", "--id", info["id"]).returncode, 0)

    def test_new_config_is_removed_on_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            prepared = self.cli(home, "prepare", "--provider", "codex")
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            info = json.loads(prepared.stdout)
            self.assertEqual(self.cli(home, "cleanup", "--provider", "codex", "--id", info["id"]).returncode, 0)
            self.assertFalse(Path(info["config"]).exists())

    @unittest.skipIf(os.name == "nt", "select does not support Windows pipes")
    def test_handler_reads_one_json_object_without_waiting_for_stdin_close(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            prepared = self.cli(home, "prepare", "--provider", "codex")
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            info = json.loads(prepared.stdout)
            try:
                process = subprocess.Popen([sys.executable, info["handler"], "PreToolUse"],
                                           stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, text=False)
                assert process.stdin is not None and process.stdout is not None
                payload = {"hook_event_name": "PreToolUse", "session_id": "test", "cwd": str(home),
                           "tool_name": "Bash", "tool_input": {}}
                process.stdin.write(json.dumps(payload).encode())
                process.stdin.flush()
                self.assertTrue(select.select([process.stdout], [], [], 2)[0], "handler waited for stdin EOF")
                self.assertIn("systemMessage", json.loads(process.stdout.readline()))
                process.stdin.close()
                self.assertEqual(process.wait(timeout=2), 0)
            finally:
                self.cli(home, "cleanup", "--provider", "codex", "--id", info["id"])

    def test_timeout_has_entry_markers_without_completed_response(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            prepared = self.cli(home, "prepare", "--provider", "codex", "--mode", "timeout",
                                "--timeout-seconds", "1", "--delay-seconds", "3")
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            info = json.loads(prepared.stdout)
            try:
                config = json.loads(Path(info["config"]).read_text(encoding="utf-8"))
                self.assertEqual(config["hooks"]["PreToolUse"][-1]["hooks"][0]["timeout"], 1)
                for event in EVENTS["codex"]:
                    payload = {"hook_event_name": event, "session_id": "test", "cwd": str(home)}
                    if event == "PreToolUse":
                        payload.update(tool_name="Bash", tool_input={})
                    else:
                        payload["stop_hook_active"] = False
                    with self.assertRaises(subprocess.TimeoutExpired):
                        subprocess.run([sys.executable, info["handler"], event],
                                       input=json.dumps(payload), text=True, capture_output=True, timeout=1.5)
                Path(info["transcript"]).write_text("Hook command timed out after 3 seconds", encoding="utf-8")
                verified = self.cli(home, "verify", "--provider", "codex", "--mode", "timeout",
                                    "--id", info["id"], "--transcript", info["transcript"])
                self.assertEqual(verified.returncode, 0, verified.stderr)
            finally:
                self.cli(home, "cleanup", "--provider", "codex", "--id", info["id"])


if __name__ == "__main__":
    unittest.main()
