# M7. Project conversation batches

Status: done
Acceptance: met

## Assignment

T7 belongs to the milestone implementer. Work from the repository root on a branch based on the committed plan. The committed plan is the only prerequisite. Reproduce any defect through the caller before editing. Stop when the behavior below is delivered, checks are recorded and any native evidence gap is named.

## Source and interfaces

- `skills/default/brain-install/assets/skills/ruminate/scripts/extract-conversations.py`
- `skills/default/brain-install/tests/test_skill_workflows.py`
- `skills/default/brain-install/assets/skills/ruminate/SKILL.md`
- `.agents/skills/ruminate/SKILL.md`

## Mode and compatibility

An explicit project mode takes the working directory and discovers available Claude, Codex and Copilot sources using their existing allowed roots. Explicit source selections restrict the run to the supplied roots. Retain each provider’s validation, directory/file protections, attribution and existing filters. A missing default root is skipped. An invalid explicitly requested root is an error. Only matching, attributed conversations with usable content enter the count. Explicit-source legacy invocations retain existing defaults (five requested batches), layout, grouping and output-directory-only stdout.

## Exact sizing

Let N be the post-filter count. For zero conversations emit zero manifests. Otherwise choose K = min(N, 10, max(2, ceil(N / 20))) unless the user supplied a positive batch count B, in which case K = min(N, B). Preserve extraction order. Divide N by K, giving each batch the quotient and the first remainder batches one more. Every accepted conversation occurs once and every requested attainable group is nonempty. Six into four yields sizes 2, 2, 1, 1.

## Installed caller

Update the portable Ruminate instructions and their repository-local copy together. The normal skill invocation passes the current project to project mode, omitting provider roots and the batch count unless the user supplies overrides. On success it dispatches one analysis assignment per manifest path from the JSON result, using each path verbatim. An empty list ends extraction without dispatch. A failed invocation cannot start analysis from leftover artifacts. In a relocated bundle workflow check, exercise the documented invocation on synthetic histories. Seed a plausible stale manifest, record the worker inputs and assert that they exactly match the returned list and every referenced file exists. Check the zero-match and failure paths produce no worker inputs, and retain the existing bundle parity check.

## Publication and acceptance

For project mode, write each invocation’s extracts and manifests into its own new private run directory beneath the approved output workspace. Emit a single JSON success result with the accepted count and ordered absolute manifest paths only after all writes succeed. On failure emit no success result. Keep diagnostics on stderr. Test 0, 1, 2, 41 and 250 accepted with automatic sizing, 6 with override 4, and 4 with override 20. Mix unrelated and missing working directories into fixtures. Repeat and overlap project runs under the same output location and verify each result continues to name only its run’s complete files. Exercise the legacy interface separately.

## Verification

Run from the checkout root. Each command must exit zero. Inspect the files or output specified above.

- `rtk proxy python3 -m unittest discover -s skills/default/brain-install/tests`
- `rtk proxy python3 scripts/validate-skill-sources.py skills`

## Progress

- [x] (2026-11-19) [milestone-7] Implemented project discovery, exact batches, private run directories and JSON publication. Preserved the explicit-source interface and synchronized both Ruminate copies.
- [x] (2026-11-19) [milestone-7] Exercised the documented caller from a relocated skill and ran the full brain-install bundle suite on macOS arm64 with Python 3.14.6.

## Results

The synthetic baseline produced three legacy manifests for six conversations and four requested batches. The new `--project PATH` invocation produced four manifests with sizes 2, 2, 1 and 1. The suite also checked automatic sizing at 0, 1, 2, 41 and 250, an override above the accepted count, filtered attribution, all three providers and invalid explicit roots.

The relocated caller printed exactly the paths published in the extractor’s JSON. A stale manifest produced no assignment, and empty and failed invocations printed no worker inputs. Four runs sharing one output location, including three launched concurrently, kept separate complete files. An imposed file-size limit made an actual output write fail with no success result.

Both verification commands above exited zero. The bundle suite ran 55 tests with four existing Windows ACL checks skipped on macOS. Byte comparisons matched the portable and repository-local script and skill. The dispatch fixture recorded worker inputs from synthetic histories. Native Windows ACL behavior and live host dispatch were not exercised.
