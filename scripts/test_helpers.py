#!/usr/bin/env python3

import os
import sys
import unittest
from pathlib import Path

# Add script directories to sys.path so we can import helpers
repo_root = Path(__file__).resolve().parent.parent
github_helpers_path = repo_root / ".github" / "hooks" / "scripts"
gemini_helpers_path = repo_root / ".gemini" / "hooks" / "scripts"
copilot_helpers_path = repo_root / ".copilot" / "hooks" / "scripts"


class TestHookHelpers(unittest.TestCase):
    def _get_common_module(self, path: Path):
        """
        Helper method to cleanly load/reload the helpers.common module
        from a specific hook scripts path without caching issues.
        """
        # Clear out any existing helpers modules from cache
        for k in list(sys.modules.keys()):
            if k == "helpers" or k.startswith("helpers."):
                del sys.modules[k]

        # Insert target path at the very beginning of sys.path
        if str(path) in sys.path:
            sys.path.remove(str(path))
        sys.path.insert(0, str(path))

        # Perform clean import
        import helpers.common
        import importlib
        importlib.reload(helpers.common)
        return helpers.common

    def test_github_convert_windows_path_to_posix(self):
        common = self._get_common_module(github_helpers_path)
        convert = common.convert_windows_path_to_posix

        # Test empty input
        self.assertEqual(convert(""), "")

        # Test Windows native platform behavior
        if os.name == "nt":
            self.assertEqual(convert("D:/foo/bar"), "D:\\foo\\bar")
        else:
            # Test POSIX behavior (like WSL/MSYS2) with Windows drive letters
            # Drive letter conversion
            self.assertTrue(convert("D:\\foo\\bar").startswith(("/mnt/d/foo/bar", "/d/foo/bar")))
            self.assertTrue(convert("C:/Users/jeff").startswith(("/mnt/c/Users/jeff", "/c/Users/jeff")))

            # Non-alphabetic character before colon should not be parsed as a drive letter
            self.assertEqual(convert("..:\\foo\\bar"), "../foo/bar")
            self.assertEqual(convert("1:\\foo\\bar"), "1:/foo/bar")

            # General backslash normalization
            self.assertEqual(convert("foo\\bar"), "foo/bar")

    def test_gemini_convert_windows_path_to_posix(self):
        common = self._get_common_module(gemini_helpers_path)
        convert = common.convert_windows_path_to_posix

        # Test empty input
        self.assertEqual(convert(""), "")

        # Test Windows native platform behavior
        if os.name == "nt":
            self.assertEqual(convert("D:/foo/bar"), "D:\\foo\\bar")
        else:
            # Test POSIX behavior
            self.assertTrue(convert("D:\\foo\\bar").startswith(("/mnt/d/foo/bar", "/d/foo/bar")))
            self.assertEqual(convert("foo\\bar"), "foo/bar")

    def test_github_unicode_emit_json_no_crash(self):
        common = self._get_common_module(github_helpers_path)
        emit_json = common.emit_json
        import io

        # Redirect stdout to capture the output and ensure it encodes properly
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            # Test payload containing non-ASCII unicode arrow character '→'
            test_payload = {"message": "D:/Projects/personal/skills/.github/global-settings.json → ~/.github/settings.json"}
            emit_json(test_payload)
            output = sys.stdout.getvalue().strip()
            self.assertIn("→", output)
        finally:
            sys.stdout = old_stdout

    def test_gemini_unicode_emit_json_no_crash(self):
        common = self._get_common_module(gemini_helpers_path)
        emit_json = common.emit_json
        import io

        # Redirect stdout to capture the output and ensure it encodes properly
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            # Test payload containing non-ASCII unicode arrow character '→'
            test_payload = {"message": "D:/Projects/personal/skills/.gemini/global-settings.json → ~/.gemini/settings.json"}
            emit_json(test_payload)
            output = sys.stdout.getvalue().strip()
            self.assertIn("→", output)
        finally:
            sys.stdout = old_stdout

    def test_copilot_unicode_emit_json_no_crash(self):
        common = self._get_common_module(copilot_helpers_path)
        emit_json = common.emit_json
        import io

        # Redirect stdout to capture the output and ensure it encodes properly
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            # Test payload containing non-ASCII unicode arrow character '→'
            test_payload = {"message": "D:/Projects/personal/skills/.copilot/global-settings.json → ~/.copilot/settings.json"}
            emit_json(test_payload)
            output = sys.stdout.getvalue().strip()
            self.assertIn("→", output)
        finally:
            sys.stdout = old_stdout

    def test_common_utility_functions(self):
        # We can use the gemini variant to test general utility functions
        common = self._get_common_module(gemini_helpers_path)

        # 1. sanitize_log_field
        self.assertEqual(common.sanitize_log_field("hello\rworld\nthis\tis\ttest"), "hello world this is test")
        self.assertEqual(common.sanitize_log_field(None), "")
        self.assertEqual(common.sanitize_log_field(123), "123")

        # 2. first_present
        payload = {"a": None, "b": 42, "c": "hello"}
        self.assertEqual(common.first_present(payload, "a", "b", "c"), 42)
        self.assertEqual(common.first_present(payload, "missing", "c"), "hello")
        self.assertEqual(common.first_present(payload, "missing1", "missing2"), "")

        # 3. nested_present
        nested_payload = {"outer": {"inner": {"target": "found", "null_val": None}, "not_dict": "string"}}
        self.assertEqual(common.nested_present(nested_payload, "outer", "inner", "target"), "found")
        self.assertEqual(common.nested_present(nested_payload, "outer", "inner", "null_val"), "")
        self.assertEqual(common.nested_present(nested_payload, "outer", "not_dict", "anything"), "")
        self.assertEqual(common.nested_present(nested_payload, "missing", "path"), "")

        # 4. stringify_value
        self.assertEqual(common.stringify_value("string"), "string")
        self.assertEqual(common.stringify_value(None), "")
        self.assertEqual(common.stringify_value(True), "true")
        self.assertEqual(common.stringify_value({"key": "val"}), '{"key":"val"}')
        self.assertEqual(common.stringify_value([1, 2, 3]), "[1,2,3]")
        self.assertEqual(common.stringify_value(123), "123")

        # 5. trim_ws
        self.assertEqual(common.trim_ws("  hello world  \n"), "hello world")

        # 6. resolve_skill_file_path
        skills_dir = "/skills"
        home = "/home/user"
        self.assertEqual(common.resolve_skill_file_path("~/test.md", skills_dir, home), str(Path(home, "test.md")))
        self.assertEqual(common.resolve_skill_file_path("relative/path.md", skills_dir, home), str(Path(skills_dir, "relative/path.md")))
        self.assertEqual(common.resolve_skill_file_path("/absolute/path.md", skills_dir, home), str(Path("/absolute/path.md")))

        # Error cases for resolve_skill_file_path
        with self.assertRaises(ValueError):
            common.resolve_skill_file_path("", skills_dir, home)
        with self.assertRaises(ValueError):
            common.resolve_skill_file_path("~/test.md", skills_dir, None)

        # 7. merge_env_skill_files
        raw_env = "a.md:b.md,c.md\r\nd.md"
        # Since resolves use resolve_skill_file_path, we expect a list of fully resolved paths
        resolved = common.merge_env_skill_files(raw_env, skills_dir, home)
        self.assertEqual(len(resolved), 4)
        self.assertEqual(resolved[0], str(Path(skills_dir, "a.md")))
        self.assertEqual(resolved[1], str(Path(skills_dir, "b.md")))
        self.assertEqual(resolved[2], str(Path(skills_dir, "c.md")))
        self.assertEqual(resolved[3], str(Path(skills_dir, "d.md")))

        self.assertEqual(common.merge_env_skill_files("", skills_dir, home), [])

        # 8. strip_yaml_frontmatter
        yaml_text = "---\nname: test\n---\nbody content"
        self.assertEqual(common.strip_yaml_frontmatter(yaml_text), "body content")
        no_yaml_text = "body content only"
        self.assertEqual(common.strip_yaml_frontmatter(no_yaml_text), "body content only")


if __name__ == "__main__":
    unittest.main()
