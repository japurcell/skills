#!/usr/bin/env python3

import importlib.util
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
        runtime_name = path.parts[-3].replace(".", "")
        file_path = path / "helpers" / "common.py"
        spec = importlib.util.spec_from_file_location(f"helpers.common_{runtime_name}", file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from {file_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _get_observability_module(self, path: Path):
        """
        Helper method to cleanly load/reload the helpers.observability module
        from a specific hook scripts path without caching issues.
        """
        runtime_name = path.parts[-3].replace(".", "")
        common_file = path / "helpers" / "common.py"
        common_spec = importlib.util.spec_from_file_location(f"helpers.common_{runtime_name}", common_file)
        common_mod = importlib.util.module_from_spec(common_spec)
        common_spec.loader.exec_module(common_mod)

        file_path = path / "helpers" / "observability.py"
        spec = importlib.util.spec_from_file_location(f"helpers.observability_{runtime_name}", file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from {file_path}")
        module = importlib.util.module_from_spec(spec)
        module.__package__ = f"helpers_{runtime_name}"
        sys.modules[f"helpers_{runtime_name}"] = common_mod
        sys.modules[f"helpers_{runtime_name}.common"] = common_mod
        spec.loader.exec_module(module)
        return module

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

        bytes_io = io.BytesIO()
        old_stdout = sys.stdout
        sys.stdout = io.TextIOWrapper(bytes_io, encoding="cp1252")
        try:
            # Test payload containing non-ASCII unicode arrow character '→'
            test_payload = {"message": "D:/Projects/personal/skills/.github/global-settings.json → ~/.github/settings.json"}
            emit_json(test_payload)
            sys.stdout.flush()
            written_bytes = bytes_io.getvalue()
            decoded_output = written_bytes.decode("utf-8")
            self.assertIn("→", decoded_output)
        finally:
            sys.stdout = old_stdout

    def test_gemini_unicode_emit_json_no_crash(self):
        common = self._get_common_module(gemini_helpers_path)
        emit_json = common.emit_json
        import io

        bytes_io = io.BytesIO()
        old_stdout = sys.stdout
        sys.stdout = io.TextIOWrapper(bytes_io, encoding="cp1252")
        try:
            # Test payload containing non-ASCII unicode arrow character '→'
            test_payload = {"message": "D:/Projects/personal/skills/.gemini/global-settings.json → ~/.gemini/settings.json"}
            emit_json(test_payload)
            sys.stdout.flush()
            written_bytes = bytes_io.getvalue()
            decoded_output = written_bytes.decode("utf-8")
            self.assertIn("→", decoded_output)
        finally:
            sys.stdout = old_stdout

    def test_copilot_unicode_emit_json_no_crash(self):
        common = self._get_common_module(copilot_helpers_path)
        emit_json = common.emit_json
        import io

        bytes_io = io.BytesIO()
        old_stdout = sys.stdout
        sys.stdout = io.TextIOWrapper(bytes_io, encoding="cp1252")
        try:
            # Test payload containing non-ASCII unicode arrow character '→'
            test_payload = {"message": "D:/Projects/personal/skills/.copilot/global-settings.json → ~/.copilot/settings.json"}
            emit_json(test_payload)
            sys.stdout.flush()
            written_bytes = bytes_io.getvalue()
            decoded_output = written_bytes.decode("utf-8")
            self.assertIn("→", decoded_output)
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
            self.assertEqual(resolved_abs[0], str(Path(skills_dir, "C:\\path\\to\\a.md")))
            self.assertEqual(resolved_abs[1], str(Path(skills_dir, "D:\\another\\path\\b.md")))

        # 8. strip_yaml_frontmatter
        yaml_text = "---\nname: test\n---\nbody content"
        self.assertEqual(common.strip_yaml_frontmatter(yaml_text), "body content")
        no_yaml_text = "body content only"
        self.assertEqual(common.strip_yaml_frontmatter(no_yaml_text), "body content only")

    def test_maintenance_reaping_gemini(self):
        self._check_maintenance_reaping(gemini_helpers_path)

    def test_maintenance_reaping_copilot(self):
        self._check_maintenance_reaping(copilot_helpers_path)

    def _check_maintenance_reaping(self, helpers_path):
        import tempfile
        import time
        import sqlite3
        import shutil

        t0 = time.time()
        print(f"[{helpers_path.name}] Start test...")
        # Load the observability module
        obs = self._get_observability_module(helpers_path)
        print(f"[{helpers_path.name}] Loaded module in {time.time()-t0:.3f}s")

        # Create temp dir
        temp_dir = tempfile.mkdtemp()

        # Set env var so db path points there
        log_path = Path(temp_dir) / "observability.log"
        old_log_path = os.environ.get("OBSERVABILITY_LOG_PATH")
        os.environ["OBSERVABILITY_LOG_PATH"] = str(log_path)

        old_timeout = os.environ.get("OBSERVABILITY_FINALIZATION_TIMEOUT_MS")
        os.environ["OBSERVABILITY_FINALIZATION_TIMEOUT_MS"] = "10"
        old_stale = os.environ.get("OBSERVABILITY_RUNNING_SPAN_STALE_MS")
        os.environ["OBSERVABILITY_RUNNING_SPAN_STALE_MS"] = "10"

        # Also clear any runtime-specific vars that might override this
        old_copilot_timeout = os.environ.get("COPILOT_OBSERVABILITY_FINALIZATION_TIMEOUT_MS")
        os.environ.pop("COPILOT_OBSERVABILITY_FINALIZATION_TIMEOUT_MS", None)
        old_gemini_timeout = os.environ.get("GEMINI_OBSERVABILITY_FINALIZATION_TIMEOUT_MS")
        os.environ.pop("GEMINI_OBSERVABILITY_FINALIZATION_TIMEOUT_MS", None)

        try:
            t1 = time.time()
            db_path = obs._get_db_path()
            # Initialize db directly with SCHEMA_DDL and set user_version=1 to bypass WAL mode setup (which hangs on Windows)
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.executescript(obs.SCHEMA_DDL)
            cursor.execute("PRAGMA user_version = 1;")
            conn.commit()
            print(f"[{helpers_path.name}] DB initialized in {time.time()-t1:.3f}s")

            # Now let's insert some mock sessions
            now_ms = int(time.time() * 1000)

            # Session 1: 'running' but has a dead PID (999999)
            conn.execute(
                "INSERT INTO sessions (session_id, status, start_time_ms, workspace_root) VALUES (?, ?, ?, ?)",
                ("sess-dead-pid", "running", now_ms, "mock-root")
            )
            # Add a span with the dead pid
            conn.execute(
                "INSERT INTO spans (span_id, session_id, sequence_no, pid, updated_at_ms) VALUES (?, ?, ?, ?, ?)",
                ("span-dead-pid", "sess-dead-pid", 1, 999999, now_ms)
            )

            # Session 2: 'running' and stale (started/last active 3 hours ago)
            three_hours_ago_ms = now_ms - 3 * 3600 * 1000
            conn.execute(
                "INSERT INTO sessions (session_id, status, start_time_ms, workspace_root) VALUES (?, ?, ?, ?)",
                ("sess-stale", "running", three_hours_ago_ms, "mock-root")
            )
            # Add a span with no PID or active PID, but old timestamp
            conn.execute(
                "INSERT INTO spans (span_id, session_id, sequence_no, pid, updated_at_ms) VALUES (?, ?, ?, ?, ?)",
                ("span-stale", "sess-stale", 1, 0, three_hours_ago_ms)
            )

            # Session 3: 'running', active, valid PID (our own process PID) and not stale
            our_pid = os.getpid()
            conn.execute(
                "INSERT INTO sessions (session_id, status, start_time_ms, workspace_root) VALUES (?, ?, ?, ?)",
                ("sess-active", "running", now_ms, "mock-root")
            )
            conn.execute(
                "INSERT INTO spans (span_id, session_id, sequence_no, pid, updated_at_ms) VALUES (?, ?, ?, ?, ?)",
                ("span-active", "sess-active", 1, our_pid, now_ms)
            )

            conn.commit()
            conn.close()
            print(f"[{helpers_path.name}] Sessions inserted in {time.time()-t1:.3f}s total")

            t2 = time.time()
            # Run maintenance work!
            obs._run_maintenance_work()
            print(f"[{helpers_path.name}] Maintenance run completed in {time.time()-t2:.3f}s")

            t3 = time.time()
            # Reconnect and assert results
            try:
                conn = obs._connect_and_init_db(db_path, 100)
                cursor = conn.cursor()

                # Let's see the status of our test sessions
                cursor.execute("SELECT session_id, status FROM sessions")
                results = dict(cursor.fetchall())
                conn.close()
                print(f"[{helpers_path.name}] Results retrieved in {time.time()-t3:.3f}s")
            except Exception as reconnect_err:
                print(f"[{helpers_path.name}] Failed to reconnect/retrieve results: {reconnect_err}")
                raise reconnect_err

            self.assertIn("sess-dead-pid", results)
            self.assertIn("sess-stale", results)
            self.assertIn("sess-active", results)

            # The dead/stale sessions must NOT be 'running' anymore
            self.assertNotEqual(results["sess-dead-pid"], "running")
            self.assertNotEqual(results["sess-stale"], "running")

            # But the active session must still be 'running'
            self.assertEqual(results["sess-active"], "running")
            print(f"[{helpers_path.name}] Assertions passed!")

        finally:
            t4 = time.time()
            if old_log_path is not None:
                os.environ["OBSERVABILITY_LOG_PATH"] = old_log_path
            else:
                os.environ.pop("OBSERVABILITY_LOG_PATH", None)

            if old_timeout is not None:
                os.environ["OBSERVABILITY_FINALIZATION_TIMEOUT_MS"] = old_timeout
            else:
                os.environ.pop("OBSERVABILITY_FINALIZATION_TIMEOUT_MS", None)

            if old_stale is not None:
                os.environ["OBSERVABILITY_RUNNING_SPAN_STALE_MS"] = old_stale
            else:
                os.environ.pop("OBSERVABILITY_RUNNING_SPAN_STALE_MS", None)

            if old_copilot_timeout is not None:
                os.environ["COPILOT_OBSERVABILITY_FINALIZATION_TIMEOUT_MS"] = old_copilot_timeout
            if old_gemini_timeout is not None:
                os.environ["GEMINI_OBSERVABILITY_FINALIZATION_TIMEOUT_MS"] = old_gemini_timeout

            shutil.rmtree(temp_dir, ignore_errors=True)
            print(f"[{helpers_path.name}] Cleaned up in {time.time()-t4:.3f}s")

            # Clean up sys.modules to prevent circular references or unittest leaks
            for key in list(sys.modules.keys()):
                if "helpers_gemini" in key or "helpers_copilot" in key:
                    sys.modules.pop(key, None)


    @classmethod
    def tearDownClass(cls):
        import threading
        print("Active threads at teardown:", threading.enumerate())

if __name__ == "__main__":
    unittest.main()
