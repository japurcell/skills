#!/usr/bin/env python3
"""Public generated-hook checks for touched Markdown validation."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
HOOKS = {
    "copilot": ROOT / ".copilot/hooks/scripts/markdown-health.py",
    "gemini": ROOT / ".gemini/hooks/scripts/markdown-health.py",
    "codex": ROOT / ".codex/hooks/markdown-health.py",
}


class MarkdownHealthTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "workspace"
        self.root.mkdir()
        self.state = Path(self.temp.name) / "state"
        self.audit = Path(self.temp.name) / "audit.log"

    def run_hook(self, provider: str, event: str, *, tool: str = "Bash", args: dict | None = None) -> dict:
        if provider == "copilot":
            payload = {"sessionId": "test-session", "cwd": str(self.root), "toolName": tool,
                       "toolArgs": args or {}, "stop_hook_active": False}
        else:
            payload = {"session_id": "test-session", "cwd": str(self.root),
                       "hook_event_name": event, "tool_name": tool,
                       "tool_input": args or {}, "stop_hook_active": False}
        environment = os.environ.copy()
        environment.update(MARKDOWN_HEALTH_EVENT=event, MARKDOWN_HEALTH_STATE_DIR=str(self.state),
                           AUDIT_LOG=str(self.audit))
        completed = subprocess.run([sys.executable, str(HOOKS[provider])], input=json.dumps(payload),
                                   text=True, capture_output=True, env=environment, timeout=10)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def test_broken_local_link_after_shell_edit_and_one_audit_line(self) -> None:
        for provider in HOOKS:
            with self.subTest(provider=provider):
                self.state.mkdir(exist_ok=True)
                self.run_hook(provider, "pre")
                (self.root / "guide.md").write_text("[missing](absent.md)\n", encoding="utf-8")
                result = self.run_hook(provider, "post")
                self.assertIn("guide.md", json.dumps(result))
                self.assertIn("absent.md", json.dumps(result))
                lines = self.audit.read_text().splitlines()
                self.assertEqual(len(lines), 1)
                self.assertIn("status=fail", lines[0])
                self.assertNotIn("absent.md", lines[0])
                self.audit.unlink()
                for item in self.state.iterdir():
                    item.unlink()
                (self.root / "guide.md").unlink()

    def test_clean_remote_and_untouched_file(self) -> None:
        (self.root / "untouched.md").write_text("[broken](missing.md)\n", encoding="utf-8")
        self.run_hook("copilot", "pre")
        (self.root / "new.md").write_text("[remote](https://example.invalid/no-request)\n", encoding="utf-8")
        result = self.run_hook("copilot", "post")
        self.assertNotIn("untouched.md", json.dumps(result))
        self.assertIn("status=pass", self.audit.read_text())
        self.run_hook("copilot", "final")
        self.assertEqual(len(self.audit.read_text().splitlines()), 1)

    def test_provider_registration_has_pre_post_and_final_events(self) -> None:
        paths = {
            "copilot": ROOT / ".copilot/hooks/hooks.json",
            "gemini": ROOT / ".gemini/global-settings.json",
            "codex": ROOT / ".codex/global-hooks.json",
        }
        events = {
            "copilot": ("preToolUse", "postToolUse", "agentStop"),
            "gemini": ("BeforeTool", "AfterTool", "AfterAgent"),
            "codex": ("PreToolUse", "PostToolUse", "Stop"),
        }
        for provider, path in paths.items():
            settings = json.loads(path.read_text())
            for event in events[provider]:
                with self.subTest(provider=provider, event=event):
                    handlers = settings["hooks"][event]
                    if provider != "copilot":
                        handlers = [hook for group in handlers for hook in group["hooks"]]
                    self.assertTrue(any("markdown-health.py" in json.dumps(hook) for hook in handlers))

    def test_parser_ignores_code_and_checks_references_and_duplicate_slugs(self) -> None:
        (self.root / "target.md").write_text("# Repeat\n# Repeat\n", encoding="utf-8")
        self.run_hook("copilot", "pre")
        (self.root / "new.md").write_text(
            "`[ignore](lost.md)`\n```md\n[ignore](lost.md)\n```\n"
            "[good](target.md#repeat-1)\n[bad][undefined]\n",
            encoding="utf-8",
        )
        result = self.run_hook("copilot", "post")
        output = json.dumps(result)
        self.assertIn("undefined reference", output)
        self.assertNotIn("lost.md", output)
        self.assertNotIn("missing heading fragment", output)

    def test_outside_workspace_is_reported_without_becoming_failure(self) -> None:
        self.run_hook("gemini", "pre")
        (self.root / "new.md").write_text("[outside](../outside.md)\n", encoding="utf-8")
        result = self.run_hook("gemini", "post")
        self.assertIn("outside workspace, not checked", json.dumps(result))
        self.assertIn("status=pass", self.audit.read_text())

    def test_audit_failure_does_not_change_failure_status(self) -> None:
        self.run_hook("copilot", "pre")
        (self.root / "new.md").write_text("[broken](missing.md)\n", encoding="utf-8")
        self.audit.mkdir()
        result = self.run_hook("copilot", "post")
        self.assertIn("missing local target", json.dumps(result))
        self.assertIn("audit unavailable", json.dumps(result))

    def test_missing_baseline_is_incomplete(self) -> None:
        (self.root / "new.md").write_text("[broken](missing.md)\n", encoding="utf-8")
        result = self.run_hook("codex", "final")
        self.assertIn("incomplete", json.dumps(result))
        self.assertFalse(self.audit.exists())

    @unittest.skipUnless(os.name == "nt", "native Windows path case")
    def test_native_windows_absolute_tool_path(self) -> None:
        self.run_hook("codex", "pre")
        target = self.root / "windows.markdown"
        target.write_text("[missing](missing%20name.md)\n", encoding="utf-8")
        result = self.run_hook("codex", "post", tool="Write", args={"file_path": str(target)})
        self.assertIn("windows.markdown", json.dumps(result))
        self.assertIn("missing%20name.md", json.dumps(result))

    def test_final_check_catches_later_edit_and_limits_retries(self) -> None:
        self.run_hook("codex", "pre")
        (self.root / "new.md").write_text("okay\n", encoding="utf-8")
        self.run_hook("codex", "post")
        (self.root / "new.md").write_text("[bad](gone.md)\n", encoding="utf-8")
        first = self.run_hook("codex", "final")
        second = self.run_hook("codex", "final")
        third = self.run_hook("codex", "final")
        self.assertEqual(first["decision"], "block")
        self.assertEqual(second["decision"], "block")
        self.assertEqual(third["decision"], "allow")
        self.assertEqual(len(self.audit.read_text().splitlines()), 2)

    def test_unclosed_fence_and_missing_heading_fragment(self) -> None:
        (self.root / "target.md").write_text("# Existing\n", encoding="utf-8")
        self.run_hook("gemini", "pre")
        (self.root / "new.md").write_text("[bad](target.md#lost)\n```python\n", encoding="utf-8")
        result = self.run_hook("gemini", "post")
        self.assertIn("missing heading fragment", json.dumps(result))
        self.assertIn("unclosed fence", json.dumps(result))

    def test_encoded_and_balanced_destinations(self) -> None:
        (self.root / "name (one).md").write_text("# Good\n", encoding="utf-8")
        self.run_hook("copilot", "pre")
        (self.root / "new.md").write_text(
            "[good](<name%20(one).md#good>)\n"
            "[also good](name%20\\(one\\).md#good)\n"
            "[bad](<name%20(one).md#lost>)\n",
            encoding="utf-8",
        )
        result = self.run_hook("copilot", "post")
        output = json.dumps(result)
        self.assertEqual(output.count("missing heading fragment"), 1)
        self.assertNotIn("missing local target", output)

    def test_large_batch_audit_is_one_bounded_line_with_omitted_count(self) -> None:
        self.run_hook("codex", "pre")
        for index in range(120):
            (self.root / (f"{index:03d}-" + "x" * 48 + ".md")).write_text("okay\n", encoding="utf-8")
        self.run_hook("codex", "post")
        lines = self.audit.read_bytes().splitlines()
        self.assertEqual(len(lines), 1)
        self.assertLessEqual(len(lines[0]) + 1, 4096)
        self.assertIn(b"checked=120", lines[0])
        self.assertRegex(lines[0].decode(), r"omitted=[1-9][0-9]*")

    def test_many_findings_have_bounded_provider_response(self) -> None:
        self.run_hook("gemini", "pre")
        for index in range(25):
            name = f"{index:03d}-" + "long" * 42 + ".md"
            (self.root / name).write_text("[bad](missing.md)\n", encoding="utf-8")
        result = self.run_hook("gemini", "post")
        self.assertLessEqual(len(json.dumps(result, separators=(",", ":")).encode()), 8192)
        displayed = result["systemMessage"].count("missing local target")
        self.assertLessEqual(displayed, 20)
        self.assertIn(f"{25-displayed} more findings omitted", result["systemMessage"])

    def test_explicit_rerun_command_checks_named_file_without_session(self) -> None:
        (self.root / "new.md").write_text("[bad](missing.md)\n", encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(HOOKS["codex"]), "--check", "new.md"],
            cwd=self.root, text=True, capture_output=True, timeout=10,
        )
        self.assertEqual(completed.returncode, 1)
        self.assertIn("new.md:1: missing local target", completed.stdout)


if __name__ == "__main__":
    unittest.main()
