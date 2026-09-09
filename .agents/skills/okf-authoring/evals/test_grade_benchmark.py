import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


GRADER = Path(__file__).with_name("grade_benchmark.py")
BENCHMARK_SYNC = Path(__file__).with_name("sync_benchmark.py")
HARNESS_EVIDENCE = "harness/lint-evidence.json"

EVAL_PATHS = {
    0: [
        (".agents/memory/telemetry.md", "Agent Memory", "# Telemetry\n\nRecord durable telemetry guidance.\n"),
        (".agents/memory/INDEX.md", "Knowledge Index", "# Index\n\nRoute canonical knowledge.\n"),
        (".agents/memory/LOG.md", "Source Ingestion Log", "# Log\n\nRecord source ingestion.\n"),
        (".agents/memory/adrs/retention.md", "Architecture Decision", "# Retention\n\nKeep stable paths.\n"),
    ],
    1: [(".agents/instructions/hooks.md", "Agent Instruction", "# Hook Guidance\n\nRetain this sentence exactly.\n")],
    2: [(".agents/memory/sources/pending-md.summary.md", "Source Summary", "# Pending example summary\n\nThis source summary is intentionally unresolved but structurally conforming.\n")],
    3: [(".agents/memory/sources/example-md.summary.md", "Source Summary", "# Example source summary\n\nThe source demonstrates a completed manifest-backed summary.\n")],
    4: [(".agents/memory/testing/skills.md", "Testing Guidance", "# Skills Testing\n\nRun targeted skill validation.\n")],
    5: [(".agents/memory/KNOWN_ISSUES.md", "Known Issue", "")],
    6: [("docs/outside.md", "out_of_scope", "")],
    7: [(".agents/memory/ARCHITECTURE.md", "Agent Memory", "# Architecture\n\nPreserve this canonical body.\n")],
}


def document(eval_id: int, type_name: str, body: str) -> str:
    metadata = f"type: {type_name}\ndescription: Synthetic routing description\n"
    if eval_id in {2, 3}:
        raw_name = "pending" if eval_id == 2 else "example"
        metadata += f"sources:\n  - resource: ../../sources/{raw_name}.md\n"
        if eval_id == 2:
            metadata += "status: draft\n"
    return f"---\n{metadata}---\n{body}"


