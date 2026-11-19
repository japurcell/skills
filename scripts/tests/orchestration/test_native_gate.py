"""Adversarial checks for native Copilot gate evidence grading."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from grade_native_gate import grade_native_gate, main as grade_native_main, summarize_native_events
from run_native_gate import load_actor_records
from route_capture import main as capture_route


class ProviderLaunchTests(unittest.TestCase):
    def test_runner_defaults_prepare_without_invoking_either_provider_cli(self):
        here = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".codex").mkdir()
            (root / ".codex/config.toml").write_text('model = "test-model"\n')
            bin_dir = root / "bin"
            bin_dir.mkdir()
            (bin_dir / "python3").symlink_to(sys.executable)
            (bin_dir / "git").symlink_to(shutil.which("git"))
            for name in ("rtk", "codex", "copilot"):
                stub = bin_dir / name
                stub.write_text('#!/bin/sh\nprintf "%s %s %s\\n" "$1" "$2" "$3" >> "$CALL_LOG"\n')
                stub.chmod(0o755)
            runners = [
                ("run_actors.py", ["--caller", "delegate-to-subagents", "--arm", "short",
                                   "--scratch-root", str(root / "actors")],
                 root / "actors/projects/short-delegate-to-subagents/.w1/cases.json"),
                ("run_native_gate.py", ["--caller", "execplan", "--run-dir", str(root / "gate")],
                 root / "gate/private/manifest.json"),
            ]
            for script, args, fixture in runners:
                with self.subTest(script=script):
                    calls = root / (script + ".calls")
                    env = {"PATH": str(bin_dir), "HOME": temp, "CALL_LOG": str(calls)}
                    result = subprocess.run([sys.executable, str(here / script), *args], env=env,
                                            text=True, capture_output=True, timeout=30)
                    self.assertEqual(calls.read_text() if calls.exists() else "", "")
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertTrue(fixture.is_file())

    def test_live_permission_requires_the_full_option_name(self):
        here = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as temp:
            # An empty PATH makes even a parser regression safe to exercise.
            for runner, args in [
                ("run_actors.py", ["--arm", "short", "--caller", "execplan-implement",
                                   "--scratch-root", temp]),
                ("run_native_gate.py", ["--caller", "execplan", "--run-dir", temp]),
            ]:
                with self.subTest(runner=runner):
                    command = [sys.executable, str(here / runner), *args]
                    env = {"PATH": temp, "HOME": temp}
                    help_text = subprocess.check_output([*command, "--help"], env=env, text=True)
                    self.assertIn("--allow-model-calls", help_text)
                    refused = subprocess.run([*command, "--allow-model"], env=env,
                                             capture_output=True, text=True)
                    self.assertEqual(refused.returncode, 2)
                    self.assertIn("unrecognized arguments: --allow-model", refused.stderr)


ALLOWED = {"check-total": ["claude-haiku-5.5"]}
ROUTE_OUTPUT = {
    "route_available": True,
    "model": "gpt-6-luna",
    "reasoning_effort": None,
    "effort_policy": "host_default",
    "fallback": {"model": "claude-haiku-5.5", "reasoning_effort": None, "effort_policy": "host_default"},
}


def native_events(model="claude-haiku-5.5", success=True):
    events = [
        {"type": "tool.execution_start", "timestamp": "2026-11-19T03:00:00Z", "data": {
            "toolName": "shell", "toolCallId": "policy", "arguments": {"command": "policy38"}}},
        {"type": "tool.execution_complete", "timestamp": "2026-11-19T03:00:01Z", "data": {
            "toolCallId": "policy", "success": True}},
        {"type": "tool.execution_start", "timestamp": "2026-11-19T03:00:02Z", "data": {
            "toolName": "shell", "toolCallId": "route", "arguments": {"command": "route38 --input route-request.json"}}},
        {"type": "tool.execution_complete", "timestamp": "2026-11-19T03:00:03Z", "data": {
            "toolCallId": "route", "success": True}},
        {"type": "tool.execution_start", "timestamp": "2026-11-19T03:00:03.500Z", "data": {
            "toolName": "apply_patch", "toolCallId": "write-before",
            "arguments": "*** Begin Patch\n*** Update File: /private/tmp/run/project/coordination.json\n*** End Patch"}},
        {"type": "tool.execution_complete", "timestamp": "2026-11-19T03:00:03.600Z", "data": {
            "toolCallId": "write-before", "success": True}},
        {"type": "tool.execution_start", "timestamp": "2026-11-19T03:00:04Z", "data": {
            "toolName": "task", "toolCallId": "task-1", "model": "gpt-6-luna",
            "arguments": {"agent_type": "check-total", "model": model, "prompt": "private prompt must not be retained"}}},
    ]
    if model == "claude-haiku-5.5" and success:
        events.extend([
            {"type": "subagent.started", "timestamp": "2026-11-19T03:00:05Z", "agentId": "child-1", "data": {
                "toolCallId": "task-1", "agentName": "check-total", "agentType": "custom", "model": model}},
            {"type": "subagent.configured", "timestamp": "2026-11-19T03:00:06Z", "agentId": "child-1", "data": {
                "model": model, "reasoningEffort": "medium"}},
            {"type": "subagent.completed", "timestamp": "2026-11-19T03:00:07Z", "agentId": "child-1", "data": {
                "toolCallId": "task-1", "agentName": "check-total", "model": model, "firstDispatchedModel": model}},
        ])
    events.extend([
        {"type": "tool.execution_complete", "timestamp": "2026-11-19T03:00:08Z", "data": {
            "toolCallId": "task-1", "success": success,
            "result": {"content": "73" if success else None, "detailedContent": "private worker details"}}},
        {"type": "tool.execution_start", "timestamp": "2026-11-19T03:00:08.500Z", "data": {
            "toolName": "apply_patch", "toolCallId": "write-after",
            "arguments": "*** Begin Patch\n*** Update File: /private/tmp/run/project/coordination.json\n*** End Patch"}},
        {"type": "tool.execution_complete", "timestamp": "2026-11-19T03:00:08.600Z", "data": {
            "toolCallId": "write-after", "success": True}},
        {"type": "result", "timestamp": "2026-11-19T03:00:09Z", "exitCode": 0},
    ])
    return events


def run_records():
    request = {"task": {"work": "bounded"}}
    argv = ["route38", "--input", "route-request.json"]
    intended = {"agent_type": "check-total", "model": "claude-haiku-5.5"}
    before = {"recorded_at": "2026-11-19T03:00:03.750Z", "assignment_id": "smoke-1", "router_argv": argv, "router_request": request,
              "router_output": ROUTE_OUTPUT, "intended_child_controls": intended,
              "parent_controls": {"model": "gpt-6-luna", "effort": None}}
    after = dict(before, actual_args={"agent_type": "check-total", "model": "claude-haiku-5.5",
                                      "parent_model": "gpt-6-luna", "requested_effort": None},
                 worker_id="child-1", observed_worker_model="claude-haiku-5.5",
                 blocker=None, override_fallback="claude-haiku-5.5")
    manifest = {"caller": "delegate", "source_hashes": {key: "a" * 64 for key in (
        "caller", "router_skill", "router_script", "router_catalog", "route_executable", "gate", "hook", "worker_policy", "worker_agent", "scheduler")},
        "worker_policy": ALLOWED, "parent_model": "gpt-6-luna", "parent_effort": None,
        "assignment_id": "smoke-1"}
    router = [{"timestamp": "2026-11-19T03:00:03.500Z", "exit_code": 0, "argv": ["--input", "route-request.json"],
               "request": request, "output": ROUTE_OUTPUT}]
    policy_reads = [{"timestamp": "2026-11-19T03:00:00.500Z", "sha256": "a" * 64}]
    return manifest, router, before, after, policy_reads


class NativeGateGraderTests(unittest.TestCase):
    def test_runner_loads_actor_records_without_reconstructing_them(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            before = {"actor": "before"}
            after = {"actor": "after"}
            (project / "coordination.json").write_text(json.dumps({"before": before, "after": after}), encoding="utf-8")

            self.assertEqual(load_actor_records(project), (before, after))

    def test_runner_preserves_missing_actor_after_record_as_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)

            self.assertEqual(load_actor_records(project), (None, None))

    def test_accepts_zero_primary_attempts_and_one_real_routed_fallback(self):
        manifest, router, before, after, policy_reads = run_records()
        verdict = grade_native_gate(native_events(), manifest, router, before, after, policy_reads)
        self.assertEqual(verdict["status"], "pass")
        self.assertEqual(verdict["observed"]["worker_model"], "claude-haiku-5.5")
        self.assertEqual(verdict["observed"]["worker_effort"], "medium")
        self.assertEqual(verdict["observed"]["primary_attempts"], 0)
        self.assertEqual(verdict["observed"]["fallback_attempts"], 1)

    def test_exact_router_shell_string_matches_the_captured_argv(self):
        manifest, router, before, after, policy_reads = run_records()
        before["router_argv"] = "route38 --input route-request.json"
        after["router_argv"] = before["router_argv"]
        verdict = grade_native_gate(native_events(), manifest, router, before, after, policy_reads)
        self.assertFalse(any("router argv" in item or "actual router invocation" in item
                             for item in verdict["record_failures"]))

    def test_synchronous_task_unknown_identity_text_is_not_a_worker_id_or_blocker(self):
        manifest, router, before, after, policy_reads = run_records()
        events = native_events()
        events = [event for event in events if event.get("type") not in ("subagent.started", "subagent.configured", "subagent.completed")]
        after["worker_id"] = "not exposed by task tool"
        after["observed_worker_model"] = "claude-haiku-5.5 (requested; runtime model not separately reported)"
        after["blocker"] = "Task tool exposed no worker ID; result completed successfully."
        after["actual_args"].update(description="Compute arithmetic assignment",
                                     prompt="Return only the integer result.", worker_output="73")
        verdict = grade_native_gate(events, manifest, router, before, after, policy_reads)
        self.assertEqual(verdict["observed"]["answer"], 73)
        self.assertIsNone(verdict["observed"]["worker_id"])
        self.assertFalse(verdict["behavior_failures"])
        self.assertFalse(verdict["record_failures"])
        self.assertEqual(verdict["status"], "unavailable")

    def test_matching_child_assistant_message_proves_output_after_dispatch_receipt(self):
        manifest, router, before, after, policy_reads = run_records()
        events = native_events()
        events = [event for event in events if event.get("type") not in ("subagent.started", "subagent.configured", "subagent.completed")]
        task_result = next(event for event in events if event.get("type") == "tool.execution_complete"
                           and event.get("data", {}).get("toolCallId") == "task-1")
        worker_id = "1995fa43-34c1-41e8-86d9-96bc063fa0ba"
        task_result["data"]["result"] = {"content": f"Agent started in background with agent_id: {worker_id}"}
        after["worker_id"] = worker_id
        events.extend([
            {"type": "tool.execution_start", "timestamp": "2026-11-19T03:00:08.500Z", "data": {
                "toolName": "apply_patch", "toolCallId": "write-after-receipt",
                "arguments": "*** Begin Patch\n*** Update File: /private/tmp/run/project/coordination.json\n*** End Patch"}},
            {"type": "tool.execution_complete", "timestamp": "2026-11-19T03:00:08.600Z", "data": {
                "toolCallId": "write-after-receipt", "success": True}},
            {"type": "assistant.message", "timestamp": "2026-11-19T03:00:09Z", "agentId": worker_id,
             "data": {"content": "73"}},
        ])
        verdict = grade_native_gate(events, manifest, router, before, after, policy_reads)
        self.assertEqual(verdict["observed"]["answer"], 73)
        self.assertEqual(verdict["observed"]["worker_id"], worker_id)
        self.assertFalse(any("after worker completion" in item for item in verdict["record_failures"]))
        self.assertFalse(verdict["behavior_failures"])

    def test_child_assistant_output_counts_only_for_matching_child_id(self):
        manifest, router, before, after, policy_reads = run_records()
        events = native_events()
        events = [event for event in events if event.get("type") not in ("subagent.started", "subagent.configured", "subagent.completed")]
        task_result = next(event for event in events if event.get("type") == "tool.execution_complete"
                           and event.get("data", {}).get("toolCallId") == "task-1")
        worker_id = "1995fa43-34c1-41e8-86d9-96bc063fa0ba"
        task_result["data"]["result"] = {"content": f"Agent started in background with agent_id: {worker_id}"}
        after["worker_id"] = worker_id
        events.append({"type": "assistant.message", "timestamp": "2026-11-19T03:00:10Z",
                       "agentId": "another-worker", "data": {"content": "73"}})
        verdict = grade_native_gate(events, manifest, router, before, after, policy_reads)
        self.assertIsNone(verdict["observed"]["answer"])
        summary = summarize_native_events(events)
        self.assertNotIn({"type": "assistant.message", "worker_id": "another-worker", "answer": 73}, summary)

    def test_rejected_primary_attempt_fails_even_when_the_hook_denies_it(self):
        manifest, router, before, after, policy_reads = run_records()
        events = native_events("gpt-6-luna", success=False)
        verdict = grade_native_gate(events, manifest, router, before, after, policy_reads)
        self.assertEqual(verdict["status"], "fail")
        self.assertTrue(any("excluded primary" in item for item in verdict["behavior_failures"]))

    def test_missing_native_model_is_unavailable_not_a_pass(self):
        manifest, router, before, after, policy_reads = run_records()
        events = native_events()
        del events[6]["data"]["arguments"]["model"]
        verdict = grade_native_gate(events, manifest, router, before, after, policy_reads)
        self.assertEqual(verdict["status"], "unavailable")
        self.assertTrue(verdict["unavailable"])

    def test_gate_record_mismatch_is_separate_from_native_behavior(self):
        manifest, router, before, after, policy_reads = run_records()
        after["assignment_id"] = "tampered"
        verdict = grade_native_gate(native_events(), manifest, router, before, after, policy_reads)
        self.assertEqual(verdict["status"], "fail")
        self.assertFalse(verdict["behavior_failures"])
        self.assertTrue(verdict["record_failures"])

    def test_sanitizer_discards_prompt_and_unrelated_result_text(self):
        summary = summarize_native_events(native_events())
        serialized = json.dumps(summary)
        self.assertNotIn("private prompt", serialized)
        self.assertNotIn("private worker details", serialized)
        self.assertIn('"answer": 73', serialized)

    def test_missing_policy_read_and_attempted_wrong_fallback_are_failures(self):
        manifest, router, before, after, policy_reads = run_records()
        events = [event for event in native_events() if event.get("data", {}).get("toolCallId") != "policy"]
        verdict = grade_native_gate(events, manifest, router, before, after, policy_reads)
        self.assertIn(verdict["status"], {"unavailable", "fail"})
        self.assertTrue(verdict["unavailable"])
        events = native_events()
        events[6]["data"]["arguments"]["model"] = "gpt-6-luna"
        verdict = grade_native_gate(events, manifest, router, before, after, policy_reads)
        self.assertTrue(any("excluded primary" in item for item in verdict["behavior_failures"]))

    def test_native_policy_file_view_is_a_policy_read(self):
        events = [
            {"type": "tool.execution_start", "timestamp": "2026-11-19T03:00:00Z", "data": {
                "toolName": "view", "toolCallId": "view-1", "arguments": {"path": ".github/hooks/worker-models.json"}}},
            {"type": "tool.execution_complete", "timestamp": "2026-11-19T03:00:01Z", "data": {"toolCallId": "view-1"}},
        ]
        reads = [row for row in summarize_native_events(events) if row.get("policy_read")]
        self.assertEqual(len(reads), 1)

    def test_shell_string_and_argv_list_preserve_the_same_invocation(self):
        string_event = {"type": "tool.execution_start", "data": {
            "toolName": "shell", "toolCallId": "string", "arguments": "route38 --input route-request.json"}}
        argv_event = {"type": "tool.execution_start", "data": {
            "toolName": "shell", "toolCallId": "argv", "arguments": ["route38", "--input", "route-request.json"]}}
        string_row = summarize_native_events([string_event])[0]
        argv_row = summarize_native_events([argv_event])[0]
        self.assertEqual((string_row["router_call"], string_row["policy_read"]), (True, False))
        self.assertEqual((argv_row["router_call"], argv_row["policy_read"]), (True, False))

    def test_native_coordination_write_after_task_is_not_a_before_write(self):
        manifest, router, before, after, policy_reads = run_records()
        events = native_events()
        events[4]["timestamp"] = "2026-11-19T03:00:05Z"
        events[5]["timestamp"] = "2026-11-19T03:00:05.100Z"
        verdict = grade_native_gate(events, manifest, router, before, after, policy_reads)
        self.assertTrue(any("before dispatch" in item for item in verdict["record_failures"]))

    def test_route_wrapper_executes_non_executable_frozen_router_and_logs_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "route-request.json").write_text('{"task":{"work":"bounded"}}\n', encoding="utf-8")
            router = root / "route.py"
            router.write_text('import json\nprint(json.dumps({"route_available": True}))\n', encoding="utf-8")
            router.chmod(0o600)
            log = root / "router.jsonl"
            with patch.dict(os.environ, {"P0_REAL_ROUTER_SCRIPT": str(router), "P0_ROUTER_LOG": str(log)}):
                old_cwd = Path.cwd()
                try:
                    os.chdir(root)
                    output = StringIO()
                    with redirect_stdout(output):
                        self.assertEqual(capture_route(["--input", "route-request.json"]), 0)
                finally:
                    os.chdir(old_cwd)
            self.assertEqual(json.loads(output.getvalue()), {"route_available": True})
            self.assertEqual(json.loads(log.read_text(encoding="utf-8"))["exit_code"], 0)

    def test_background_worker_result_is_matched_by_agent_id(self):
        manifest, router, before, after, policy_reads = run_records()
        events = native_events()
        events = [event for event in events if event.get("type") not in ("subagent.started", "subagent.configured", "subagent.completed")]
        completion = next(event for event in events if event.get("type") == "tool.execution_complete" and event.get("data", {}).get("toolCallId") == "task-1")
        completion["data"]["result"] = {"content": "Agent started in background with agent_id: 1995fa43-34c1-41e8-86d9-96bc063fa0ba"}
        events.extend([
            {"type": "tool.execution_start", "timestamp": "2026-11-19T03:00:08Z", "data": {
                "toolName": "read_agent", "toolCallId": "read-1", "arguments": {
                    "agent_id": "1995fa43-34c1-41e8-86d9-96bc063fa0ba", "since_turn": 0}}},
            {"type": "tool.execution_complete", "timestamp": "2026-11-19T03:00:09Z", "data": {
                "toolCallId": "read-1", "success": True,
                "result": {"content": "[Turn 0]\n73"}}},
            {"type": "tool.execution_start", "timestamp": "2026-11-19T03:00:10Z", "data": {
                "toolName": "apply_patch", "toolCallId": "write-after-read",
                "arguments": "*** Begin Patch\n*** Update File: /private/tmp/run/project/coordination.json\n*** End Patch"}},
            {"type": "tool.execution_complete", "timestamp": "2026-11-19T03:00:10.100Z", "data": {
                "toolCallId": "write-after-read", "success": True}},
        ])
        after["worker_id"] = "1995fa43-34c1-41e8-86d9-96bc063fa0ba"
        verdict = grade_native_gate(events, manifest, router, before, after, policy_reads)
        self.assertEqual(verdict["observed"]["answer"], 73)
        self.assertEqual(verdict["observed"]["worker_id"], after["worker_id"])

    def test_wrong_profile_is_a_real_behavior_failure(self):
        manifest, router, before, after, policy_reads = run_records()
        events = native_events()
        events[6]["data"]["arguments"]["agent_type"] = "general-purpose"
        after["actual_args"]["agent_type"] = "general-purpose"
        verdict = grade_native_gate(events, manifest, router, before, after, policy_reads)
        self.assertTrue(any("wrong required project worker" in item for item in verdict["behavior_failures"]))

    def test_malformed_coordination_does_not_hide_wrong_native_type_even_with_matching_name(self):
        manifest, router, before, after, _ = run_records()
        events = native_events()
        events[6]["data"]["arguments"].update(agent_type="task", name="check-total")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            event_file = root / "events.jsonl"
            event_file.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")
            manifest_file = root / "manifest.json"
            manifest_file.write_text(json.dumps(manifest), encoding="utf-8")
            router_file = root / "router.jsonl"
            router_file.write_text("".join(json.dumps(event) + "\n" for event in router), encoding="utf-8")
            coordination = root / "coordination.json"
            for malformed in ('{"before":{}}\n{"after":{}}', '{"before":{}}\n}\n'):
                coordination.write_text(malformed, encoding="utf-8")
                output = StringIO()
                with redirect_stdout(output):
                    code = grade_native_main(["--events", str(event_file), "--manifest", str(manifest_file),
                                              "--router-log", str(router_file), "--coordination", str(coordination)])
                verdict = json.loads(output.getvalue())
                self.assertEqual(code, 1)
                self.assertTrue(any("wrong required project worker" in item for item in verdict["behavior_failures"]))
                self.assertTrue(any("invalid JSON" in item for item in verdict["record_failures"]))

    def test_synchronous_result_without_public_worker_identity_is_unavailable_not_failure(self):
        manifest, router, before, after, policy_reads = run_records()
        events = native_events()
        events = [event for event in events if event.get("type") not in ("subagent.started", "subagent.configured", "subagent.completed")]
        del events[6]["data"]["arguments"]["model"]
        after["worker_id"] = None
        after["observed_worker_model"] = None
        verdict = grade_native_gate(events, manifest, router, before, after, policy_reads)
        self.assertEqual(verdict["observed"]["answer"], 73)
        self.assertEqual(verdict["observed"]["worker_id"], None)
        self.assertFalse(verdict["behavior_failures"])
        self.assertFalse(verdict["record_failures"])
        self.assertEqual(verdict["status"], "unavailable")
        self.assertTrue(any("worker ID" in item for item in verdict["unavailable"]))

    def test_constrained_english_fallback_record_is_reported_without_claiming_native_exposure(self):
        manifest, router, before, after, policy_reads = run_records()
        events = native_events()
        events = [event for event in events if event.get("type") not in ("subagent.started", "subagent.configured", "subagent.completed")]
        del events[6]["data"]["arguments"]["model"]
        after["worker_id"] = None
        after["observed_worker_model"] = None
        after["override_fallback"] = (
            "Policy restriction required claude-haiku-5.5 instead of routed gpt-6-luna; "
            "effort omitted as host-default."
        )
        verdict = grade_native_gate(events, manifest, router, before, after, policy_reads)
        self.assertEqual(verdict["observed"]["actor_reported_fallback_model"], "claude-haiku-5.5")
        self.assertFalse(verdict["behavior_failures"])
        self.assertFalse(verdict["record_failures"])
        self.assertTrue(any("native task model" in item for item in verdict["unavailable"]))

    def test_unverifiable_fallback_prose_is_reported_for_manual_review(self):
        manifest, router, before, after, policy_reads = run_records()
        after["override_fallback"] = "I did not use the routed fallback model claude-haiku-5.5."
        verdict = grade_native_gate(native_events(), manifest, router, before, after, policy_reads)
        self.assertTrue(verdict["manual_review"])
        self.assertIsNone(verdict["observed"]["actor_reported_fallback_model"])
        self.assertFalse(verdict["behavior_failures"])


if __name__ == "__main__":
    unittest.main()
