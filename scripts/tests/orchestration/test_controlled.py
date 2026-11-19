"""Controlled, public-CLI orchestration checks."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from grade_controlled import grade_continuity, grade_transfer, grade_turn


ROOT = Path(__file__).resolve().parents[3]
SCHEDULER = ROOT / "skills/default/delegate-to-subagents/scripts/scheduler.py"


def run_scheduler(state, *args, ok=True):
    result = subprocess.run(
        [sys.executable, str(SCHEDULER), "--state", str(state), *args],
        capture_output=True, text=True, timeout=5,
    )
    if ok:
        if result.returncode != 0:
            raise AssertionError(result.stderr)
    elif result.returncode == 0:
        raise AssertionError("scheduler command unexpectedly succeeded")
    parsed = json.loads(result.stdout) if result.stdout.strip() else None
    return {"returncode": result.returncode, "result": parsed, "stderr": result.stderr}


class ControlledOrchestrationTests(unittest.TestCase):
    def test_simulated_inverse_completion_is_admitted_before_expiry(self):
        # Offline host trace: delivery and observation are distinct; no native
        # timing or host notification capability is asserted by this fixture.
        for caller in ('delegate-to-subagents', 'execplan-implement'):
            guidance = (ROOT / 'skills/default' / caller / 'SKILL.md').read_text()
            self.assertIn('Drain delivered completions before expiring assignments', guidance)
            self.assertIn('Refresh after completion, a registry mutation, a deadline or an interruption', guidance)
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / 'state.json'
            run_scheduler(state, 'register', 'silent', 'worker-silent', 'work', '--deadline', '10', '--grace', '5', '--now', '0')
            run_scheduler(state, 'register', 'quick', 'worker-quick', 'work', '--deadline', '20', '--now', '0')
            wake = run_scheduler(state, 'next-wake', '--now', '1')['result']['wake']
            self.assertEqual((wake['assignment'], wake['due']), ('silent', 10))
            delivered = [{'assignment': 'quick', 'result': 'QUICK', 'completed_at': 5}]
            observed = delivered.pop(0)
            self.assertEqual(observed['result'], 'QUICK')
            run_scheduler(state, 'complete', observed['assignment'], '--now', '6')
            wake = run_scheduler(state, 'next-wake', '--now', '6')['result']['wake']
            self.assertEqual((wake['assignment'], wake['due']), ('silent', 10))
            events = run_scheduler(state, 'tick', '--now', '10')['result']['events']
            self.assertEqual([(e['assignment'], e['type']) for e in events], [('silent', 'deadline_expired')])
            wake = run_scheduler(state, 'next-wake', '--now', '10')['result']['wake']
            self.assertEqual((wake['assignment'], wake['due'], wake['reason']), ('silent', 15, 'checkpoint_expired'))

    def test_simulated_standalone_reservation_survives_delayed_dispatch(self):
        # The standalone registry is parent-owned guidance, not executable code.
        # Pin the rules this offline simulation exercises to the current caller.
        caller = (ROOT / 'skills/default/execplan-implement/SKILL.md').read_text()
        self.assertIn('including reservations whose worker handle has not yet returned', caller)
        self.assertIn('then expiry before reminder, then assignment ID', caller)
        self.assertIn('re-anchor the deadline once', caller)
        registry = {
            'reserved': {'handle': None, 'deadline': 10},
            'attached': {'handle': 'worker-b', 'deadline': 20},
        }
        def next_wake():
            return min((entry['deadline'], assignment) for assignment, entry in registry.items())

        self.assertEqual(next_wake(), (10, 'reserved'))
        # Dispatch returns late; attaching a handle alone does not change the
        # original absolute deadline. This scenario does not use re-anchoring.
        registry['reserved']['handle'] = 'worker-a'
        self.assertEqual(next_wake(), (10, 'reserved'))
        del registry['reserved']
        self.assertEqual(next_wake(), (20, 'attached'))

    def test_turn_requires_assignment_timing_and_action_observations(self):
        errors = grade_turn({"before": {}, "after": {}})
        details = "\n".join(errors)
        for evidence in ("assignment id", "phase", "deadline", "observation time", "action list"):
            with self.subTest(evidence=evidence):
                self.assertIn(evidence, details)

    def test_transfer_requires_known_worker_and_writer_states(self):
        self.assertIn("worker state", " ".join(grade_transfer(None, False, True)))
        self.assertIn("writer state", " ".join(grade_transfer(False, None, True)))

    def test_continuity_requires_worker_ids_fact_and_handoff_context(self):
        report = {"owner": "owner", "pinned_revision": "r7", "completed_evidence": ["run-4"],
                  "blocker": "none", "deadline": 50, "next_action": "review"}
        errors = "\n".join(grade_continuity(report, report, {}, {}, {}))
        for evidence in ("worker id", "setup fact", "replacement worker id", "environment", "revision", "evidence"):
            with self.subTest(evidence=evidence):
                self.assertIn(evidence, errors)

    def test_transfer_waits_for_worker_and_outstanding_writer_processes(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            run_scheduler(state, "register", "w", "agent", "work", "--deadline", "100", "--now", "0")
            worker = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
            output = Path(directory) / "pending-write.log"
            writer_code = "import pathlib,sys,time; p=pathlib.Path(sys.argv[1]);\nwhile True:\n p.open('a').write('pending\\n'); time.sleep(.02)"
            writer = subprocess.Popen([sys.executable, "-c", writer_code, str(output)])
            try:
                self.assertIsNone(worker.poll())
                self.assertIsNone(writer.poll())
                initial = output.stat().st_size if output.exists() else 0
                time.sleep(.07)
                self.assertGreater(output.stat().st_size, initial)
                self.assertTrue(grade_transfer(worker.poll() is None, writer.poll() is None, True))
            finally:
                worker.terminate()
                writer.terminate()
                worker.wait(timeout=3)
                writer.wait(timeout=3)
            confirmed = run_scheduler(state, "confirm-stopped", "w", "--confirmation", "worker-and-writes-stopped", "--now", "1")
            self.assertTrue(confirmed["result"]["stop_confirmed"])
            transferred = run_scheduler(state, "transfer", "w", "--now", "2")
            self.assertEqual(grade_transfer(worker.poll() is None, writer.poll() is None, bool(transferred["result"])), [])

    def test_five_minute_lookup_is_quiet_before_real_deadline(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            run_scheduler(state, "register", "worker-a", "agent-a", "unit task", "--deadline", "600", "--now", "0")
            before = run_scheduler(state, "list")["result"]["assignments"][0]
            tick = run_scheduler(state, "tick", "--now", "300")
            after = run_scheduler(state, "list")["result"]["assignments"][0]
            observation = {
                "at": 300,
                "before": before,
                "tick": tick,
                "after": after,
                "actions": [],
                "dispatches": [],
                "setup_reads": [],
                "parent_status_lookups": [],
            }
            self.assertEqual(grade_turn(observation), [])
            lookup_only = dict(observation, parent_status_lookups=["worker-a"])
            self.assertTrue(grade_turn(lookup_only))

    def test_deadline_action_and_two_worker_early_completion(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            run_scheduler(state, "register", "early", "worker-a", "early work", "--deadline", "10", "--grace", "20", "--now", "0")
            run_scheduler(state, "register", "later", "worker-b", "later work", "--deadline", "20", "--grace", "20", "--now", "0")
            run_scheduler(state, "complete", "early", "--now", "5")
            wait = run_scheduler(state, "wait", "--now", "19", "--max-wait", "0")
            self.assertEqual(wait["result"]["events"], [])
            before = next(a for a in run_scheduler(state, "list")["result"]["assignments"] if a["id"] == "later")
            due = run_scheduler(state, "tick", "--now", "20")
            self.assertEqual([e["assignment"] for e in due["result"]["events"]], ["later"])
            after = next(a for a in run_scheduler(state, "list")["result"]["assignments"] if a["id"] == "later")
            observation = {"at": 20, "before": before, "after": after,
                           "actions": due["result"]["events"], "dispatches": [], "setup_reads": []}
            self.assertEqual(grade_turn(observation), [])
            bad = dict(observation, before=dict(before, id="other"))
            self.assertTrue(grade_turn(bad))

    def test_silent_expiry_one_extension_then_stop(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            run_scheduler(state, "register", "w", "agent", "work", "--deadline", "10", "--grace", "5", "--now", "0")
            event = run_scheduler(state, "tick", "--now", "10")["result"]["events"][0]
            self.assertEqual(event["type"], "deadline_expired")
            run_scheduler(state, "checkpoint", "w", "--eta", "13", "--now", "11")
            extension = run_scheduler(state, "extend", "w", "--eta", "30", "--now", "11")
            self.assertEqual(extension["result"]["extended_to"], 30)
            self.assertNotEqual(run_scheduler(state, "extend", "w", "--eta", "40", "--now", "12", ok=False)["returncode"], 0)
            stopped = run_scheduler(state, "tick", "--now", "30")["result"]["events"][0]
            self.assertEqual(stopped["type"], "extension_expired")
            confirmed = run_scheduler(state, "confirm-stopped", "w", "--confirmation", "worker-and-writes-stopped", "--now", "32")
            self.assertTrue(confirmed["result"]["stop_confirmed"])
            transfer = run_scheduler(state, "transfer", "w", "--now", "33")
            self.assertEqual(grade_transfer(False, False, bool(transfer["result"])), [])
            self.assertTrue(grade_transfer(False, True, True))
            self.assertTrue(grade_transfer(True, False, True))

    def test_missing_status_expires_at_bounded_grace(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            run_scheduler(state, "register", "silent", "agent", "work", "--deadline", "10", "--grace", "5", "--now", "0")
            requested = run_scheduler(state, "tick", "--now", "10")["result"]["events"]
            self.assertEqual(requested[0]["type"], "deadline_expired")
            early = run_scheduler(state, "tick", "--now", "14")["result"]["events"]
            self.assertEqual(early, [])
            expired = run_scheduler(state, "tick", "--now", "15")["result"]["events"]
            self.assertEqual(expired[0]["type"], "checkpoint_expired")

    def test_same_worker_and_replacement_context_reports(self):
        # A single child keeps setup in memory; the replacement receives only a
        # compact handoff containing environment, revision, and evidence.
        worker_code = "import json,sys; fact='pinned revision r7'; print(json.dumps({'setup_read':True}),flush=True); line=sys.stdin.readline(); print(json.dumps({'fact':fact}),flush=True)"
        worker = subprocess.Popen([sys.executable, "-u", "-c", worker_code], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        first = json.loads(worker.stdout.readline())
        worker.stdin.write("follow-up\n")
        worker.stdin.flush()
        returned = json.loads(worker.stdout.readline())
        worker.wait(timeout=3)
        worker.stdin.close()
        worker.stdout.close()
        replacement_code = "import json,sys; d=json.loads(sys.stdin.readline()); print(json.dumps(d),flush=True)"
        replacement_proc = subprocess.run([sys.executable, "-c", replacement_code], input=json.dumps({"environment":"py3", "pinned_revision":"r7", "evidence":"run-4"}) + "\n", capture_output=True, text=True, timeout=3, check=True)
        received = json.loads(replacement_proc.stdout)
        same_worker = {"worker_id": "worker-a", "known_fact_returned": returned.get("fact") if first["setup_read"] else None}
        replacement = {"worker_id": "worker-b", **received}
        expected = {"worker_id": "worker-a", "replacement_id": "worker-b", "known_fact": "pinned revision r7", "environment": "py3", "pinned_revision": "r7", "evidence": "run-4"}
        report1 = {"owner": "worker-a", "pinned_revision": "r7", "completed_evidence": ["run-4"], "blocker": "none", "deadline": 50, "next_action": "review"}
        report2 = dict(report1, owner="worker-b", completed_evidence=["run-4", "run-5"], next_action="merge")
        self.assertEqual(grade_continuity(report1, report2, same_worker, replacement, expected), [])
        bad_replacement = dict(replacement, evidence="")
        self.assertTrue(grade_continuity(report1, report2, same_worker, bad_replacement, expected))
        self.assertTrue(grade_continuity(dict(report1, blocker=""), dict(report2, setup_dump="full setup"), same_worker, replacement, expected))


if __name__ == "__main__":
    unittest.main()
