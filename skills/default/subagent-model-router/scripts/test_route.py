import json
import os
import pty
import select
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
ROUTE = SKILL / "scripts" / "route.py"


def run_cli(*arguments, input_text=None, script=ROUTE):
    return subprocess.run([sys.executable, str(script), *arguments], input=input_text,
                          text=True, capture_output=True, check=False)


def run_route(value, script=ROUTE):
    return run_cli(input_text=json.dumps(value), script=script)


def decision(value):
    result = run_route(value)
    if result.returncode:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


class RouterCliTests(unittest.TestCase):
    def test_effort_policy_is_selective_across_public_cli(self):
        cases = (
            (("--work", "coding"), "gpt-6-luna", "Standard", "host_default", None),
            (("--work", "bounded"), None, "Fast", "host_default", None),
            (("--work", "exploration"), None, "Fast", "host_default", None),
            (("--work", "standard"), None, "Standard", "host_default", None),
            (("--review", "mechanical"), None, "Fast", "host_default", None),
            (("--work", "coding", "--risk", "high_stakes"), None, "Premium", "host_default", None),
            (("--work", "planning"), "gpt-6.1-sol", "Standard", "explicit", "medium"),
            (("--work", "execplan"), "gpt-6.1-sol", "Standard", "explicit", "medium"),
            (("--review", "substantive"), "gpt-6-luna", "Standard", "explicit", "high"),
            (("--review", "security"), "gpt-6.1-terra", "Premium", "explicit", "high"),
            (("--work", "coding", "--effort", "high"), None, "Standard", "explicit", "high"),
        )
        for arguments, expected_model, expected_tier, policy, effort in cases:
            with self.subTest(arguments=arguments):
                result = run_cli(*arguments)
                self.assertEqual(result.returncode, 0, result.stderr)
                output = json.loads(result.stdout)
                if expected_model:
                    self.assertEqual(output["model"], expected_model)
                self.assertEqual(output["tier"], expected_tier)
                self.assertEqual(output["effort_policy"], policy)
                self.assertEqual(output["reasoning_effort"], effort)
                self.assertFalse(output["capability_at_host_default_verified"])
                if isinstance(output["fallback"], dict):
                    self.assertEqual(output["fallback"]["effort_policy"], policy)
                    if policy == "host_default":
                        self.assertIsNone(output["fallback"]["reasoning_effort"])
                        self.assertNotEqual(output["fallback"]["model"], output["model"])
                    else:
                        self.assertIsNotNone(output["fallback"]["reasoning_effort"])

    def test_no_match_keeps_no_recommendation_distinct_from_effort_omission(self):
        result = run_cli("--work", "coding", "--model", "no-such-model")
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertFalse(output["recommendation_available"])
        self.assertIsNone(output["model"])
        self.assertIsNone(output["reasoning_effort"])

    def test_effort_policy_json_cli_parity_and_help(self):
        request = {"task": {"work": "coding", "risks": {"unusually_difficult": True}}}
        from_json = decision(request)
        from_flags = json.loads(run_cli("--input", "-", "--work", "coding",
                                        "--risk", "unusually_difficult",
                                        input_text=json.dumps(request)).stdout)
        self.assertEqual(from_flags, from_json)
        help_text = run_cli("--help").stdout
        self.assertIn("host_default", help_text)
        self.assertIn("argument in host_default mode", help_text)

    def test_unspecified_usage_still_uses_copilot_rate_baseline(self):
        result = decision({"task": {"work": "standard", "review": "substantive",
                                    "prior_important_miss": True}})
        self.assertEqual((result["floor"], result["model"], result["reasoning_effort"]),
                         ("Premium", "gpt-6.1-terra", "high"))
        self.assertIsNone(result["estimated_cost_usd"])
        self.assertFalse(result["cost_minimum_verified"])

    def test_equal_price_prefers_newer_model_in_same_family(self):
        result = decision({"task": {"risks": {"high_stakes": True}},
                           "constraints": {"models": ["claude-opus-4.8", "claude-opus-5"]},
                           "usage": {"input_tokens": 1000, "output_tokens": 1000}})
        self.assertEqual(result["model"], "claude-opus-5")
        self.assertEqual(result["fallback"]["model"], "claude-opus-4.8")

    def test_minimal_planning_request_has_primary_and_alternative(self):
        result = decision({"task": {"work": "planning"}})
        self.assertTrue(result["recommendation_available"])
        self.assertEqual((result["floor"], result["model"], result["reasoning_effort"]),
                         ("Standard", "gpt-6.1-sol", "medium"))
        self.assertEqual(result["fallback"]["model"], "gpt-6-sol")
        self.assertFalse(result["availability_verified"])
        self.assertFalse(result["cost_minimum_verified"])
        self.assertIsNone(result["estimated_cost_usd"])

    def test_planning_catalog_lists_requested_models_in_order(self):
        data = json.loads((SKILL / "reference" / "catalog.json").read_text())
        planning = next(item for item in data["task_defaults"] if item["name"] == "Planning")
        self.assertEqual(planning["starting"], {"model": "gpt-6.1-sol", "effort": "medium"})
        self.assertEqual(planning["alternatives"], [
            {"model": "gpt-6-sol", "effort": "medium"},
            {"model": "claude-opus-5.5", "effort": "medium"},
            {"model": "claude-fable-5.1", "effort": "medium"},
            {"model": "gpt-6-astra", "effort": "medium"},
        ])

    def test_planning_respects_floor_and_explicit_constraints(self):
        premium = decision({"task": {"work": "planning", "risks": {"high_stakes": True}}})
        self.assertEqual((premium["floor"], premium["model"], premium["reasoning_effort"]),
                         ("Premium", "gpt-6.1-sol", "high"))
        alternative = decision({"task": {"work": "execplan"},
                                "constraints": {"models": ["gpt-6-sol"]}})
        self.assertEqual((alternative["model"], alternative["reasoning_effort"]),
                         ("gpt-6-sol", "medium"))
        override = decision({"task": {"work": "planning"},
                             "constraints": {"models": ["gpt-6.1-terra"]}})
        self.assertEqual(override["model"], "gpt-6.1-terra")
        blocked = decision({"task": {"work": "planning", "risks": {"high_stakes": True}},
                            "constraints": {"models": ["gpt-6-sol"], "efforts": ["medium"]}})
        self.assertFalse(blocked["recommendation_available"])

    def test_planning_model_allowlist_selects_lowest_eligible_tier(self):
        result = decision({"task": {"work": "planning"},
                           "constraints": {"models": ["gpt-6.1-terra", "gpt-6-astra"]}})
        self.assertEqual((result["floor"], result["tier"], result["model"], result["reasoning_effort"]),
                         ("Standard", "Standard", "gpt-6.1-terra", "medium"))
        effort_only = decision({"task": {"work": "planning"},
                                "constraints": {"efforts": ["medium"]}})
        self.assertEqual(effort_only["model"], "gpt-6.1-sol")

    def test_risk_review_and_escalation_floors(self):
        ordinary = decision({"task": {"review": "substantive"}})
        self.assertEqual(ordinary["floor"], "Standard")
        security = decision({"task": {"review": "security"}})
        self.assertEqual(security["floor"], "Premium")
        mechanical = decision({"task": {"review": "mechanical"}})
        self.assertEqual(mechanical["floor"], "Fast")
        previous = decision({"task": {"work": "bounded", "selected_tier": "Standard",
                                      "failure": {"reasoning_gap": True}}})
        self.assertEqual(previous["floor"], "Premium")
        context = decision({"task": {"work": "bounded", "failure": {"context_does_not_fit": True}}})
        self.assertEqual(context["floor"], "Standard")

    def test_bounded_exploration_is_fast_and_risks_raise_floor(self):
        result = decision({"task": {"work": "exploration"}})
        self.assertEqual(result["floor"], "Fast")
        risk = decision({"task": {"work": "exploration", "risks": {"high_stakes": True}}})
        self.assertEqual(risk["floor"], "Premium")
        substantive = decision({"task": {"work": "standard"}})
        self.assertEqual(substantive["floor"], "Standard")

    def test_token_estimates_and_threshold_pricing(self):
        request = {"task": {"work": "bounded"},
                   "constraints": {"models": ["claude-haiku-5.5", "gpt-5.6-luna"]},
                   "usage": {"input_tokens": 150000, "output_tokens": 2000}}
        result = decision(request)
        self.assertEqual(result["estimated_cost_usd"], 0.0324)
        request["constraints"]["models"] = ["claude-haiku-5.5"]
        self.assertEqual(decision(request)["estimated_cost_usd"], 0.08)
        self.assertEqual(result["model"], "gpt-5.6-luna")
        self.assertFalse(result["cost_minimum_verified"])
        self.assertIn("exclude retries", result["reason"])

    def test_cache_rates_and_write_threshold(self):
        request = {"task": {"work": "bounded"}, "constraints": {"models": ["claude-haiku-5.5"]},
                   "usage": {"input_tokens": 100000, "cache_write_tokens": 1, "output_tokens": 0}}
        self.assertEqual(decision(request)["estimated_cost_usd"], 0.050000625)
        request = {"constraints": {"models": ["claude-sonnet-5.5"]},
                   "usage": {"input_tokens": 0, "cached_input_tokens": 100000,
                             "output_tokens": 1000, "cache_reuse_confirmed": True}}
        self.assertEqual(decision(request)["estimated_cost_usd"], 0.02)
        request["usage"]["cache_reuse_confirmed"] = False
        self.assertEqual(decision(request)["estimated_cost_usd"], 0.21)

    def test_unknown_price_and_unprovided_estimates_do_not_imply_free(self):
        request = {"constraints": {"models": ["gpt-5.4-nano"]}, "task": {"work": "bounded"},
                   "usage": {"input_tokens": 1000, "cache_write_tokens": 1000, "output_tokens": 0}}
        result = decision(request)
        self.assertIsNone(result["estimated_cost_usd"])
        self.assertTrue(result["catalog_restrictions"])
        request["usage"] = {"input_tokens": None, "output_tokens": 0}
        self.assertIsNone(decision(request)["estimated_cost_usd"])
        request["usage"] = {"input_tokens": 1000, "cached_input_tokens": None, "output_tokens": 0}
        self.assertIsNone(decision(request)["estimated_cost_usd"])

    def test_premium_alternative_cost_ties_follow_planning_order(self):
        request = {"task": {"work": "planning", "risks": {"high_stakes": True}},
                   "constraints": {"models": ["claude-opus-5.5", "claude-fable-5.1", "gpt-6-astra"]},
                   "usage": {"input_tokens": 80000, "output_tokens": 2000}}
        result = decision(request)
        self.assertEqual(result["model"], "claude-opus-5.5")
        self.assertEqual(result["fallback"]["model"], "claude-fable-5.1")
        self.assertTrue(result["fallback_restrictions"])

    def test_promotion_expiry_boundaries(self):
        with tempfile.TemporaryDirectory() as temporary:
            skill = Path(temporary) / "skill"
            shutil.copytree(SKILL, skill)
            path = skill / "reference" / "catalog.json"
            data = json.loads(path.read_text())
            route = skill / "scripts" / "route.py"
            request = {"task": {"work": "standard"}, "constraints": {"models": ["gemini-4-argon"]},
                       "usage": {"input_tokens": 1000, "output_tokens": 1000}}
            data["rates"]["gemini-4-argon"][0]["condition"] = f"promotional before {date.today().isoformat()}"
            path.write_text(json.dumps(data))
            self.assertIsNone(json.loads(run_route(request, route).stdout)["estimated_cost_usd"])
            data["rates"]["gemini-4-argon"][0]["condition"] = f"promotional through {date.today().isoformat()}"
            path.write_text(json.dumps(data))
            self.assertIsNotNone(json.loads(run_route(request, route).stdout)["estimated_cost_usd"])

    def test_catalog_drift_and_retired_candidate_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            skill = Path(temporary) / "skill"
            shutil.copytree(SKILL, skill)
            path = skill / "reference" / "catalog.json"
            data = json.loads(path.read_text())
            data["tiers"]["Fast"][0]["model"] = "gpt-5.4"
            path.write_text(json.dumps(data))
            result = run_route({}, skill / "scripts" / "route.py")
            self.assertEqual(result.returncode, 2)
            self.assertIn("retired", result.stderr)
            data["tiers"].pop("Fast")
            path.write_text(json.dumps(data))
            result = run_route({}, skill / "scripts" / "route.py")
            self.assertEqual(result.returncode, 2)
            self.assertIn("tiers must contain", result.stderr)

    def test_invalid_task_and_usage_diagnostics(self):
        for value in ({"task": {"risks": {"security_sensitive": "true"}}},
                      {"task": {"risks": {"security_sensitiv": True}}},
                      {"task": {"selected_tier": {"tier": "Premium"}}},
                      {"usage": {"input_tokens": -1}}):
            result = run_route(value)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertNotIn("Traceback", result.stderr)
        invalid = subprocess.run([sys.executable, str(ROUTE)], input="{", text=True, capture_output=True)
        self.assertEqual(invalid.returncode, 2)
        self.assertIn("invalid JSON", invalid.stderr)

    def test_help_tty_and_copied_skill_file(self):
        help_result = subprocess.run([sys.executable, str(ROUTE), "--help"], text=True, capture_output=True)
        self.assertEqual(help_result.returncode, 0)
        self.assertIn("Examples:", help_result.stdout)
        master, slave = pty.openpty()
        try:
            process = subprocess.Popen([sys.executable, str(ROUTE)], stdin=slave,
                                       stdout=slave, stderr=slave, close_fds=True)
            os.close(slave)
            ready, _, _ = select.select([master], [], [], 2)
            self.assertTrue(ready)
            self.assertIn("use --input FILE or pipe", os.read(master, 4096).decode())
            self.assertEqual(process.wait(timeout=2), 2)
        finally:
            os.close(master)
        master, slave = pty.openpty()
        try:
            process = subprocess.Popen([sys.executable, str(ROUTE), "--input", "-", "--work", "bounded"],
                                       stdin=slave, stdout=slave, stderr=slave, close_fds=True)
            os.close(slave)
            ready, _, _ = select.select([master], [], [], 2)
            self.assertTrue(ready)
            self.assertIn("use --input FILE or pipe", os.read(master, 4096).decode())
            self.assertEqual(process.wait(timeout=2), 2)
        finally:
            os.close(master)
        with tempfile.TemporaryDirectory() as temporary:
            skill = Path(temporary) / "skill"
            shutil.copytree(SKILL, skill)
            request = {"task": {"work": "planning"}, "constraints": {}, "usage": {}}
            request_path = Path(temporary) / "request.json"
            request_path.write_text(json.dumps(request))
            result = run_cli("--input", str(request_path), script=skill / "scripts" / "route.py")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["model"], "gpt-6.1-sol")
        missing = subprocess.run([sys.executable, str(ROUTE), "--input", "/missing/route.json"],
                                 text=True, capture_output=True)
        self.assertEqual(missing.returncode, 2)
        self.assertNotIn("Traceback", missing.stderr)

    def test_flags_match_json_and_override_nested_values_including_false(self):
        request = {"task": {"work": "standard", "risks": {"high_stakes": True},
                            "failure": {"reasoning_gap": True}, "prior_important_miss": True},
                   "constraints": {"models": ["gpt-6.1-terra"], "efforts": ["high"]},
                   "usage": {"input_tokens": 100, "cached_input_tokens": 20,
                             "cache_write_tokens": 3, "output_tokens": 10,
                             "cache_reuse_confirmed": True}}
        expected_request = json.loads(json.dumps(request))
        expected_request["task"]["risks"]["high_stakes"] = False
        expected_request["task"]["failure"]["reasoning_gap"] = False
        expected_request["task"]["prior_important_miss"] = False
        expected_request["usage"]["cache_reuse_confirmed"] = False
        expected = decision(expected_request)
        result = run_cli(
            "--input", "-", "--work", "standard", "--no-risk", "high_stakes",
            "--no-failure", "reasoning_gap", "--no-prior-important-miss",
            "--model", "gpt-6.1-terra", "--effort", "high",
            "--input-tokens", "100", "--cached-input-tokens", "20",
            "--cache-write-tokens", "3", "--output-tokens", "10",
            "--no-cache-reuse-confirmed",
            input_text=json.dumps(request),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), expected)

    def test_repeated_model_and_effort_flags_replace_json_lists(self):
        request = {"constraints": {"models": ["model-not-in-catalog"], "efforts": ["invalid"]}}
        result = run_cli("--input", "-", "--model", "gpt-6.1-terra", "--model", "gpt-6-astra",
                         "--effort", "medium", input_text=json.dumps(request))
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["tier"], "Standard")
        self.assertIn(output["model"], ("gpt-6.1-terra", "gpt-6-astra"))
        self.assertEqual(output["reasoning_effort"], "medium")

    def test_flags_work_without_json_without_waiting_for_stdin(self):
        process = subprocess.Popen([sys.executable, str(ROUTE), "--work", "bounded"],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True)
        try:
            process.wait(timeout=5)
            exited_before_stdin_close = True
        except subprocess.TimeoutExpired:
            exited_before_stdin_close = False
        finally:
            if process.poll() is None:
                process.kill()
            stdout, stderr = process.communicate(timeout=5)
        self.assertTrue(exited_before_stdin_close,
                        "flags-only invocation waited for stdin while its pipe remained open")
        self.assertEqual(process.returncode, 0, stderr)
        self.assertEqual(json.loads(stdout)["floor"], "Fast")
        master, slave = pty.openpty()
        try:
            process = subprocess.run([sys.executable, str(ROUTE), "--work", "bounded"],
                                     stdin=slave, text=True, capture_output=True, timeout=5)
        finally:
            os.close(master)
            os.close(slave)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads(process.stdout)["floor"], "Fast")

    def test_input_file_and_explicit_stdin_accept_flag_overlays(self):
        request = {"task": {"work": "bounded"}}
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "request.json"
            path.write_text(json.dumps(request))
            from_file = run_cli("--input", str(path), "--work", "coding")
            from_stdin = run_cli("--input", "-", "--work", "coding", input_text=json.dumps(request))
        self.assertEqual(from_file.returncode, 0, from_file.stderr)
        self.assertEqual(from_stdin.returncode, 0, from_stdin.stderr)
        self.assertEqual(json.loads(from_file.stdout), json.loads(from_stdin.stdout))

    def test_invalid_cli_values_and_invalid_json_base_fail_cleanly(self):
        for arguments in (("--work", "made-up"), ("--risk", "unknown"),
                          ("--model", ""), ("--input-tokens", "-1"),
                          ("--no-review",), ("--wor", "bounded")):
            result = run_cli(*arguments)
            self.assertEqual(result.returncode, 2, arguments)
            self.assertEqual(result.stdout, "", arguments)
            self.assertNotIn("Traceback", result.stderr, arguments)
        for base in ("{", json.dumps({"task": "bad"}),
                     json.dumps({"task": {"risks": {"high_stakes": "bad"}}})):
            result = run_cli("--input", "-", "--work", "bounded", input_text=base)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertNotIn("Traceback", result.stderr)

    def test_last_risk_or_failure_flag_occurrence_wins(self):
        risk_false = run_cli("--work", "bounded", "--risk", "high_stakes",
                             "--no-risk", "high_stakes")
        risk_true = run_cli("--work", "bounded", "--no-risk", "high_stakes",
                            "--risk", "high_stakes")
        self.assertEqual(json.loads(risk_false.stdout)["floor"], "Fast")
        self.assertEqual(json.loads(risk_true.stdout)["floor"], "Premium")
        failure_false = run_cli("--work", "bounded", "--failure", "reasoning_gap",
                                "--no-failure", "reasoning_gap")
        failure_true = run_cli("--work", "bounded", "--no-failure", "reasoning_gap",
                               "--failure", "reasoning_gap")
        self.assertEqual(json.loads(failure_false.stdout)["floor"], "Fast")
        self.assertEqual(json.loads(failure_true.stdout)["floor"], "Standard")

    def test_help_is_complete_and_does_not_require_catalog(self):
        with tempfile.TemporaryDirectory() as temporary:
            script = Path(temporary) / "route.py"
            shutil.copy2(ROUTE, script)
            result = run_cli("--help", script=script)
        self.assertEqual(result.returncode, 0, result.stderr)
        for text in ("--work", "--review", "--selected-tier", "--risk", "--no-risk",
                     "--failure", "--no-failure", "--prior-important-miss",
                     "--model", "--effort", "--input-tokens", "--cached-input-tokens",
                     "--cache-write-tokens", "--output-tokens", "--cache-reuse-confirmed",
                     "JSON request", "override", "availability", "Copilot",
                     "security_sensitive (security)", "important_review_miss", "context_does_not_fit",
                     "low, medium, high, xhigh, max, ultra", "rate threshold uses their sum",
                     "Planning uses its catalog pool"):
            self.assertIn(text, result.stdout)


if __name__ == "__main__":
    unittest.main()