class BenchmarkContractTests(unittest.TestCase):
    def run_grader(self, iteration: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(GRADER), str(iteration)], check=False, capture_output=True, text=True)

    def make_eval_dirs(self, iteration: Path, ids=range(8)) -> None:
        for eval_id in ids:
            eval_dir = iteration / f"eval-{eval_id}"
            eval_dir.mkdir()
            (eval_dir / "eval_metadata.json").write_text(json.dumps({"eval_id": eval_id}) + "\n", encoding="utf-8")

    def make_complete_layout(self, iteration: Path) -> None:
        self.make_eval_dirs(iteration)
        for eval_id in range(8):
            for config in ("with_skill", "without_skill"):
                run_dir = iteration / f"eval-{eval_id}" / config / "run-1"
                repo = run_dir / "outputs" / "repo"
                repo.mkdir(parents=True)
                (run_dir / "response.md").write_text("Result recorded.\n", encoding="utf-8")
                (run_dir / "transcript.md").write_text("Synthetic transcript.\n", encoding="utf-8")
                (run_dir / "timing.json").write_text('{"total_tokens": 1, "duration_ms": 1}\n', encoding="utf-8")
                targets = EVAL_PATHS[eval_id]
                changed = sorted(path for path, _, _ in targets) if eval_id in {0, 1, 2, 3, 4, 7} else []
                outcome = {
                    "mode": "out_of_scope" if eval_id == 6 else "review" if eval_id == 5 else "change",
                    "completion": {5: "incomplete", 6: "not_applicable", 7: "unverified"}.get(eval_id, "complete"),
                    "affected": [{"path": path, "type": type_name} for path, type_name, _ in targets],
                    "references_loaded": [] if eval_id == 6 else ["profile", "source-summaries"] if eval_id in {2, 3} else ["profile"],
                    "lint": None if eval_id == 6 else {"command": "./scripts/lint-okf.py", "exit_code": None if eval_id == 7 else 1 if eval_id == 5 else 0, "outcome": "unavailable" if eval_id == 7 else "nonconforming" if eval_id == 5 else "clean"},
                    "scoped_diff": {"outcome": "clean" if changed else "no_changes", "paths": changed},
                }
                if eval_id == 4:
                    outcome["orchestration"] = {"semantic_owner": "update-agent-docs", "representation_owner": "okf-authoring", "reverse_invocation": False}
                (run_dir / "outputs" / "outcome.json").write_text(json.dumps(outcome) + "\n", encoding="utf-8")
                for path, type_name, body in targets:
                    if eval_id in {5, 6}:
                        continue
                    target = repo / path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(document(eval_id, type_name, body), encoding="utf-8")

    def grading(self, run_dir: Path) -> dict:
        return json.loads((run_dir / "grading.json").read_text(encoding="utf-8"))

    def test_empty_iteration_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_grader(Path(temp_dir))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing eval ids", result.stdout)

    def test_every_eval_id_and_metadata_are_required(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            self.make_eval_dirs(iteration, range(7))
            result = self.run_grader(iteration)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing eval ids [7]", result.stdout)

    def test_every_eval_requires_both_comparison_configurations(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            self.make_eval_dirs(iteration)
            for eval_dir in iteration.glob("eval-*"):
                (eval_dir / "with_skill" / "run-1").mkdir(parents=True)
            result = self.run_grader(iteration)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("without_skill", result.stdout)

    def test_every_run_requires_saved_artifacts_and_expected_outputs(self):
        for missing in ("response.md", "transcript.md", "timing.json", "outputs/outcome.json", "outputs/repo/.agents/memory/telemetry.md"):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as temp_dir:
                iteration = Path(temp_dir)
                self.make_complete_layout(iteration)
                (iteration / "eval-0" / "with_skill" / "run-1" / missing).unlink()
                result = self.run_grader(iteration)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(missing, result.stdout)

    def test_complete_benchmark_runs_actual_linter_in_seeded_fixture(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            self.make_complete_layout(iteration)
            result = self.run_grader(iteration)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for run_dir in iteration.glob("eval-*/*/run-*"):
                grading = self.grading(run_dir)
                self.assertEqual(grading["summary"]["failed"], 0, str(run_dir))
                evidence = json.loads((run_dir / HARNESS_EVIDENCE).read_text(encoding="utf-8"))
                self.assertEqual(evidence["owner"], "grade_benchmark.py")
                self.assertTrue(evidence["sandbox_cwd"].endswith("validation-sandbox"))
                expected = sorted(path for path, _, _ in EVAL_PATHS[evidence["eval_id"]]) if evidence["eval_id"] in {0, 1, 2, 3, 4, 7} else []
                self.assertEqual(evidence["changed_paths"], expected)

    def test_grading_output_is_deterministic_across_hash_seeds(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            self.make_complete_layout(iteration)
            grading_path = iteration / "eval-0" / "with_skill" / "run-1" / "grading.json"
            outputs = []
            for hash_seed in ("1", "2"):
                env = os.environ.copy()
                env["PYTHONHASHSEED"] = hash_seed
                result = subprocess.run(
                    [sys.executable, str(GRADER), str(iteration)],
                    check=False,
                    capture_output=True,
                    text=True,
                    env=env,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                outputs.append(grading_path.read_bytes())
        self.assertEqual(outputs[0], outputs[1])

    def test_benchmark_sync_refreshes_expectations_and_rejects_score_changes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            self.make_complete_layout(iteration)
            grader_result = self.run_grader(iteration)
            self.assertEqual(grader_result.returncode, 0, grader_result.stdout + grader_result.stderr)
            run_dir = iteration / "eval-0" / "with_skill" / "run-1"
            grading_path = run_dir / "grading.json"
            grading = json.loads(grading_path.read_text(encoding="utf-8"))
            benchmark_path = iteration / "benchmark.json"
            benchmark = {
                "runs": [{
                    "eval_id": 0,
                    "configuration": "with_skill",
                    "run_number": 1,
                    "result": {**grading["summary"], "tool_calls": 0, "errors": 0},
                    "expectations": [],
                }],
            }
            benchmark_path.write_text(json.dumps(benchmark) + "\n", encoding="utf-8")

            sync_result = subprocess.run(
                [sys.executable, str(BENCHMARK_SYNC), str(iteration)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(sync_result.returncode, 0, sync_result.stdout + sync_result.stderr)
            synchronized = json.loads(benchmark_path.read_text(encoding="utf-8"))
            self.assertEqual(synchronized["runs"][0]["expectations"], grading["expectations"])

            synchronized["runs"][0]["result"]["passed"] -= 1
            benchmark_path.write_text(json.dumps(synchronized) + "\n", encoding="utf-8")
            mismatch_result = subprocess.run(
                [sys.executable, str(BENCHMARK_SYNC), str(iteration)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(mismatch_result.returncode, 0)
        self.assertIn("score changed", mismatch_result.stderr)

    def test_claimed_clean_outcome_with_actual_lint_failure_is_graded_failing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            self.make_complete_layout(iteration)
            run_dir = iteration / "eval-0" / "with_skill" / "run-1"
            (run_dir / "outputs" / "repo" / ".agents/memory/telemetry.md").write_text("# Not OKF\n", encoding="utf-8")
            result = self.run_grader(iteration)
            grading = self.grading(run_dir)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        actual_lint = next(item for item in grading["expectations"] if item["text"] == "Actual linter result matches this scenario.")
        self.assertFalse(actual_lint["passed"])

    def test_missing_reported_reference_or_scoped_diff_is_graded_failing(self):
        for missing in ("references_loaded", "scoped_diff"):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as temp_dir:
                iteration = Path(temp_dir)
                self.make_complete_layout(iteration)
                run_dir = iteration / "eval-0" / "with_skill" / "run-1"
                outcome_path = run_dir / "outputs/outcome.json"
                outcome = json.loads(outcome_path.read_text(encoding="utf-8"))
                del outcome[missing]
                outcome_path.write_text(json.dumps(outcome) + "\n", encoding="utf-8")
                self.run_grader(iteration)
                grading = self.grading(run_dir)
            expectation = next(item for item in grading["expectations"] if missing.replace("_", " ") in item["text"].lower())
            self.assertFalse(expectation["passed"])

    def test_scoped_diff_path_order_does_not_change_meaning(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            self.make_complete_layout(iteration)
            run_dir = iteration / "eval-0" / "with_skill" / "run-1"
            outcome_path = run_dir / "outputs/outcome.json"
            outcome = json.loads(outcome_path.read_text(encoding="utf-8"))
            outcome["scoped_diff"]["paths"].reverse()
            outcome_path.write_text(json.dumps(outcome) + "\n", encoding="utf-8")
            result = self.run_grader(iteration)
            grading = self.grading(run_dir)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        check = next(item for item in grading["expectations"] if item["text"] == "Reports the expected scoped diff.")
        self.assertTrue(check["passed"])

    def test_outside_root_accepts_explicit_not_run_lint_envelope(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            self.make_complete_layout(iteration)
            run_dir = iteration / "eval-6" / "with_skill" / "run-1"
            outcome_path = run_dir / "outputs/outcome.json"
            outcome = json.loads(outcome_path.read_text(encoding="utf-8"))
            outcome["lint"] = {"command": None, "exit_code": None, "outcome": "not_run"}
            outcome_path.write_text(json.dumps(outcome) + "\n", encoding="utf-8")
            result = self.run_grader(iteration)
            grading = self.grading(run_dir)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        check = next(item for item in grading["expectations"] if item["text"] == "Reports the expected outside-root outcome.")
        self.assertTrue(check["passed"])

    def test_missing_or_forged_harness_evidence_cannot_pass(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            self.make_complete_layout(iteration)
            run_dir = iteration / "eval-0" / "with_skill" / "run-1"
            (run_dir / "outputs" / "repo" / ".agents/memory/telemetry.md").write_text("# Not OKF\n", encoding="utf-8")
            forged = run_dir / HARNESS_EVIDENCE
            forged.parent.mkdir()
            forged.write_text('{"owner":"grade_benchmark.py","exit_code":0,"changed_paths":[]}\n', encoding="utf-8")
            self.run_grader(iteration)
            forged_result = self.grading(run_dir)
            (run_dir / HARNESS_EVIDENCE).unlink()
            self.run_grader(iteration)
            missing_result = self.grading(run_dir)
        for result in (forged_result, missing_result):
            actual_lint = next(item for item in result["expectations"] if item["text"] == "Actual linter result matches this scenario.")
            self.assertFalse(actual_lint["passed"])

    def test_review_and_outside_root_have_no_actual_diff_and_only_review_runs_lint(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            self.make_complete_layout(iteration)
            result = self.run_grader(iteration)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            review = json.loads((iteration / "eval-5" / "with_skill" / "run-1" / HARNESS_EVIDENCE).read_text(encoding="utf-8"))
            outside = json.loads((iteration / "eval-6" / "with_skill" / "run-1" / HARNESS_EVIDENCE).read_text(encoding="utf-8"))
        self.assertEqual(review["exit_code"], 1)
        self.assertEqual(review["changed_paths"], [])
        self.assertFalse(outside["attempted"])
        self.assertEqual(outside["changed_paths"], [])

    def test_unverified_response_cannot_claim_success(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            self.make_complete_layout(iteration)
            run_dir = iteration / "eval-7" / "with_skill" / "run-1"
            (run_dir / "response.md").write_text("The work completed successfully.\n", encoding="utf-8")
            self.run_grader(iteration)
            grading = self.grading(run_dir)
        expectation = next(item for item in grading["expectations"] if "success claim" in item["text"].lower())
        self.assertFalse(expectation["passed"])

    def test_unavailable_linter_records_real_file_not_found_evidence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            self.make_complete_layout(iteration)
            result = self.run_grader(iteration)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            evidence = json.loads((iteration / "eval-7" / "with_skill" / "run-1" / HARNESS_EVIDENCE).read_text(encoding="utf-8"))
        self.assertTrue(evidence["attempted"])
        self.assertIsNone(evidence["exit_code"])
        self.assertIn("FileNotFoundError", evidence["execution_error"])

    def test_timing_artifact_requires_a_compatible_schema(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            iteration = Path(temp_dir)
            self.make_complete_layout(iteration)
            timing = iteration / "eval-0" / "with_skill" / "run-1" / "timing.json"
            timing.write_text("{}\n", encoding="utf-8")
            result = self.run_grader(iteration)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid timing.json", result.stdout)

    def test_timing_accepts_runner_duration_variants(self):
        for timing in ({"total_tokens": None, "duration_ms": 1}, {"duration_seconds": 0.1}, {"total_duration_seconds": None}):
            with self.subTest(timing=timing), tempfile.TemporaryDirectory() as temp_dir:
                iteration = Path(temp_dir)
                self.make_complete_layout(iteration)
                target = iteration / "eval-0" / "with_skill" / "run-1" / "timing.json"
                target.write_text(json.dumps(timing) + "\n", encoding="utf-8")
                result = self.run_grader(iteration)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
