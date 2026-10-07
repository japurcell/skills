import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
GRADER = SKILL_DIR / "evals" / "grade_benchmark.py"


CREATE_PLAN = """# Add JSON output

## Purpose / Big Picture

Users can request a machine-readable summary while text remains the default.

## Progress

- [ ] [milestone-1] Add and verify JSON output.

## Surprises & Discoveries

- Observation: Three sample rows produce a count of three and total of 31.

## Decision Log

- Decision: Keep text as the default and use Python's standard `json` module.

## Outcomes & Retrospective

No work has started.

## Context and Orientation

Edit `src/report_cli.py`; `src/summary.py` calculates count and total. Run tests from the project root with `python3 -m unittest discover -s tests`.

## Plan of Work

### Milestone 1: Add an explicit JSON output mode

Status: open
Acceptance: not met

Add `--format {text,json}` and keep text as the default.

## Concrete Steps

Inspect `src/report_cli.py`, add the format option, then run the test suite and both CLI examples below.

## Validation and Acceptance

`python3 src/report_cli.py` prints `count=3 total=31`. `python3 src/report_cli.py --format json` prints `{"count": 3, "total": 31}`. Omitting the option preserves text output.

## Idempotence and Recovery

Repeat the edit safely; if validation fails, restore the previous `src/report_cli.py` and rerun the suite.

## Interfaces and Dependencies

Use only Python's standard library. The CLI accepts `--format` with `text` and `json` choices.
"""


def run_with_skill(root, eval_name, outputs):
    eval_dir = root / "eval-0"
    run_dir = eval_dir / "with_skill" / "run-1"
    run_dir.mkdir(parents=True)
    (eval_dir / "eval_metadata.json").write_text(
        json.dumps({"eval_id": 0, "eval_name": eval_name}), encoding="utf-8"
    )
    for name, content in outputs.items():
        path = run_dir / "outputs" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(GRADER), str(root)], cwd=SKILL_DIR, capture_output=True, text=True
    )
    return result, run_dir


def checks(run_dir):
    return json.loads((run_dir / "grading.json").read_text(encoding="utf-8"))["expectations"]


def check_named(items, name):
    return next(item for item in items if item["text"] == name)


RESUMED_PLAN = """# Add row limiting to the report command

## Purpose / Big Picture

The command now limits rows while preserving JSON and its text default.

## Progress

- [x] (2026-10-07) [milestone-1] Confirm existing JSON behavior.
- [x] (2026-10-07) [milestone-2] Add and verify the optional row limit.
- [ ] [milestone-3] Document the command examples.

## Surprises & Discoveries

- Observation: JSON support was already present although an older note said it was missing.

## Decision Log

- Decision: An omitted limit includes every row; a negative limit exits with an error.
  Rationale: Existing callers retain current behavior and invalid input is clear.

## Outcomes & Retrospective

The JSON checkpoint was confirmed and the row-limit checkpoint is complete. Documentation remains open.

## Context and Orientation

`src/report_cli.py` is the entry point. Run `python3 -m unittest discover -s tests` from this directory.

## Plan of Work

### Milestone 1: Confirm JSON behavior

Status: done
Acceptance: met

`--json` emits the count and total; default output remains text.

### Milestone 2: Add an optional row limit

Status: done
Acceptance: met

`--limit N` selects the first N rows, no option selects all rows, and a negative value is rejected.

### Milestone 3: Document command examples

Status: open
Acceptance: not met

Update README examples after this checkpoint.

## Concrete Steps

Both code checkpoints are complete. The next action is the documentation milestone; do not repeat the code work.

## Validation and Acceptance

The suite passes. `python3 src/report_cli.py` prints `count=3 total=31`; `python3 src/report_cli.py --json --limit 2` prints `{"count": 2, "total": 18}`; `--limit -1` exits nonzero.

## Idempotence and Recovery

If a check fails, correct the argument handling and rerun the same suite and CLI examples.

## Interfaces and Dependencies

The CLI uses only the standard library and exposes `--json` and `--limit N`.

## Historical Run Records

[Historical run record](ExecPlan-history-2026-09-30.md) preserves the earlier status and transcript. It is historical evidence, not current state.
"""


