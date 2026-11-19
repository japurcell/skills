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

    def test_next_wake_orders_timers_without_mutating_state(self):
        self.assertEqual(self.run_cli("next-wake", "--now", "0"), {"wake": None})
        self.run_cli("register", "z", "agent-z", "task", "--deadline", "20", "--checkpoint", "10", "--now", "0")
        self.run_cli("register", "b", "agent-b", "task", "--deadline", "10", "--now", "0")
        self.run_cli("register", "a", "agent-a", "task", "--deadline", "10", "--now", "0")
        original = self.state.read_bytes()
        self.assertEqual(self.run_cli("next-wake", "--now", "1"), {"wake": {"assignment": "a", "agent": "agent-a", "due": 10, "reason": "deadline_expired"}})
        self.assertEqual(self.state.read_bytes(), original)
        self.assertEqual(len(self.run_cli("tick", "--now", "10")["events"]), 3)

    def test_next_wake_legacy_overdue_phase_preserves_bytes(self):
        self.state.write_text(json.dumps({"version": 2, "assignments": {"legacy": {
            "id": "legacy", "agent": "worker", "task": "task", "route": "",
            "status": "active", "phase": "running", "deadline": 20,
            "checkpoint_interval": 10, "checkpoint_grace": 5, "next_checkpoint": 10,
            "extension_used": False, "stop_confirmed": False, "transferred": False
        }}}))
        original = self.state.read_bytes()
        self.assertEqual(self.run_cli("next-wake", "--now", "30"), {"wake": {"assignment": "legacy", "agent": "worker", "due": 20, "reason": "deadline_expired"}})
        self.assertEqual(self.state.read_bytes(), original)
        self.run_cli("complete", "legacy", "--now", "30")
        self.assertEqual(self.run_cli("next-wake", "--now", "30"), {"wake": None})

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

    def test_registration_without_interval_waits_only_for_deadline(self):
        self.run_cli("register", "x", "agent", "task", "--deadline", "600", "--now", "0")
        self.assertEqual(json.loads(self.state.read_text())["version"], 3)
        state = self.run_cli("list")["assignments"][0]
        self.assertNotIn("checkpoint_interval", state)
        self.assertNotIn("next_checkpoint", state)
        self.assertEqual(self.run_cli("tick", "--now", "300")["events"], [])
        self.assertEqual(self.run_cli("tick", "--now", "600")["events"][0]["type"], "deadline_expired")

    def test_existing_v2_state_keeps_its_opt_in_interval(self):
        self.state.write_text(json.dumps({
            "version": 2,
            "assignments": {
                "legacy": {
                    "id": "legacy", "agent": "agent", "task": "task", "route": "",
                    "status": "active", "phase": "running", "deadline": 100,
                    "checkpoint_interval": 10, "checkpoint_grace": 60,
                    "next_checkpoint": 10, "extension_used": False,
                    "stop_confirmed": False, "transferred": False,
                },
                "extended": {
                    "id": "extended", "agent": "agent", "task": "task", "route": "",
                    "status": "active", "phase": "extended", "deadline": 40,
                    "checkpoint_interval": 10, "checkpoint_grace": 60,
                    "next_checkpoint": 30, "extension_used": True,
                    "stop_confirmed": False, "transferred": False,
                },
                "stopped": {
                    "id": "stopped", "agent": "agent", "task": "task", "route": "",
                    "status": "active", "phase": "stop", "deadline": 40,
                    "checkpoint_interval": 10, "checkpoint_grace": 60,
                    "next_checkpoint": 30, "extension_used": True,
                    "stop_confirmed": False, "transferred": False,
                },
            },
        }))
        self.run_cli("list")
        self.assertEqual(json.loads(self.state.read_text())["version"], 2)
        self.assertEqual(self.run_cli("tick", "--now", "9")["events"], [])
        self.assertEqual(json.loads(self.state.read_text())["version"], 2)
        self.assertEqual(self.run_cli("wait", "--max-wait", ".01", "--now", "9")["events"], [])
        self.assertEqual(json.loads(self.state.read_text())["version"], 2)
        event = self.run_cli("tick", "--now", "10")["events"][0]
        self.assertEqual((event["assignment"], event["type"]), ("legacy", "progress_reminder"))
        self.assertEqual(json.loads(self.state.read_text())["version"], 3)
        self.run_cli("complete", "legacy", "--now", "11")
        self.assertEqual(self.run_cli("tick", "--now", "40")["events"], [
            {"assignment": "extended", "host_action": "request stop; confirm worker and writes stopped before ownership transfer", "type": "extension_expired"},
        ])
        self.run_cli("transfer", "stopped", "--now", "41", ok=False)
        self.run_cli("confirm-stopped", "stopped", "--confirmation", "worker-and-writes-stopped", "--now", "41")
        self.run_cli("transfer", "stopped", "--now", "42")

    def test_late_tick_and_wait_expire_all_due_assignments_once(self):
        for command in (["tick"], ["wait", "--max-wait", "0"]):
            with self.subTest(command=command):
                for key, interval in (("overdue", "10"), ("tied", "40")):
                    self.run_cli("register", key, "worker", "work", "--now", "0",
                                 "--deadline", "40", "--checkpoint", interval, "--grace", "0")

                def due(now):
                    return [(event["assignment"], event["type"])
                            for event in self.run_cli(*command, "--now", now)["events"]]
                self.assertCountEqual(due("41"), [("overdue", "deadline_expired"), ("tied", "deadline_expired")])
                self.assertCountEqual(due("42"), [("overdue", "checkpoint_expired"), ("tied", "checkpoint_expired")])
                self.assertEqual(due("43"), [])
                self.state.unlink()

    def test_late_observation_starts_grace_and_reminder_does_not_forbid_checkpoint(self):
        self.run_cli("register", "x", "worker", "work", "--now", "0", "--deadline", "40",
                     "--checkpoint", "10", "--grace", "5")
        self.run_cli("checkpoint", "x", "--now", "12")
        self.assertEqual(self.run_cli("tick", "--now", "50")["events"][0]["type"], "deadline_expired")
        self.assertEqual(self.run_cli("tick", "--now", "54")["events"], [])
        self.assertEqual(self.run_cli("tick", "--now", "55")["events"][0]["type"], "checkpoint_expired")

    def test_multiple_deadlines_skip_completed_assignment(self):
        self.run_cli("register", "early", "agent", "task", "--deadline", "100", "--now", "0")
        self.run_cli("register", "late", "agent", "task", "--deadline", "200", "--now", "0")
        self.run_cli("complete", "early", "--now", "50")
        self.assertEqual(self.run_cli("tick", "--now", "100")["events"], [])
        events = self.run_cli("tick", "--now", "200")["events"]
        self.assertEqual([(event["assignment"], event["type"]) for event in events], [("late", "deadline_expired")])

    def test_deadline_only_checkpoint_keeps_grace_and_extension(self):
        self.run_cli("register", "x", "agent", "task", "--deadline", "100", "--grace", "5", "--now", "0")
        self.run_cli("tick", "--now", "100")
        self.run_cli("checkpoint", "x", "--eta", "130", "--now", "101")
        self.assertNotIn("next_checkpoint", self.run_cli("list")["assignments"][0])
        self.run_cli("extend", "x", "--eta", "130", "--now", "102")
        self.assertEqual(self.run_cli("tick", "--now", "130")["events"][0]["type"], "extension_expired")

    def test_deadline_only_wait_has_no_early_progress_wakeup(self):
        deadline = time.time() + .45
        self.run_cli("register", "quiet", "agent", "task", "--deadline", str(deadline))
        early = self.run_cli("wait", "--max-wait", ".15")
        self.assertEqual(early["events"], [])
        self.assertGreaterEqual(early["wait_seconds"], .12)
        due = self.run_cli("wait", "--max-wait", "1")
        self.assertEqual(due["events"][0]["type"], "deadline_expired")

    def test_last_completion_removes_deadline_wakeup(self):
        self.run_cli("register", "only", "agent", "task", "--deadline", str(time.time() + 10))
        waiter = subprocess.Popen([sys.executable, str(CLI), "--state", str(self.state), "wait", "--max-wait", ".25"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(.05)
        self.run_cli("complete", "only")
        stdout, stderr = waiter.communicate(timeout=2)
        self.assertEqual(waiter.returncode, 0, stderr)
        result = json.loads(stdout)
        self.assertEqual(result["events"], [])
        self.assertGreaterEqual(result["wait_seconds"], .22)

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
