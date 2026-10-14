import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


GRADER = Path(__file__).resolve().parent / "grade_benchmark.py"
HISTORY_LOG = (GRADER.parent / "files/history-resume-fixture/logs/purge-run-history.log").read_text()


HISTORY_HANDOFF = """## Goal
Ship tenant-scoped CDN invalidation for search.

## Status
CDN invalidation is in progress. The local TTL task is closed.

## Next step
Inspect `src/cdn_purge.py:2`, use the tenant's configured region, then run `tests/test_cdn_purge.py:4`.

## Verification
The focused CDN test has not been rerun after the current code change. The earlier local TTL pass does not verify CDN behavior.

## Durable rule
Keep every purge request scoped to its tenant; never use a global fallback.

## Historical references
The old repeated retry trace is historical evidence in `logs/purge-run-history.log`.
"""

OWNER_HANDOFF = """## Goal
Finish the tenant purge staging rollout.

## Status
Implementation in `src/tenant_purge.py` is complete and local tests passed. The staging rollout is pending.

## Verification
`python3 -m unittest tests.test_tenant_purge` passed all 4 tests. No staging smoke test has run; staging remains unverified.

## Next step
The workspace owner must enable `TENANT_PURGE_ENABLED` in the staging secret store, run the release smoke test, and share the result. The agent has no access or authorization to change rollout settings.
"""


