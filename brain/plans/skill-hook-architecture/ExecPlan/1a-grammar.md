# T1a, grammar parity

The commit-skill maintainer starts on the integration branch with the accepted default grammar below. Use the wrapped-bullet case in `skills/default/commit/evals/test_validate_message.py` to drive the same drafts through validator and benchmark grader. Replace the separate grammar in `has_commit_message_shape` with a call into the bundled validator resolved relative to the skill. Have the parser return the header, parsed sections and ordered trailer entries. Keep the existing `validate` and CLI error behavior for callers. Stop after single-line, wrapped and empty bullets give the expected three verdicts on both paths.

The commit-skill implementer owns the validator, dry-run grader and focused tests. The approved grammar and public cases are in the milestone. From the checkout root run `rtk proxy python3 skills/default/commit/evals/test_validate_message.py` and `rtk proxy python3 skills/default/commit/evals/test_grade_benchmark.py`. Record both exit codes, the before/after grader assertion and the tested commit.

Use the [milestone contract and verification commands](1-commit-validation.md) and the [integration plan](../ExecPlan.md). Record results and remaining evidence here.
