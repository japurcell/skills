# Qualification review pass 1

Review target `294a741602fb08822fb3d604de67dd1a1ec56cc3`. Base and merge-base `df54c117e8b8bccc46420d87ae6e3671c6c14ae1`. Integrated B source `f79e560b39778ac96b236a8e1858d3348c048586`.

Standards reports zero findings and approves its axis. Spec reports one Important / P2 finding and requests changes. T4-Q1-R1 is assigned to `/root/observed_qualification` in `/private/tmp/skills-scheduler-observed-qualification`. The current reproduced failure accepts a lexical `..` patch target despite the traversal prohibition. M2 and source acceptance remain incomplete pending correction and fresh independent review.

The source diff SHA-256 is `5dce40e69ba3a7722e51aff4f7696bae42c63099c3cc0f477084292d257b6fb2`. The full diff SHA-256 is `ebf15cbb2d0737bfaf89ae7d697e8dbeceeffee18803eac1a8803d2320ddbc6a`. Both axes below preserve the reviewers' findings and verification limits with heading levels adjusted for this combined report.

The Spec reproduction command uses `<E>` for `/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification`.

## Retained inputs and originals

- [Frozen review metadata](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification/review-input.json)
- [Scoped source diff](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification/source.diff)
- [Full diff](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification/full.diff)
- [Frozen specification](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification/spec.md)
- [Standards original](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification/standards.md)
- [Spec original](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification/spec-review.md)
- [Traversal reproduction driver](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification/spec-traversal-repro.py)
- [Traversal reproduction output](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification/spec-traversal-repro.json)
- [Traversal public command receipt](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification/spec-traversal-command.json)
- [Traversal native-shaped records](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification/spec-traversal-native.jsonl)

## Standards

### Scope and verdict

APPROVE for the Standards axis. Zero Critical or Important findings and zero actionable heuristic advisories met the confidence threshold.

Reviewed `df54c117e8b8bccc46420d87ae6e3671c6c14ae1...294a741602fb08822fb3d604de67dd1a1ec56cc3`, with the base also the merge-base. Target and inspected HEAD matched `294a741602fb08822fb3d604de67dd1a1ec56cc3`. All three source SHA-256 values and all five supplied artifact hashes matched `review-input.json`.

### Per-file assessment

- `scheduler_pilot.py`, preparation/discovery/native parsing/phase validation/run/grading hunks. No confirmed documented breach. Uses stdlib, bounded discovery with named process cleanup, exclusive phase attempts, atomic final receipts and raw-evidence revalidation. Missing native capabilities remain explicit invalid evidence. Examined the new validation flow against the supplied smell baseline. Its responsibilities form one qualification boundary, and no named smell justified a finding.
- `test_scheduler_pilot.py`, fixture and qualification hunks. No confirmed breach. Public CLI fixtures execute actual helpers and scheduler operations, preserve malformed-event negatives and assert individual rubric observations despite invalid setup. This follows `brain/codebase/script-testing.md`, “Fixtures that must remain meaningful,” and `brain/codebase/testing.md`, “Preserve failing cases and evidence.”
- `evals/README.md`, observed-run qualification section. No new documented-standard violation. Documents selectors, private configuration, replay controls, supported native envelopes and diagnostic limits, consistent with `brain/codebase/scripts-and-installers.md` CLI/evidence rules.

### Verification and limits

Tests reviewed first. Retained worker evidence reports 33 tests in 128.223 seconds plus two strengthened tests in 5.907 seconds. Those tests were not rerun. Read the frozen diff, log, metadata and current contract independently of the Spec report. No source changes were made.

Bounded public CLI help checks used `rtk proxy python3 skills/default/delegate-to-subagents/evals/scheduler_pilot.py [prepare|preflight|run|grade] --help`, including the root form. All five exited 0, with usage output and empty stderr. Each subprocess had a ten-second bound. Environment was macOS with Python 3.14.6.

Static source review covered error handling and evidence boundaries. Build, aggregate tests and native/model execution were unverified. No failure claim or native qualification is inferred from this review. Applicable sources were repository AGENTS.md, the three supplied brain standards, owning eval README, and code-review/brain/create-skill guidance.

## Spec

Verdict REQUEST CHANGES

Reviewed `df54c117e8b8bccc46420d87ae6e3671c6c14ae1...294a741602fb08822fb3d604de67dd1a1ec56cc3`, merge-base equal to base. All three source hashes match `review-input.json`. Authority is frozen `spec.md`, particularly Current observed-run acceptance and T4-Q1.

### Implemented wrongly

- Important / P2, confidence 100. `skills/default/delegate-to-subagents/evals/scheduler_pilot.py:696` accepts traversal in Copilot Add File targets. Current T4-Q1-B requires “Reject extra targets, traversal, linked paths, unsupported headers, updates, deletes and moves.” The implementation resolves containment without rejecting `..` segments. A supported offline provider emitting `*** Add File: outputs/../outputs/extend-103.json` and corresponding completion paths qualifies. Both public smoke calls, scenario run and grade exit 0. Grade reports `setup_status=valid`, `behavior_status=pass`, `comparison_eligible=true`, with no invalid reasons. Reject absolute/non-outputs targets and lexical `..` components before filesystem resolution, then retain the physical confinement/readback checks. Add a focused public-CLI traversal negative.

Reproduction uses existing fake Copilot transport and actual immutable scheduler/helper children. Exact public argv, synthetic-token environment description, exit codes and observed output are retained in `spec-traversal-repro.json` and `spec-traversal-command.json`. `spec-traversal-native.jsonl` retains native-shaped records. Run `rtk proxy python3 <E>/spec-traversal-repro.py` from the repository root to reproduce. The driver prepares its changed fake executable before manifest pinning.

### Missing or partial requirements

No additional findings.

### Unasked behavior

No findings.

### Verification and limits

Tests reviewed first, including original semantic per-claim negatives and qualification fixtures. Source inspection covers the three scoped files. Separate setup/phase identities, provider-wide both-smoke gates, replay protection and raw revalidation are present. Original semantic assertions remain independently observable under invalid Codex setup. Codex unsupported telemetry stays invalid.

Retained worker evidence records 33 passing tests and two strengthened checks. This review ran only the bounded offline traversal reproduction. No aggregate suite, build, native/model call, authentication or trust changes occurred. Synthetic transport establishes the adapter failure only. No Standards report was inspected.
