#!/usr/bin/env python3
"""Public process checks for independently copied brain hooks."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import shlex
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BrainHooksTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="brain hooks ")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name).resolve()
        self.vault = self.directory / "brain"
        self.vault.mkdir()

    def invoke(self, name, payload, provider="copilot"):
        source = ROOT / ".github/hooks/scripts" / (name + ".py")
        copied = self.directory / source.name
        shutil.copyfile(source, copied)
        return subprocess.run(
            [sys.executable, "-I", "-S", "-B", str(copied), "--provider", provider],
            input=json.dumps(payload).encode(), capture_output=True,
            cwd=self.directory, timeout=5,
        )

    def successful_tool(self):
        return {"cwd": str(self.directory), "toolName": "bash",
                "toolResult": {"resultType": "success", "textResultForLlm": "done"}}

    def test_project_launches_work_from_nested_directory_without_git(self):
        (self.vault / "note.md").touch()
        nested = self.directory / "nested"
        nested.mkdir()
        for provider, config, start, field, relative in (
            ("copilot", ".github/hooks/hooks.json", "sessionStart", "bash", ".github/hooks/scripts"),
            ("codex", ".codex/hooks.json", "SessionStart", "command", ".codex/hooks"),
            ("gemini", ".gemini/settings.json", "SessionStart", "command", ".gemini/hooks/scripts"),
        ):
            with self.subTest(provider=provider):
                hooks = json.loads((ROOT / config).read_text(encoding="utf-8"))["hooks"]
                entries = hooks.get(start, [])
                handlers = entries if provider == "copilot" else [h for g in entries for h in g["hooks"]]
                matches = [h for h in handlers if "inject-brain.py" in h.get(field, "")]
                self.assertEqual(len(matches), 1)
                assets = self.directory / relative
                assets.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative / "inject-brain.py", assets / "inject-brain.py")
                arguments = shlex.split(matches[0][field])
                self.assertEqual(arguments[1], "-c")
                result = subprocess.run([sys.executable, *arguments[1:]], cwd=nested,
                                        input=json.dumps({"cwd": str(nested), "source": "startup",
                                                          "hook_event_name": start}).encode(),
                                        capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stderr)
                output = json.loads(result.stdout.splitlines()[-1])
                context = output.get("additionalContext") or output["hookSpecificOutput"]["additionalContext"]
                self.assertIn("[[note]]", context)

    def test_installed_brain_launches_are_pinned_and_reinstall_is_idempotent(self):
        for provider in ("codex", "copilot", "gemini"):
            with self.subTest(provider=provider):
                home = self.directory / ("home " + provider)
                home.mkdir()
                source = ROOT / (".codex/hooks" if provider == "codex" else "." + provider + "/hooks/scripts")
                assets = home / (".codex/hooks" if provider == "codex" else "." + provider + "/hooks/scripts")
                assets.mkdir(parents=True)
                for name in ("scan-status.py", "inject-brain.py", "auto-index-brain.py"):
                    shutil.copyfile(source / name, assets / name)
                template = ROOT / {"codex": ".codex/global-hooks.json", "copilot": ".copilot/hooks/hooks.json", "gemini": ".gemini/global-settings.json"}[provider]
                destination = home / (".codex/hooks.json" if provider == "codex" else "." + provider + "/settings.json")
                destination.write_text('{"custom": "keep", "hooks": {}}')
                installer = "install-codex-hooks.py" if provider == "codex" else "install-provider-hooks.py"
                command = [sys.executable, str(ROOT / "scripts" / installer), "--template", str(template), "--destination", str(destination)]
                if provider != "codex":
                    command += ["--provider", provider, "--home", str(home)]
                result = subprocess.run(command, capture_output=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                first = destination.read_bytes()
                doc = json.loads(first)
                self.assertEqual(doc["custom"], "keep")
                launches = []
                for entries in doc["hooks"].values():
                    for entry in entries:
                        launches.extend([entry] if provider == "copilot" else entry["hooks"])
                for name in ("inject-brain.py", "auto-index-brain.py"):
                    field = "bash" if provider == "copilot" else "command"
                    matches = [h for h in launches if name in h.get(field, "")]
                    self.assertEqual(len(matches), 1)
                    launch = matches[0][field]
                    self.assertIn(str(sys.executable), launch)
                    self.assertIn(str(assets / name), launch)
                    self.assertTrue(launch.endswith("--provider " + provider))
                    self.assertIn(" -I -S -B ", launch)
                result = subprocess.run(command, capture_output=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(destination.read_bytes(), first)

    def test_supported_resets_load_index_with_safe_startup_status(self):
        (self.vault / "private-name.md").touch()
        for provider, sources in (("codex", ("startup", "resume", "clear", "compact", "fork")),
                                  ("copilot", ("startup", "resume", "new")),
                                  ("gemini", ("startup", "resume", "clear"))):
            for source in sources:
                with self.subTest(provider=provider, source=source):
                    event = "sessionStart" if provider == "copilot" else "SessionStart"
                    result = self.invoke("inject-brain", {"cwd": str(self.directory), "source": source,
                                         "hook_event_name": event}, provider)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    documents = [json.loads(line) for line in result.stdout.splitlines()]
                    if provider == "copilot":
                        self.assertEqual(documents[0], {"type": "progress", "message": "inject-brain: pass; index loaded"})
                        context = documents[-1]["additionalContext"]
                    else:
                        self.assertEqual(documents[-1]["systemMessage"], "inject-brain: pass; index loaded")
                        context = documents[-1]["hookSpecificOutput"]["additionalContext"]
                    self.assertIn("[[private-name]]", context)

    def test_maintained_templates_register_startup_and_completion(self):
        for provider, relative, start, completed, field in (
            ("codex", ".codex/global-hooks.json", "SessionStart", "PostToolUse", "command"),
            ("copilot", ".copilot/hooks/hooks.json", "sessionStart", "postToolUse", "bash"),
            ("gemini", ".gemini/global-settings.json", "SessionStart", "AfterTool", "command"),
        ):
            hooks = json.loads((ROOT / relative).read_text(encoding="utf-8"))["hooks"]
            for event, name in ((start, "inject-brain.py"), (completed, "auto-index-brain.py")):
                entries = hooks.get(event, [])
                handlers = entries if provider == "copilot" else [h for g in entries for h in g["hooks"]]
                owned = [h for h in handlers if name in h.get(field, "")]
                self.assertEqual(len(owned), 1, (provider, event))
                self.assertTrue(owned[0][field].endswith("--provider " + provider))

    def test_completion_policy_respects_each_provider_result(self):
        (self.vault / "note.md").touch()
        cases = (
            ("copilot", {"hookEventName": "postToolUse", "toolResult": {"resultType": "failure"}}, False),
            ("copilot", {"hookEventName": "postToolUse", "toolResult": {"resultType": "success"}}, True),
            ("codex", {"hook_event_name": "PostToolUse", "tool_response": {"exit_code": 1}}, True),
            ("gemini", {"hook_event_name": "AfterTool", "tool_response": {"error": "failed"}}, False),
            ("gemini", {"hook_event_name": "AfterTool", "tool_response": {"output": "done"}}, True),
            ("codex", {"hook_event_name": "PreToolUse"}, False),
        )
        for provider, payload, expected in cases:
            with self.subTest(provider=provider, payload=payload):
                (self.vault / "index.md").unlink(missing_ok=True)
                result = self.invoke("auto-index-brain", {"cwd": str(self.directory), **payload}, provider)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout), {})
                self.assertEqual((self.vault / "index.md").exists(), expected)

    def test_copied_indexer_discovers_nested_notes_without_reading_bodies(self):
        (self.vault / "principles.md").write_text("private body must stay out")
        (self.vault / "codebase").mkdir()
        (self.vault / "codebase/index.md").write_text("curated subindex")
        (self.vault / "codebase/café.md").write_text("another private body")
        result = self.invoke("auto-index-brain", self.successful_tool())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {})
        self.assertEqual((self.vault / "index.md").read_text(encoding="utf-8"),
                         "# Brain\n\n## Root\n\n- [[principles]]\n\n## codebase\n\n"
                         "- [[codebase/café]]\n- [[codebase/index]]\n")
        self.assertEqual((self.vault / "codebase/index.md").read_text(encoding="utf-8"), "curated subindex")

    def test_linked_notes_and_directories_never_enter_inventory(self):
        outside = self.directory / "outside"
        outside.mkdir()
        (outside / "secret.md").write_text("outside")
        try:
            (self.vault / "linked").symlink_to(outside, target_is_directory=True)
            (self.vault / "secret.md").symlink_to(outside / "secret.md")
        except OSError as error:
            if sys.platform == "win32":
                self.skipTest("Windows symlink privilege unavailable: " + str(error))
            raise
        (self.vault / "safe.md").write_text("safe")
        result = self.invoke("auto-index-brain", self.successful_tool())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.vault / "index.md").read_text(encoding="utf-8"), "# Brain\n\n## Root\n\n- [[safe]]\n")

    def test_linked_index_is_preserved_without_touching_its_target(self):
        outside = self.directory / "outside.md"
        outside.write_text("untouched")
        try:
            (self.vault / "index.md").symlink_to(outside)
        except OSError as error:
            if sys.platform == "win32":
                self.skipTest("Windows symlink privilege unavailable: " + str(error))
            raise
        result = self.invoke("auto-index-brain", self.successful_tool())
        self.assertEqual(result.returncode, 0)
        self.assertEqual(outside.read_text(encoding="utf-8"), "untouched")
        self.assertTrue((self.vault / "index.md").is_symlink())
        self.assertIn(b"brain:", result.stderr)

    def test_busy_writer_preserves_previous_index_and_returns_promptly(self):
        (self.vault / "index.md").write_text("previous inventory")
        lock = self.vault / ".brain-index.lock"
        code = """import os, sys
