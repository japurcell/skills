#!/usr/bin/env python3
"""Exercise create-skill benchmark grading through its public CLI."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[4]
GRADER = REPO_ROOT / "skills/default/create-skill/evals/grade_benchmark.py"
WORKSPACE_EXPECTATION = (
    "Generated output describes a category-level published sibling "
    "(skills/<category>/<skill>-workspace/iteration-N) or a repo-local "
    "sibling (.agents/skills/<name>-workspace/iteration-N or "
    "../<name>-workspace/iteration-N from its owner)."
)


class TestCreateSkillWorkspaceLayout(unittest.TestCase):
    def grade_layout_reference(self, reference: str) -> dict:
        with tempfile.TemporaryDirectory(prefix="create-skill-grader-") as temporary:
            iteration_dir = Path(temporary) / "iteration-1"
            run_dir = (
                iteration_dir
                / "eval-3-workspace-layout"
                / "with_skill"
                / "run-1"
            )
            outputs_dir = run_dir / "outputs"
            outputs_dir.mkdir(parents=True)
            eval_dir = run_dir.parents[1]
            (eval_dir / "eval_metadata.json").write_text(
                json.dumps({"eval_name": "harden-skill-for-weaker-models"}),
                encoding="utf-8",
            )
            (outputs_dir / "output.md").write_text(
                f"Benchmark workspace guidance: {reference}\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(GRADER), str(iteration_dir)],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Wrote grading.json files", result.stdout)
            self.assertEqual(result.stderr, "")

            grading_path = run_dir / "grading.json"
            self.assertTrue(grading_path.is_file())
            grading = json.loads(grading_path.read_text(encoding="utf-8"))
            expectations = {
                item["text"]: item for item in grading["expectations"]
            }
            self.assertIn(WORKSPACE_EXPECTATION, expectations)
            return expectations[WORKSPACE_EXPECTATION]

    def test_category_level_published_workspace_is_accepted(self):
        expectation = self.grade_layout_reference(
            "skills/<category>/<skill>-workspace/iteration-N/"
        )
        self.assertTrue(expectation["passed"], expectation["evidence"])

    def test_concrete_default_category_workspace_is_accepted(self):
        expectation = self.grade_layout_reference(
            "skills/default/task-wave-workspace/iteration-3/ beside "
            "skills/default/task-wave/"
        )
        self.assertTrue(expectation["passed"], expectation["evidence"])

    def test_repo_local_workspace_sibling_is_accepted(self):
        expectation = self.grade_layout_reference(
            ".agents/skills/<name>-workspace/iteration-N/ beside "
            ".agents/skills/<name>/"
        )
        self.assertTrue(expectation["passed"], expectation["evidence"])

    def test_repo_local_owner_relative_workspace_sibling_is_accepted(self):
        expectation = self.grade_layout_reference(
            "../<name>-workspace/iteration-N/ from .agents/skills/<name>/"
        )
        self.assertTrue(expectation["passed"], expectation["evidence"])

    def test_obsolete_root_workspace_is_not_accepted(self):
        expectation = self.grade_layout_reference(
            "skills/<skill>-workspace/iteration-N/"
        )
        self.assertFalse(expectation["passed"], expectation["evidence"])


class TestMinimizationInvocation(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.iteration = Path(temporary.name)
        self.case = self.iteration / "eval-invocation"
        self.run_dir = self.case / "with_skill" / "run-1"
        self.baseline = self.run_dir / "outputs" / "report-guide"
        self.baseline.mkdir(parents=True)
        fixture = GRADER.parent / "files" / "report-guide" / "SKILL.md"
        (self.baseline / "SKILL.md").write_text(fixture.read_text().replace("--pretty", "--readable"))
        self.trials = self.baseline.parent / "trials"

    def grade(self, name):
        (self.case / "eval_metadata.json").write_text(json.dumps({"eval_name": name}))
        subprocess.run([sys.executable, str(GRADER), str(self.iteration)], check=True, capture_output=True)
        return json.loads((self.run_dir / "grading.json").read_text())["summary"]["failed"]

    def test_the_same_edit_requires_different_evidence_by_invocation(self):
        plain = "revise-without-minimization"
        flagged = "revise-with-minimization"
        self.assertEqual(self.grade(plain), 0)
        self.assertGreater(self.grade(flagged), 0)
        self.trials.mkdir()
        helper = GRADER.parents[1] / "scripts" / "wording_trial.py"
        cut = subprocess.check_output([
            sys.executable, str(helper), "cut", str(self.baseline), str(self.trials / "candidate"),
            "For compact output, use the compact output option.",
        ])
        record = self.trials / "cut.json"
        record.write_bytes(cut)
        self.assertEqual(self.grade(flagged), 0)
        self.assertGreater(self.grade(plain), 0)
        self.assertGreater(self.grade("revise-with-target-argument"), 0)
        record.write_text(json.dumps({**json.loads(cut), "candidate_skill_sha256": "stale"}))
        self.assertGreater(self.grade(flagged), 0)
        record.write_text("invalid JSON")
        self.assertGreater(self.grade(flagged), 0)
        record.write_bytes(cut)
        (self.trials / "candidate" / "SKILL.md").write_text("unrelated")
        self.assertGreater(self.grade(flagged), 0)

    def test_empty_plain_run_fails(self):
        (self.baseline / "SKILL.md").unlink()
        self.assertGreater(self.grade("revise-without-minimization"), 0)


if __name__ == "__main__":
    unittest.main()
