#!/usr/bin/env python3

import importlib.util
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

# Add script directories to sys.path so we can import helpers
repo_root = Path(__file__).resolve().parents[3]
gemini_helpers_path = repo_root / ".gemini" / "hooks" / "scripts"
copilot_helpers_path = repo_root / ".copilot" / "hooks" / "scripts"


class TestHookHelpers(unittest.TestCase):
    def test_json_reader_custom_bounds_preserve_exact_units_and_default_calls(self):
        import json
        import subprocess

        for path in (gemini_helpers_path, copilot_helpers_path):
            for options, payload, expected in (
                ({}, '{"x":"[{,:}\\\""}', {"x": '[{,:}"'}),
                ({"max_bytes": 64}, '{"x":1' + ' ' * 57 + '}', {"x": 1}),
                ({"max_bytes": 64}, '{"x":1' + ' ' * 58 + '}',
                 {"rule": "raw_input_bytes", "limit": 64, "measured": 65, "unit": "bytes"}),
                ({"max_markers": 5}, '{"x":"[{,:}\\\""}', {"x": '[{,:}"'}),
                ({"max_markers": 4}, '{"x":"[{,:}\\\""}',
                 {"rule": "raw_structural_markers", "limit": 4, "measured": 5, "unit": "markers"}),
            ):
                with self.subTest(provider=str(path), options=options, expected=expected):
                    code = (
                        "import json,sys\n"
                        f"sys.path.insert(0, {str(path)!r})\n"
                        "from helpers.common import read_json_input, InputLimitError\n"
                        "try:\n"
                        f" result=read_json_input(**{options!r})\n"
                        "except InputLimitError as error:\n"
                        " result=dict(rule=error.rule_id,limit=error.limit,measured=error.measured,unit=error.unit)\n"
                        "print(json.dumps(result))\n"
                    )
                    result = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", code],
                                            input=payload, text=True, capture_output=True, timeout=5)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(json.loads(result.stdout), expected)


    def test_run_command_preserves_arguments_environment_and_process_results(self):
        import json
        import subprocess
        import tempfile

        helper_paths = (gemini_helpers_path, copilot_helpers_path)
        with tempfile.TemporaryDirectory(prefix="common-command-") as directory:
            for path in helper_paths:
                with self.subTest(provider=path.parts[-3]):
                    common = self._get_common_module(path)
                    args = [sys.executable, "-c",
                            "import json,os,sys; print(json.dumps([os.getcwd(),os.environ['COMMON_TEST'],sys.argv[1:]])); print('stderr value',file=sys.stderr)",
                            "literal ; $(ignored)", "snowman \u2603"]
                    result = common.run_command(args, cwd=directory,
                                                env={**os.environ, "COMMON_TEST": "provided"},
                                                check=True, capture_output=True)
                    self.assertIsInstance(result, subprocess.CompletedProcess)
                    self.assertEqual(result.args, args)
                    self.assertEqual(result.returncode, 0)
                    self.assertEqual(json.loads(result.stdout),
                                     [str(Path(directory).resolve()), "provided", args[3:]])
                    self.assertEqual(result.stderr, "stderr value\n")

    def test_run_command_preserves_failures_timeout_and_bytes_output(self):
        import subprocess

        helper_paths = (gemini_helpers_path, copilot_helpers_path)
        for path in helper_paths:
            with self.subTest(provider=path.parts[-3]):
                common = self._get_common_module(path)
                args = [sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'output'); sys.exit(7)"]
                result = common.run_command(args, capture_output=True, text=False)
                self.assertEqual((result.returncode, result.stdout, result.stderr), (7, b"output", b""))
                with self.assertRaises(subprocess.CalledProcessError) as failure:
                    common.run_command(args, check=True, capture_output=True)
                self.assertEqual((failure.exception.returncode, failure.exception.stdout), (7, "output"))
                with self.assertRaises(subprocess.TimeoutExpired):
                    common.run_command([sys.executable, "-c", "import time; time.sleep(5)"], timeout=0.05)
                with self.assertRaises(FileNotFoundError):
                    common.run_command(["hook-test-nonexistent-executable-" + uuid4().hex])
                for invalid in ("echo safe", b"echo safe"):
                    with self.assertRaises(TypeError):
                        common.run_command(invalid)

    def _load_helper_module(self, path: Path, module_name: str):
        """Load a provider helper into its own correctly registered package."""
        runtime_name = path.parts[-3].replace(".", "")
        helpers_dir = path / "helpers"
        package_name = f"_test_helpers_{runtime_name}_{uuid4().hex}"

        package_init = helpers_dir / "__init__.py"
        if package_init.exists():
            package_spec = importlib.util.spec_from_file_location(
                package_name,
                package_init,
                submodule_search_locations=[str(helpers_dir)],
            )
        else:
            package_spec = importlib.util.spec_from_loader(
                package_name,
                loader=None,
                is_package=True,
            )
            if package_spec is not None:
                package_spec.submodule_search_locations = [str(helpers_dir)]
        if package_spec is None or (package_init.exists() and package_spec.loader is None):
            raise ImportError(f"Cannot load package from {helpers_dir}")
        package = importlib.util.module_from_spec(package_spec)
        sys.modules[package_name] = package
        self.addCleanup(sys.modules.pop, package_name, None)
        if package_spec.loader is not None:
            package_spec.loader.exec_module(package)

        common_file = helpers_dir / "common.py"
        common_spec = importlib.util.spec_from_file_location(
            f"{package_name}.common",
            common_file,
        )
        if common_spec is None or common_spec.loader is None:
            raise ImportError(f"Cannot load module from {common_file}")
        common_module = importlib.util.module_from_spec(common_spec)
        sys.modules[common_spec.name] = common_module
        self.addCleanup(sys.modules.pop, common_spec.name, None)
        common_spec.loader.exec_module(common_module)
        if module_name == "common":
            return common_module

        file_path = helpers_dir / f"{module_name}.py"
        spec = importlib.util.spec_from_file_location(
            f"{package_name}.{module_name}",
            file_path,
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from {file_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        self.addCleanup(sys.modules.pop, spec.name, None)
        spec.loader.exec_module(module)
        return module

    def _get_common_module(self, path: Path):
        return self._load_helper_module(path, "common")

    def _get_audit_module(self, path: Path):
        return self._load_helper_module(path, "audit")

    def _create_disposable_test_dir(self, name: str) -> Path:
        return Path(tempfile.mkdtemp(prefix=f"{name}-"))


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
            self.assertTrue(convert("C:/Users/jeff").startswith(("/mnt/c/Users/jeff", "/c/Users/jeff")))
            self.assertEqual(convert("..:\\foo\\bar"), "..:/foo/bar")
            self.assertEqual(convert("1:\\foo\\bar"), "1:/foo/bar")
            self.assertEqual(convert("foo\\bar"), "foo/bar")


    def _assert_unicode_emit_json(self, helper_path, test_payload):
        common = self._get_common_module(helper_path)
        emit_json = common.emit_json
        import io

        bytes_io = io.BytesIO()
        old_stdout = sys.stdout
        sys.stdout = io.TextIOWrapper(bytes_io, encoding="cp1252")
        try:
            # Test payload containing non-ASCII unicode arrow character '→'
            emit_json(test_payload)
            sys.stdout.flush()
            written_bytes = bytes_io.getvalue()
            decoded_output = written_bytes.decode("utf-8")
            self.assertIn("→", decoded_output)
        finally:
            sys.stdout = old_stdout

    def test_gemini_unicode_emit_json_no_crash(self):
        self._assert_unicode_emit_json(
            gemini_helpers_path,
            {"message": "D:/Projects/personal/skills/.gemini/global-settings.json → ~/.gemini/settings.json"},
        )

    def test_copilot_unicode_emit_json_no_crash(self):
        self._assert_unicode_emit_json(
            copilot_helpers_path,
            {"message": "D:/Projects/personal/skills/.copilot/global-settings.json → ~/.copilot/settings.json"},
        )

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
        if os.name == "nt":
            raw_env = "a.md;b.md,c.md\r\nd.md"
        else:
            raw_env = "a.md:b.md,c.md\r\nd.md"

        # Since resolves use resolve_skill_file_path, we expect a list of fully resolved paths
        resolved = common.merge_env_skill_files(raw_env, skills_dir, home)
        self.assertEqual(len(resolved), 4)
        self.assertEqual(resolved[0], str(Path(skills_dir, "a.md")))
        self.assertEqual(resolved[1], str(Path(skills_dir, "b.md")))
        self.assertEqual(resolved[2], str(Path(skills_dir, "c.md")))
        self.assertEqual(resolved[3], str(Path(skills_dir, "d.md")))

        self.assertEqual(common.merge_env_skill_files("", skills_dir, home), [])

        # Test Windows absolute paths splitting
        if os.name == "nt":
            raw_env_abs = "C:\\path\\to\\a.md;D:\\another\\path\\b.md"
            resolved_abs = common.merge_env_skill_files(raw_env_abs, skills_dir, home)
            self.assertEqual(len(resolved_abs), 2)
            self.assertEqual(resolved_abs[0], "C:\\path\\to\\a.md")
            self.assertEqual(resolved_abs[1], "D:\\another\\path\\b.md")
        else:
            raw_env_abs = "C:\\path\\to\\a.md:D:\\another\\path\\b.md"
            resolved_abs = common.merge_env_skill_files(raw_env_abs, skills_dir, home)
            self.assertEqual(len(resolved_abs), 2)
            self.assertEqual(resolved_abs[0], common.convert_windows_path_to_posix("C:\\path\\to\\a.md"))
            self.assertEqual(resolved_abs[1], common.convert_windows_path_to_posix("D:\\another\\path\\b.md"))

        # 8. strip_yaml_frontmatter
        yaml_text = "---\nname: test\n---\nbody content"
        self.assertEqual(common.strip_yaml_frontmatter(yaml_text), "body content")
        no_yaml_text = "body content only"
        self.assertEqual(common.strip_yaml_frontmatter(no_yaml_text), "body content only")

    def test_windows_drive_paths_resolve_as_absolute_on_posix(self):
        for helpers_path in (copilot_helpers_path, gemini_helpers_path):
            with self.subTest(runtime=helpers_path.parts[-3]):
                common = self._get_common_module(helpers_path)
                skills_dir = "/skills"
                home = "/home/user"
                raw = "C:\\path\\to\\a.md"

                resolved = common.resolve_skill_file_path(raw, skills_dir, home)
                if os.name == "nt":
                    self.assertEqual(resolved, raw)
                else:
                    self.assertEqual(resolved, common.convert_windows_path_to_posix(raw))




    @classmethod
    def tearDownClass(cls):
        import threading
        print("Active threads at teardown:", threading.enumerate())

if __name__ == "__main__":
    unittest.main()
