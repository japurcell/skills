# Harden evaluation, delegation, and review workflows

## Purpose / Big Picture

Make skill authoring/evaluation, delegation, code review, and retrospectives safer and easier to verify. Success is observable through an isolated fake-provider runner, evidence-bounded grading, a persistent scheduler, review and retro instructions tied to verifiable source/session boundaries, and passing deterministic public-CLI checks. No CI changes, commits, or model/provider evaluations are part of this work.

## Progress

- [x] (2026-11-11) [milestone-1] Preserve the original skill snapshots and source HEAD.
- [x] (2026-11-12) [milestone-1] T1: Add the isolated provider runner and commit-evidence containment checks.
- [x] (2026-11-12) [milestone-2] T2: Add a persistent delegation scheduler with bounded deadlines and host-action events.
- [x] (2026-11-12) [milestone-3] T3: Bind review and retrospective reports to explicit source/session coverage.
- [x] (2026-11-12) [milestone-4] T5: Resolve first-cycle integration findings and add public-CLI acceptance coverage.
- [x] (2026-11-12) [milestone-5] T4: Review the integrated snapshot, confirm acceptance evidence, and archive this plan.

## Surprises & Discoveries

- T1 first reproduced grader acceptance of an external file reached through a run-root symlink. The corrected grader rejects both direct and symlink escapes.
- T2's initial late-checkpoint reproduction at tick 500 emitted only `progress_reminder`; the corrected scheduler test suite passes its deadline, expiry, numeric validation, and CLI contract cases.
- The first integrated review found gaps in Copilot permission scope, adopted-root privacy, empty grading input, and platform support. T5 addressed them; cycle-two reviews report no outstanding substantive findings.
- The source HEAD advanced concurrently from `c61a71d9e1661e24e60401e02bf2b1e889022712` to `565214e3975a24488cf599f7d98bccd296e333fc`. That commit changes only the reflect skill description in `.agents/skills/reflect/SKILL.md` and its brain-install template. It is preserved and is not part of this task's uncommitted work.

## Decision Log

- 2026-11-11: Keep the generic provider runner in create-skill, commit-specific evidence checks in commit/evals, scheduling in delegate-to-subagents, and review/retro judgment rules in their owning skills.
- 2026-11-11: Do not run skill/model evaluations. Use fake providers, deterministic public-CLI tests, static validation, and reviews; real provider behavior remains unverified.
- 2026-11-12: Operational CLI entrypoints need useful help, noninteractive input/output and exit contracts, distinct stdout results and stderr diagnostics, and clean cancellation/broken-pipe behavior. Focused public-CLI tests enforce this.
- 2026-11-12: No extra brain note is needed for CLI steering: create-skill guidance now specifies the CLI contract, and deterministic tests enforce it. T3 review/retro source changes were explicitly authorized despite the importer overwrite caveat.
- 2026-11-12: Leave all task changes uncommitted and do not edit CI or workflows.

## Outcomes & Retrospective

All five workstreams are complete. The final deterministic public-CLI suites passed 72 tests total: runner 17, grader 30, validator 14, scheduler 11. Python compilation, changed-skill quick validation, and `git diff --check` passed. The cycle-two spec review found no new substantive issues; the standards review approved with no findings above its confidence threshold. The cycle-two snapshot manifest matches all 48 current source file hashes. No model or provider evaluations, CI changes, or task commits occurred. The task changes remain uncommitted; the concurrent reflect-only commit at HEAD is preserved. The runner documents macOS/Linux support; Windows runtime and locking behavior remain unverified.

## Context and Orientation

Published skill sources are under `skills/default/`. T1 owns the create-skill provider runner and commit/evals grading boundary. T2 owns the delegate-to-subagents scheduler. T3 owns code-review-biaxis and retro guidance. T5 resolved findings from review cycle one. T4 owns integrated acceptance and review cycle two. The source snapshots, test logs, and reviews are retained at `/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/skill-hardening-vi0ujfj3/`; its original skill copies are under `old_skill/`.

