# M1. Commit message validation

Status: in progress
Acceptance: not met

## Tasks and prerequisites

**T1a, grammar parity.** The commit-skill maintainer starts on the integration branch with the accepted default grammar below. Use the wrapped-bullet case in `skills/default/commit/evals/test_validate_message.py` to drive the same drafts through validator and benchmark grader. Replace the separate grammar in `has_commit_message_shape` with a call into the bundled validator resolved relative to the skill. Have the parser return the header, parsed sections and ordered trailer entries. Keep the existing `validate` and CLI error behavior for callers. Stop after single-line, wrapped and empty bullets give the expected three verdicts on both paths. [Assignment](1a-grammar.md)

**T1b, intent and attribution.** After T1a gives the grader real trailer entries, update `eval_one` or the applicable scenario handler, `skills/default/commit/evals/evals.json`, fixture input and public grader tests together. Compare trailer entries with the scenario's independently specified issues and authors. Test unauthorized PR closure even when the PR also contains a neutral reference. Stop after the two intent cases and existing live Git workflow checks pass together. [Assignment](1b-intent.md)

## Source and interfaces

- `skills/default/commit/scripts/validate_message.py`
- `skills/default/commit/evals/grade_benchmark.py`
- `skills/default/commit/evals/files/staged-bugfix-pr/input.json`

## Ownership

The bundled commit validator owns default grammar. The dry-run grader uses the same parser for the subject, body and trailer block. It derives issue and author expectations from the scenario inputs and compares actual trailer entries in order. It independently checks the reported subject against the message header, issue intent, contributor, selected files and requested Git actions. Repository-specific conventions retain their current precedence. The live-workflow grader continues to require original validation events and actual Git readback.

## Correct the fixture

A PR “for issue 456” expects Refs #456 in the commit trailer and a neutral issue reference in the PR body. Give the explicit-closing case its own request, --fixes 456 authorization, Fixes #456 trailer and matching PR expectation. Align fixture prompts, expected outputs, assertions and grader. Words in body prose cannot satisfy a required trailer. A PR with an unauthorized closing directive fails even when it also contains a neutral reference.

## Acceptance

Run both public CLIs on the same single-line, wrapped and empty Summary drafts. Expect pass, pass and fail on the format assertion. Test reference-only and explicit-close scenarios, a closing phrase confined to a Summary bullet with the trailer missing, and a wrong or extra contributor. Preserve independent expected outcomes and existing Git workflow checks.

## Verification

Run from the checkout root. Each command must exit zero. Inspect the files or output specified above.

- `rtk proxy python3 skills/default/commit/evals/test_validate_message.py`
- `rtk proxy python3 skills/default/commit/evals/test_grade_benchmark.py`

## Progress

- [x] (2026-11-19) [milestone-1] T1a passed both integrated suites at `059166bf`.
- [ ] [milestone-1] Complete T1b and run both suites together.
