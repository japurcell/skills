"""Check extraction and curated navigation at their public CLI boundaries."""

import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote

BUNDLE = Path(__file__).resolve().parents[1]
EXTRACTOR = BUNDLE / "assets/skills/ruminate/scripts/extract-conversations.py"
INDEXER = BUNDLE / "assets/skills/brain/scripts/auto-index-brain.py"


class SkillWorkflowTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="ruminate-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.project = self.root / "project café with spaces"
        self.project.mkdir()
        home = self.root / "home"
        home.mkdir()
        self.claude = home / ".claude/projects/project"
        self.codex = home / ".codex/sessions"
        self.environment = dict(os.environ, HOME=str(home), USERPROFILE=str(home),
                                PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")

    def run_cli(self, script, *arguments, payload=None, expected=0):
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-B", str(script), *map(str, arguments)],
            cwd=self.project, env=self.environment,
            input=None if payload is None else json.dumps(payload),
            capture_output=True, text=True, encoding="utf-8", timeout=15, check=False,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def write_histories(self):
        sources = {}
        for provider in ("claude", "codex"):
            directory = self.claude if provider == "claude" else self.codex / "2026/11/03"
            directory.mkdir(parents=True)
            for attribution in ("matching", "different", "missing", "empty"):
                cwd = {"matching": str(self.project / ".." / self.project.name),
                       "different": str(self.root / "other-project"),
                       "empty": ""}.get(attribution)
                text = f"Synthetic {provider} {attribution} conversation."
                if provider == "claude":
                    entry = {"type": "user", "message": {"content": text}}
                    if cwd is not None:
                        entry["cwd"] = cwd
                    rows = [entry]
                else:
                    metadata = {} if cwd is None else {"cwd": cwd}
                    rows = [
                        {"type": "session_meta", "payload": metadata},
                        {"type": "response_item", "payload": {
                            "type": "message", "role": "user",
                            "content": [{"type": "input_text", "text": text}],
                        }},
                    ]
                source = directory / f"{attribution}.jsonl"
                source.write_text("".join(json.dumps(row) + "\n" for row in rows),
                                  encoding="utf-8")
                sources[provider, attribution] = source
        return sources

    def extract(self, output, *arguments, expected=0):
        return self.run_cli(
            EXTRACTOR, output, "--claude-dir", self.claude,
            "--codex-dir", self.codex, "--min-size", "0",
            "--batches", "2", *arguments, expected=expected,
        )

    def test_explicit_cwd_requires_matching_attribution_for_both_providers(self):
        sources = self.write_histories()
        output = self.root / "filtered"
        self.extract(output, "--cwd", self.project)
        extracted = list(output.glob("*.txt"))
        self.assertEqual(len(extracted), 2, [p.name for p in extracted])
        for provider in ("claude", "codex"):
            text = next(p for p in extracted if f"_{provider}_" in p.name).read_text(
                encoding="utf-8")
            self.assertIn(f"[PROVIDER]: {provider}\n", text)
            self.assertIn(f"[SOURCE_FILE]: {sources[provider, 'matching']}\n", text)
            self.assertIn(f"[CWD]: {self.project / '..' / self.project.name}\n", text)
            self.assertIn(f"[USER]: Synthetic {provider} matching conversation.", text)
        manifested = [Path(line) for manifest in (output / "batches").glob("*.txt")
                      for line in manifest.read_text(encoding="utf-8").splitlines()]
        self.assertCountEqual(manifested, extracted)

    def test_unfiltered_extraction_keeps_all_attribution_cases(self):
        sources = self.write_histories()
        output = self.root / "unfiltered"
        self.extract(output)
        extracted = list(output.glob("*.txt"))
        self.assertEqual(len(extracted), 8)
        for (provider, attribution), source in sources.items():
            text = next(p for p in extracted if p.name.endswith(
                f"_{provider}_{attribution}.txt")).read_text(encoding="utf-8")
            self.assertIn(f"[PROVIDER]: {provider}\n", text)
            self.assertIn(f"[SOURCE_FILE]: {source}\n", text)
            self.assertIn(f"[USER]: Synthetic {provider} {attribution} conversation.", text)
            if attribution in ("missing", "empty"):
                self.assertNotIn("[CWD]:", text)

    def test_empty_cwd_filters_to_current_directory(self):
        self.write_histories()
        scripts = (EXTRACTOR, BUNDLE.parents[2] / ".agents/skills/ruminate/scripts/extract-conversations.py")
        for index, script in enumerate(scripts):
            with self.subTest(script=script):
                output = self.root / f"empty-cwd-{index}"
                self.run_cli(script, output, "--claude-dir", self.claude, "--codex-dir", self.codex,
                             "--min-size", "0", "--cwd", "")
                extracted = list(output.glob("*.txt"))
                self.assertEqual(len(extracted), 2, [p.name for p in extracted])
                self.assertTrue(all(path.name.endswith("_matching.txt") for path in extracted))

    @unittest.skipUnless(os.name == "nt", "Windows ACL behavior")
    def test_windows_mkdtemp_workspace_extracts_and_reruns(self):
        self.write_histories()
        output = self.root / "extracted"
        self.extract(output)
        self.extract(output)
        self.assertEqual(len(list(output.glob("*.txt"))), 8)

    @unittest.skipUnless(os.name == "nt", "Windows ACL behavior")
    def test_windows_rejects_shared_workspace_before_writing(self):
        self.write_histories()
        subprocess.run(["icacls", str(self.root), "/grant", "*S-1-1-0:(OI)(CI)F"],
                       check=True, capture_output=True)
        output = self.root / "extracted"
        result = self.extract(output, expected=2)
        self.assertIn("private", result.stderr)
        self.assertFalse(output.exists())

    @unittest.skipUnless(os.name == "nt", "Windows ACL behavior")
    def test_windows_rejects_shared_existing_output_before_rewriting(self):
        self.write_histories()
        output = self.root / "extracted"
        self.extract(output)
        manifest = output / "batches/batch_0.txt"
        subprocess.run(["icacls", str(manifest), "/grant", "*S-1-1-0:F"],
                       check=True, capture_output=True)
        before = {path: path.read_bytes() for path in output.rglob("*.txt")}
        result = self.extract(output, expected=2)
        self.assertIn("private", result.stderr)
        self.assertEqual({path: path.read_bytes() for path in before}, before)

    @unittest.skipUnless(os.name == "nt", "Windows ACL behavior")
    def test_windows_rejects_shared_default_acl_before_writing_new_file(self):
        self.write_histories()
        output = self.root / "extracted"
        output.mkdir(mode=0o700)
        # Replace the inheritable entries with private, non-inheritable ones.
        subprocess.run(["icacls", str(output), "/grant:r", "*S-1-3-4:F",
                        "*S-1-5-18:F", "*S-1-5-32-544:F"],
                       check=True, capture_output=True)
        # Only the child's duplicated impersonation token is changed.
        bootstrap = r'''
import ctypes, runpy, sys
from ctypes import wintypes as w
a = ctypes.WinDLL("advapi32", use_last_error=True)
k = ctypes.WinDLL("kernel32", use_last_error=True)
p, d = ctypes.c_void_p, w.DWORD
k.GetCurrentProcess.restype = p
a.OpenProcessToken.argtypes = [p, d, ctypes.POINTER(p)]
a.DuplicateTokenEx.argtypes = [p, d, p, d, d, ctypes.POINTER(p)]
a.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [w.LPCWSTR, d, ctypes.POINTER(p), ctypes.POINTER(d)]
a.GetSecurityDescriptorDacl.argtypes = [p, ctypes.POINTER(w.BOOL), ctypes.POINTER(p), ctypes.POINTER(w.BOOL)]
a.SetTokenInformation.argtypes = [p, d, p, d]
a.SetThreadToken.argtypes = [p, p]
def check(ok):
    if not ok:
        raise ctypes.WinError(ctypes.get_last_error())
token, duplicate, descriptor, acl = p(), p(), p(), p()
check(a.OpenProcessToken(k.GetCurrentProcess(), 0xA, ctypes.byref(token)))
check(a.DuplicateTokenEx(token, 0x8C, None, 2, 2, ctypes.byref(duplicate)))
check(a.ConvertStringSecurityDescriptorToSecurityDescriptorW("D:(A;;FA;;;WD)", 1, ctypes.byref(descriptor), None))
present, defaulted = w.BOOL(), w.BOOL()
check(a.GetSecurityDescriptorDacl(descriptor, ctypes.byref(present), ctypes.byref(acl), ctypes.byref(defaulted)))
check(a.SetTokenInformation(duplicate, 6, ctypes.byref(acl), ctypes.sizeof(acl)))
check(a.SetThreadToken(None, duplicate))
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
'''
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-B", "-c", bootstrap, str(EXTRACTOR), str(output),
             "--claude-dir", str(self.claude), "--codex-dir", str(self.codex), "--min-size", "0"],
            cwd=self.project, env=self.environment, capture_output=True, text=True,
            encoding="utf-8", timeout=15, check=False,
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("private", result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertTrue(all(path.stat().st_size == 0 for path in output.rglob("*.txt")))

    def test_repeated_roots_deduplicate_and_claude_discovery_stays_nonrecursive(self):
        self.write_histories()
        nested = self.claude / "nested"
        nested.mkdir()
        (nested / "ignored.jsonl").write_text(
            (self.claude / "matching.jsonl").read_text(encoding="utf-8"), encoding="utf-8")
        output = self.root / "extracted"
        self.extract(output, "--claude-dir", self.claude, "--codex-dir", self.codex / "2026")
        extracted = list(output.glob("*.txt"))
        self.assertEqual(len(extracted), 8)
        manifests = sorted((output / "batches").glob("*.txt"))
        self.assertEqual(len(manifests), 2)
        self.assertCountEqual(
            [Path(line) for manifest in manifests
             for line in manifest.read_text(encoding="utf-8").splitlines()], extracted)

    def test_rejects_sources_outside_provider_roots_before_creating_output(self):
        self.write_histories()
        outside = self.root / "unrelated"
        outside.mkdir()
        for option in ("--claude-dir", "--codex-dir"):
            with self.subTest(option=option):
                output = self.root / "extracted"
                result = self.extract(output, option, outside, expected=2)
                self.assertIn("input directory must be within", result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertFalse(output.exists())

    def test_rejects_output_outside_existing_invocation_workspace(self):
        self.write_histories()
        other = tempfile.TemporaryDirectory(prefix="not-ruminate-")
        self.addCleanup(other.cleanup)
        # An isolated temporary root keeps rejected paths inside disposable fixtures.
        self.environment.update(TMPDIR=other.name, TEMP=other.name, TMP=other.name)
        for output in (self.root / "out", Path(other.name) / "out",
                       Path(other.name) / "ruminate-missing/out"):
            with self.subTest(output=output):
                before = set(self.root.rglob("*"))
                result = self.extract(output, expected=2)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(set(self.root.rglob("*")), before)
                self.assertFalse((output / "batches").exists())

    def test_output_cannot_replace_the_workspace_itself(self):
        self.write_histories()
        result = self.extract(self.root, expected=2)
        self.assertIn("strict descendant", result.stderr)
        self.assertFalse((self.root / "batches").exists())

    def test_date_range_is_inclusive_and_minimum_size_filters_before_batching(self):
        sources = self.write_histories()
        for (provider, attribution), path in sources.items():
            day = {"matching": 3, "different": 2, "missing": 4, "empty": 3}[attribution]
            if attribution == "empty":
                path.write_text("{}\n", encoding="utf-8")
            timestamp = datetime(2026, 11, day, 12).timestamp()
            os.utime(path, (timestamp, timestamp))
        output = self.root / "filtered"
        result = self.extract(output, "--from", "2026-11-03", "--to", "2026-11-03", "--min-size", "10")
        self.assertIn("Found 2 candidate conversations", result.stderr)
        self.assertEqual(len(list(output.glob("*.txt"))), 2)
        for path in output.glob("*.txt"):
            self.assertTrue(path.name.endswith("_matching.txt"), path.name)

    def test_empty_result_creates_no_batch_manifests(self):
        self.write_histories()
        output = self.root / "empty"
        result = self.extract(output, "--cwd", self.root / "unrelated-project")
        self.assertEqual(result.stdout.strip(), str(output))
        self.assertIn("Extracted 0 conversations", result.stderr)
        self.assertEqual(list(output.glob("*.txt")), [])
        self.assertTrue((output / "batches").is_dir())
        self.assertEqual(list((output / "batches").iterdir()), [])

    def test_rejects_traversal_and_manifest_line_injection_before_writes(self):
        self.write_histories()
        for suffix in ("../escape", "nested/../escape", "out\nforged", "out\u2028forged"):
            with self.subTest(suffix=suffix):
                before = set(self.root.rglob("*"))
                result = self.extract(str(self.root) + "/" + suffix, expected=2)
                self.assertIn("paths must not contain", result.stderr)
                self.assertEqual(set(self.root.rglob("*")), before)

    def test_rejects_invalid_limits_and_date_ranges_before_writes(self):
        self.write_histories()
        output = self.root / "extracted"
        for arguments, diagnostic in (
                (("--batches", "0"), "--batches must be positive"),
                (("--batches", "-1"), "--batches must be positive"),
                (("--min-size", "-1"), "--min-size must be nonnegative"),
                (("--from", "2026-11-04", "--to", "2026-11-03"),
                 "--from must be on or before --to")):
            with self.subTest(arguments=arguments):
                result = self.extract(output, *arguments, expected=2)
                self.assertIn(diagnostic, result.stderr)
                self.assertFalse(output.exists())

    @unittest.skipIf(os.name == "nt", "POSIX permission bits; Windows needs native ACL validation")
    def test_rejects_shared_output_directories(self):
        self.write_histories()
        output = self.root / "extracted"
        output.mkdir(mode=0o700)
        batches = output / "batches"
        batches.mkdir(mode=0o700)
        for directory in (self.root, output, batches):
            with self.subTest(directory=directory):
                directory.chmod(0o755)
                try:
                    result = self.extract(output, expected=2)
                    self.assertIn("private (mode 700)", result.stderr)
                    self.assertEqual(list(output.rglob("*.txt")), [])
                finally:
                    directory.chmod(0o700)

    @unittest.skipIf(os.name == "nt", "POSIX symlinks without Windows developer mode")
    def test_rejects_source_symlink_escape_before_creating_output(self):
        self.write_histories()
        outside = self.root / "unrelated.jsonl"
        sentinel = b'Never read this file outside the selected source root.\n'
        outside.write_bytes(sentinel)
        (self.claude / "escape.jsonl").symlink_to(outside)
        output = self.root / "extracted"
        result = self.extract(output, expected=2)
        self.assertIn("source escapes input directory", result.stderr)
        self.assertFalse(output.exists())
        self.assertEqual(outside.read_bytes(), sentinel)

    @unittest.skipIf(os.name == "nt", "POSIX symlinks without Windows developer mode")
    def test_rejects_linked_output_directory_before_writes(self):
        self.write_histories()
        outside = self.root / "elsewhere"
        outside.mkdir(mode=0o700)
        output = self.root / "extracted"
        output.symlink_to(outside, target_is_directory=True)
        result = self.extract(output, expected=2)
        self.assertIn("not a symlink", result.stderr)
        self.assertEqual(list(outside.iterdir()), [])

    @unittest.skipIf(os.name == "nt", "POSIX symlinks without Windows developer mode")
    def test_rejects_linked_manifest_without_overwriting_any_extracted_file(self):
        self.write_histories()
        output = self.root / "extracted"
        self.extract(output)
        manifest = output / "batches/batch_0.txt"
        manifest.unlink()
        sentinel = self.root / "sentinel.txt"
        sentinel.write_bytes(b"Keep these bytes.\n")
        # Corrupt the old output deliberately: a refusal must not start a rewrite.
        for path in output.glob("*.txt"):
            path.write_bytes(b"Old extraction remains untouched.\n")
        before = {path: path.read_bytes() for path in output.rglob("*.txt")}
        for kind in ("symlink", "hardlink"):
            with self.subTest(kind=kind):
                if kind == "symlink":
                    manifest.symlink_to(sentinel)
                else:
                    os.link(sentinel, manifest)
                try:
                    self.extract(output, expected=2)
                    self.assertEqual(sentinel.read_bytes(), b"Keep these bytes.\n")
                    self.assertEqual({path: path.read_bytes() for path in before}, before)
                finally:
                    manifest.unlink()

    def test_rerun_truncates_regular_outputs_and_creates_private_artifacts(self):
        self.write_histories()
        output = self.root / "extracted"
        self.extract(output)
        before = {path: path.read_bytes() for path in output.rglob("*.txt")}
        for path, content in before.items():
            path.write_bytes(content + b"stale trailing bytes" * 100)
        self.extract(output)
        self.assertEqual({path: path.read_bytes() for path in before}, before)
        if os.name != "nt":
            for path in (output, *output.rglob("*")):
                self.assertEqual(stat.S_IMODE(path.stat().st_mode),
                                 0o700 if path.is_dir() else 0o600, str(path))

    def reachable_notes(self, entrypoint):
        seen = set()
        pending = [entrypoint.resolve()]
        while pending:
            note = pending.pop()
            if note in seen:
                continue
            self.assertTrue(note.is_file(), f"Broken navigation link: {note}")
            seen.add(note)
            for destination in re.findall(
                    r"\[[^\]]+\]\((?:<([^>]+)>|([^\s)]+))\)",
                    note.read_text(encoding="utf-8")):
                relative = unquote(next(part for part in destination if part).split("#")[0])
                pending.append((note.parent / relative).resolve())
        return seen

    def test_audit_and_archive_notes_need_curated_links_before_reconciliation(self):
        notes = []
        curated = []
        for category in ("audits", "archive"):
            directory = self.project / "brain" / category
            directory.mkdir(parents=True)
            index = directory / "index.md"
            index.write_text(f"# {category.title()}\n", encoding="utf-8")
            curated.append(index)
            note = directory / "new note.md"
            note.write_text("# Synthetic finding\n", encoding="utf-8")
            notes.append(note)

        payload = {"cwd": str(self.project), "hook_event_name": "PostToolUse"}
        result = self.run_cli(INDEXER, "--provider", "codex", payload=payload)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout), {})
        root_index = self.project / "brain/index.md"
        before = (root_index.read_bytes(), root_index.stat().st_mtime_ns)
        reachable = self.reachable_notes(root_index)
        for index, note in zip(curated, notes):
            self.assertIn(index.resolve(), reachable)
            self.assertNotIn(note.resolve(), reachable)

        for index in curated:
            index.write_text(index.read_text(encoding="utf-8")
                             + "\n- [New finding](new%20note.md)\n", encoding="utf-8")
        curated_bytes = {index: index.read_bytes() for index in curated}
        result = self.run_cli(INDEXER, "--provider", "codex", payload=payload)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout), {})
        self.assertEqual((root_index.read_bytes(), root_index.stat().st_mtime_ns), before)
        self.assertEqual({index: index.read_bytes() for index in curated}, curated_bytes)
        reachable = self.reachable_notes(root_index)
        for note in notes:
            self.assertIn(note.resolve(), reachable)


if __name__ == "__main__":
    unittest.main()
