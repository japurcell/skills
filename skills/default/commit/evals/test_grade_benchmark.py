#!/usr/bin/env python3
"""Check workflow grading through disposable repositories and public CLIs."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
PREPARE = SKILL / "evals" / "prepare_validation_workflow.py"
GRADER = SKILL / "evals" / "grade_benchmark.py"


class WorkflowGradingTests(unittest.TestCase):
    def prepare(self):
        temporary = tempfile.TemporaryDirectory(prefix="commit-workflow-")
        self.addCleanup(temporary.cleanup)
        iteration = Path(temporary.name) / "iteration-1"
        evaluation = iteration / "eval-4-validation"
        evaluation.mkdir(parents=True)
        (evaluation / "eval_metadata.json").write_text('{"eval_id": 4}\n')
        run = evaluation / "with_skill" / "run-1"
        subprocess.run(
            [sys.executable, str(PREPARE), str(run), str(SKILL)],
            check=True, capture_output=True, text=True, timeout=10,
        )
        return iteration, run

    def validate(self, run, message=None):
        return subprocess.run(
            [sys.executable, str(run / "skill/scripts/validate_message.py"), str(message or run / "message.txt")],
            capture_output=True, text=True, timeout=5,
        )

    def repair(self, run):
        path = run / "message.txt"
        path.write_bytes(path.read_bytes().replace("\u2028".encode(), b"\n"))

    def commit(self, run, message=None):
        subprocess.run(
            ["git", "commit", "-F", str(message or run / "message.txt")],
            cwd=run / "repo", check=True, capture_output=True, text=True, timeout=10,
        )

    def grade(self, iteration, run):
        subprocess.run(
            [sys.executable, str(GRADER), str(iteration)],
            check=True, capture_output=True, text=True, timeout=10,
        )
        return json.loads((run / "grading.json").read_text())

    def test_observed_failure_repair_revalidation_and_commit_pass(self):
        iteration, run = self.prepare()
        self.assertEqual(self.validate(run).returncode, 1)
        self.repair(run)
        self.assertEqual(self.validate(run).returncode, 0)
        self.commit(run)
        grading = self.grade(iteration, run)
        self.assertEqual(grading["summary"]["failed"], 0, grading)
        self.assertGreaterEqual(grading["summary"]["total"], 4)

    def test_repaired_draft_can_use_a_new_validated_file(self):
        iteration, run = self.prepare()
        self.assertEqual(self.validate(run).returncode, 1)
        message = run / "outputs/repaired-message.txt"
        message.write_bytes((run / "message.txt").read_bytes().replace("\u2028".encode(), b"\n"))
        self.assertEqual(self.validate(run, message).returncode, 0)
        self.commit(run, message)
        grading = self.grade(iteration, run)
        self.assertEqual(grading["summary"]["failed"], 0, grading)

    def test_missing_revalidation_or_changed_content_cannot_pass(self):
        for failure in ("no-validation", "no-revalidation", "changed-after-validation", "no-initial-failure"):
            with self.subTest(failure=failure):
                iteration, run = self.prepare()
                if failure not in ("no-validation", "no-initial-failure"):
                    self.validate(run)
                self.repair(run)
                if failure not in ("no-validation", "no-revalidation"):
                    self.validate(run)
                if failure == "changed-after-validation":
                    path = run / "message.txt"
                    path.write_text(path.read_text().replace("document response target", "update support notes"))
                self.commit(run)
                grading = self.grade(iteration, run)
                self.assertGreater(grading["summary"]["failed"], 0, grading)

    def test_replacing_the_staged_change_cannot_pass(self):
        iteration, run = self.prepare()
        self.validate(run)
        self.repair(run)
        self.validate(run)
        (run / "repo/notes.txt").write_text("An unrelated replacement.\n")
        subprocess.run(["git", "add", "notes.txt"], cwd=run / "repo", check=True, timeout=5)
        self.commit(run)
        grading = self.grade(iteration, run)
        self.assertGreater(grading["summary"]["failed"], 0, grading)

    def test_first_validation_must_use_the_supplied_unedited_draft(self):
        for failure in ("edited-draft", "different-file"):
            with self.subTest(failure=failure):
                iteration, run = self.prepare()
                original = run / "message.txt"
                if failure == "edited-draft":
                    original.write_bytes(original.read_bytes().replace(b"document response target", b"change draft first"))
                    self.validate(run)
                else:
                    substitute = run / "outputs/substitute.txt"
                    substitute.write_bytes(original.read_bytes())
                    self.validate(run, substitute)
                self.repair(run)
                self.validate(run)
                self.commit(run)
                grading = self.grade(iteration, run)
                self.assertGreater(grading["summary"]["failed"], 0, grading)

    def test_missing_and_malformed_observations_fail_grading(self):
        for content in (None, "", "not json", "[]\n", '{"kind":"validation","message":[]}\n'):
            with self.subTest(content=content):
                iteration, run = self.prepare()
                events = run / "events.jsonl"
                if content is None:
                    events.unlink()
                else:
                    events.write_text(content)
                grading = self.grade(iteration, run)
                self.assertGreater(grading["summary"]["failed"], 0, grading)

    def test_bad_event_field_types_fail_without_crashing(self):
        iteration, run = self.prepare()
        self.validate(run)
        self.repair(run)
        self.validate(run)
        self.commit(run)
        events = run / "events.jsonl"
        records = [json.loads(line) for line in events.read_text().splitlines()]
        records[1]["message"] = []
        events.write_text("".join(json.dumps(record) + "\n" for record in records))
        grading = self.grade(iteration, run)
        self.assertGreater(grading["summary"]["failed"], 0, grading)


if __name__ == "__main__":
    unittest.main()