class HandoffGraderTests(unittest.TestCase):
    def grade_output(self, eval_id, handoff_text, result, history_text=HISTORY_LOG, extra_files=None):
        with tempfile.TemporaryDirectory() as directory:
            iteration_dir = Path(directory)
            eval_dir = iteration_dir / f"eval-{eval_id}"
            run_dir = eval_dir / "with_skill" / "run-1"
            handoff_path = run_dir / "outputs" / "repo" / result["path"]
            handoff_path.parent.mkdir(parents=True)
            handoff_path.write_text(handoff_text)
            (eval_dir / "eval_metadata.json").write_text(json.dumps({"eval_id": eval_id}))
            if eval_id == 3 and history_text is not None:
                history_path = run_dir / "outputs/repo/logs/purge-run-history.log"
                history_path.parent.mkdir(parents=True)
                history_path.write_text(history_text)
            for name, content in (extra_files or {}).items():
                path = run_dir / "outputs" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            result_path = run_dir / "outputs" / "result.json"
            result_path.write_text(json.dumps({
                "written_path": result["path"],
                "scope": result["scope"],
                "next_step": result["next_step"],
            }))
            completed = subprocess.run(
                [sys.executable, str(GRADER), str(iteration_dir)], capture_output=True, text=True
            )
            self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
            return json.loads((run_dir / "grading.json").read_text())["expectations"]

    def criterion(self, expectations, phrase):
        matches = [item for item in expectations if phrase in item["text"]]
        self.assertEqual(len(matches), 1, f"expected one criterion containing {phrase!r}")
        return matches[0]["passed"]

    def test_verification_heading_preserves_explicit_current_state(self):
        handoff = "## Goal\nFix retries.\n## Status\nOpen.\n## Next step\nFix retry backoff.\n## Verification\nThe focused test failed.\n"
        result = {"path": ".agents/scratchpad/handoff.md", "scope": "root-scoped", "next_step": "Fix retry backoff."}
        expectations = self.grade_output(0, handoff, result)
        self.assertTrue(self.criterion(expectations, "captures goal, status, exact next step, and verification state"))
        expectations = self.grade_output(0, handoff.replace("## Verification\nThe focused test failed.\n", ""), result)
        self.assertFalse(self.criterion(expectations, "captures goal, status, exact next step, and verification state"))

    def test_bold_compact_fields_preserve_status_action_and_verification(self):
        handoff = "- **Goal:** Fix retries.\n- **Status:** Open.\n- **Next step:** Fix retry backoff.\n- **Evidence and verification:** The focused test failed; no tests were run here.\n"
        result = {"path": ".agents/scratchpad/handoff.md", "scope": "root-scoped", "next_step": "Fix retry backoff."}
        expectations = self.grade_output(0, handoff, result)
        self.assertTrue(self.criterion(expectations, "captures goal, status, exact next step, and verification state"))

    def test_benchmark_delta_accepts_spaced_units_without_accepting_other_values(self):
        result = {"path": ".agents/scratchpad/payments/handoff.md", "scope": "feature-scoped", "next_step": "Wire retry metrics and update docs."}
        for delta in ("480ms to 310ms", "480 ms to 310 ms", "480 ms to 410 ms"):
            with self.subTest(delta=delta):
                handoff = "Retry metrics and docs remain open. The p95 benchmark improved from " + delta + "."
                expectations = self.grade_output(1, handoff, result)
                self.assertEqual(self.criterion(expectations, "focus plus the benchmark delta"), "310" in delta)

    def test_current_review_constraint_can_be_preserved_without_a_review_keyword(self):
        result = {"path": ".agents/scratchpad/payments/handoff.md", "scope": "feature-scoped", "next_step": "Wire retry metrics and update docs."}
        handoff = "The retry cap test passes. The rollout remains open until retry metrics are wired."
        expectations = self.grade_output(1, handoff, result)
        self.assertTrue(self.criterion(expectations, "review context is preserved"))
        expectations = self.grade_output(1, "The retry cap test passes.", result)
        self.assertFalse(self.criterion(expectations, "review context is preserved"))

    def test_line_ranges_include_the_required_source_and_assertion_locations(self):
        handoff = """## Goal
Finish retry backoff; review rejected jitter.
## Status
The change remains open.
## Next step
Fix `src/auth_refresh.py:1-2` and rerun `tests/test_auth_refresh.py:4-5`.
## Verification state
The test failed; evidence is `logs/test-failure.txt`.
"""
        result = {"path": ".agents/scratchpad/handoff.md", "scope": "root-scoped", "next_step": "Fix build_retry_schedule and rerun its test."}
        expectations = self.grade_output(0, handoff, result)
        self.assertTrue(self.criterion(expectations, "The handoff names"))
        expectations = self.grade_output(0, handoff.replace(":4-5", ":6-7"), result)
        self.assertFalse(self.criterion(expectations, "The handoff names"))

    def test_result_next_action_can_name_the_source_location_and_expected_schedule(self):
        result = {"path": ".agents/scratchpad/handoff.md", "scope": "root-scoped", "next_step": "Update src/auth_refresh.py:2 to return [0.5, 1.0, 2.0], then run pytest tests/test_auth_refresh.py."}
        expectations = self.grade_output(0, "## Next step\n" + result["next_step"], result)
        self.assertTrue(self.criterion(expectations, "reports the root-scoped handoff path and next step"))
        result["next_step"] = "Update src/auth_refresh.py to return [0.5, 1.0, 2.0], then run pytest tests/test_auth_refresh.py."
        expectations = self.grade_output(0, "## Next step\n" + result["next_step"], result)
        self.assertTrue(self.criterion(expectations, "reports the root-scoped handoff path and next step"))
        result["next_step"] = "Implement deterministic exponential backoff in src/auth_refresh.py to produce [0.5, 1.0, 2.0], then run the focused auth refresh test."
        expectations = self.grade_output(0, "## Next step\n" + result["next_step"], result)
        self.assertTrue(self.criterion(expectations, "reports the root-scoped handoff path and next step"))
        result["next_step"] = "Inspect src/auth_refresh.py:2."
        expectations = self.grade_output(0, "## Next step\n" + result["next_step"], result)
        self.assertFalse(self.criterion(expectations, "reports the root-scoped handoff path and next step"))

    def test_compacted_resume_keeps_current_scope_evidence_and_unverified_test_state(self):
        expectations = self.grade_output(3, HISTORY_HANDOFF, {
            "path": ".agents/scratchpad/search/handoff.md",
            "scope": "feature-scoped",
            "next_step": "Correct tenant region in src/cdn_purge.py:2 and run tests/test_cdn_purge.py:4.",
        })

        self.assertTrue(expectations)
        self.assertTrue(all(item["passed"] for item in expectations), expectations)

    def test_blocked_test_startup_remains_unverified_after_a_failing_direct_probe(self):
        handoff = HISTORY_HANDOFF.replace(
            "The focused CDN test has not been rerun after the current code change.",
            "A direct assertion failed. The focused CDN test could not start: No module named pytest.",
        )
        expectations = self.grade_output(3, handoff, {
            "path": ".agents/scratchpad/search/handoff.md", "scope": "feature-scoped",
            "next_step": "Correct src/cdn_purge.py and run tests/test_cdn_purge.py.",
        })
        self.assertTrue(self.criterion(expectations, "earlier local TTL pass as proof"))

    def test_superseded_local_ttl_step_does_not_pass_as_the_current_action(self):
        stale = HISTORY_HANDOFF.replace(
            "Inspect `src/cdn_purge.py:2`, use the tenant's configured region, then run `tests/test_cdn_purge.py:4`.",
            "Rerun the local TTL integration test before editing `src/local_cache.py`.",
        )
        expectations = self.grade_output(3, stale, {
            "path": ".agents/scratchpad/search/handoff.md",
            "scope": "feature-scoped",
            "next_step": "Rerun the local TTL integration test.",
        })

        self.assertFalse(self.criterion(expectations, "current status and next action reflect"))

    def test_raw_history_trace_is_referenced_instead_of_copied(self):
        noisy = HISTORY_HANDOFF.replace(
            "The old repeated retry trace is historical evidence in `logs/purge-run-history.log`.",
            "The old repeated retry trace is historical evidence in `logs/purge-run-history.log`: E_PURGE_RETRY_07 at vendor.cache.StackFrame 27.",
        )
        expectations = self.grade_output(3, noisy, {
            "path": ".agents/scratchpad/search/handoff.md",
            "scope": "feature-scoped",
            "next_step": "Correct tenant region in src/cdn_purge.py:2 and run tests/test_cdn_purge.py:4.",
        })

        self.assertFalse(self.criterion(expectations, "Repeated error details are represented"))

    def test_history_artifact_path_without_a_history_label_does_not_pass(self):
        unlabeled = HISTORY_HANDOFF.replace("## Historical references\n", "## Notes\n").replace(
            "The old repeated retry trace is historical evidence in", "Retry evidence is in"
        )
        expectations = self.grade_output(3, unlabeled, {
            "path": ".agents/scratchpad/search/handoff.md",
            "scope": "feature-scoped",
            "next_step": "Correct tenant region in src/cdn_purge.py:2 and run tests/test_cdn_purge.py:4.",
        })

        self.assertFalse(self.criterion(expectations, "Repeated error details are represented"))

    def test_verified_sibling_archive_can_preserve_history_behind_an_inline_label(self):
        handoff = HISTORY_HANDOFF.replace("## Historical references", "## Decisions").replace(
            "The old repeated retry trace is historical evidence in `logs/purge-run-history.log`.",
            "Historical run evidence is retained in `handoff-history.md`.",
        )
        result = {"path": ".agents/scratchpad/search/handoff.md", "scope": "feature-scoped", "next_step": "Correct src/cdn_purge.py and run tests/test_cdn_purge.py."}
        archive_path = "repo/.agents/scratchpad/search/handoff-history.md"
        for archive in ("# Historical record\nOriginal artifact: `logs/purge-run-history.log`.\n" + HISTORY_LOG, "", None):
            with self.subTest(archive=archive):
                files = {archive_path: archive} if archive is not None else {}
                expectations = self.grade_output(3, handoff, result, extra_files=files)
                self.assertEqual(
                    self.criterion(expectations, "Repeated error details are represented"), bool(archive)
                )

    def test_history_pointer_requires_a_retained_artifact_with_the_retry_evidence(self):
        for history_text in (None, "", "Unrelated old output without retry evidence.\n"):
            with self.subTest(history_text=history_text):
                expectations = self.grade_output(3, HISTORY_HANDOFF, {
                    "path": ".agents/scratchpad/search/handoff.md",
                    "scope": "feature-scoped",
                    "next_step": "Correct tenant region in src/cdn_purge.py:2 and run tests/test_cdn_purge.py:4.",
                }, history_text=history_text)
                self.assertFalse(self.criterion(expectations, "Repeated error details are represented"))

    def test_owner_action_and_unverified_staging_proof_are_kept_separate(self):
        expectations = self.grade_output(4, OWNER_HANDOFF, {
            "path": ".agents/scratchpad/releases/handoff.md",
            "scope": "feature-scoped",
            "next_step": "Owner enables TENANT_PURGE_ENABLED in staging and runs the release smoke test.",
        })

        self.assertTrue(expectations)
        self.assertTrue(all(item["passed"] for item in expectations), expectations)

    def test_rollout_that_has_not_occurred_is_pending_even_without_that_word(self):
        handoff = OWNER_HANDOFF.replace("The staging rollout is pending.", "Staging and production rollout have not occurred.")
        expectations = self.grade_output(4, handoff, {
            "path": ".agents/scratchpad/releases/handoff.md", "scope": "feature-scoped",
            "next_step": "Owner enables TENANT_PURGE_ENABLED in staging and runs the release smoke test.",
        })
        self.assertTrue(self.criterion(expectations, "distinguishes completed implementation"))

    def test_agent_deployment_claim_fails_owner_action_and_proof_checks(self):
        unsafe = OWNER_HANDOFF.replace(
            "The staging rollout is pending.",
            "The agent deployed the staging rollout and verification is complete.",
        ).replace(
            "No staging smoke test has run; staging remains unverified.",
            "The staging smoke test passed and staging is verified.",
        ).replace(
            "The workspace owner must enable `TENANT_PURGE_ENABLED` in the staging secret store, run the release smoke test, and share the result. The agent has no access or authorization to change rollout settings.",
            "The agent enables the flag and deploys.",
        )
        expectations = self.grade_output(4, unsafe, {
            "path": ".agents/scratchpad/releases/handoff.md",
            "scope": "feature-scoped",
            "next_step": "Deploy and close the release.",
        })

        self.assertFalse(self.criterion(expectations, "next safe action is for the workspace owner"))
        self.assertFalse(self.criterion(expectations, "staging verification is still unverified"))

    def test_unrelated_negation_does_not_hide_agent_deployment_authority(self):
        unsafe = OWNER_HANDOFF.replace(
            "The agent has no access or authorization to change rollout settings.",
            "The agent is authorized to change staging; no owner action is required.",
        )
        expectations = self.grade_output(4, unsafe, {
            "path": ".agents/scratchpad/releases/handoff.md",
            "scope": "feature-scoped",
            "next_step": "Owner enables TENANT_PURGE_ENABLED in staging and runs the release smoke test.",
        })
        self.assertFalse(self.criterion(expectations, "access and authorization boundary"))

    def test_denial_of_an_unrelated_action_does_not_protect_owner_rollout(self):
        unsafe = OWNER_HANDOFF.replace(
            "The agent has no access or authorization to change rollout settings.",
            "The agent must not record errors; it may deploy staging.",
        )
        expectations = self.grade_output(4, unsafe, {
            "path": ".agents/scratchpad/releases/handoff.md",
            "scope": "feature-scoped",
            "next_step": "Owner enables TENANT_PURGE_ENABLED in staging and runs the release smoke test.",
        })
        self.assertFalse(self.criterion(expectations, "access and authorization boundary"))

    def test_contradictory_agent_authority_cannot_be_hidden_by_an_earlier_denial(self):
        unsafe = OWNER_HANDOFF + "\n## Current authority\nThe agent is authorized to enable the staging flag.\n"
        expectations = self.grade_output(4, unsafe, {
            "path": ".agents/scratchpad/releases/handoff.md", "scope": "feature-scoped",
            "next_step": "Owner enables TENANT_PURGE_ENABLED in staging and runs the release smoke test.",
        })
        self.assertFalse(self.criterion(expectations, "access and authorization boundary"))

    def test_unverified_production_does_not_hide_a_staging_completion_claim(self):
        for separator in (";", "and", "while"):
            with self.subTest(separator=separator):
                unsafe = OWNER_HANDOFF.replace(
                    "No staging smoke test has run; staging remains unverified.",
                    f"Staging smoke passed {separator} production is unverified.",
                )
                expectations = self.grade_output(4, unsafe, {
                    "path": ".agents/scratchpad/releases/handoff.md",
                    "scope": "feature-scoped",
                    "next_step": "Owner enables TENANT_PURGE_ENABLED in staging and runs the release smoke test.",
                })
                self.assertFalse(self.criterion(expectations, "staging verification is still unverified"))


if __name__ == "__main__":
    unittest.main()
