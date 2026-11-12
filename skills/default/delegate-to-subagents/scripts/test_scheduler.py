#!/usr/bin/env python3
"""Public CLI acceptance tests for scheduler.py."""
import json
import os
import signal
import time
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CLI = Path(__file__).with_name("scheduler.py")


class SchedulerCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state = Path(self.tmp.name) / "state.json"

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args, ok=True):
        p = subprocess.run([sys.executable, str(CLI), "--state", str(self.state), *args], text=True, capture_output=True)
        if ok:
            self.assertEqual(p.returncode, 0, p.stderr)
        else:
            self.assertNotEqual(p.returncode, 0)
        return json.loads(p.stdout) if p.stdout.strip() else None

    def test_deadline_checkpoint_extension_and_host_stop_gate(self):
        self.run_cli("register", "a1", "agent", "task", "--deadline", "100", "--checkpoint", "300", "--grace", "5", "--now", "0")
        self.assertEqual(self.run_cli("tick", "--now", "100")["events"][0]["type"], "deadline_expired")
        self.run_cli("checkpoint", "a1", "--eta", "130", "--now", "101")
        self.run_cli("extend", "a1", "--eta", "130", "--now", "102")
        self.run_cli("extend", "a1", "--eta", "140", "--now", "103", ok=False)
        self.assertEqual(self.run_cli("tick", "--now", "130")["events"][0]["type"], "extension_expired")
        self.run_cli("checkpoint", "a1", "--now", "131", ok=False)
        self.run_cli("transfer", "a1", "--now", "132", ok=False)
        self.run_cli("confirm-stopped", "a1", "--confirmation", "worker-and-writes-stopped", "--now", "133")
        self.assertTrue(self.run_cli("transfer", "a1", "--now", "134")["host_action"])

    def test_status_decision_is_bounded_and_late_status_cannot_revive(self):
        self.run_cli("register", "x", "agent", "task", "--deadline", "110", "--checkpoint", "300", "--grace", "5", "--now", "100")
        self.run_cli("tick", "--now", "110")
        self.run_cli("checkpoint", "x", "--now", "111")
        self.assertEqual(self.run_cli("tick", "--now", "500")["events"][0]["type"], "checkpoint_expired")
        self.run_cli("checkpoint", "x", "--now", "501", ok=False)
        self.run_cli("extend", "x", "--eta", "600", "--now", "501", ok=False)

    def test_invalid_eta_and_state_fail_without_traceback(self):
        self.run_cli("register", "x", "agent", "task", "--deadline", "10", "--checkpoint", "5", "--now", "0")
        self.run_cli("tick", "--now", "10")
        self.run_cli("checkpoint", "x", "--eta", "nan", "--now", "11", ok=False)
        self.run_cli("checkpoint", "x", "--now", "11")
        self.run_cli("extend", "x", "--eta", "nan", "--now", "12", ok=False)
        self.state.write_text("[]")
        p = subprocess.run([sys.executable, str(CLI), "--state", str(self.state), "list"], capture_output=True, text=True)
        self.assertIn("malformed state", p.stderr)
        self.assertNotIn("Traceback", p.stderr)
        self.assertEqual(self.state.read_text(), "[]")

    def test_progress_reminder_completion_cancel_and_malformed_state(self):
        self.run_cli("register", "a2", "agent", "task", "--deadline", "100", "--checkpoint", "10", "--now", "0")
        self.assertEqual(self.run_cli("tick", "--now", "11")["events"][0]["type"], "progress_reminder")
        self.run_cli("complete", "a2", "--now", "12")
        self.assertEqual(self.run_cli("tick", "--now", "50")["events"], [])
        self.run_cli("register", "a3", "agent", "task", "--deadline", "100", "--checkpoint", "10", "--now", "0")
        self.run_cli("cancel", "a3", "--now", "1")
        self.state.write_text("{bad")
        result = subprocess.run([sys.executable, str(CLI), "--state", str(self.state), "list"], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("malformed state", result.stderr.lower())

    def test_wait_is_bounded_and_help_is_public(self):
        p = subprocess.run([sys.executable, str(CLI), "--help"], text=True, capture_output=True)
        self.assertEqual(p.returncode, 0)
        self.assertIn("wait", p.stdout)
        self.run_cli("register", "a4", "agent", "task", "--deadline", "100", "--checkpoint", "10", "--now", "0")
        self.assertEqual(self.run_cli("wait", "--max-wait", "0", "--now", "1")["wait_seconds"], 0)

    def test_real_wait_wakes_for_earliest_event(self):
        now = time.time()
        self.run_cli("register", "a5", "agent", "task", "--deadline", str(now + .25), "--checkpoint", "30", "--grace", "1", "--now", str(now))
        started = time.monotonic()
        out = self.run_cli("wait", "--max-wait", "2", "--now", str(now))
        self.assertLess(time.monotonic() - started, 1.5)
        self.assertEqual(out["events"][0]["type"], "deadline_expired")

    def test_wait_rechecks_concurrent_changes_without_holding_lock(self):
        self.run_cli("register", "x", "agent", "task", "--deadline", str(time.time() + 30), "--checkpoint", "30")
        waiter = subprocess.Popen([sys.executable, str(CLI), "--state", str(self.state), "wait", "--max-wait", "2"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(.2)
        started = time.monotonic()
        self.run_cli("register", "y", "agent", "task", "--deadline", str(time.time() + .25), "--checkpoint", "30")
        self.assertLess(time.monotonic() - started, 1)
        stdout, stderr = waiter.communicate(timeout=2)
        self.assertEqual(waiter.returncode, 0, stderr)
        self.assertEqual(json.loads(stdout)["events"][0]["assignment"], "y")

    def test_wait_returns_already_due_and_partial_state_is_rejected(self):
        self.run_cli("register", "x", "agent", "task", "--deadline", "10", "--checkpoint", "30", "--now", "0")
        started = time.monotonic()
        self.assertEqual(self.run_cli("wait", "--max-wait", "2", "--now", "11")["events"][0]["type"], "deadline_expired")
        self.assertLess(time.monotonic() - started, 1)
        state = json.loads(self.state.read_text())
        del state["assignments"]["x"]["checkpoint_interval"]
        self.state.write_text(json.dumps(state))
        p = subprocess.run([sys.executable, str(CLI), "--state", str(self.state), "tick"], capture_output=True, text=True)
        self.assertIn("malformed state", p.stderr)
        self.assertNotIn("Traceback", p.stderr)

    def test_help_contract_and_unknown_options(self):
        for command in ([], ["register"], ["wait"], ["checkpoint"]):
            p = subprocess.run([sys.executable, str(CLI), *command, "--help"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("seconds", p.stdout)
            self.assertIn("stdout", p.stdout)
        p = subprocess.run([sys.executable, str(CLI), "--state", str(self.state), "register", "x", "a", "t", "--dead", "10", "--checkpoint", "2"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
        self.assertEqual(p.returncode, 2)
        self.assertEqual(p.stdout, "")
        self.assertIn("error", p.stderr)

    def test_interrupt_and_closed_stdout_have_no_traceback(self):
        waiter = subprocess.Popen([sys.executable, str(CLI), "--state", str(self.state), "wait", "--max-wait", "10"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, text=True)
        time.sleep(.2)
        waiter.send_signal(signal.SIGINT)
        stdout, stderr = waiter.communicate(timeout=3)
        self.assertEqual(waiter.returncode, 130)
        self.assertEqual(stdout, "")
        self.assertNotIn("Traceback", stderr)
        read_fd, write_fd = os.pipe()
        os.close(read_fd)
        p = subprocess.run([sys.executable, str(CLI), "--state", str(self.state), "list"], stdout=write_fd, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, text=True)
        os.close(write_fd)
        self.assertNotEqual(p.returncode, 0)
        self.assertNotIn("Traceback", p.stderr)
        self.assertNotIn("Exception ignored", p.stderr)

    def test_concurrent_registration_is_serialized_and_bad_numbers_rejected(self):
        commands = []
        for name in ("a6", "a7", "a8", "a9"):
            commands.append(subprocess.Popen([sys.executable, str(CLI), "--state", str(self.state), "register", name, "agent", "task", "--deadline", "100", "--checkpoint", "10", "--now", "0"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
        for p in commands:
            stdout, stderr = p.communicate(timeout=5)
            self.assertEqual(p.returncode, 0, stderr)
        self.assertEqual(len(self.run_cli("list")["assignments"]), 4)
        self.run_cli("register", "bad", "agent", "task", "--deadline", "inf", "--checkpoint", "10", "--now", "0", ok=False)
        self.run_cli("wait", "--max-wait", "-1", "--now", "0", ok=False)


if __name__ == "__main__":
    unittest.main()