## Plan of Work

### Milestone 1: Isolated evaluation tooling and evidence containment
Status: done
Acceptance: met

T1 added a standard-library CLI runner, fake-provider public-CLI tests, provider preflight and session continuity, isolated/private run roots, adopted commit-fixture support, and grader path-containment checks. Final evidence in `evidence/t5/t5-final-runner.log`, `t5-final-grader.log`, and `t5-final-validator.log` records 17 runner, 30 grader, and 14 validator tests passing. `evidence/t1/runner-and-containment.md` retains the initial symlink-escape reproduction and earlier validation details. `py_compile`, skill quick validation, and `git diff --check` passed. No real provider was invoked.

### Milestone 2: Persistent delegation scheduler
Status: done
Acceptance: met

T2 added persistent scheduler state, JSON events, bounded waits/deadlines, one extension, reminders, cancellation/completion, and host-action boundaries. `evidence/t2/RESULTS.md` records the initial late-checkpoint failure and corrected 11-test public-CLI pass, plus compilation, quick validation, and diff checks. Windows locking is unverified.

### Milestone 3: Evidence-bound reviews and scoped retrospectives
Status: done
Acceptance: met

T3 updated `skills/default/code-review-biaxis/SKILL.md` to pin full base/target commit IDs, capture complete committed or dirty source snapshots including relevant untracked files, avoid staged-diff duplication, bind failures to the captured source, label historical evidence, and keep static race hypotheses distinct from observed event traces. `skills/default/retro/SKILL.md` now records the root session, verifies descendants and source coverage, marks inaccessible or compacted history, excludes unrelated sessions, and distinguishes current-tree checks from historical observations. Both skills passed quick validation; `git diff --check` passed.

### Milestone 4: First-cycle integration fixes
Status: done
Acceptance: met

T5 addressed review-cycle-one findings with targeted tests: scoped Copilot tool grants and preflight, private adopted fixture roots, empty-iteration grading errors, and documented macOS/Linux runner support with descendant cleanup. Final CLI-contract logs record 17 runner and 30 grader tests passing. The runner test suite also covered SIGINT cleanup, closed stdout, and help/error behavior. Windows runtime is not claimed.

### Milestone 5: Integrated acceptance and review
Status: done
Acceptance: met

T4 reviewed the integrated cycle-two snapshot at `565214e3975a24488cf599f7d98bccd296e333fc`. The cycle-two manifest in `review-2/manifest.json` matches 48 of 48 current source hashes. `spec-review-2.md` reports no new substantive findings; `review-2/standards-review-2.md` approves with no critical, important, or confidence-qualified suggestion findings. Current changed paths include no workflow files. All task files remain uncommitted. The external reflect-only HEAD commit is preserved.

## Validation and Acceptance

Observed final public-CLI results from the retained evidence are runner 17/17, grader 30/30, validator 14/14, and scheduler 11/11. Compilation, quick validation for changed skill bundles, and `git diff --check` passed. Independent cycle-two spec and standards reviews are retained at the artifact root. The review manifest hash check found 48 files verified and zero mismatches. No tests were rerun during closure because no source changes followed the recorded passing runs. No skill/model evaluations, real provider executions, CI runs, or task commits occurred. No `.github/workflows/` paths appear in the current task diff/status.

## Idempotence and Recovery

All original source snapshots and verification artifacts remain in the shared temporary artifact root for audit. Do not reset or revert concurrent changes. If later source edits occur, capture a new complete snapshot and rerun only affected checks; prior evidence applies to its recorded snapshot. The task diff remains uncommitted by instruction.

## Interfaces and Dependencies

The runner and scheduler use Python's standard library and fake provider CLIs in deterministic tests. Real provider executables are only used when a future user invokes an evaluation. The scheduler emits actions for its host and does not terminate or message agents itself. The cycle-two review is tied to its pinned source snapshot and manifest rather than a moving ref.
