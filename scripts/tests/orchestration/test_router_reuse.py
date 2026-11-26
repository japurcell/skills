"""Exercise the public grader with a sanitized parent rollout and mutations."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).parent
FIXTURE = ROOT / "fixtures/router-reuse-rollout.jsonl"
PRIMARY_MODEL = "claude-haiku-5.5"
FALLBACK_ROUTE = dict(model="gpt-6-luna", effort_policy="host_default", reasoning_effort=None)


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

    def change_route(self, index, **changes):
        row = json.loads(self.rows[index])
        item = row["payload"]["item"]
        route = json.loads(item["aggregated_output"])
        route.update(changes)
        item["aggregated_output"] = json.dumps(route)
        self.rows[index] = json.dumps(row)

    def test_blocked_route(self):
        self.change_route(7, route_available=False, model=None, fallback="none")
        self.check(1)

    def test_different_followup_model(self):
        self.change_route(7, model="another-model")
        self.check(1)

    def test_omitted_effort_does_not_match_explicit_effort(self):
        self.change_route(7, effort_policy="explicit", reasoning_effort="medium")
        self.check(1)

    def test_missing_spawn_evidence(self):
        row = json.loads(self.rows[4])
        del row["payload"]["arguments"]
        self.rows[4] = json.dumps(row)
        self.check(2)

    def spawn_with_args(self, **changes):
        spawn = json.loads(self.rows[4])
        args = json.loads(spawn["payload"]["arguments"])
        args.update(changes)
        spawn["payload"]["arguments"] = json.dumps(args)
        return spawn

    def insert_rejected_spawn(self, index, model):
        attempt = self.spawn_with_args(model=model)
        attempt["payload"]["call_id"] = "failed-spawn"
        receipt = {"type": "response_item", "payload": {
            "type": "function_call_output", "call_id": "failed-spawn",
            "output": json.dumps({"error": "Model unavailable"}),
        }}
        self.rows[index:index] = [json.dumps(attempt), json.dumps(receipt)]

    def test_explicit_effort_must_match_both_routes(self):
        for index in (3, 7):
            self.change_route(index, effort_policy="explicit", reasoning_effort="medium")
        self.rows[4] = json.dumps(self.spawn_with_args(reasoning_effort="medium"))
        self.check(0)
        self.change_route(7, reasoning_effort="high")
        self.check(1)
        self.change_route(7, effort_policy="host_default", reasoning_effort=None)
        self.check(1)

    def test_fallback_requires_prior_primary_rejection(self):
        for index in (3, 7):
            self.change_route(index, model=PRIMARY_MODEL, fallback=FALLBACK_ROUTE)
        self.check(1)
        self.insert_rejected_spawn(4, PRIMARY_MODEL)
        self.check(0)
        receipt = json.loads(self.rows[5])
        receipt["payload"]["call_id"] = "unrelated"
        self.rows[5] = json.dumps(receipt)
        self.check(1)

    def test_primary_blocked_only_on_second_assignment(self):
        self.change_route(7, model=PRIMARY_MODEL, fallback=FALLBACK_ROUTE)
        self.insert_rejected_spawn(8, PRIMARY_MODEL)
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
