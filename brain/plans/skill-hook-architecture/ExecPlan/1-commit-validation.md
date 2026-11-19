# M1. Commit message validation

Status: open
Acceptance: not met

## Assignment

T1 belongs to the milestone implementer. Work from the repository root on a branch based on the committed plan. The committed plan is the only prerequisite. Reproduce any defect through the caller before editing. Stop when the behavior below is delivered, checks are recorded and any native evidence gap is named.

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

- [ ] [milestone-1] Implement T1 and exercise the public entry points.
- [ ] [milestone-1] Verify integrated behavior and record platform evidence.
