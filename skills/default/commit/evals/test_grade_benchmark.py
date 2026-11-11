#!/usr/bin/env python3
"""Check workflow grading through disposable repositories and public CLIs."""

import json
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
PREPARE = SKILL / "evals" / "prepare_validation_workflow.py"
GRADER = SKILL / "evals" / "grade_benchmark.py"


class WorkflowGradingTests(unittest.TestCase):
    def prepare(self, fixture=None):
        temporary = tempfile.TemporaryDirectory(prefix="commit-workflow-")
        self.addCleanup(temporary.cleanup)
        iteration = Path(temporary.name) / "iteration-1"
        evaluation = iteration / "eval-4-validation"
        evaluation.mkdir(parents=True)
        (evaluation / "eval_metadata.json").write_text('{"eval_id": 4}\n')
        run = evaluation / "with_skill" / "run-1"
        command = [sys.executable, str(PREPARE), str(run), str(SKILL)]
        if fixture is not None:
            fixture_path = iteration / "input.json"
            fixture_path.write_text(json.dumps(fixture) + "\n")
            command.extend(("--fixture", str(fixture_path)))
        subprocess.run(
            command,
            check=True, capture_output=True, text=True, timeout=10,
        )
        return iteration, run

    def test_preparation_supports_read_only_skill_snapshots(self):
        temporary = tempfile.TemporaryDirectory(prefix="commit-readonly-skill-")
        self.addCleanup(temporary.cleanup)
        snapshot = Path(temporary.name) / "skill-snapshot"
        shutil.copytree(SKILL, snapshot)

        def permissions(root):
            paths = [root, *root.rglob("*")]
            return {
                path.relative_to(root).as_posix() if path != root else ".": stat.S_IMODE(path.stat().st_mode)
                for path in paths
            }

        def restore_write_access(root):
            for path in [root, *root.rglob("*")]:
                mode = stat.S_IMODE(path.stat().st_mode)
                path.chmod(mode | stat.S_IWUSR)

        self.addCleanup(restore_write_access, snapshot)
        for path in [snapshot, *snapshot.rglob("*")]:
            path.chmod(stat.S_IMODE(path.stat().st_mode) & ~stat.S_IWUSR)
        original_modes = permissions(snapshot)
        original_content = {
            path.relative_to(snapshot).as_posix(): path.read_bytes()
            for path in snapshot.rglob("*") if path.is_file()
        }

        run = Path(temporary.name) / "run"
        prepared = subprocess.run(
            [sys.executable, str(PREPARE), str(run), str(snapshot)],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(prepared.returncode, 0, prepared.stderr)
        self.assertEqual(permissions(snapshot), original_modes)
        self.assertEqual(
            {path.relative_to(snapshot).as_posix(): path.read_bytes()
             for path in snapshot.rglob("*") if path.is_file()},
            original_content,
        )
        self.assertEqual(
            stat.S_IMODE((run / "skill/scripts").stat().st_mode),
            original_modes["scripts"],
        )
        self.assertEqual(self.validate(run).returncode, 1)
        events = [json.loads(line) for line in (run / "events.jsonl").read_text().splitlines()]
        self.assertEqual(events[0]["kind"], "validation")
        self.assertEqual(events[0]["exit_code"], 1)

    def validate(self, run, message=None, options=()):
        return subprocess.run(
            [sys.executable, str(run / "skill/scripts/validate_message.py"), str(message or run / "message.txt"), *options],
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
        result = subprocess.run(
            [sys.executable, str(GRADER), str(iteration)],
            check=False, capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
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

    def test_expected_coauthor_requires_observed_option_and_committed_trailer(self):
        author = "Codex <noreply@openai.com>"
        iteration, run = self.prepare()
        fixture_path = run / "fixture.json"
        fixture = json.loads(fixture_path.read_text())
        fixture["expected_coauthors"] = [author]
        fixture_path.write_text(json.dumps(fixture) + "\n")

        self.assertEqual(self.validate(run).returncode, 1)
        self.repair(run)
        message = run / "message.txt"
        message.write_text(message.read_text() + "\nCo-authored-by: " + author + "\n")
        self.assertEqual(self.validate(run, options=("--co-author", author)).returncode, 0)
        self.commit(run)
        grading = self.grade(iteration, run)
        self.assertEqual(grading["summary"]["failed"], 0, grading)

        events_path = run / "events.jsonl"
        events = [json.loads(line) for line in events_path.read_text().splitlines()]
        next(event for event in reversed(events) if event["kind"] == "validation")["argv"] = [str(message.resolve())]
        events_path.write_text("".join(json.dumps(event) + "\n" for event in events))
        grading = self.grade(iteration, run)
        self.assertGreater(grading["summary"]["failed"], 0, grading)

    def test_expected_coauthor_rejects_malformed_invocation_evidence(self):
        author = "Codex <noreply@openai.com>"
        iteration, run = self.prepare()
        fixture_path = run / "fixture.json"
        fixture = json.loads(fixture_path.read_text())
        fixture["expected_coauthors"] = [author]
        fixture_path.write_text(json.dumps(fixture) + "\n")
        self.validate(run)
        self.repair(run)
        self.commit(run)

        events_path = run / "events.jsonl"
        events = [json.loads(line) for line in events_path.read_text().splitlines()]
        events[0]["argv"] = ["--co-author", []]
        events_path.write_text("".join(json.dumps(event) + "\n" for event in events))
        grading = self.grade(iteration, run)
        self.assertGreater(grading["summary"]["failed"], 0, grading)

    def test_expected_coauthor_rejects_missing_git_trailer(self):
        author = "Codex <noreply@openai.com>"
        iteration, run = self.prepare()
        fixture_path = run / "fixture.json"
        fixture = json.loads(fixture_path.read_text())
        fixture["expected_coauthors"] = [author]
        fixture_path.write_text(json.dumps(fixture) + "\n")
        self.validate(run)
        self.repair(run)
        self.assertEqual(self.validate(run).returncode, 0)
        self.commit(run)
        grading = self.grade(iteration, run)
        trailer_check = next(
            item for item in grading["expectations"]
            if item["text"] == "The actual Git message contains each expected co-author trailer exactly once."
        )
        self.assertFalse(trailer_check["passed"], grading)

    def test_agent_attribution_scenario_uses_fixture_expected_identity(self):
        author = "Codex <noreply@openai.com>"
        fixture = {
            "before": "Support hours: weekdays.\n",
            "after": "Support hours: weekdays.\nResponse target: one business day.\n",
            "draft": "docs: document response target\u2028\u2028Summary:\u2028- Document the target.\u2028\u2028Rationale:\u2028- Clarify timing.\u2028\u2028Tests:\u2028- not run\u2028",
            "expected_coauthors": [author],
            "agent_edits": True,
        }
        iteration, run = self.prepare(fixture)
        metadata = json.loads((run / "fixture.json").read_text())
        self.assertEqual(metadata["expected_coauthors"], [author])
        clean = subprocess.run(
            ["git", "status", "--porcelain"], cwd=run / "repo",
            check=True, capture_output=True, text=True, timeout=5,
        )
        self.assertEqual(clean.stdout, "")
        self.assertEqual(self.validate(run).returncode, 1)
        self.repair(run)
        (run / "repo/notes.txt").write_text(fixture["after"], encoding="utf-8")
        subprocess.run(["git", "add", "notes.txt"], cwd=run / "repo", check=True, timeout=5)
        message = run / "message.txt"
        message.write_text(message.read_text() + "\nCo-authored-by: " + author + "\n")
        self.assertEqual(self.validate(run, options=("--co-author", author)).returncode, 0)
        self.commit(run)
        (run.parent.parent / "eval_metadata.json").write_text('{"eval_id": 5}\n')
        grading = self.grade(iteration, run)
        self.assertEqual(grading["summary"]["failed"], 0, grading)

    def test_copilot_attribution_scenario_uses_fixture_expected_identity(self):
        author = "Copilot <223556219+Copilot@users.noreply.github.com>"
        fixture = {
            "before": "Support hours: weekdays.\n",
            "after": "Support hours: weekdays.\nResponse target: one business day.\n",
            "draft": "docs: document response target\u2028\u2028Summary:\u2028- Document the target.\u2028\u2028Rationale:\u2028- Clarify timing.\u2028\u2028Tests:\u2028- not run\u2028",
            "expected_coauthors": [author],
            "agent_edits": True,
        }
        iteration, run = self.prepare(fixture)
        self.assertEqual(self.validate(run).returncode, 1)
        self.repair(run)
        (run / "repo/notes.txt").write_text(fixture["after"], encoding="utf-8")
        subprocess.run(["git", "add", "notes.txt"], cwd=run / "repo", check=True, timeout=5)
        message = run / "message.txt"
        message.write_text(message.read_text() + "\nCo-authored-by: " + author + "\n")
        self.assertEqual(self.validate(run, options=("--co-author", author)).returncode, 0)
        self.commit(run)
        (run.parent.parent / "eval_metadata.json").write_text('{"eval_id": 6}\n')
        grading = self.grade(iteration, run)
        self.assertEqual(grading["summary"]["failed"], 0, grading)

    def test_copilot_eval_separates_contribution_from_neutral_commit_request(self):
        scenarios = json.loads((SKILL / "evals" / "evals.json").read_text())["evals"]
        scenario = next(item for item in scenarios if item["id"] == 6)
        self.assertIn("Do not commit.", scenario["contribution_prompt"])
        self.assertEqual(scenario["prompt"], "Commit the current change.")
        self.assertNotIn("co-author", scenario["prompt"].lower())
        self.assertNotIn("trailer", scenario["prompt"].lower())

    def test_codex_eval_does_not_prompt_for_attribution(self):
        scenarios = json.loads((SKILL / "evals" / "evals.json").read_text())["evals"]
        scenario = next(item for item in scenarios if item["id"] == 5)
        self.assertIn("Do not commit.", scenario["contribution_prompt"])
        self.assertNotIn("co-author", scenario["prompt"].lower())
        self.assertNotIn("trailer", scenario["prompt"].lower())
        self.assertNotIn("attribution", scenario["prompt"].lower())

    def test_repository_policy_fixture_is_committed_before_agent_turn(self):
        policy = "Commit messages must omit all co-author trailers.\n"
        fixture = {
            "before": "Support hours: weekdays.\n",
            "after": "Support hours: weekdays.\nResponse target: one business day.\n",
            "draft": "docs: document response target\\u2028\\u2028Summary:\\u2028- Document the target.\\u2028\\u2028Rationale:\\u2028- Clarify timing.\\u2028\\u2028Tests:\\u2028- not run\\u2028",
            "expected_coauthors": [],
            "agent_edits": True,
            "policy_file": "AGENTS.md",
            "repository_policy": policy,
        }
        _, run = self.prepare(fixture)
        self.assertEqual((run / "repo/AGENTS.md").read_text(), policy)
        actual = subprocess.run(
            ["git", "show", "HEAD:AGENTS.md"], cwd=run / "repo",
            check=True, capture_output=True, text=True, timeout=5,
        )
        self.assertEqual(actual.stdout, policy)

    def test_override_optout_no_contribution_and_dedup_fixtures_grade(self):
        evals = SKILL / "evals"
        cases = (
            (7, "explicit-identity-override"),
            (8, "explicit-opt-out"),
            (10, "user-overrides-repository-policy"),
            (11, "no-agent-contribution"),
            (12, "preserve-and-deduplicate-contributors"),
        )
        for eval_id, name in cases:
            with self.subTest(name=name):
                fixture = json.loads((evals / "files" / name / "input.json").read_text())
                iteration, run = self.prepare(fixture)
                if fixture["agent_edits"]:
                    (run / "repo/notes.txt").write_text(fixture["after"], encoding="utf-8")
                    subprocess.run(["git", "add", "notes.txt"], cwd=run / "repo", check=True, timeout=5)
                authors = fixture["expected_coauthors"]
                message = (
                    "docs: record review reminder\n\n"
                    "Summary:\n- Record the review reminder.\n\n"
                    "Rationale:\n- Keep the change clear.\n\n"
                    "Tests:\n- Not run (documentation-only change).\n"
                ) + "".join(f"\nCo-authored-by: {author}" for author in authors) + "\n"
                message_path = run / "message.txt"
                message_path.write_text(message, encoding="utf-8")
                options = tuple(arg for author in authors for arg in ("--co-author", author))
                self.assertEqual(self.validate(run, options=options).returncode, 0)
                self.commit(run)
                (run.parent.parent / "eval_metadata.json").write_text(json.dumps({"eval_id": eval_id}) + "\n")
                grading = self.grade(iteration, run)
                self.assertEqual(grading["summary"]["failed"], 0, grading)

    def make_valid_no_identity_run(self):
        fixture = json.loads((SKILL / "evals/files/explicit-opt-out/input.json").read_text())
        iteration, run = self.prepare(fixture)
        (run / "repo/notes.txt").write_text(fixture["after"], encoding="utf-8")
        subprocess.run(["git", "add", "notes.txt"], cwd=run / "repo", check=True, timeout=5)
        message = (
            "docs: record review reminder\n\n"
            "Summary:\n- Record the review reminder.\n\n"
            "Rationale:\n- Respect the explicit attribution opt-out.\n\n"
            "Tests:\n- Not run (documentation-only change).\n"
        )
        (run / "message.txt").write_text(message, encoding="utf-8")
        self.assertEqual(self.validate(run).returncode, 0)
        self.commit(run)
        (run.parent.parent / "eval_metadata.json").write_text('{"eval_id": 8}\n')
        self.assertEqual(self.grade(iteration, run)["summary"]["failed"], 0)
        return iteration, run

    def test_empty_expected_identities_reject_missing_or_malformed_argv(self):
        malformed_argv_values = (None, [], ["--co-author"], ["message.txt", 7])
        for missing, argv in ((True, None), *((False, value) for value in malformed_argv_values)):
            with self.subTest(missing=missing, argv=argv):
                iteration, run = self.make_valid_no_identity_run()
                events_path = run / "events.jsonl"
                events = [json.loads(line) for line in events_path.read_text().splitlines()]
                validation = next(event for event in events if event["kind"] == "validation")
                if missing:
                    validation.pop("argv")
                else:
                    validation["argv"] = argv
                events_path.write_text("".join(json.dumps(event) + "\n" for event in events))
                grading = self.grade(iteration, run)
                self.assertGreater(grading["summary"]["failed"], 0, grading)

    def test_empty_expected_identities_require_validator_before_commit(self):
        iteration, run = self.make_valid_no_identity_run()
        events_path = run / "events.jsonl"
        events = [json.loads(line) for line in events_path.read_text().splitlines()]
        validation = next(event for event in events if event["kind"] == "validation")
        commit = next(event for event in events if event["kind"] == "commit")
        events[:] = [commit, validation]
        events_path.write_text("".join(json.dumps(event) + "\n" for event in events))
        grading = self.grade(iteration, run)
        self.assertGreater(grading["summary"]["failed"], 0, grading)

    def test_empty_expected_identities_require_validated_message_to_match_commit(self):
        iteration, run = self.make_valid_no_identity_run()
        events_path = run / "events.jsonl"
        events = [json.loads(line) for line in events_path.read_text().splitlines()]
        validation = next(event for event in events if event["kind"] == "validation")
        validation["message"] = validation["message"].replace(
            "Respect the explicit attribution opt-out.", "Change the observed validation message."
        )
        events_path.write_text("".join(json.dumps(event) + "\n" for event in events))
        grading = self.grade(iteration, run)
        self.assertGreater(grading["summary"]["failed"], 0, grading)

    def test_empty_expected_identities_require_path_and_matching_argv(self):
        for mutation in ("missing-path", "mismatched-argv-path"):
            with self.subTest(mutation=mutation):
                iteration, run = self.make_valid_no_identity_run()
                events_path = run / "events.jsonl"
                events = [json.loads(line) for line in events_path.read_text().splitlines()]
                validation = next(event for event in events if event["kind"] == "validation")
                if mutation == "missing-path":
                    validation.pop("path")
                else:
                    validation["argv"][0] = str(run / "different-message.txt")
                events_path.write_text("".join(json.dumps(event) + "\n" for event in events))
                grading = self.grade(iteration, run)
                self.assertGreater(grading["summary"]["failed"], 0, grading)

    def test_malformed_event_records_fail_grading_without_crashing(self):
        for malformed in ("validation-record", "commit-message"):
            with self.subTest(malformed=malformed):
                iteration, run = self.make_valid_no_identity_run()
                events_path = run / "events.jsonl"
                events = [json.loads(line) for line in events_path.read_text().splitlines()]
                if malformed == "validation-record":
                    validation_index = next(i for i, event in enumerate(events) if event["kind"] == "validation")
                    events[validation_index] = []
                else:
                    commit_event = next(event for event in events if event["kind"] == "commit")
                    commit_event["message"] = None
                events_path.write_text("".join(json.dumps(event) + "\n" for event in events))
                grading = self.grade(iteration, run)
                self.assertGreater(grading["summary"]["failed"], 0, grading)


if __name__ == "__main__":
    unittest.main()
