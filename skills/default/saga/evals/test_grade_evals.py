import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


GRADER = Path(__file__).resolve().parent / "grade_evals.py"


class SagaEvalGraderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.fixture = self.root / "fixture"
        self.source.mkdir()
        (self.source / "README.md").write_text("Disposable feature fixture.\n")
        (self.source / "AGENTS.md").write_text("Fixture boundary.\n")
        (self.source / "brain/index.md").parent.mkdir(parents=True)
        (self.source / "brain/index.md").write_text("# Brain\n")
        shutil.copytree(self.source, self.fixture)
        self.response = self.root / "response.md"
        self.response.write_text("Saga created at brain/sagas/cache-refresh-20261105.\n")
        self.transcript = self.root / "transcript.md"
        self.transcript.write_text("Created only planning documents.\n")
        self.output = self.root / "grading.json"

    def tearDown(self):
        self.temp.cleanup()

    def run_grader(self, eval_id="0", **overrides):
        values = {
            "--eval-id": eval_id,
            "--fixture-root": str(self.fixture),
            "--source-fixture": str(self.source),
            "--response": str(self.response),
            "--transcript": str(self.transcript),
            "--output": str(self.output),
        }
        values.update(overrides)
        args = [sys.executable, str(GRADER)]
        for name, value in values.items():
            args.extend([name, value])
        return subprocess.run(args, text=True, capture_output=True)

    def create_saga(self, relative="brain/sagas/cache-refresh-20261105", path_record=None):
        saga = self.fixture / relative
        saga.mkdir(parents=True)
        recorded = path_record or relative
        (saga / "SAGA.md").write_text(
            f"# Saga: cache refresh\n- Saga directory: {recorded}\n\n"
            "## Saga exit criteria\n1. Existing clients retain synchronous refresh.\n"
        )
        (saga / "PROGRESS.md").write_text(
            f"# Saga progress: cache refresh\n- Saga directory: {recorded}\n"
        )
        return saga

    def seed_existing_saga(self, relative):
        saga = self.source / relative
        saga.mkdir(parents=True)
        (saga / "SAGA.md").write_text(f"# Saga\n- Saga directory: {relative}\n")
        (saga / "PROGRESS.md").write_text(f"# Progress\n- Saga directory: {relative}\n")
        shutil.rmtree(self.fixture)
        shutil.copytree(self.source, self.fixture)

    def test_creation_passes_only_at_brain_sagas_with_consistent_paths(self):
        self.create_saga()
        result = self.run_grader()
        self.assertEqual(result.returncode, 0, result.stderr)
        grade = json.loads(self.output.read_text())
        self.assertEqual(grade["summary"]["failed"], 0, grade["expectations"])

    def test_creation_fails_when_saga_is_elsewhere_in_fixture(self):
        self.create_saga("plans/cache-refresh-20261105")
        result = self.run_grader()
        self.assertEqual(result.returncode, 0, result.stderr)
        grade = json.loads(self.output.read_text())
        self.assertGreater(grade["summary"]["failed"], 0)

    def test_creation_fails_when_template_paths_disagree_with_location(self):
        self.create_saga(path_record="brain/sagas/another-saga")
        result = self.run_grader()
        self.assertEqual(result.returncode, 0, result.stderr)
        grade = json.loads(self.output.read_text())
        self.assertGreater(grade["summary"]["failed"], 0)

    def test_creation_accepts_resolved_absolute_paths_from_template(self):
        relative = "brain/sagas/cache-refresh-20261105"
        self.create_saga(path_record=str((self.fixture / relative).resolve()))
        result = self.run_grader()
        self.assertEqual(result.returncode, 0, result.stderr)
        grade = json.loads(self.output.read_text())
        path_check = next(item for item in grade["expectations"] if item["text"].startswith("SAGA.md and PROGRESS.md"))
        self.assertTrue(path_check["passed"], path_check)

    def test_creation_allows_generated_navigation_links_but_rejects_other_changes(self):
        self.create_saga()
        original_index = (self.source / "brain/index.md").read_text()
        index = self.fixture / "brain/index.md"
        index.write_text(
            original_index
            + "\n## sagas/cache-refresh-20261105\n\n"
            + "- [PROGRESS](<sagas/cache-refresh-20261105/PROGRESS.md>)\n"
            + "- [SAGA](<sagas/cache-refresh-20261105/SAGA.md>)\n"
        )
        result = self.run_grader()
        self.assertEqual(result.returncode, 0, result.stderr)
        grade = json.loads(self.output.read_text())
        outside_scope = next(item for item in grade["expectations"] if item["text"].startswith("No fixture files"))
        self.assertTrue(outside_scope["passed"], outside_scope)

        (self.fixture / "README.md").write_text("Unrelated change.\n")
        result = self.run_grader()
        self.assertEqual(result.returncode, 0, result.stderr)
        grade = json.loads(self.output.read_text())
        outside_scope = next(item for item in grade["expectations"] if item["text"].startswith("No fixture files"))
        self.assertFalse(outside_scope["passed"], outside_scope)

    def test_creation_ignores_only_harness_working_directory(self):
        self.create_saga()
        (self.fixture / "nested").mkdir()
        result = self.run_grader()
        self.assertEqual(result.returncode, 0, result.stderr)
        grade = json.loads(self.output.read_text())
        outside_scope = next(item for item in grade["expectations"] if item["text"].startswith("No fixture files"))
        self.assertTrue(outside_scope["passed"], outside_scope)

        (self.fixture / "unexpected-empty-dir").mkdir()
        result = self.run_grader()
        self.assertEqual(result.returncode, 0, result.stderr)
        grade = json.loads(self.output.read_text())
        outside_scope = next(item for item in grade["expectations"] if item["text"].startswith("No fixture files"))
        self.assertFalse(outside_scope["passed"], outside_scope)

    def test_missing_response_is_an_invalid_invocation(self):
        result = self.run_grader(**{"--response": str(self.root / "missing.md")})
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.output.exists())

    def test_malformed_eval_id_is_an_invalid_invocation(self):
        result = self.run_grader(eval_id="not-an-integer")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.output.exists())

    def test_resume_passes_for_unchanged_existing_saga_and_live_worker(self):
        self.seed_existing_saga("brain/sagas/cache-refresh-20261105")
        self.response.write_text("Resume cache-refresh-20261105. worker-17 is reachable and in progress; wait for its report.\n")
        result = self.run_grader(eval_id="1")
        self.assertEqual(result.returncode, 0, result.stderr)
        grade = json.loads(self.output.read_text())
        self.assertEqual(grade["summary"]["failed"], 0, grade["expectations"])

    def test_resume_fails_if_response_omits_existing_saga_identity(self):
        self.seed_existing_saga("brain/sagas/cache-refresh-20261105")
        self.response.write_text("worker-17 is reachable and in progress; wait for its report.\n")
        result = self.run_grader(eval_id="1")
        self.assertEqual(result.returncode, 0, result.stderr)
        grade = json.loads(self.output.read_text())
        response_check = next(item for item in grade["expectations"] if "next action" in item["text"])
        self.assertFalse(response_check["passed"], response_check)

    def test_duplicate_eval_fails_when_an_empty_saga_directory_is_added(self):
        self.seed_existing_saga("brain/sagas/label-copy")
        (self.fixture / "brain/sagas/duplicate").mkdir(parents=True)
        self.response.write_text("The existing label-copy plan already covers this small one-line change.\n")
        result = self.run_grader(eval_id="2")
        self.assertEqual(result.returncode, 0, result.stderr)
        grade = json.loads(self.output.read_text())
        self.assertGreater(grade["summary"]["failed"], 0)


if __name__ == "__main__":
    unittest.main()
