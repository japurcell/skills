"""Exercise the public grader with a sanitized parent rollout and mutations."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).parent
FIXTURE = ROOT / "fixtures/router-reuse-rollout.jsonl"


class RouterReuseTests(unittest.TestCase):
    def setUp(self):
        self.rows = FIXTURE.read_text().splitlines()

    def check(self, expected):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rollout.jsonl"
            path.write_text("\n".join(self.rows) + "\n")
            result = subprocess.run(
                [sys.executable, ROOT / "grade_router_reuse.py", "execplan-implement", path],
                capture_output=True, text=True,
            )
        self.assertEqual(expected, result.returncode, result.stderr + result.stdout)

    def test_two_assignments_same_worker(self):
        self.check(0)

    def test_reload_during_reuse(self):
        self.rows.insert(7, self.rows[1])
        self.check(1)

    def test_indirect_extra_read_is_flagged_for_review(self):
        row = json.loads(self.rows[1])
        item = row["payload"]["item"]
        item["command"][-1] = "wc -c < .agents/skills/subagent-model-router/SKILL.md"
        item["aggregated_output"] = "4393"
        self.rows.insert(7, json.dumps(row))
        self.check(1)

    def test_repeated_help(self):
        self.rows.insert(7, self.rows[2])
        self.check(1)

    def test_missing_second_route(self):
        del self.rows[7]
        self.check(1)

    def test_followup_before_second_route(self):
        self.rows[7], self.rows[8] = self.rows[8], self.rows[7]
        self.check(1)

    def test_followup_delivered_to_another_worker(self):
        self.rows[9] = self.rows[9].replace("worker-a", "worker-b")
        self.check(1)

    def test_log_text_does_not_count_as_execution(self):
        row = json.loads(self.rows[7])
        item = row["payload"]["item"]
        item["command"][-1] = "echo " + repr(item["command"][-1])
        self.rows[7] = json.dumps(row)
        self.check(1)

    def test_malformed_trace(self):
        self.rows = ["{"]
        self.check(2)
