#!/usr/bin/env python3
"""Test imports through the copy-from-git CLI with disposable Git repositories."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class CopyFromGitTests(unittest.TestCase):
    def test_relative_repository_can_be_imported_repeatedly(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            repo = parent / "repo"
            scripts = repo / "scripts"
            scripts.mkdir(parents=True)
            script = scripts / "copy-from-git.sh"
            shutil.copy(Path(__file__).with_name("copy-from-git.sh"), script)
            origin = parent / "origin"
            origin.mkdir()

            def git(*args):
                return subprocess.run(
                    ["git", "-C", str(origin), *args], check=True,
                    capture_output=True, text=True,
                )

            git("init", "-q", "-b", "main")

            def commit(content):
                (origin / "README").write_text(content)
                git("add", "README")
                git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                    "-c", "commit.gpgsign=false", "commit", "-qm", "Fixture update")

            def copy():
                return subprocess.run(
                    ["bash", str(script), "--repo", "../origin", "--clone-dir",
                     "local-fixture", "README", "out"], cwd=repo,
                    capture_output=True, text=True,
                )

            commit("first version\n")
            first = copy()
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual((repo / "out").read_text(), "first version\n")
            commit("updated version\n")
            second = copy()
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual((repo / "out").read_text(), "updated version\n")
            self.assertIn("Found existing matching repo", second.stderr)
            self.assertFalse(list(parent.glob("*.clone.*")))


if __name__ == "__main__":
    unittest.main()
