"""Check extraction and curated navigation at their public CLI boundaries."""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote

BUNDLE = Path(__file__).resolve().parents[1]
EXTRACTOR = BUNDLE / "assets/skills/ruminate/scripts/extract-conversations.py"
INDEXER = BUNDLE / "assets/skills/brain/scripts/auto-index-brain.py"


class SkillWorkflowTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.project = self.root / "project café with spaces"
        self.project.mkdir()
        home = self.root / "home"
        home.mkdir()
        self.environment = dict(os.environ, HOME=str(home), USERPROFILE=str(home),
                                PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")

    def run_cli(self, script, *arguments, payload=None):
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-B", str(script), *map(str, arguments)],
            cwd=self.project, env=self.environment,
            input=None if payload is None else json.dumps(payload),
            capture_output=True, text=True, encoding="utf-8", timeout=15, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def write_histories(self):
        sources = {}
        for provider in ("claude", "codex"):
            directory = self.root / provider / "sessions"
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

    def extract(self, output, *arguments):
        return self.run_cli(
            EXTRACTOR, output, "--claude-dir", self.root / "claude/sessions",
            "--codex-dir", self.root / "codex", "--min-size", "0",
            "--batches", "2", *arguments,
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
