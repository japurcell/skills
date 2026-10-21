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
        (nested / "pathlib.py").write_text("raise RuntimeError('cwd module imported')\n")
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
                result = subprocess.run([sys.executable, *arguments[1:]], cwd=nested,
                                        input=json.dumps({"cwd": str(nested), "source": "startup",
                                                          "hook_event_name": start}).encode(),
                                        capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stderr)
                output = json.loads(result.stdout.splitlines()[-1])
                context = output.get("additionalContext") or output["hookSpecificOutput"]["additionalContext"]
                self.assertIn("[[note]]", context)

    def test_project_launches_ignore_nested_scripts_inside_git_root(self):
        (self.directory / ".git").write_text("gitdir: elsewhere")
        nested = self.directory / "dependency"
        nested.mkdir()
        (nested / "pathlib.py").write_text("raise RuntimeError('cwd module imported')")
        (self.vault / "trusted.md").touch()
        for provider, config, field, relative in (
            ("copilot", ".github/hooks/hooks.json", "bash", ".github/hooks/scripts"),
            ("codex", ".codex/hooks.json", "command", ".codex/hooks"),
            ("gemini", ".gemini/settings.json", "command", ".gemini/hooks/scripts"),
        ):
            hooks = json.loads((ROOT / config).read_text())["hooks"]
            for event, entries in hooks.items():
                handlers = entries if provider == "copilot" else [h for g in entries for h in g["hooks"]]
                for handler in handlers:
                    command = handler.get(field, "")
                    for name in ("inject-brain.py", "auto-index-brain.py"):
                        if name not in command:
                            continue
                        with self.subTest(provider=provider, event=event):
                            for base in (self.directory, nested):
                                (base / relative).mkdir(parents=True, exist_ok=True)
                            shutil.copyfile(ROOT / relative / name, self.directory / relative / name)
                            (nested / relative / name).write_text("raise RuntimeError('nested hook executed')")
                            (self.vault / "index.md").unlink(missing_ok=True)
                            payload = {"cwd": str(nested), "source": "startup", "hook_event_name": event,
                                       "toolResult": {"resultType": "success"}, "tool_response": {"output": "done"}}
                            arguments = shlex.split(command)
                            result = subprocess.run([sys.executable, *arguments[1:]], cwd=nested,
                                                    input=json.dumps(payload).encode(), capture_output=True, timeout=5)
                            self.assertEqual(result.returncode, 0, result.stderr)
                            self.assertIn("[[trusted]]", (self.vault / "index.md").read_text())

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

    def test_project_registrations_run_startup_and_completion(self):
        (self.directory / "pathlib.py").write_text("raise RuntimeError('cwd module imported')\n")
        for provider, relative, start, completed, field in (
            ("codex", ".codex/hooks.json", "SessionStart", "PostToolUse", "command"),
            ("copilot", ".github/hooks/hooks.json", "sessionStart", "postToolUse", "bash"),
            ("gemini", ".gemini/settings.json", "SessionStart", "AfterTool", "command"),
        ):
            hooks = json.loads((ROOT / relative).read_text(encoding="utf-8"))["hooks"]
            for event, name in ((start, "inject-brain.py"), (completed, "auto-index-brain.py")):
                entries = hooks.get(event, [])
                handlers = entries if provider == "copilot" else [h for g in entries for h in g["hooks"]]
                owned = [h for h in handlers if name in h.get(field, "")]
                self.assertEqual(len(owned), 1, (provider, event))
                relative = {"copilot": ".github/hooks/scripts", "codex": ".codex/hooks",
                            "gemini": ".gemini/hooks/scripts"}[provider]
                assets = self.directory / relative
                assets.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative / name, assets / name)
                (self.vault / "registered-note.md").touch()
                (self.vault / "index.md").unlink(missing_ok=True)
                payload = {"cwd": str(self.directory), "source": "startup", "hook_event_name": event,
                           "toolResult": {"resultType": "success"}, "tool_response": {"output": "done"}}
                arguments = shlex.split(owned[0][field])
                result = subprocess.run([sys.executable, *arguments[1:]], cwd=self.directory,
                                        input=json.dumps(payload).encode(), capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("[[registered-note]]", (self.vault / "index.md").read_text())

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
        self.assertEqual(result.stderr, b"")
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

    def test_directory_replacement_during_scan_cannot_escape_vault(self):
        self.check_directory_replacement(use_symlink=True)

    def test_plain_directory_replacement_during_scan_cannot_redirect_writes(self):
        # This case also runs on Windows hosts without symlink privileges.
        self.check_directory_replacement(use_symlink=False)

    def check_directory_replacement(self, use_symlink):
        # Python's filesystem audit event coordinates another writer exactly
        # at the OS boundary, without mocking hook functions or timing sleeps.
        harness = r'''import json, os, pathlib, runpy, sys
script, target, outside, marker = map(pathlib.Path, sys.argv[1:5])
use_symlink = sys.argv[5] == 'symlink'
expected = target.stat()
attempted = False
def replace_directory(event, args):
    global attempted
    if event != 'os.scandir' or attempted:
        return
    candidate = args[0]
    actual = os.fstat(candidate) if isinstance(candidate, int) else os.stat(candidate)
    if not os.path.samestat(expected, actual):
        return
    attempted = True
    try:
        target.rename(target.with_name(target.name + '-saved'))
        if use_symlink:
            target.symlink_to(outside, target_is_directory=True)
        else:
            outside.rename(target)
    except PermissionError:
        # Windows directory handles deny replacement while in use.
        pass
sys.addaudithook(replace_directory)
if os.name == 'nt':
    # Wrap only the native enumeration boundary, always calling the real API.
    import ctypes
    from ctypes import wintypes
    original_dll = ctypes.WinDLL
    def load_dll(*args, **kwargs):
        library = original_dll(*args, **kwargs)
        if str(args[0]).lower() == 'kernel32':
            query = library.GetFileInformationByHandleEx
            query.argtypes = (wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD)
            query.restype = wintypes.BOOL
            def before_query(handle, kind, buffer, size):
                if kind == 19:
                    identity = ctypes.create_string_buffer(24)
                    if query(handle, 18, identity, 24) and int.from_bytes(identity.raw[8:], 'little') == expected.st_ino:
                        replace_directory('os.scandir', (target,))
                return query(handle, kind, buffer, size)
            library.GetFileInformationByHandleEx = before_query
        return library
    ctypes.WinDLL = load_dll
sys.argv = [str(script), '--provider', 'copilot']
try:
    runpy.run_path(str(script), run_name='__main__')
finally:
    marker.write_text(json.dumps({'attempted': attempted}))
'''
        for relative in (".", "queued"):
            with self.subTest(directory=relative), tempfile.TemporaryDirectory() as temporary:
                project = Path(temporary).resolve()
                vault = project / "brain"
                vault.mkdir()
                target = vault if relative == "." else vault / relative
                target.mkdir(exist_ok=True)
                (target / "safe.md").touch()
                outside = project / "outside"
                outside.mkdir()
                (outside / "private-leak.md").touch()
                (outside / "index.md").write_text("outside index unchanged")
                probe = project / "symlink-probe"
                if use_symlink:
                    try:
                        probe.symlink_to(outside, target_is_directory=True)
                        probe.unlink()
                    except OSError as error:
                        if sys.platform == "win32":
                            self.skipTest("Windows symlink privilege unavailable: " + str(error))
                        raise
                script = project / "auto-index-brain.py"
                shutil.copyfile(ROOT / ".github/hooks/scripts/auto-index-brain.py", script)
                marker = project / "attempt.json"
                payload = {"cwd": str(project), "toolResult": {"resultType": "success"}}
                result = subprocess.run(
                    [sys.executable, "-I", "-S", "-B", "-c", harness,
                     str(script), str(target), str(outside), str(marker),
                     "symlink" if use_symlink else "directory"],
                    input=json.dumps(payload).encode(), capture_output=True, timeout=5,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(json.loads(marker.read_text())["attempted"])
                self.assertEqual(json.loads(result.stdout), {})
                victim = outside if outside.exists() else target
                self.assertEqual((victim / "index.md").read_text(), "outside index unchanged")
                for directory in (vault, project / "brain-saved"):
                    index = directory / "index.md"
                    if index.exists() and not directory.is_symlink() and directory != victim:
                        self.assertNotIn("private-leak", index.read_text())

    @unittest.skipUnless(sys.platform == "win32", "requires native Windows reparse APIs")
    def test_in_place_junction_conversion_cannot_redirect_inventory_or_first_lock(self):
        harness = r'''import ctypes, json, pathlib, runpy, struct, sys
from ctypes import wintypes
script, target, outside, marker = map(pathlib.Path, sys.argv[1:5])
phase = sys.argv[5]
expected = target.stat().st_ino
original_dll = ctypes.WinDLL
kernel = original_dll('kernel32', use_last_error=True)
kernel.CreateFileW.argtypes = (wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE)
kernel.CreateFileW.restype = wintypes.HANDLE
kernel.DeviceIoControl.argtypes = (wintypes.HANDLE, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), wintypes.LPVOID)
kernel.DeviceIoControl.restype = wintypes.BOOL
kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
attempted = False
def convert():
    global attempted
    if attempted:
        return
    attempted = True
    handle = kernel.CreateFileW(str(target), 0x100, 7, None, 3, 0x2200000, None)
    if handle == wintypes.HANDLE(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    substitute = (chr(92) + '??' + chr(92) + str(outside)).encode('utf-16-le')
    display = str(outside).encode('utf-16-le')
    paths = substitute + b'\0\0' + display + b'\0\0'
    data = struct.pack('<IHHHHHH', 0xA0000003, 8 + len(paths), 0, 0, len(substitute), len(substitute) + 2, len(display)) + paths
    returned = wintypes.DWORD()
    try:
        if not kernel.DeviceIoControl(handle, 0x900A4, ctypes.create_string_buffer(data), len(data), None, 0, ctypes.byref(returned), None):
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        kernel.CloseHandle(handle)
    marker.write_text('converted')
def load_dll(*args, **kwargs):
    library = original_dll(*args, **kwargs)
    if str(args[0]).lower() == 'kernel32':
        query = library.GetFileInformationByHandleEx
        query.argtypes = (wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD)
        query.restype = wintypes.BOOL
        def before_query(handle, kind, buffer, size):
            if kind == 19 and phase == 'scan':
                identity = ctypes.create_string_buffer(24)
                if query(handle, 18, identity, 24) and int.from_bytes(identity.raw[8:], 'little') == expected:
                    convert()
            return query(handle, kind, buffer, size)
        library.GetFileInformationByHandleEx = before_query
    return library
ctypes.WinDLL = load_dll
# The open audit boundary precedes the original path-based first lock; the
# native function lookup precedes the replacement handle-relative first lock.
def before_open(event, args):
    if phase == 'scan' and event == 'os.scandir' and not attempted:
        if pathlib.Path(args[0]).stat().st_ino == expected:
            convert()
    if phase == 'lock' and ((event == 'open' and str(args[0]).endswith('.brain-index.lock')) or
                            (event == 'ctypes.dlsym' and args[1] in ('NtCreateFile', 'CreateFileW'))):
        # Wait until the target directory has been validated and the runtime
        # starts opening the lock, not while it pins ancestor directories.
        import inspect
        if any(frame.function == 'open_file' for frame in inspect.stack()):
            convert()
sys.addaudithook(before_open)
sys.argv = [str(script), '--provider', 'copilot']
runpy.run_path(str(script), run_name='__main__')
'''
        for phase in ("scan", "lock"):
            with self.subTest(phase=phase), tempfile.TemporaryDirectory() as temporary:
                project = Path(temporary).resolve()
                vault = project / "brain"
                vault.mkdir()
                target = vault / "empty" if phase == "scan" else vault
                target.mkdir(exist_ok=True)
                outside = project / "outside"
                outside.mkdir()
                (outside / "private-leak.md").touch()
                (outside / "index.md").write_text("outside unchanged")
                script = project / "auto-index-brain.py"
                shutil.copyfile(ROOT / ".github/hooks/scripts/auto-index-brain.py", script)
                marker = project / "converted"
                result = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", harness,
                                         str(script), str(target), str(outside), str(marker), phase],
                                        input=json.dumps({"cwd": str(project), "toolResult": {"resultType": "success"}}).encode(),
                                        capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(marker.exists(), result.stderr)
                self.assertEqual(json.loads(result.stdout), {})
                self.assertEqual((outside / "index.md").read_text(), "outside unchanged")
                self.assertFalse((outside / ".brain-index.lock").exists())
                if phase == "scan" and (vault / "index.md").exists():
                    self.assertNotIn("private-leak", (vault / "index.md").read_text())

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
