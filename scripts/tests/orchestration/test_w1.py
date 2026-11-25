from __future__ import annotations

import errno
import json
import os
import subprocess
import sys
import tempfile
import time
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
        fallback = next(model for model, outcome in json.loads(OUTCOMES.read_text())["case03"].items()
                        if outcome == "worker_completed")
        self.assertNotIn(fallback, json.dumps(cases))
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

    def test_case03_requires_rejection_before_fallback_begins(self) -> None:
        routes = {}
        for number in range(1, 17):
            case = f"case{number:02d}"
            routes[case] = json.loads(self.command("route38", case).stdout)
            if case != "case04":
                self.command("host38", case)
        self.command("dispatch38", "case02", "--model", routes["case02"]["model"])
        self.command("dispatch38", "case03", "--model", routes["case03"]["model"])
        self.command("host38", "case04")  # Global sequence gap within case03.
        self.command("dispatch38", "case03", "--model", routes["case03"]["fallback"]["model"])
        for case in ("case05", "case12", "case14", "case16"):
            self.command("dispatch38", case, "--model", routes[case]["model"])
        self.command("dispatch38", "case04", "--model", routes["case04"]["model"], "--effort", "high")
        self.command("dispatch38", "case07", "--model", "gpt-9-user-requested")
        self.command("dispatch38", "case11", "--model", routes["case11"]["fallback"]["model"])
        self.command("reuse38", "case13", "--worker", "worker-old-same")
        self.command("reuse38", "case15", "--worker", "worker-old-explicit")
        original = self.events()
        trace = self.root / "replay.jsonl"

        def replay(rows, expected, reason=None):
            trace.write_text("".join(json.dumps(row) + "\n" for row in rows))
            result = subprocess.check_output([sys.executable, str(HERE / "grade_events.py"), str(trace)])
            verdict = json.loads(result)
            self.assertEqual(verdict["verdict"], "pass" if expected else "fail",
                             [item for item in verdict["checks"] if not item["pass"]])
            checks = {item["case_id"]: item for item in verdict["checks"]}
            self.assertTrue(checks["case02"]["pass"])
            self.assertEqual(checks["case03"]["pass"], expected, checks["case03"])
            if reason:
                self.assertIn(reason, checks["case03"]["evidence"]["reason"])
            report = self.root / "report.jsonl"
            subprocess.run([sys.executable, str(HERE / "case_records.py"), str(trace), str(report)],
                           check=True, capture_output=True)
            record = json.loads(report.read_text().splitlines()[2])
            attempts = record["after"]["actual_dispatch_or_reuse_events"]
            self.assertEqual(attempts, [row for row in rows if row["case_id"] == "case03"
                                        and row["kind"] in ("dispatch", "reuse")])
            if reason == "insufficient ordering evidence":
                self.assertTrue(record["ordering_issues"])

        # Old-format receipts in even the expected order cannot establish when fallback began.
        legacy = [{key: value for key, value in row.items() if key != "sequence"}
                  for row in original if row["kind"] != "dispatch_start"]
        replay(legacy, False, "insufficient ordering evidence")
        replay(original, True)

        primary, fallback = [row for row in original if row["case_id"] == "case03" and row["kind"] == "dispatch"]
        start = next(row for row in original if row["sequence"] == fallback["start_sequence"])
        # A delayed start record can appear after the primary even though the
        # fallback command entered before the primary started.
        early_start = dict(start, entered_ns=0)
        replay([early_start if row is start else row for row in original], False, "overlap")
        overlap = original.copy()
        overlap.remove(start)
        overlap.insert(overlap.index(primary), start)
        # Renumber the observed trace, retaining each receipt's link to its start.
        sequence = {row["sequence"]: i for i, row in enumerate(overlap)}
        overlap = [dict(row) for row in overlap]
        for index, row in enumerate(overlap):
            row["sequence"] = index
            for ref in ("start_sequence", "receipt_sequence"):
                if ref in row:
                    row[ref] = sequence[row[ref]]
        replay(overlap, False, "overlap")
        reversed_receipts = original.copy()
        left, right = original.index(primary), original.index(fallback)
        reversed_receipts[left], reversed_receipts[right] = fallback, primary
        replay(reversed_receipts, False, "reversed")
        replay([dict(row, sequence=primary["sequence"]) if row is fallback else row for row in original],
               False, "insufficient ordering evidence")
        replay([*original, dict(fallback, kind="reuse", sequence=len(original))], False, "exactly")
        replay([*original, dict(start, sequence=len(original))], False, "extra")

    def test_concurrent_fallback_cannot_pass_by_recording_its_receipt_late(self):
        for number in range(1, 17):
            case = f"case{number:02d}"
            route = json.loads(self.command("route38", case).stdout)
            self.command("host38", case)
            if case == "case03":
                primary, fallback = route["model"], route["fallback"]["model"]

        # Hold the fallback inside the running host command while the primary finishes.
        cases = self.project / ".w1" / "cases.json"
        saved = cases.read_bytes()
        cases.unlink()
        os.mkfifo(cases)
        with subprocess.Popen([str(self.project / "bin/dispatch38"), "case03", "--model", fallback],
                              env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as pending:
            try:
                deadline = time.monotonic() + 5
                while True:
                    try:
                        writer = os.open(cases, os.O_WRONLY | os.O_NONBLOCK)
                        break
                    except OSError as error:
                        if error.errno != errno.ENXIO or time.monotonic() >= deadline:
                            raise
                        time.sleep(.01)
                with os.fdopen(writer, "wb") as gate:
                    cases.unlink()
                    cases.write_bytes(saved)
                    self.command("dispatch38", "case03", "--model", primary)
                    os.set_blocking(gate.fileno(), True)
                    gate.write(saved)
                _, stderr = pending.communicate(timeout=5)
                self.assertEqual(pending.returncode, 0, stderr)
            finally:
                if pending.poll() is None:
                    pending.kill()

        result = grade_events.grade(self.project / ".w1/events.jsonl")
        check = next(row for row in result["checks"] if row["case_id"] == "case03")
        self.assertFalse(check["pass"], check)
        self.assertIn("overlap", check["evidence"]["reason"])

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

    def test_p2_arms_render_exact_candidate_bytes_and_keep_p1_arms(self) -> None:
        counts = json.loads((self.rendered / "counts.json").read_text())
        rows = {(row["arm"], row["caller"]): row for row in counts}
        expected = {
            ("p2-screen", "delegate-to-subagents"): (59, 102, 161, "10c5f6019d240e883e0badaffcd9cb187e0e6e4e80f21cf43e13002bcc1670f0", "6d5eb3bcc89f1416e8046b390a5ad1f466ac7459a0b432c32843d6124ae6abc3"),
            ("p2-screen", "execplan-implement"): (102, 102, 204, "9afcb7baafd835267a392a4a75a9d4819031b0fefed8481a16052ccb4662d984", "6d5eb3bcc89f1416e8046b390a5ad1f466ac7459a0b432c32843d6124ae6abc3"),
            ("p2-deletion", "delegate-to-subagents"): (59, 100, 159, "10c5f6019d240e883e0badaffcd9cb187e0e6e4e80f21cf43e13002bcc1670f0", "6beae12c1e9d36f46c417971ee004656cc419d5a7dacaf1a4f433628cc68a8f5"),
            ("p2-deletion", "execplan-implement"): (102, 100, 202, "9afcb7baafd835267a392a4a75a9d4819031b0fefed8481a16052ccb4662d984", "6beae12c1e9d36f46c417971ee004656cc419d5a7dacaf1a4f433628cc68a8f5"),
            ("p2-final", "delegate-to-subagents"): (59, 98, 157, "10c5f6019d240e883e0badaffcd9cb187e0e6e4e80f21cf43e13002bcc1670f0", "656c361a8326899e8f6e166cf538d2cef9fed617e6d26df10d4a119d1bfe5e34"),
            ("p2-final", "execplan-implement"): (102, 98, 200, "9afcb7baafd835267a392a4a75a9d4819031b0fefed8481a16052ccb4662d984", "656c361a8326899e8f6e166cf538d2cef9fed617e6d26df10d4a119d1bfe5e34"),
        }
        for (arm, caller), (caller_words, router_words, total_words, caller_hash, router_hash) in expected.items():
            with self.subTest(arm=arm, caller=caller):
                row = rows[(arm, caller)]
                self.assertEqual(row["caller_gate_words"], caller_words)
                self.assertEqual(row["shared_router_words"], router_words)
                self.assertEqual(row["selected_total"], total_words)
                self.assertEqual(row["caller_sha256"], caller_hash)
                self.assertEqual(row["router_sha256"], router_hash)
                self.assertGreater(row["selected_total"], 0)
        self.assertTrue({"baseline", "short", "challenger", "challenger2"}.issubset(
            {arm for arm, _ in rows}
        ))


if __name__ == "__main__":
    unittest.main()
