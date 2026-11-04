#!/usr/bin/env python3
"""Exercise workspace parsing and pulls through their public CLIs."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name)
        self.scripts = self.parent / "repo/scripts"
        self.scripts.mkdir(parents=True)
        for name in ("pull-skill-repos.sh", "read-workspace-folders.py"):
            shutil.copy(ROOT / name, self.scripts)
        self.config = self.parent / "skills.code-workspace"

    def parse(self, text):
        self.config.write_text(text)
        return subprocess.run([sys.executable, str(self.scripts / "read-workspace-folders.py"),
                               str(self.config)], capture_output=True, text=True)

    def test_vscode_comments_and_trailing_commas(self):
        result = self.parse('''{
          // Workspace folders
          "folders": [
            {"path": "skills",},
            {"path": "mattpocock-skills",}, /* imported skills */
          ],
          "settings": {"example": [1, 2,],},
        }''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "skills\nmattpocock-skills\n")

    def test_strings_preserve_comment_and_comma_characters(self):
        result = self.parse(r'''{"folders": [{"path": "folder//name/*text*/,}"}],
                                "settings": {"escaped": "a\\\"//b"}}''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "folder//name/*text*/,}\n")

    def test_invalid_config_has_location_and_no_partial_output(self):
        result = self.parse('{\n "folders": [{"path": "skills"}],\n "settings": invalid\n}')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("line 3", result.stderr)
        self.assertIn(str(self.config), result.stderr)

    def test_invalid_folder_path_is_actionable(self):
        for text in ('{"folders": [{"path": "skills"}, {}]}',
                     '{"folders": [{"path": "line\\nbreak"}]}'):
            with self.subTest(text=text):
                result = self.parse(text)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertIn("folders[", result.stderr)

    def test_malformed_comma_sequences_are_not_repaired(self):
        for value in ('[,]', '[{},,]', '{"path":,}'):
            with self.subTest(value=value):
                result = self.parse('{"folders": ' + value + '}')
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")

    def test_pull_uses_vscode_file_without_rewriting_it(self):
        text = '{"folders": [{"path": "vendor",},],}'
        self.config.write_text(text)
        (self.parent / "vendor/.git").mkdir(parents=True)
        commands = self.parent / "commands"
        commands.mkdir()
        git = commands / "git"
        git.write_text('#!/bin/sh\nprintf "fixture git %s\\n" "$*"\n')
        git.chmod(0o755)
        result = subprocess.run(["bash", str(self.scripts / "pull-skill-repos.sh")],
                                env=dict(os.environ, PATH=f"{commands}:{os.environ['PATH']}"),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("fixture git pull", result.stdout)
        self.assertEqual(self.config.read_text(), text)

    def test_missing_workspace_is_optional(self):
        result = subprocess.run(["bash", str(self.scripts / "pull-skill-repos.sh")],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Skipping workspace repository updates", result.stderr)


if __name__ == "__main__":
    unittest.main()
