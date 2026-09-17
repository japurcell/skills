#!/usr/bin/env python3
"""Exercise the repository test runner through its public CLI."""

import os
from pathlib import Path
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest


REPO_ROOT = Path(__file__).resolve().parent.parent
RUNNER = REPO_ROOT / "scripts" / "test-all.py"


class TestTestAll(unittest.TestCase):
    def fixture(self):
        temporary = tempfile.TemporaryDirectory(prefix="test-all-")
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        root = directory / "checkout with spaces"
        (root / "scripts").mkdir(parents=True)
        shutil.copy2(RUNNER, root / "scripts/test-all.py")
        listing = subprocess.run(
            [sys.executable, str(RUNNER), "--list"],
            capture_output=True, text=True, check=True, timeout=5,
        )
        for line in listing.stdout.splitlines():
            command = shlex.split(line)
            for part in command:
                if not part.startswith("scripts/"):
                    continue
                path = root / part
                if path.suffix == ".sh":
                    path.write_text(f"printf '%s\\n' '{part}'\n", encoding="utf-8")
                elif path.suffix == ".py":
                    path.write_text(f"print({part!r})\n", encoding="utf-8")
                else:
                    path.touch()
        evaluations = root / "skills/subagent-model-router/evals"
        evaluations.mkdir(parents=True)
        (evaluations / "test_fixture.py").write_text(
            "import unittest\nprint('router evaluation')\n"
            "class TestFixture(unittest.TestCase):\n"
            "    def test_fixture(self):\n        pass\n", encoding="utf-8"
        )
        bin_dir = directory / "bin"
        bin_dir.mkdir()
        (bin_dir / "bash").symlink_to(shutil.which("bash"))
        (bin_dir / "python3").symlink_to(sys.executable)
        for tool in ("git", "jq", "flock", "sqlite3"):
            path = bin_dir / tool
            path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            path.chmod(0o755)
        pwsh = bin_dir / "pwsh"
        pwsh.write_text(
            f"#!{sys.executable}\nimport sys\n"
            "if '-Command' in sys.argv:\n    print('7')\n"
            "else:\n    print('scripts/test-install.ps1')\n"
            "    print('SKIP: host-specific junction test', file=sys.stderr)\n",
            encoding="utf-8",
        )
        pwsh.chmod(0o755)
        return root, {**os.environ, "PATH": str(bin_dir)}

    def run_fixture(self, root, env, *args, **kwargs):
        return subprocess.run(
            [sys.executable, str(root / "scripts/test-all.py"), *args],
            cwd=root.parent, env=env, capture_output=True, text=True,
            timeout=15, **kwargs,
        )

    def test_help_works_without_suite_dependencies(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(RUNNER), "--help"],
                cwd=directory,
                env={**os.environ, "PATH": directory},
                capture_output=True,
                text=True,
                timeout=5,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--list", result.stdout)
        self.assertIn("143", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_list_covers_maintained_suites_without_running_them(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(RUNNER), "--list"],
                cwd=directory,
                env={**os.environ, "PATH": directory},
                capture_output=True,
                text=True,
                timeout=5,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        commands = [shlex.split(line) for line in result.stdout.splitlines()]
        expected = {
            str(path.relative_to(REPO_ROOT))
            for pattern in ("test-*.sh", "test-*.ps1", "test_*.py")
            for path in (REPO_ROOT / "scripts").glob(pattern)
            if path.name != "test-common.sh"
        }
        listed = {
            part for command in commands for part in command if part.startswith("scripts/")
        }
        self.assertEqual(listed, expected)
        self.assertEqual(len(commands), len(expected) + 1)
        self.assertIn(
            ["python3", "-m", "unittest", "discover", "-s",
             "skills/subagent-model-router/evals", "-p", "test_*.py"],
            commands,
        )

    def test_missing_dependencies_fail_before_any_suite_runs(self):
        root, env = self.fixture()
        for tool in ("jq", "flock", "sqlite3", "pwsh"):
            (Path(env["PATH"]) / tool).unlink()
        result = self.run_fixture(root, env)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, "")
        for tool in ("jq", "flock", "sqlite3", "pwsh"):
            self.assertIn(tool, result.stderr)
        self.assertIn("Install", result.stderr)

    def test_failure_continues_with_separate_streams_and_eof_stdin(self):
        root, env = self.fixture()
        (root / "scripts/test-addy-install.sh").write_text(
            "if IFS= read -r input; then exit 90; fi\n"
            "pwd\nprintf 'FIRST_STDOUT\\n'\nprintf 'FIRST_STDERR\\n' >&2\nexit 7\n",
            encoding="utf-8",
        )
        result = self.run_fixture(root, env, input="must not reach suites\n")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn(str(root), result.stdout)
        self.assertIn("FIRST_STDOUT", result.stdout)
        self.assertNotIn("FIRST_STDERR", result.stdout)
        self.assertIn("FIRST_STDERR", result.stderr)
        self.assertNotIn("FIRST_STDOUT", result.stderr)
        self.assertIn("router evaluation", result.stdout)
        self.assertIn("1 failed", result.stderr)
        self.assertIn("exit 7", result.stderr)
        self.assertIn("SKIP: host-specific junction test", result.stderr)
        self.assertNotIn("PASS", result.stdout)

    def test_success_and_invalid_flags(self):
        root, env = self.fixture()
        result = self.run_fixture(root, env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("0 failed", result.stderr)
        self.assertIn("router evaluation", result.stdout)
        for flag in ("--unknown", "--li"):
            with self.subTest(flag=flag):
                result = self.run_fixture(root, env, flag)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertIn("usage:", result.stderr)

    def test_old_powershell_fails_before_suites_run(self):
        root, env = self.fixture()
        (Path(env["PATH"]) / "pwsh").write_text(
            "#!/bin/sh\nprintf '5\\n'\n", encoding="utf-8"
        )
        result = self.run_fixture(root, env)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("PowerShell 7", result.stderr)

    def start_fixture(self, root, env):
        process = subprocess.Popen(
            [sys.executable, str(root / "scripts/test-all.py")],
            cwd=root.parent, env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            start_new_session=True,
        )

        def cleanup():
            suite_pid = root / "suite-pid"
            if suite_pid.exists():
                try:
                    os.killpg(int(suite_pid.read_text()), signal.SIGKILL)
                except ProcessLookupError:
                    pass
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.communicate(timeout=5)

        self.addCleanup(cleanup)
        return process

    def wait_for_file(self, path, process):
        deadline = time.monotonic() + 5
        while not path.exists():
            if process.poll() is not None:
                stdout, stderr = process.communicate(timeout=2)
                self.fail(f"Runner exited before fixture was ready: {stdout}\n{stderr}")
            if time.monotonic() >= deadline:
                self.fail(f"Fixture never became ready: {path}")
            time.sleep(0.01)

    def test_signals_stop_active_suite_and_its_descendant(self):
        for signum in (signal.SIGINT, signal.SIGTERM):
            with self.subTest(signal=signum):
                root, env = self.fixture()
                (root / "scripts/test-addy-install.sh").write_text(
                    "exec python3 scripts/long-running.py\n", encoding="utf-8"
                )
                (root / "scripts/long-running.py").write_text(
                    "import os, pathlib, signal, subprocess, sys, time\n"
                    "pathlib.Path('suite-pid').write_text(str(os.getpid()))\n"
                    "child = subprocess.Popen([sys.executable, '-c', '''\n"
                    "import pathlib, signal, sys, time\n"
                    "def stop(signum, frame):\n"
                    "    pathlib.Path('descendant-stopped').touch()\n"
                    "    sys.exit(0)\n"
                    "signal.signal(signal.SIGINT, stop)\n"
                    "signal.signal(signal.SIGTERM, stop)\n"
                    "pathlib.Path('descendant-ready').touch()\n"
                    "while True: time.sleep(0.1)\n'''])\n"
                    "def stop(signum, frame):\n"
                    "    child.wait(timeout=3)\n"
                    "    pathlib.Path('suite-stopped').touch()\n"
                    "    sys.exit(0)\n"
                    "signal.signal(signal.SIGINT, stop)\n"
                    "signal.signal(signal.SIGTERM, stop)\n"
                    "while True: time.sleep(0.1)\n",
                    encoding="utf-8",
                )
                process = self.start_fixture(root, env)
                self.wait_for_file(root / "descendant-ready", process)
                process.send_signal(signum)
                stdout, stderr = process.communicate(timeout=8)
                self.assertEqual(process.returncode, 128 + signum, stderr)
                self.assertTrue((root / "descendant-stopped").exists(), stderr)
                self.assertTrue((root / "suite-stopped").exists(), stderr)
                self.assertNotIn("scripts/test-cleanup-skill-workspaces.sh", stdout)
                self.assertNotIn("Traceback", stderr)

    def test_cleanup_deadline_and_second_interrupt_kill_orphaned_descendant(self):
        for force in (False, True):
            with self.subTest(second_interrupt=force):
                root, env = self.fixture()
                (root / "scripts/test-addy-install.sh").write_text(
                    "exec python3 scripts/long-running.py\n", encoding="utf-8"
                )
                (root / "scripts/long-running.py").write_text(
                    "import os, pathlib, signal, subprocess, sys, time\n"
                    "pathlib.Path('suite-pid').write_text(str(os.getpid()))\n"
                    "def stop(signum, frame):\n"
                    "    pathlib.Path('leader-stopped').touch()\n"
                    "    sys.exit(0)\n"
                    "signal.signal(signal.SIGINT, stop)\n"
                    "subprocess.Popen([sys.executable, '-c', '''\n"
                    "import pathlib, signal, time\n"
                    "signal.signal(signal.SIGINT, signal.SIG_IGN)\n"
                    "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
                    "pathlib.Path('descendant-ready').touch()\n"
                    "while True: time.sleep(0.1)\n'''])\n"
                    "while True: time.sleep(0.1)\n",
                    encoding="utf-8",
                )
                process = self.start_fixture(root, env)
                self.wait_for_file(root / "descendant-ready", process)
                started = time.monotonic()
                process.send_signal(signal.SIGINT)
                self.wait_for_file(root / "leader-stopped", process)
                if force:
                    process.send_signal(signal.SIGINT)
                # The descendant holds both output pipes; EOF proves it cannot remain alive.
                stdout, stderr = process.communicate(timeout=8)
                elapsed = time.monotonic() - started
                self.assertEqual(process.returncode, 130, stderr)
                self.assertLess(elapsed, 3 if force else 7)
                if not force:
                    self.assertGreaterEqual(elapsed, 4.5)
                self.assertNotIn("scripts/test-cleanup-skill-workspaces.sh", stdout)
                self.assertIn("Ctrl-C again", stderr)
                self.assertNotIn("Traceback", stderr)

    def test_runner_broken_pipes_exit_without_tracebacks(self):
        root, env = self.fixture()
        for stream in ("stdout", "stderr"):
            with self.subTest(stream=stream):
                read_fd, write_fd = os.pipe()
                os.close(read_fd)
                try:
                    result = subprocess.run(
                        [sys.executable, str(root / "scripts/test-all.py"),
                         "--list" if stream == "stdout" else "--unknown"],
                        env=env,
                        stdout=write_fd if stream == "stdout" else subprocess.PIPE,
                        stderr=write_fd if stream == "stderr" else subprocess.PIPE,
                        timeout=5,
                    )
                finally:
                    os.close(write_fd)
                self.assertEqual(result.returncode, 141, result.stderr)
                self.assertNotIn(b"Traceback", result.stderr or b"")

    def test_child_broken_pipe_does_not_stop_remaining_suites(self):
        root, env = self.fixture()
        read_fd, write_fd = os.pipe()
        os.close(read_fd)
        try:
            result = subprocess.run(
                [sys.executable, str(root / "scripts/test-all.py")],
                env=env, stdout=write_fd, stderr=subprocess.PIPE,
                text=True, timeout=15,
            )
        finally:
            os.close(write_fd)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("exit 141", result.stderr)
        self.assertIn("RUN python3 -m unittest discover", result.stderr)
        self.assertIn("Suites:", result.stderr)

    def test_missing_suite_is_a_preflight_error(self):
        root, env = self.fixture()
        (root / "scripts/test_helpers.py").unlink()
        result = self.run_fixture(root, env)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("scripts/test_helpers.py", result.stderr)

    def test_unexecutable_dependency_is_a_runner_error(self):
        root, env = self.fixture()
        (Path(env["PATH"]) / "pwsh").write_text("not an executable format\n", encoding="utf-8")
        result = self.run_fixture(root, env)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("runner error", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_open_stdin_is_not_read_or_waited_on(self):
        root, env = self.fixture()
        read_fd, write_fd = os.pipe()
        try:
            os.write(write_fd, b"input belongs to the caller\n")
            result = subprocess.run(
                [sys.executable, str(root / "scripts/test-all.py")],
                env=env, stdin=read_fd, capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            os.set_blocking(read_fd, False)
            self.assertEqual(os.read(read_fd, 100), b"input belongs to the caller\n")
        finally:
            os.close(read_fd)
            os.close(write_fd)

    def test_preflight_process_can_be_cancelled(self):
        root, env = self.fixture()
        (Path(env["PATH"]) / "pwsh").write_text(
            f"#!{sys.executable}\n"
            "import os, pathlib, signal, sys, time\n"
            "pathlib.Path('suite-pid').write_text(str(os.getpid()))\n"
            "def stop(signum, frame):\n"
            "    pathlib.Path('preflight-stopped').touch()\n"
            "    sys.exit(0)\n"
            "signal.signal(signal.SIGTERM, stop)\n"
            "pathlib.Path('preflight-ready').touch()\n"
            "while True: time.sleep(0.1)\n",
            encoding="utf-8",
        )
        process = self.start_fixture(root, env)
        self.wait_for_file(root / "preflight-ready", process)
        process.send_signal(signal.SIGTERM)
        stdout, stderr = process.communicate(timeout=8)
        self.assertEqual(process.returncode, 143, stderr)
        self.assertTrue((root / "preflight-stopped").exists(), stderr)
        self.assertEqual(stdout, "")
        self.assertNotIn("RUN", stderr)
        self.assertNotIn("Traceback", stderr)


if __name__ == "__main__":
    unittest.main()