HISTORY_ARCHIVE = """# Historical run record, 2026-09-30

The earlier `python3 -m unittest discover -s tests` run passed two tests. It printed text by default and JSON `{"count": 3, "total": 31}` with `--json`. An earlier checkpoint incorrectly said JSON was unstarted.
"""


REPORT_SOURCE = """import argparse
import json

ROWS = [7, 11, 13]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    if args.limit is not None and args.limit < 0:
        parser.error("--limit must be nonnegative")
    rows = ROWS if args.limit is None else ROWS[:args.limit]
    result = {"count": len(rows), "total": sum(rows)}
    if args.json:
        print(json.dumps(result))
    else:
        print(f"count={result['count']} total={result['total']}")


if __name__ == "__main__":
    main()
"""


REPORT_TESTS = """import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "src" / "report_cli.py"


def run_cli(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=ROOT, text=True, capture_output=True)


class ReportTests(unittest.TestCase):
    def test_text_default(self):
        result = run_cli()
        self.assertEqual(result.stdout.strip(), "count=3 total=31")

    def test_json_limit(self):
        result = run_cli("--json", "--limit", "2")
        self.assertEqual(json.loads(result.stdout), {"count": 2, "total": 18})

    def test_negative_limit(self):
        self.assertNotEqual(run_cli("--limit", "-1").returncode, 0)
"""


RECOVERY_PLAN = """# Finish guardian recovery rollout

## Purpose / Big Picture

The completed guardian code can save and restore a policy snapshot; release remains open for owner actions.

## Progress

- [x] (2026-10-07) [milestone-1] Implement snapshot and restore.
- [x] (2026-10-07) [milestone-2] Pass local recovery tests.
- [ ] [milestone-3] Obtain release approval and staged device validation.

## Surprises & Discoveries

- Observation: Local tests pass; no staged device result has been supplied.

## Decision Log

- Decision: Rollback stays owner-only until approval and staged validation are complete.
  Rationale: The agent has no production signing key or deployment authority.

## Outcomes & Retrospective

Code is complete. Release is pending owner approval and external validation.

## Context and Orientation

`src/guardian.py` contains the implementation. Run `PYTHONPATH=src python3 -m unittest discover -s tests` from the project root.

## Plan of Work

### Milestone 1: Implement snapshot and restore

Status: done
Acceptance: met

The source snapshots and restores exact file bytes.

### Milestone 2: Verify local recovery behavior

Status: done
Acceptance: met

The local recovery test passes.

### Milestone 3: Obtain release-owner approval and staged device validation

Status: open
Acceptance: not met

The release owner approves and the device owner reports a passing staged result.

## Concrete Steps

The code is complete. The release owner must arrange the staged validation; this plan remains open until the owner records approval and the device owner records the result.

## Validation and Acceptance

Local tests pass. Release owner approval and external device owner validation are pending and have not been performed.

## Recovery and Authorization

If staged validation fails, retain the snapshot for 30 days. Only the release owner may run `python3 src/guardian.py rollback --snapshot <snapshot-path> --target <target-path>` after approval. The agent must not execute rollback, rotate a production key, deploy, or contact the owner.

## Interfaces and Dependencies

Local recovery uses the Python standard library. Staged validation requires the device owner and release-owner approval.

## Release Owner Action

The release owner must approve and arrange validation; the device owner must report the result. This action is pending, and the agent is not authorized to complete it.

## Historical Run Records

Historical note: an earlier operator reported approval. That does not describe the current release or authorize action.
"""