f = open(sys.argv[1], 'a+b')
f.write(b'0'); f.flush(); f.seek(0)
if os.name == 'nt':
 import msvcrt
 msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
else:
 import fcntl
 fcntl.flock(f.fileno(), fcntl.LOCK_EX)
print('ready', flush=True)
sys.stdin.read()
"""
        writer = subprocess.Popen([sys.executable, "-c", code, str(lock)],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        try:
            self.assertEqual(writer.stdout.readline().strip(), b"ready")
            result = self.invoke("auto-index-brain", self.successful_tool())
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((self.vault / "index.md").read_text(encoding="utf-8"), "previous inventory")
            self.assertIn(b"brain:", result.stderr)
        finally:
            writer.communicate(timeout=3)

    def test_link_metacharacters_use_valid_encoded_markdown_destinations(self):
        (self.vault / "question#answer.md").write_text("note")
        (self.vault / "[draft].md").write_text("note")
        result = self.invoke("auto-index-brain", self.successful_tool())
        self.assertEqual(result.returncode, 0, result.stderr)
        index = (self.vault / "index.md").read_text(encoding="utf-8")
        self.assertIn("(<question%23answer.md>)", index)
        self.assertIn("(<%5Bdraft%5D.md>)", index)
        self.assertNotIn("[[question#answer]]", index)

    def test_startup_reconciles_before_returning_only_index_context(self):
        (self.vault / "note.md").write_text("never inject this note body")
        for provider in ("copilot", "codex", "gemini"):
            with self.subTest(provider=provider):
                (self.vault / "index.md").unlink(missing_ok=True)
                result = self.invoke("inject-brain", {"cwd": str(self.directory), "source": "startup"}, provider)
                self.assertEqual(result.returncode, 0, result.stderr)
                output = json.loads(result.stdout)
                expected = (self.vault / "index.md").read_text(encoding="utf-8")
                if provider == "copilot":
                    self.assertEqual(output, {"additionalContext": expected})
                else:
                    specific = {"additionalContext": expected}
                    if provider == "codex":
                        specific["hookEventName"] = "SessionStart"
                    self.assertEqual(output, {"hookSpecificOutput": specific})

    def test_large_index_keeps_full_inventory_but_injects_bounded_pointer(self):
        for number in range(200):
            (self.vault / (str(number) + "x" * 140 + ".md")).touch()
        result = self.invoke("inject-brain", {"cwd": str(self.directory), "source": "startup"}, "codex")
        self.assertEqual(result.returncode, 0, result.stderr)
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertLess(len(context.encode()), 24000)
        self.assertIn("brain/index.md", context)
        self.assertIn("too large", context)
        self.assertEqual((self.vault / "index.md").read_text(encoding="utf-8").count("- [["), 200)

    def test_oversized_inventory_preserves_previous_index(self):
        for number in range(3000):
            (self.vault / (str(number) + "x" * 180 + ".md")).touch()
        (self.vault / "index.md").write_text("previous inventory")
        result = self.invoke("auto-index-brain", self.successful_tool())
        self.assertEqual(result.returncode, 0)
        self.assertEqual((self.vault / "index.md").read_text(encoding="utf-8"), "previous inventory")
        self.assertIn(b"brain:", result.stderr)
        self.assertIn(b"inventory budget exceeded", result.stderr)

    def test_injector_ignores_prompt_and_tool_events(self):
        for provider in ("copilot", "codex", "gemini"):
            result = self.invoke("inject-brain", {"cwd": str(self.directory),
                                 "hook_event_name": "BeforeAgent", "source": "startup"}, provider)
            self.assertEqual(json.loads(result.stdout), {})
            self.assertFalse((self.vault / "index.md").exists())

    def test_each_provider_artifact_runs_when_copied_alone(self):
        (self.vault / "note.md").touch()
        for provider, relative in (("copilot", ".github/hooks/scripts"),
                                   ("copilot", ".copilot/hooks/scripts"),
                                   ("gemini", ".gemini/hooks/scripts"),
                                   ("codex", ".codex/hooks")):
            for name in ("auto-index-brain.py", "inject-brain.py"):
                with self.subTest(provider=provider, relative=relative, name=name):
                    copied = self.directory / name
                    shutil.copyfile(ROOT / relative / name, copied)
                    (self.vault / "index.md").unlink(missing_ok=True)
                    payload = {"cwd": str(self.directory), "source": "startup"} if name.startswith("inject") else self.successful_tool()
                    if provider == "gemini" and name.startswith("auto"):
                        payload = {"cwd": str(self.directory), "hook_event_name": "AfterTool", "tool_response": {"llmContent": "done"}}
                    result = subprocess.run([sys.executable, "-I", "-S", "-B", str(copied), "--provider", provider],
                                            input=json.dumps(payload).encode(), capture_output=True, timeout=5)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIsInstance(json.loads(result.stdout), dict)
                    self.assertIn("[[note]]", (self.vault / "index.md").read_text(encoding="utf-8"))

    def test_add_rename_delete_and_unchanged_runs_converge(self):
        note = self.vault / "first.md"
        note.touch()
        self.invoke("auto-index-brain", self.successful_tool())
        index = self.vault / "index.md"
        before = index.stat().st_mtime_ns
        self.invoke("auto-index-brain", self.successful_tool())
        self.assertEqual(index.stat().st_mtime_ns, before)
        note.rename(self.vault / "second.md")
        self.invoke("auto-index-brain", self.successful_tool())
        self.assertEqual(index.read_text(encoding="utf-8"), "# Brain\n\n## Root\n\n- [[second]]\n")
        (self.vault / "second.md").unlink()
        self.invoke("auto-index-brain", self.successful_tool())
        self.assertEqual(index.read_text(encoding="utf-8"), "# Brain\n")
        self.assertEqual(list(self.vault.glob(".brain-index-*")), [])

    def test_nested_cwd_worktree_marker_and_missing_vault_boundaries(self):
        nested = self.directory / "nested"
        nested.mkdir()
        (self.directory / ".git").write_text("gitdir: elsewhere")
        self.invoke("auto-index-brain", {**self.successful_tool(), "cwd": str(nested)})
        self.assertTrue((self.vault / "index.md").exists())
        (self.vault / "index.md").unlink()
        (nested / ".git").mkdir()
        self.invoke("auto-index-brain", {**self.successful_tool(), "cwd": str(nested)})
        self.assertFalse((self.vault / "index.md").exists())
        self.assertFalse((nested / "brain").exists())
        for cwd in (None, "relative", str(self.directory / "missing")):
            self.invoke("auto-index-brain", {"cwd": cwd})
            self.assertFalse((self.vault / "index.md").exists())

    def test_retained_stdin_finishes_for_complete_and_bad_inputs(self):
        source = ROOT / ".github/hooks/scripts/auto-index-brain.py"
        good = json.dumps(self.successful_tool()).encode()
        for raw in (good, b"", b'{"cwd":', good + b" trailing", b"[]", b'{"x":"\xff"}'):
            with self.subTest(raw=raw[:30]):
                (self.vault / "index.md").unlink(missing_ok=True)
                process = subprocess.Popen([sys.executable, "-I", "-S", str(source), "--provider", "copilot"],
                                           stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                try:
                    if raw:
                        process.stdin.write(raw)
                        process.stdin.flush()
                    process.wait(timeout=3)
                    self.assertEqual(process.returncode, 0)
                    self.assertEqual(json.loads(process.stdout.read()), {})
                    self.assertEqual((self.vault / "index.md").exists(), raw == good)
                finally:
                    if process.poll() is None:
                        process.kill()
                    process.communicate(timeout=2)

    def test_read_only_destination_preserves_index(self):
        if sys.platform == "win32":
            self.skipTest("POSIX mode fixture; Windows ACL coverage requires native ACL fixture")
        index = self.vault / "index.md"
        index.write_text("previous inventory")
        self.vault.chmod(0o555)
        try:
            result = self.invoke("auto-index-brain", self.successful_tool())
            self.assertEqual(result.returncode, 0)
            self.assertEqual(index.read_text(encoding="utf-8"), "previous inventory")
            self.assertIn(b"brain:", result.stderr)
        finally:
            self.vault.chmod(0o755)

    def test_unsupported_python_reports_prerequisite_without_mutation(self):
        executable = Path("/usr/bin/python3")
        if not executable.is_file():
            self.skipTest("No separate unsupported Python interpreter available")
        version = subprocess.check_output([str(executable), "-c", "import sys; print(sys.version_info.minor)"])
        if int(version) >= 12:
            self.skipTest("Separate interpreter is supported")
        result = subprocess.run([str(executable), "-I", "-S", str(ROOT / ".github/hooks/scripts/auto-index-brain.py"),
                                 "--provider", "copilot"], input=json.dumps(self.successful_tool()).encode(), capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout), {})
        self.assertIn(b"Python 3.12", result.stderr)
        self.assertFalse((self.vault / "index.md").exists())

    def test_malformed_startup_metadata_does_not_fail_the_session(self):
        result = self.invoke("inject-brain", {"cwd": str(self.directory), "source": {"invalid": True}})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {})
        self.assertFalse((self.vault / "index.md").exists())

    def test_concurrent_processes_leave_one_complete_inventory(self):
        (self.vault / "a.md").touch()
        (self.vault / "b.md").touch()
        script = ROOT / ".github/hooks/scripts/auto-index-brain.py"
        processes = []
        try:
            for _ in range(8):
                process = subprocess.Popen([sys.executable, "-I", "-S", str(script), "--provider", "copilot"],
                                           stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process.stdin.write(json.dumps(self.successful_tool()).encode())
                process.stdin.flush()
                processes.append(process)
            for process in processes:
                output, diagnostic = process.communicate(timeout=5)
                self.assertEqual(process.returncode, 0, diagnostic)
                self.assertEqual(json.loads(output), {})
        finally:
            for process in processes:
                if process.poll() is None:
                    process.kill()
                process.communicate(timeout=2)
        self.assertEqual((self.vault / "index.md").read_text(encoding="utf-8"),
                         "# Brain\n\n## Root\n\n- [[a]]\n- [[b]]\n")

    def test_linked_lock_never_changes_outside_content(self):
        outside = self.directory / "outside"
        outside.write_text("unchanged")
        try:
            (self.vault / ".brain-index.lock").symlink_to(outside)
        except OSError as error:
            if sys.platform == "win32":
                self.skipTest("Windows symlink privilege unavailable: " + str(error))
            raise
        result = self.invoke("auto-index-brain", self.successful_tool())
        self.assertEqual(result.returncode, 0)
        self.assertEqual(outside.read_text(encoding="utf-8"), "unchanged")
        self.assertFalse((self.vault / "index.md").exists())


if __name__ == "__main__":
    unittest.main()
