#!/usr/bin/env python3
"""Ordinary POSIX cancellation through generated status process entrypoints."""
from pathlib import Path
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = {"codex": ".codex/hooks/scan-status.py", "copilot": ".copilot/hooks/scripts/scan-status.py", "gemini": ".gemini/hooks/scripts/scan-status.py"}


class CancellationTests(unittest.TestCase):
    def setUp(self):
        if os.name != "posix":
            self.fail("POSIX cancellation evidence requires a POSIX host")
        self.temporary = tempfile.TemporaryDirectory(prefix="scan-cancellation-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.home = self.base / "home"
        self.home.mkdir()
        self.cli = self.home / ".local/lib/scan-secrets/scripts/scan-secrets.py"
        self.cli.parent.mkdir(parents=True)
        self.marker = self.base / "owned-processes.json"
        self.env = {key: value for key, value in os.environ.items() if not key.startswith(("GIT_", "PYTHON", "SCAN_SECRETS_"))}
        self.env.update(HOME=str(self.home), USERPROFILE=str(self.home), CODEX_HOME=str(self.home / ".codex"))

    def state(self, pid):
        result = subprocess.run(["/bin/ps", "-o", "stat=", "-p", str(pid)], capture_output=True, timeout=1, check=False)
        self.assertIn(result.returncode, (0, 1), result.stderr)
        return result.stdout.strip().decode("ascii")

    def fixture(self, *, root_exits=False):
        self.cli.write_text("import json,os,subprocess,sys,time\nfrom pathlib import Path\n"
            "child=subprocess.Popen([sys.executable,'-I','-S','-B','-c','import time; time.sleep(30)'])\n"
            "Path(" + repr(str(self.marker)) + ").write_text(json.dumps({'root':os.getpid(),'child':child.pid,'group':os.getpgrp()}))\n"
            + ("print('{}')\n" if root_exits else "time.sleep(30)\n"))

    def await_fixture(self, process):
        deadline = time.monotonic() + 0.5
        while time.monotonic() < deadline and process.poll() is None:
            try:
                owned = json.loads(self.marker.read_text())
            except (FileNotFoundError, ValueError):
                time.sleep(0.002)
                continue
            self.assertEqual(owned["root"], owned["group"])
            self.assertEqual(os.getpgid(owned["root"]), owned["group"])
            self.assertEqual(os.getpgid(owned["child"]), owned["group"])
            return owned
        self.fail("controlled status CLI did not start before cancellation")

    def cleanup(self, process, owned):
        # Only this callback's private, marker-identified process group is owned.
        if owned is None and self.marker.exists():
            owned = json.loads(self.marker.read_text())
        if owned is not None:
            self.assertGreater(owned["group"], 1)
            self.assertEqual(owned["root"], owned["group"])
            self.assertNotEqual(owned["group"], os.getpgrp())
            try:
                os.killpg(owned["group"], signal.SIGKILL)
            except ProcessLookupError:
                pass
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=2)

    def assert_response(self, provider, process, output, error):
        self.assertEqual(process.returncode, 0, error)
        self.assertEqual(error, b"")
        self.assertLess(len(output), 512)
        rows = [json.loads(row) for row in output.splitlines()]
        if provider == "copilot":
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[-1], {})
            self.assertEqual(rows[0]["type"], "progress")
            message = rows[0]["message"]
        else:
            self.assertEqual(len(rows), 1)
            self.assertEqual(set(rows[0]), {"systemMessage"})
            message = rows[0]["systemMessage"]
        self.assertIn("scan-secrets status: unavailable", message)
        self.assertIn("Historical only; never authorizes publication.", message)

    def cancel_tree(self, provider, signum, *, closed_output=False):
        self.fixture()
        self.marker.unlink(missing_ok=True)
        started = time.monotonic()
        process = subprocess.Popen([sys.executable, "-I", "-S", "-B", str(ROOT / ENTRIES[provider])],
            cwd=self.base, env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        owned = None
        try:
            process.stdin.write(json.dumps({"hook_event_name": "agentStop"}).encode())
            process.stdin.flush()
            owned = self.await_fixture(process)
            if closed_output:
                process.stdout.close()
                process.stdout = None
            cancelled = time.monotonic()
            process.send_signal(signum)
            output, error = process.communicate(timeout=1)
            elapsed = time.monotonic() - started
            states = {key: self.state(owned[key]) for key in ("root", "child")}
            print(json.dumps({"provider": provider, "signal": signal.Signals(signum).name,
                "closed_output": closed_output, "exit": process.returncode, "seconds": elapsed,
                "cancel_seconds": time.monotonic() - cancelled, "states": states}), flush=True)
            self.assertLess(elapsed, 1.0)
            self.assertFalse(any(state and not state.startswith("Z") for state in states.values()), states)
            if closed_output:
                self.assertEqual(process.returncode, 0, error)
                self.assertEqual(error, b"")
            else:
                self.assert_response(provider, process, output, error)
        finally:
            self.cleanup(process, owned)

    def test_sigterm_cleans_hanging_status_tree(self):
        for provider in ENTRIES:
            with self.subTest(provider=provider):
                self.cancel_tree(provider, signal.SIGTERM)

    def test_sigint_cleans_hanging_status_tree(self):
        for provider in ENTRIES:
            with self.subTest(provider=provider):
                self.cancel_tree(provider, signal.SIGINT)

    def test_cancellation_with_closed_output_is_quiet(self):
        for provider in ENTRIES:
            for signum in (signal.SIGTERM, signal.SIGINT):
                with self.subTest(provider=provider, signal=signum):
                    self.cancel_tree(provider, signum, closed_output=True)

    def test_cancellation_during_incomplete_input_never_starts_status(self):
        import array
        import fcntl
        import termios
        self.cli.write_text("from pathlib import Path\nPath(" + repr(str(self.marker)) + ").write_text('unexpected child')\n")
        for provider in ENTRIES:
            for signum in (signal.SIGTERM, signal.SIGINT):
                with self.subTest(provider=provider, signal=signum):
                    started = time.monotonic()
                    read_fd, write_fd = os.pipe()
                    os.write(write_fd, b"{")
                    unread = array.array("i", [0])
                    fcntl.ioctl(read_fd, termios.FIONREAD, unread, True)
                    self.assertEqual(unread[0], 1)
                    process = subprocess.Popen([sys.executable, "-I", "-S", "-B", str(ROOT / ENTRIES[provider])],
                        cwd=self.base, env=self.env, stdin=read_fd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    try:
                        # The public pipe's unread-byte count proves that the
                        # adapter consumed the incomplete prefix before signal.
                        while True:
                            unread = array.array("i", [0])
                            fcntl.ioctl(read_fd, termios.FIONREAD, unread, True)
                            self.assertIsNone(process.poll(), "adapter ended before input cancellation")
                            if unread[0] == 0:
                                break
                            self.assertLess(time.monotonic() - started, 0.5)
                            time.sleep(0.001)
                        process.send_signal(signum)
                        output, error = process.communicate(timeout=1)
                        elapsed = time.monotonic() - started
                        print(json.dumps({"provider": provider, "signal": signal.Signals(signum).name,
                            "incomplete_input": True, "seconds": elapsed, "exit": process.returncode}), flush=True)
                        self.assertLess(elapsed, 1.0)
                        self.assertFalse(self.marker.exists())
                        # Input was incomplete, so Copilot uses one portable final document.
                        self.assert_response("unknown", process, output, error)
                    finally:
                        os.close(read_fd)
                        os.close(write_fd)
                        self.cleanup(process, None)

    def test_finished_root_descendant_is_cleaned_before_response(self):
        self.fixture(root_exits=True)
        for provider in ENTRIES:
            with self.subTest(provider=provider):
                self.marker.unlink(missing_ok=True)
                started = time.monotonic()
                process = subprocess.Popen([sys.executable, "-I", "-S", "-B", str(ROOT / ENTRIES[provider])],
                    cwd=self.base, env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                owned = None
                try:
                    output, error = process.communicate(b'{}', timeout=1)
                    owned = json.loads(self.marker.read_text())
                    self.assertEqual(owned["root"], owned["group"])
                    states = {key: self.state(owned[key]) for key in ("root", "child")}
                    elapsed = time.monotonic() - started
                    print(json.dumps({"provider": provider, "finished_root": True,
                        "seconds": elapsed, "states": states}), flush=True)
                    self.assertLess(elapsed, 1.0)
                    self.assertFalse(any(state and not state.startswith("Z") for state in states.values()), states)
                    self.assert_response("unknown", process, output, error)
                finally:
                    self.cleanup(process, owned)


if __name__ == "__main__":
    unittest.main()