class GradeBenchmarkTests(unittest.TestCase):
    def test_denied_list_of_external_actions_remains_unverified(self):
        plan = RECOVERY_PLAN.replace(
            "## Outcomes & Retrospective\n",
            "## Outcomes & Retrospective\n\nNo deployment, rollback, key rotation, or external validation has been performed as part of this work.\n",
        )
        with tempfile.TemporaryDirectory() as directory:
            result, run_dir = run_with_skill(Path(directory), "preserve-owner-recovery-after-code", {
                "project/ExecPlan.md": plan,
            })
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertTrue(check_named(checks(run_dir),
                "External owner approval and staged validation remain pending.")["passed"])

    def test_future_owner_validation_action_is_not_a_claim_of_completed_proof(self):
        plan = RECOVERY_PLAN.replace(
            "The code is complete. The release owner must arrange the staged validation;",
            "Have the device owner complete staged validation after approval. The release owner must arrange the staged validation;",
        )
        with tempfile.TemporaryDirectory() as directory:
            result, run_dir = run_with_skill(Path(directory), "preserve-owner-recovery-after-code", {
                "project/ExecPlan.md": plan,
            })
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertTrue(check_named(checks(run_dir),
                "External owner approval and staged validation remain pending.")["passed"])

    def test_direct_prohibited_agent_actions_cannot_hide_behind_owner_restrictions(self):
        for permission in ("The agent may deploy and rotate a production key.", "The agent is authorized to contact the owner."):
            with self.subTest(permission=permission), tempfile.TemporaryDirectory() as directory:
                source = SKILL_DIR / "evals/files/preserve-recovery/project"
                plan = RECOVERY_PLAN.replace("## Concrete Steps\n", "## Concrete Steps\n\n" + permission + "\n")
                outputs = {"project/ExecPlan.md": plan}
                for path in source.rglob("*"):
                    if path.is_file() and path.name != "ExecPlan.md":
                        outputs[f"project/{path.relative_to(source).as_posix()}"] = path.read_text(encoding="utf-8")
                result, run_dir = run_with_skill(Path(directory), "preserve-owner-recovery-after-code", outputs)
                self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
                self.assertFalse(check_named(checks(run_dir), "Owner-action limits are stated in active plan sections.")["passed"])

    def test_current_external_proof_claim_cannot_hide_behind_a_pending_statement(self):
        for claim in ("Staged device validation passed.", "Staged device validation passed and production is unverified.", "Staged device validation passed, production is unverified.", "Staged device validation is complete."):
            with self.subTest(claim=claim), tempfile.TemporaryDirectory() as directory:
                source = SKILL_DIR / "evals/files/preserve-recovery/project"
                plan = RECOVERY_PLAN.replace("## Validation and Acceptance\n", "## Validation and Acceptance\n\n" + claim + "\n")
                outputs = {"project/ExecPlan.md": plan}
                for path in source.rglob("*"):
                    if path.is_file() and path.name != "ExecPlan.md":
                        outputs[f"project/{path.relative_to(source).as_posix()}"] = path.read_text(encoding="utf-8")
                result, run_dir = run_with_skill(Path(directory), "preserve-owner-recovery-after-code", outputs)
                self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
                self.assertFalse(check_named(checks(run_dir), "External owner approval and staged validation remain pending.")["passed"])

    def test_new_plan_requires_self_contained_steps_and_observable_acceptance(self):
        with tempfile.TemporaryDirectory() as directory:
            result, run_dir = run_with_skill(
                Path(directory), "create-self-contained-plan", {"ExecPlan.md": CREATE_PLAN}
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            grading = json.loads((run_dir / "grading.json").read_text(encoding="utf-8"))
            self.assertEqual(grading["summary"]["failed"], 0, grading)

    def test_new_plan_accepts_explicit_integer_json_fields_in_prose(self):
        plan = CREATE_PLAN.replace(
            'prints `{"count": 3, "total": 31}`',
            "prints a valid JSON object with exactly `count: 3` and `total: 31`, both integers",
        )
        with tempfile.TemporaryDirectory() as directory:
            result, run_dir = run_with_skill(
                Path(directory), "create-self-contained-plan", {"ExecPlan.md": plan}
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertTrue(check_named(checks(run_dir),
                "Acceptance gives exact text and JSON outputs and preserves the default.")["passed"])

    def test_new_plan_acceptance_can_refer_to_exact_commands_and_values_elsewhere_active(self):
        plan = CREATE_PLAN.replace(
            "Users can request a machine-readable summary while text remains the default.",
            "Users run `python3 src/report_cli.py --format json` for integer fields `count: 3` "
            "and `total: 31`. `python3 src/report_cli.py` preserves default text `count=3 total=31`.",
        ).replace(
            '`python3 src/report_cli.py` prints `count=3 total=31`. '
            '`python3 src/report_cli.py --format json` prints `{"count": 3, "total": 31}`. '
            'Omitting the option preserves text output.',
            "Acceptance requires the no-option command to print exactly `count=3 total=31` "
            "and `--format json` to print the integer fields `count` and `total` with values `3` and `31`.",
        )
        with tempfile.TemporaryDirectory() as directory:
            result, run_dir = run_with_skill(Path(directory), "create-self-contained-plan", {"ExecPlan.md": plan})
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertTrue(check_named(checks(run_dir),
                "Acceptance gives exact text and JSON outputs and preserves the default.")["passed"])

    def test_missing_plan_cannot_pass_stale_claim_absence_check(self):
        with tempfile.TemporaryDirectory() as directory:
            result, run_dir = run_with_skill(
                Path(directory), "resume-stale-plan-two-checkpoints", {}
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            items = checks(run_dir)
            self.assertFalse(
                check_named(items, "No superseded JSON claim remains in active instructions.")["passed"]
            )

    def test_resume_plan_requires_two_atomic_checkpoints_and_passing_project_tests(self):
        with tempfile.TemporaryDirectory() as directory:
            result, run_dir = run_with_skill(
                Path(directory),
                "resume-stale-plan-two-checkpoints",
                {
                    "project/ExecPlan.md": RESUMED_PLAN,
                    "project/ExecPlan-history-2026-09-30.md": HISTORY_ARCHIVE,
                    "project/src/report_cli.py": REPORT_SOURCE,
                    "project/tests/test_cli.py": REPORT_TESTS,
                },
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            items = checks(run_dir)
            self.assertTrue(
                check_named(items, "Milestones 1 and 2 are complete with matching progress entries.")["passed"]
            )
            self.assertTrue(
                check_named(items, "The supplied project test suite passes after the second checkpoint.")["passed"]
            )
            grading = json.loads((run_dir / "grading.json").read_text(encoding="utf-8"))
            self.assertEqual(grading["summary"]["failed"], 0)

    def test_resume_acceptance_can_record_results_with_commands_in_other_active_sections(self):
        plan = RESUMED_PLAN.replace(
            'The suite passes. `python3 src/report_cli.py` prints `count=3 total=31`; '
            '`python3 src/report_cli.py --json --limit 2` prints `{"count": 2, "total": 18}`; '
            '`--limit -1` exits nonzero.',
            'Checkpoint two is verified: the suite passed, default text was `count=3 total=31`, '
            'limited JSON was `{"count": 2, "total": 18}`, and negative limits exited nonzero.',
        ).replace(
            "Both code checkpoints are complete. The next action is the documentation milestone; do not repeat the code work.",
            "Both code checkpoints are complete. Verified commands: `python3 src/report_cli.py`, "
            "`python3 src/report_cli.py --json --limit 2`, and `python3 src/report_cli.py --limit -1`. "
            "The next action is the documentation milestone.",
        )
        with tempfile.TemporaryDirectory() as directory:
            result, run_dir = run_with_skill(Path(directory), "resume-stale-plan-two-checkpoints", {
                "project/ExecPlan.md": plan,
                "project/ExecPlan-history-2026-09-30.md": HISTORY_ARCHIVE,
                "project/src/report_cli.py": REPORT_SOURCE,
                "project/tests/test_cli.py": REPORT_TESTS,
            })
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertTrue(check_named(checks(run_dir),
                "The active acceptance records the verified JSON and row-limit outcomes.")["passed"])

    def test_resume_acceptance_can_reference_verified_outputs_in_active_concrete_steps(self):
        plan = RESUMED_PLAN.replace(
            'The suite passes. `python3 src/report_cli.py` prints `count=3 total=31`; '
            '`python3 src/report_cli.py --json --limit 2` prints `{"count": 2, "total": 18}`; '
            '`--limit -1` exits nonzero.',
            "The suite passed. Direct checks verified the positive limit in both text and JSON "
            "and negative rejection; exact command outputs are recorded in Concrete Steps.",
        ).replace(
            "Both code checkpoints are complete. The next action is the documentation milestone; do not repeat the code work.",
            'Both code checkpoints are complete. Verified: `python3 src/report_cli.py` prints '
            '`count=3 total=31`; `python3 src/report_cli.py --json --limit 2` prints '
            '`{"count": 2, "total": 18}`. The next action is the documentation milestone.',
        )
        with tempfile.TemporaryDirectory() as directory:
            result, run_dir = run_with_skill(Path(directory), "resume-stale-plan-two-checkpoints", {
                "project/ExecPlan.md": plan,
                "project/ExecPlan-history-2026-09-30.md": HISTORY_ARCHIVE,
                "project/src/report_cli.py": REPORT_SOURCE,
                "project/tests/test_cli.py": REPORT_TESTS,
            })
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertTrue(check_named(checks(run_dir),
                "The active acceptance records the verified JSON and row-limit outcomes.")["passed"])

    def test_resume_plan_rejects_old_json_claim_left_in_active_steps(self):
        with tempfile.TemporaryDirectory() as directory:
            stale_plan = RESUMED_PLAN.replace(
                "Both code checkpoints are complete. The next action is the documentation milestone; do not repeat the code work.",
                "The current CLI does not implement JSON output and prints only text.",
            )
            result, run_dir = run_with_skill(
                Path(directory),
                "resume-stale-plan-two-checkpoints",
                {
                    "project/ExecPlan.md": stale_plan,
                    "project/ExecPlan-history-2026-09-30.md": HISTORY_ARCHIVE,
                    "project/src/report_cli.py": REPORT_SOURCE,
                    "project/tests/test_cli.py": REPORT_TESTS,
                },
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertFalse(
                check_named(checks(run_dir), "No superseded JSON claim remains in active instructions.")["passed"]
            )

    def test_resume_plan_rejects_current_instructions_to_repeat_completed_implementation(self):
        for instruction in (
            "Add a CLI test that runs `python3 src/report_cli.py --limit 2` and expects `count=2 total=18`.",
            "Add only the minimal argument parsing and row selection needed to pass that test.",
            "Implement `--limit` parsing in `src/report_cli.py`, then run the suite.",
        ):
            plan = RESUMED_PLAN.replace(
                "Both code checkpoints are complete. The next action is the documentation milestone; do not repeat the code work.",
                "1. " + instruction + "\n2. Update README examples.",
            )
            with self.subTest(instruction=instruction), tempfile.TemporaryDirectory() as directory:
                result, run_dir = run_with_skill(Path(directory), "resume-stale-plan-two-checkpoints", {
                    "project/ExecPlan.md": plan,
                    "project/ExecPlan-history-2026-09-30.md": HISTORY_ARCHIVE,
                    "project/src/report_cli.py": REPORT_SOURCE,
                    "project/tests/test_cli.py": REPORT_TESTS,
                })
                self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
                self.assertFalse(check_named(checks(run_dir),
                    "Completed implementation work is not left as current Concrete Steps.")["passed"])

    def test_resume_steps_allow_explicitly_completed_or_historical_implementation(self):
        for steps in (
            "1. Completed: add CLI tests for `--limit`.\n2. Update README examples.",
            "1. Add CLI tests for `--limit`. (completed)\n2. Update README examples.",
            "### Completed implementation\n\nAdd CLI tests for `--limit`.\n\n"
            "### Remaining work\n\nUpdate README examples.",
            "### Historical steps\n\nAdd CLI tests for `--limit`.\n\n"
            "### Remaining work\n\nUpdate README examples.",
        ):
            plan = RESUMED_PLAN.replace(
                "Both code checkpoints are complete. The next action is the documentation milestone; do not repeat the code work.",
                steps,
            )
            with self.subTest(steps=steps), tempfile.TemporaryDirectory() as directory:
                result, run_dir = run_with_skill(Path(directory), "resume-stale-plan-two-checkpoints", {
                    "project/ExecPlan.md": plan,
                    "project/ExecPlan-history-2026-09-30.md": HISTORY_ARCHIVE,
                    "project/src/report_cli.py": REPORT_SOURCE,
                    "project/tests/test_cli.py": REPORT_TESTS,
                })
                self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
                self.assertTrue(check_named(checks(run_dir),
                    "Completed implementation work is not left as current Concrete Steps.")["passed"])

    def test_completed_milestone_allows_multiple_completed_progress_entries(self):
        split_plan = RESUMED_PLAN.replace(
            "- [x] (2026-10-07) [milestone-2] Add and verify the optional row limit.",
            "- [x] (2026-10-07) [milestone-2] Add the optional row limit.\n"
            "- [x] (2026-10-07) [milestone-2] Verify limit behavior.",
        )
        with tempfile.TemporaryDirectory() as directory:
            result, run_dir = run_with_skill(Path(directory), "resume-stale-plan-two-checkpoints", {
                "project/ExecPlan.md": split_plan,
                "project/ExecPlan-history-2026-09-30.md": HISTORY_ARCHIVE,
                "project/src/report_cli.py": REPORT_SOURCE,
                "project/tests/test_cli.py": REPORT_TESTS,
            })
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertTrue(check_named(checks(run_dir), "Milestone states match their progress entries.")["passed"])
            self.assertTrue(check_named(checks(run_dir), "Milestones 1 and 2 are complete with matching progress entries.")["passed"])

    def test_open_milestone_keeps_completed_and_remaining_progress_separate(self):
        split_plan = RESUMED_PLAN.replace(
            "- [ ] [milestone-3] Document the command examples.",
            "- [x] (2026-10-07) [milestone-3] Identify command examples.\n"
            "- [ ] [milestone-3] Write the command examples.",
        )
        with tempfile.TemporaryDirectory() as directory:
            result, run_dir = run_with_skill(Path(directory), "resume-stale-plan-two-checkpoints", {
                "project/ExecPlan.md": split_plan,
                "project/ExecPlan-history-2026-09-30.md": HISTORY_ARCHIVE,
                "project/src/report_cli.py": REPORT_SOURCE,
                "project/tests/test_cli.py": REPORT_TESTS,
            })
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertTrue(check_named(checks(run_dir), "Milestone states match their progress entries.")["passed"])
            self.assertTrue(check_named(checks(run_dir), "Milestones 1 and 2 are complete with matching progress entries.")["passed"])

    def test_resume_plan_rejects_a_done_milestone_with_an_unchecked_progress_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            unsynchronized = RESUMED_PLAN.replace(
                "- [x] (2026-10-07) [milestone-2] Add and verify the optional row limit.",
                "- [ ] [milestone-2] Add and verify the optional row limit.",
            )
            result, run_dir = run_with_skill(
                Path(directory),
                "resume-stale-plan-two-checkpoints",
                {
                    "project/ExecPlan.md": unsynchronized,
                    "project/ExecPlan-history-2026-09-30.md": HISTORY_ARCHIVE,
                    "project/src/report_cli.py": REPORT_SOURCE,
                    "project/tests/test_cli.py": REPORT_TESTS,
                },
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertFalse(
                check_named(
                    checks(run_dir), "Milestones 1 and 2 are complete with matching progress entries."
                )["passed"]
            )

    def test_historical_pointer_requires_a_real_archive_with_unique_evidence(self):
        for archive in (None, "# Historical record\nAn archive without the source date or result.\n"):
            with self.subTest(archive_exists=archive is not None), tempfile.TemporaryDirectory() as directory:
                outputs = {
                    "project/ExecPlan.md": RESUMED_PLAN,
                    "project/src/report_cli.py": REPORT_SOURCE,
                    "project/tests/test_cli.py": REPORT_TESTS,
                }
                if archive is not None:
                    outputs["project/ExecPlan-history-2026-09-30.md"] = archive
                result, run_dir = run_with_skill(
                    Path(directory), "resume-stale-plan-two-checkpoints", outputs
                )
                self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
                self.assertFalse(
                    check_named(
                        checks(run_dir),
                        "The linked historical archive exists and preserves the unique dated test evidence.",
                    )["passed"]
                )

    def test_owner_recovery_limits_must_remain_active_after_code_completion(self):
        with tempfile.TemporaryDirectory() as directory:
            result, run_dir = run_with_skill(
                Path(directory), "preserve-owner-recovery-after-code", {}
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            items = checks(run_dir)
            self.assertFalse(
                check_named(items, "Owner-action limits are stated in active plan sections.")["passed"]
            )
            self.assertFalse(
                check_named(items, "Recovery instructions remain in the active plan with the owner-only command.")["passed"]
            )

    def test_owner_recovery_plan_keeps_pending_action_and_unchanged_passing_code(self):
        with tempfile.TemporaryDirectory() as directory:
            source = SKILL_DIR / "evals" / "files" / "preserve-recovery" / "project"
            outputs = {"project/ExecPlan.md": RECOVERY_PLAN}
            for path in source.rglob("*"):
                if path.is_file() and path.name != "ExecPlan.md":
                    outputs[f"project/{path.relative_to(source).as_posix()}"] = path.read_text(encoding="utf-8")
            result, actual_run = run_with_skill(
                Path(directory), "preserve-owner-recovery-after-code", outputs
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            items = checks(actual_run)
            self.assertTrue(
                check_named(items, "Owner-action limits are stated in active plan sections.")["passed"]
            )
            self.assertTrue(
                check_named(items, "Recovery instructions remain in the active plan with the owner-only command.")["passed"]
            )
            self.assertTrue(
                check_named(items, "External owner approval and staged validation remain pending.")["passed"]
            )
            grading = json.loads((actual_run / "grading.json").read_text(encoding="utf-8"))
            self.assertEqual(grading["summary"]["failed"], 0, grading)

    def test_owner_rule_in_history_does_not_satisfy_active_authorization(self):
        with tempfile.TemporaryDirectory() as directory:
            source = SKILL_DIR / "evals" / "files" / "preserve-recovery" / "project"
            archived_only = RECOVERY_PLAN.replace(
                "Only the release owner may run `python3 src/guardian.py rollback --snapshot <snapshot-path> --target <target-path>` after approval. ",
                "The release owner may run the recovery command after approval. ",
            )
            archived_only = archived_only.replace(
                "The release owner must approve and arrange validation; the device owner must report the result. This action is pending, and the agent is not authorized to complete it.",
                "The release action is pending.",
            )
            active, history = archived_only.split("## Historical Run Records", 1)
            active = active.replace("release owner", "operator").replace("release-owner", "operator")
            active = active.replace("device owner", "operator").replace("owner-only", "unrestricted")
            active = active.replace("The agent has no production signing key or deployment authority.", "")
            active = active.replace("The agent must not execute rollback, rotate a production key, deploy, or contact the owner.", "")
            archived_only = active + "## Historical Run Records" + history
            archived_only += "\nHistorical detail: Only the release owner may run rollback; the agent is not authorized.\n"
            outputs = {"project/ExecPlan.md": archived_only}
            for path in source.rglob("*"):
                if path.is_file() and path.name != "ExecPlan.md":
                    outputs[f"project/{path.relative_to(source).as_posix()}"] = path.read_text(encoding="utf-8")
            result, run_dir = run_with_skill(
                Path(directory), "preserve-owner-recovery-after-code", outputs
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertFalse(
                check_named(checks(run_dir), "Owner-action limits are stated in active plan sections.")["passed"]
            )

    def test_owner_limits_can_be_inline_without_a_specialized_owner_heading(self):
        plan = RECOVERY_PLAN.replace(
            "## Release Owner Action\n\n"
            "The release owner must approve and arrange validation; the device owner must report the result. "
            "This action is pending, and the agent is not authorized to complete it.\n\n",
            "",
        )
        with tempfile.TemporaryDirectory() as directory:
            result, run_dir = run_with_skill(Path(directory), "preserve-owner-recovery-after-code", {
                "project/ExecPlan.md": plan,
            })
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertTrue(check_named(checks(run_dir),
                "Owner-action limits are stated in active plan sections.")["passed"])

    def test_standard_recovery_section_accepts_equivalent_failure_trigger_and_agent_limit(self):
        plan = RECOVERY_PLAN.replace("## Recovery and Authorization", "## Idempotence and Recovery")
        plan = plan.replace("If staged validation fails", "The recovery trigger is a failed staged device validation")
        plan = plan.replace("The agent must not execute rollback", "The agent performing this plan must not execute rollback")
        with tempfile.TemporaryDirectory() as directory:
            result, run_dir = run_with_skill(Path(directory), "preserve-owner-recovery-after-code", {
                "project/ExecPlan.md": plan,
            })
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertTrue(check_named(checks(run_dir),
                "Recovery instructions remain in the active plan with the owner-only command.")["passed"])

    def test_recovery_validation_accepts_explicit_no_external_run_wording(self):
        plan = RECOVERY_PLAN.replace(
            "Local tests pass. Release owner approval and external device owner validation are pending and have not been performed.",
            "Local tests pass. Release acceptance remains pending until the release owner records approval "
            "and the device owner records the staged result. No staged or other external validation has been run here.",
        )
        with tempfile.TemporaryDirectory() as directory:
            result, run_dir = run_with_skill(Path(directory), "preserve-owner-recovery-after-code", {
                "project/ExecPlan.md": plan,
            })
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertTrue(check_named(checks(run_dir),
                "External owner approval and staged validation remain pending.")["passed"])

    def test_recovery_outcomes_can_name_completed_snapshot_and_restore(self):
        plan = RECOVERY_PLAN.replace(
            "Code is complete. Release is pending owner approval and external validation.",
            "Snapshot and restore are implemented. The local test passed. "
            "Release-owner approval and staged device validation remain pending.",
        )
        with tempfile.TemporaryDirectory() as directory:
            result, run_dir = run_with_skill(Path(directory), "preserve-owner-recovery-after-code", {
                "project/ExecPlan.md": plan,
            })
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertTrue(check_named(checks(run_dir),
                "The plan records completed code without claiming release completion.")["passed"])

    def test_current_agent_permission_cannot_be_masked_by_an_owner_only_rule_elsewhere(self):
        plan = RECOVERY_PLAN.replace(
            "The code is complete. The release owner must arrange the staged validation;",
            "The agent may execute rollback after approval. The release owner must arrange the staged validation;",
        )
        with tempfile.TemporaryDirectory() as directory:
            result, run_dir = run_with_skill(Path(directory), "preserve-owner-recovery-after-code", {
                "project/ExecPlan.md": plan,
            })
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertFalse(check_named(checks(run_dir),
                "Recovery instructions remain in the active plan with the owner-only command.")["passed"])

    def test_recovery_command_trigger_retention_and_owner_limit_cannot_exist_only_in_history(self):
        removals = (
            ("src/guardian.py rollback --snapshot <snapshot-path> --target <target-path>", "the documented command"),
            ("If staged validation fails", "If a local test fails"),
            ("30 days", "one day"),
            ("Only the release owner may run", "Any operator may run"),
            ("after approval", "at any time"),
        )
        for original, replacement in removals:
            active, history = RECOVERY_PLAN.split("## Historical Run Records", 1)
            plan = active.replace(original, replacement)
            if original == "after approval":
                plan = plan.replace("approval", "a note").replace("approve", "write a note")
            plan += "## Historical Run Records" + history + "\n" + original + "\n"
            with self.subTest(boundary=original), tempfile.TemporaryDirectory() as directory:
                result, run_dir = run_with_skill(Path(directory), "preserve-owner-recovery-after-code", {
                    "project/ExecPlan.md": plan,
                })
                self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
                self.assertFalse(check_named(checks(run_dir),
                    "Recovery instructions remain in the active plan with the owner-only command.")["passed"])

    def test_create_plan_rejects_wrong_or_noninteger_json_field_values(self):
        for wrong_output in ('{"count": 3, "total": 99}', '{"count": 3.0, "total": 31}', '{"count": "3", "total": 31}'):
            plan = CREATE_PLAN.replace('{"count": 3, "total": 31}', wrong_output)
            with self.subTest(output=wrong_output), tempfile.TemporaryDirectory() as directory:
                result, run_dir = run_with_skill(Path(directory), "create-self-contained-plan", {"ExecPlan.md": plan})
                self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
                self.assertFalse(check_named(checks(run_dir),
                    "Acceptance gives exact text and JSON outputs and preserves the default.")["passed"])

    def test_resume_plan_rejects_correct_limit_outputs_kept_only_in_history(self):
        plan = RESUMED_PLAN.replace('{"count": 2, "total": 18}', '{"count": 2, "total": 99}')
        plan += '\nThe earlier command returned {"count": 2, "total": 18}.\n'
        with tempfile.TemporaryDirectory() as directory:
            result, run_dir = run_with_skill(Path(directory), "resume-stale-plan-two-checkpoints", {
                "project/ExecPlan.md": plan,
                "project/ExecPlan-history-2026-09-30.md": HISTORY_ARCHIVE,
                "project/src/report_cli.py": REPORT_SOURCE,
                "project/tests/test_cli.py": REPORT_TESTS,
            })
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertFalse(check_named(checks(run_dir),
                "The active acceptance records the verified JSON and row-limit outcomes.")["passed"])


if __name__ == "__main__":
    unittest.main()
