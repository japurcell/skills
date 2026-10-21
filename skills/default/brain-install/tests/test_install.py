"""Exercise the published payload and installer through disposable targets."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from itertools import combinations
from pathlib import Path


BUNDLE = Path(__file__).resolve().parents[1]


def copy_bundle(root, *, ignore=None):
    relocated = root / "relocated bundle"
    shutil.copytree(BUNDLE, relocated, ignore=ignore)
    return relocated


class InstallerTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.bundle = copy_bundle(
            self.root, ignore=shutil.ignore_patterns("__pycache__"))
        self.target = self.root / "target café with spaces"
        self.target.mkdir()
        self.home = self.root / "home"
        self.home.mkdir()
        self.environment = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home),
                                PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")

    def run_install(self, *arguments, expected=0):
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-B", str(self.bundle / "scripts/install.py"),
             str(self.target), *arguments],
            cwd=self.root, env=self.environment, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def fingerprints(self):
        return {p.relative_to(self.target).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in self.target.rglob("*") if p.is_file()}

    def directory_link(self, link, destination):
        if os.name == "nt":
            result = subprocess.run(["cmd", "/d", "/c", "mklink", "/J", str(link), str(destination)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            link.symlink_to(destination, target_is_directory=True)

    def test_fresh_install_inspection_and_unchanged_rerun_without_hooks(self):
        self.run_install()
        self.assertEqual(list(self.target.iterdir()), [])
        self.run_install("--apply")
        assets = self.bundle / "assets"
        self.assertEqual((self.target / "AGENTS.md").read_bytes(),
                         (assets / "AGENTS-brain.md").read_bytes())
        self.assertEqual((self.target / "brain/todos.md").read_text(),
                         "# Todos\n\n<!-- next-id: 1 -->\n")
        self.assertEqual(len(list((self.target / ".agents/skills").glob("*/SKILL.md"))), 6)
        index = (self.target / "brain/index.md").read_text()
        self.assertIn("principles.md", index)
        self.assertIn("archive/index.md", index)
        for provider in (".github", ".codex", ".gemini", ".copilot"):
            self.assertFalse((self.target / provider).exists())
        before = self.fingerprints()
        self.run_install("--apply", "--index-reviewed")
        self.assertEqual(self.fingerprints(), before)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_agents_sections_preserve_policy_and_ignore_fenced_examples(self):
        original = ("# Project\r\n\r\nKeep this policy.\r\n\r\n```markdown\r\n"
                    "## Brain\r\nExample only.\r\n```\r\n\r\n## Builds\r\nRun checks.\r\n")
        (self.target / "AGENTS.md").write_bytes(original.encode())
        self.run_install("--apply")
        installed = (self.target / "AGENTS.md").read_bytes()
        self.assertTrue(installed.startswith(original.encode()))
        self.assertIn((self.bundle / "assets/AGENTS-brain.md").read_bytes(), installed)
        before = self.fingerprints()
        self.run_install("--apply", "--index-reviewed")
        self.assertEqual(self.fingerprints(), before)

    def test_edited_seed_files_can_be_kept_without_blocking_reruns(self):
        self.run_install("--apply")
        edits = {"brain/todos.md": "# Todos\n\n<!-- next-id: 8 -->\n7. [ ] Keep my task.\n",
                 "brain/principles/fix-root-causes.md": "# Local principle\nPreserve this.\n",
                 ".agents/skills/todo/SKILL.md": "---\nname: todo\ndescription: Custom todo workflow.\n---\nKeep IDs.\n"}
        for relative, content in edits.items():
            (self.target / relative).write_text(content, encoding="utf-8")
        before = self.fingerprints()
        self.run_install("--apply", "--index-reviewed", expected=2)
        self.assertEqual(self.fingerprints(), before)
        arguments = ["--apply", "--index-reviewed"]
        for relative in edits:
            arguments.extend(["--keep-existing", relative])
        self.run_install(*arguments)
        self.assertEqual(self.fingerprints(), before)
        for invalid in ("../outside.md", "brain/index.md", "AGENTS.md", "unknown.md"):
            self.run_install("--keep-existing", invalid, expected=2)
            self.assertEqual(self.fingerprints(), before)

    def test_legacy_index_requires_review_before_any_writes(self):
        (self.target / "brain").mkdir()
        original = b"# Legacy brain\n\nAlways obtain deployment approval.\n[Guide](old.md)\n"
        (self.target / "brain/index.md").write_bytes(original)
        (self.target / "brain/old.md").write_text("# Old guide\nKeep rollback steps.\n")
        before = self.fingerprints()
        self.run_install()
        self.run_install("--apply", expected=2)
        self.assertEqual(self.fingerprints(), before)
        backup = self.root / "legacy-index.md"
        backup.write_bytes(original)
        (self.target / "brain/migrated-guidance.md").write_text(
            "# Deployment\nAlways obtain deployment approval.\n[Guide](old.md)\n")
        self.run_install("--apply", "--index-reviewed")
        self.assertEqual(backup.read_bytes(), original)
        self.assertIn("migrated-guidance.md", (self.target / "brain/index.md").read_text())
        self.assertIn("deployment approval", (self.target / "brain/migrated-guidance.md").read_text())

    def test_populated_subtrees_require_curated_indexes_before_installation(self):
        options = []
        for directory in ("plans", "audits", "archive", "codebase"):
            subtree = self.target / "brain" / directory
            subtree.mkdir(parents=True)
            note = subtree / "current.md"
            note.write_bytes(b"# Current knowledge\nKeep this guidance.\n")
            before = self.fingerprints()
            for arguments in ((), ("--apply",)):
                result = self.run_install(*arguments, *options, expected=2)
                self.assertIn(f"brain/{directory}/index.md", result.stderr)
                self.assertEqual(self.fingerprints(), before)
            index = subtree / "index.md"
            index.write_bytes(b"# Index\n\n- [Current](current.md)\n")
            options.extend(("--keep-existing", f"brain/{directory}/index.md"))
        preserved = self.fingerprints()
        self.run_install("--apply", *options)
        for relative, fingerprint in preserved.items():
            self.assertEqual(self.fingerprints()[relative], fingerprint)
        inventory = (self.target / "brain/index.md").read_text(encoding="utf-8")
        for directory in ("plans", "audits", "archive", "codebase"):
            self.assertIn(f"{directory}/index.md", inventory)

    def test_ambiguous_or_conflicting_agents_sections_are_read_only_conflicts(self):
        for content in ("## Brain\nCustom policy.\n", "## Brain\nOne\n## Brain\nTwo\n"):
            (self.target / "AGENTS.md").write_text(content)
            before = self.fingerprints()
            self.run_install("--apply", expected=2)
            self.assertEqual(self.fingerprints(), before)

    def test_unclosed_agents_fences_are_read_only_conflicts_on_retries(self):
        for fence in ("```text", "~~~text"):
            (self.target / "AGENTS.md").write_bytes(f"{fence}\nExample\n".encode())
            before = self.fingerprints()
            for _ in range(2):
                result = self.run_install("--apply", "--index-reviewed", expected=2)
                self.assertIn("unclosed", result.stderr)
                self.assertEqual(self.fingerprints(), before)

    def test_setext_agents_sections_conflict_and_bound_other_sections(self):
        for content in ("Brain\n-----\nCustom policy.\n",
                        "Brain\n=====\nCustom policy.\n",
                        "## Brain\nOne\nBrain\n-----\nTwo\n"):
            (self.target / "AGENTS.md").write_bytes(content.encode())
            before = self.fingerprints()
            self.run_install("--apply", expected=2)
            self.assertEqual(self.fingerprints(), before)
        template = (self.bundle / "assets/AGENTS-brain.md").read_bytes()
        original = template + b"\nBuilds\n------\nKeep build policy.\n\n```text\nBrain\n-----\n```\n"
        (self.target / "AGENTS.md").write_bytes(original)
        self.run_install("--apply")
        self.assertEqual((self.target / "AGENTS.md").read_bytes(), original)
        before = self.fingerprints()
        self.run_install("--apply", "--index-reviewed")
        self.assertEqual(self.fingerprints(), before)

    def test_linked_destination_does_not_change_target_or_external_files(self):
        outside = self.root / "outside"
        outside.mkdir()
        self.directory_link(self.target / "brain", outside)
        self.run_install("--apply", expected=2)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertEqual([p.name for p in self.target.iterdir()], ["brain"])

    def test_target_reached_through_linked_parent_is_rejected(self):
        alias = self.root / "alias"
        self.directory_link(alias, self.target)
        self.target = alias / "nested"
        self.target.mkdir()
        self.run_install("--apply", expected=2)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_unrelated_and_hardlinked_files_are_preserved(self):
        external = self.root / "external-ignore"
        external.write_bytes(b"keep-this-rule\n")
        os.link(external, self.target / ".gitignore")
        (self.target / "unrelated.txt").write_bytes(b"unaltered")
        self.run_install("--apply")
        self.assertEqual(external.read_bytes(), b"keep-this-rule\n")
        self.assertEqual((self.target / "unrelated.txt").read_bytes(), b"unaltered")
        self.assertEqual((self.target / ".gitignore").read_text(),
                         "keep-this-rule\n/brain/.brain-index.lock\n")

    def test_failed_indexing_is_not_reported_as_success(self):
        script = self.target / ".agents/skills/brain/scripts/auto-index-brain.py"
        script.parent.mkdir(parents=True)
        script.write_text("import sys\nprint('index unavailable', file=sys.stderr)\n")
        result = self.run_install("--apply", "--keep-existing",
                                  ".agents/skills/brain/scripts/auto-index-brain.py", expected=1)
        self.assertIn("indexing failed", result.stderr)
        self.assertIn("completed paths:", result.stderr)
        self.assertFalse((self.target / "brain/index.md").exists())

    def test_provider_combinations_and_selection_transitions(self):
        configurations = {"copilot": ".github/hooks/hooks.json", "codex": ".codex/hooks.json",
                          "gemini": ".gemini/settings.json"}
        base = self.target
        for count in range(4):
            for selected in combinations(configurations, count):
                with self.subTest(selected=selected):
                    self.target = base / ("-".join(selected) or "none")
                    self.target.mkdir()
                    options = [part for provider in selected for part in ("--provider", provider)]
                    self.run_install(*options, "--apply")
                    for provider, relative in configurations.items():
                        self.assertEqual((self.target / relative).exists(), provider in selected)
                    before = self.fingerprints()
                    self.run_install(*options, "--apply", "--index-reviewed")
                    self.assertEqual(self.fingerprints(), before)
                    self.run_install("--apply", "--index-reviewed")
                    self.assertEqual(self.fingerprints(), before)
        self.target = base / "none"
        todos = self.target / "brain/todos.md"
        todos.write_text("# Todos\n\n<!-- next-id: 2 -->\n1. [ ] My task.\n")
        self.run_install("--apply", "--index-reviewed", "--keep-existing", "brain/todos.md",
                         "--provider", "codex")
        codex_before = (self.target / configurations["codex"]).read_bytes()
        self.run_install("--apply", "--index-reviewed", "--keep-existing", "brain/todos.md",
                         "--provider", "copilot")
        self.assertEqual((self.target / configurations["codex"]).read_bytes(), codex_before)
        self.assertIn("My task", todos.read_text())

    def test_selected_config_validation_and_unselected_preservation(self):
        base = self.target
        cases = ("not JSON", "[]", '{"hooks":{},"hooks":{}}',
                 '{"custom":NaN}',
                 '{"hooks":{"SessionStart":"invalid"}}',
                 '{"hooks":{"SessionStart":[{"hooks":["invalid"]}]}}',
                 '{"hooks":{"SessionStart":[{"hooks":[{"type":"command","command":123}]}]}}')
        for number, invalid in enumerate(cases):
            with self.subTest(invalid=invalid):
                self.target = base / str(number)
                (self.target / ".codex").mkdir(parents=True)
                config = self.target / ".codex/hooks.json"
                config.write_text(invalid)
                before = self.fingerprints()
                self.run_install("--provider", "codex", "--apply", expected=2)
                self.assertEqual(self.fingerprints(), before)
                self.run_install("--apply")
                self.assertEqual(config.read_text(), invalid)

    def test_merge_preserves_unrelated_handlers_and_reports_changed_brain_handlers(self):
        config = self.target / ".codex/hooks.json"
        config.parent.mkdir()
        unrelated = {"hooks": [{"type": "command", "command": "echo existing"}], "matcher": "Bash"}
        config.write_text(json.dumps({"custom": {"keep": True}, "hooks": {"PostToolUse": [unrelated]}}))
        self.run_install("--provider", "codex", "--apply")
        merged = json.loads(config.read_text())
        self.assertEqual(merged["custom"], {"keep": True})
        self.assertEqual(merged["hooks"]["PostToolUse"][0], unrelated)
        merged["hooks"]["PostToolUse"][1]["hooks"][0]["timeout"] = 999
        config.write_text(json.dumps(merged))
        before = self.fingerprints()
        self.run_install("--provider", "codex", "--index-reviewed", "--apply", expected=2)
        self.assertEqual(self.fingerprints(), before)

    def test_unicode_diagnostics_use_utf8_with_a_legacy_host_encoding(self):
        config = self.target / ".codex/hooks.json"
        config.parent.mkdir()
        config.write_text("[]")
        result = subprocess.run(
            [sys.executable, str(self.bundle / "scripts/install.py"), str(self.target),
             "--provider", "codex"],
            cwd=self.root, env=dict(self.environment, PYTHONIOENCODING="cp1252"),
            capture_output=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(str(config), result.stderr.decode("utf-8"))

    def test_registered_commands_run_from_nested_directory(self):
        self.run_install("--provider", "copilot", "--provider", "codex", "--provider", "gemini", "--apply")
        nested = self.target / "sub directory"
        nested.mkdir()
        cases = (("copilot", ".github/hooks/hooks.json", "sessionStart", "postToolUse"),
                 ("codex", ".codex/hooks.json", "SessionStart", "PostToolUse"),
                 ("gemini", ".gemini/settings.json", "SessionStart", "AfterTool"))
        for provider, relative, start, post in cases:
            config = json.loads((self.target / relative).read_text())
            for event in (start, post):
                with self.subTest(provider=provider, event=event):
                    entry = config["hooks"][event][0]
                    handler = entry if provider == "copilot" else entry["hooks"][0]
                    field = (("powershell" if provider == "copilot" else "commandWindows" if provider == "codex" else "command")
                             if os.name == "nt" else ("bash" if provider == "copilot" else "command"))
                    command = handler[field]
                    payload = {"cwd": str(nested), "source": "startup", "hook_event_name": event,
                               "toolResult": {"resultType": "success"}, "tool_response": {"output": "done"}}
                    if event == post:
                        (self.target / "brain/codebase/new.md").write_text("# New knowledge\n")
                    if os.name == "nt" and provider == "copilot":
                        invocation = [shutil.which("pwsh") or "powershell", "-NoProfile", "-NonInteractive", "-Command", command]
                        use_shell = False
                    else:
                        invocation, use_shell = command, True
                    result = subprocess.run(invocation, shell=use_shell, cwd=nested, env=self.environment,
                                            input=json.dumps(payload), text=True, encoding="utf-8", capture_output=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, "")
                    if event == start:
                        self.assertIn("Brain", result.stdout)
                        documents = [json.loads(line) for line in result.stdout.splitlines()]
                        final = documents[-1]
                        if provider == "copilot":
                            self.assertIn("additionalContext", final)
                        else:
                            self.assertIn("additionalContext", final["hookSpecificOutput"])
                    else:
                        self.assertIn("codebase/new.md", (self.target / "brain/index.md").read_text())
                        (self.target / "brain/codebase/new.md").unlink()


class PayloadTests(unittest.TestCase):
    def test_relocated_extractor_uses_utf8_for_unicode_output_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            relocated = copy_bundle(root)
            conversations = root / "conversations"
            conversations.mkdir()
            message = "Preserve this conversation guidance."
            (conversations / "session.jsonl").write_text(json.dumps(
                {"type": "user", "message": {"content": message}}) + "\n", encoding="utf-8")
            output = root / "output-漢字"
            result = subprocess.run(
                [sys.executable, str(relocated / "assets/skills/ruminate/scripts/extract-conversations.py"),
                 str(output), "--claude-dir", str(conversations), "--min-size", "0"],
                cwd=root, env=dict(os.environ, PYTHONIOENCODING="cp1252"), capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
            self.assertEqual(result.stdout.decode("utf-8").strip(), str(output))
            extracted = output / "000_claude_session.txt"
            self.assertIn(f"[USER]: {message}", extracted.read_text(encoding="utf-8"))
            self.assertEqual((output / "batches/batch_0.txt").read_text(encoding="utf-8"),
                             f"{output}/000_claude_session.txt\n")

    def test_relocated_extractor_preserves_claude_and_codex_cli_messages(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            relocated = copy_bundle(root)
            claude_dir = root / "claude projects"
            claude_dir.mkdir()
            codex_dir = root / "codex sessions"
            codex_file = codex_dir / "2026" / "10" / "21" / "codex-session.jsonl"
            codex_file.parent.mkdir(parents=True)
            claude_file = claude_dir / "claude-session.jsonl"

            claude_entries = [
                {"type": "user", "message": {"content": "Claude user string has enough detail."}},
                {"type": "assistant", "message": {"content": [
                    None,
                    {"type": "image", "text": "Claude image content is ignored."},
                    {"type": "input_text", "text": "Claude input_text content stays excluded."},
                    {"type": "output_text", "text": "Claude output_text content stays excluded."},
                    {"type": "text", "text": "Claude assistant first visible text."},
                    {"type": "text", "text": 12},
                    {"type": "text", "text": "Claude assistant second visible text."},
                ]}},
                {"type": "user", "message": {"content": 42}},
            ]
            codex_entries = [
                {"type": "session_meta", "payload": {"cwd": str(root)}},
                {"type": "response_item", "payload": {"type": "message", "role": "user",
                                                            "content": "Codex user string supports several words."}},
                {"type": "response_item", "payload": {"type": "message", "role": "assistant", "content": [
                    None,
                    {"type": "image", "text": "Codex image content is ignored."},
                    {"type": "input_text", "text": "Codex input text is accepted."},
                    {"type": "output_text", "text": "Codex output text appears after input."},
                    {"type": "text", "text": "Codex generic text appears last."},
                    {"type": "unsupported", "text": "Codex unsupported content is ignored."},
                    {"type": "text", "text": False},
                ]}},
                {"type": "response_item", "payload": {"type": "message", "role": "user",
                                                            "content": {"type": "input_text", "text": "Not a list."}}},
            ]
            claude_file.write_text(
                "\n".join(json.dumps(entry) for entry in claude_entries)
                + "\n[]\n", encoding="utf-8")
            codex_file.write_text(
                "\n".join(json.dumps(entry) for entry in codex_entries) + "\nnull\n", encoding="utf-8")
            os.utime(claude_file, (1_800_000_000, 1_800_000_000))
            os.utime(codex_file, (1_800_000_100, 1_800_000_100))

            output = root / "extract café"
            result = subprocess.run(
                [sys.executable, str(relocated / "assets/skills/ruminate/scripts/extract-conversations.py"),
                 str(output), "--claude-dir", str(claude_dir), "--codex-dir", str(codex_dir), "--min-size", "0"],
                cwd=root, env=dict(os.environ, PYTHONIOENCODING="cp1252"), capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
            self.assertEqual(result.stdout.decode("utf-8").strip(), str(output))
            self.assertIn(b"Found 2 candidate conversations", result.stderr)
            self.assertIn(b"Extracted 2 conversations with content (claude=1, codex=1, unknown=0)", result.stderr)

            codex_output = output / "000_codex_codex-session.txt"
            claude_output = output / "001_claude_claude-session.txt"
            self.assertEqual(codex_output.read_text(encoding="utf-8"),
                             f"[PROVIDER]: codex\n[CWD]: {root}\n[SOURCE_FILE]: {codex_file.resolve()}\n\n"
                             "[USER]: Codex user string supports several words.\n\n"
                             "[ASSISTANT]: Codex input text is accepted.\n\n"
                             "[ASSISTANT]: Codex output text appears after input.\n\n"
                             "[ASSISTANT]: Codex generic text appears last.\n")
            self.assertEqual(claude_output.read_text(encoding="utf-8"),
                             f"[PROVIDER]: claude\n[SOURCE_FILE]: {claude_file.resolve()}\n\n"
                             "[USER]: Claude user string has enough detail.\n\n"
                             "[ASSISTANT]: Claude assistant first visible text.\n\n"
                             "[ASSISTANT]: Claude assistant second visible text.\n")
            self.assertEqual((output / "batches/batch_0.txt").read_text(encoding="utf-8"),
                             f"{codex_output}\n")
            self.assertEqual((output / "batches/batch_1.txt").read_text(encoding="utf-8"),
                             f"{claude_output}\n")

    def test_relocated_snapshot_preserves_format_and_filters_directories(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            relocated = copy_bundle(root)
            vault = root / "brain space café"
            vault.mkdir()
            (vault / "z.md").write_text("Last", encoding="utf-8")
            (vault / "a.md").write_text("First\n", encoding="utf-8")
            for directory in ("slides", "node_modules"):
                (vault / directory).mkdir()
                (vault / directory / "ignored.md").write_text("Ignored", encoding="utf-8")
            (vault / "ignored.txt").write_text("Ignored", encoding="utf-8")
            output = root / "snapshot café.md"
            result = subprocess.run(
                [sys.executable, str(relocated / "assets/skills/meditate/scripts/snapshot.py"),
                 str(vault), str(output)],
                cwd=root, env=dict(os.environ, PYTHONIOENCODING="cp1252"),
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output.read_text(encoding="utf-8"),
                             f"=== {vault / 'a.md'} ===\nFirst\n\n\n"
                             f"=== {vault / 'z.md'} ===\nLast\n\n")
            self.assertEqual(result.stdout.strip(), str(output))


if __name__ == "__main__":
    unittest.main()
