from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import run_actors
import extract_tool_order
import grade_events
import case_records
import host_config


HERE = Path(__file__).resolve().parent
OUTCOMES = HERE / "fixtures" / "host-outcomes.json"


class W1BoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.rendered = self.root / "rendered"
        subprocess.run([sys.executable, str(HERE / "render_variants.py"), str(self.rendered)], check=True)
        self.project = self.root / "project"
        run_actors.prepare("short", "delegate-to-subagents", self.project, self.rendered)
        self.env = {
            **os.environ,
            "W1_PROJECT": str(self.project),
            "W1_OUTCOMES": str(OUTCOMES),
            "PATH": f"{self.project / 'bin'}:{os.environ.get('PATH', '')}",
        }

    def tearDown(self) -> None:
        self.temp.cleanup()

    def command(self, name: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([str(self.project / "bin" / name), *args], env=self.env,
                              text=True, capture_output=True, check=True)

    def events(self) -> list[dict]:
        path = self.project / ".w1" / "events.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()]

    def test_actor_visible_inputs_hide_simulator_outcomes(self) -> None:
        cases = json.loads(self.command("case38", "list").stdout)
        self.assertNotIn("simulator", json.dumps(cases))
        self.assertNotIn("gpt-5.6-luna", json.dumps(cases))
        controls = json.loads(self.command("host38", "case03").stdout)
        self.assertNotIn("dispatch_outcomes", controls)
        self.assertNotIn("allowed_models", controls)
        self.assertEqual(controls["availability"], "unknown")

    def test_router_and_host_trace_records_unknown_rejection_then_floor_fallback_success(self) -> None:
        routed = json.loads(self.command("route38", "case03").stdout)
        self.command("host38", "case03")
        rejected_model = routed["model"]
        fallback_model = routed["fallback"]["model"]
        primary = json.loads(self.command("dispatch38", "case03", "--model", rejected_model).stdout)
        fallback = json.loads(self.command("dispatch38", "case03", "--model", fallback_model).stdout)
        self.assertEqual(primary["result"], "model_wide_rejection")
        self.assertEqual(fallback["result"], "worker_completed")
        self.assertEqual(fallback["effort"], None)
        self.assertGreaterEqual(
            {"Fast": 0, "Standard": 1, "Premium": 2}[fallback["fallback_tier"]],
            {"Fast": 0, "Standard": 1, "Premium": 2}[fallback["route"]["floor"]],
        )
        entries = [row for row in self.events() if row["kind"] == "dispatch"]
        self.assertEqual([row["model"] for row in entries], [rejected_model, fallback_model])
        assignment = case_records.build_records(self.project / ".w1" / "events.jsonl")[2]
        self.assertEqual(assignment["before"]["router_output_unchanged"], routed)
        self.assertEqual([row["result"] for row in assignment["after"]["actual_dispatch_or_reuse_events"]],
                         ["model_wide_rejection", "worker_completed"])

    def test_route_unavailable_exact_user_override_can_dispatch(self) -> None:
        routed = json.loads(self.command("route38", "case07").stdout)
        self.command("host38", "case07")
        self.assertFalse(routed["route_available"])
        event = json.loads(self.command("dispatch38", "case07", "--model", "gpt-9-user-requested").stdout)
        self.assertEqual(event["result"], "worker_completed")

    def test_exact_user_model_does_not_override_enforced_host_restriction(self) -> None:
        self.command("route38", "case08")
        self.command("host38", "case08")
        event = json.loads(self.command("dispatch38", "case08", "--model", "gpt-9-user-requested").stdout)
        self.assertEqual(event["result"], "host_restriction")

    def test_reuse_tool_is_an_observable_unconditional_host_action(self) -> None:
        self.command("route38", "case12")
        self.command("host38", "case12")
        event = json.loads(self.command("reuse38", "case12", "--worker", "worker-old-x").stdout)
        self.assertEqual(event["result"], "worker_reused")
        self.assertFalse(event["host_enforces_reuse_eligibility"])

    def test_tool_order_extractor_preserves_cli_event_order(self) -> None:
        trace = self.root / "trace.jsonl"
        trace.write_text("\n".join([
            json.dumps({"type": "item.started", "item": {"id": "a", "type": "command_execution", "command": "route38 case01"}}),
            json.dumps({"type": "item.completed", "item": {"id": "a", "type": "command_execution", "command": "route38 case01", "exit_code": 0}}),
        ]) + "\n")
        rows = extract_tool_order.extract(trace)
        self.assertEqual([row["phase"] for row in rows], ["item.started", "item.completed"])
        self.assertEqual([row["event_index"] for row in rows], [0, 1])

    def test_grader_returns_failure_for_missing_or_arbitrary_cases(self) -> None:
        empty = self.root / "empty.jsonl"
        empty.write_text("")
        result = grade_events.grade(empty)
        self.assertEqual(result["verdict"], "fail")
        self.assertEqual(result["passed"], 0)

        arbitrary = self.root / "arbitrary.jsonl"
        arbitrary.write_text(json.dumps({"kind": "route", "case_id": "invented"}) + "\n")
        result = grade_events.grade(arbitrary)
        self.assertEqual(result["verdict"], "fail")
        self.assertEqual(result["checks"][0]["check"], "expected unique router and host input IDs")

    def test_host_config_capture_excludes_unrelated_config_values(self) -> None:
        config = self.root / "config.toml"
        config.write_text('model = "gpt-test"\nmodel_reasoning_effort = "high"\napi_key = "do-not-copy"\n')
        command = self.root / "command.json"
        command.write_text(json.dumps({"argv": ["codex", "exec"]}))
        captured = host_config.capture(config, command)
        self.assertEqual(captured["configured_default_model"], "gpt-test")
        self.assertFalse(captured["model_flag_in_actor_command"])
        self.assertNotIn("api_key", json.dumps(captured))
        self.assertNotIn("do-not-copy", json.dumps(captured))

    def test_nonbaseline_router_retains_cli_result_contract_outside_gate_count(self) -> None:
        candidate = (self.rendered / "short" / "delegate-to-subagents" / "router-SKILL.md").read_text()
        baseline = (self.rendered / "baseline" / "delegate-to-subagents" / "router-SKILL.md").read_text()
        sentence = "Return the CLI's JSON result unchanged."
        self.assertEqual(candidate.count(sentence), 1)
        self.assertEqual(baseline.count(sentence), 1)
        self.assertLess(candidate.index(sentence), candidate.index("## Dispatch controls"))
        counts = json.loads((self.rendered / "counts.json").read_text())
        self.assertTrue(all(row["retained_standalone_words_excluded_from_gate_count"] == 6 for row in counts))


if __name__ == "__main__":
    unittest.main()
