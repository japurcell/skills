# Retain complete ablation runner transcripts

This living ExecPlan is `brain/plans/ablation-full-transcripts-exec-plan.md`. Follow the repository-local exec-plans skill and its annotated outline. Parent `/root` owns execplan-implement orchestration; persistent integration coordinator `/root/integration` owns integration and this plan. Read current source before dispatching. This plan authorizes harness repair and offline verification only; the separately approved experiment has its own execution gate.

## Purpose / Big Picture

An ablation user must be able to read every byte emitted by each runner after its disposable worktree is removed, including a final answer after a long Codex JSONL transcript. Keep complete stdout and stderr as durable per-run files under the result directory and keep `summary.json` small, compatible, and explicit about previews. Preserve evidence on nonzero exit, malformed output, timeout, and cancellation. Preserve the existing verified process-group shutdown before worktree removal. A public fake-runner experiment must reproduce the present capture failure before any implementation edit.

Scope is the canonical `skills/default/ablate-ai-layer/` bundle, focused tests and documentation, this plan, and a durable lesson if warranted. Installed skills are not source. No paid model calls, installation, experiment feature implementation, user rule edits, or unrelated cleanup belong to repair tasks. The user explicitly permits inspecting and fixing scripts despite the runtime skill's source-reading restriction.

## Progress

- [x] (2026-11-17) [milestone-0] Inspect canonical source, current tests, pilot evidence, and approved experiment records; select interfaces and bounded ownership.
- [ ] [milestone-0] T0: Commit this plan on the integration branch before implementation.
- [ ] [milestone-1] T1: Reproduce loss through the public CLI with a fake runner and retain failing evidence before code edits.
- [ ] [milestone-1] T1: Implement durable raw streams and focused public CLI coverage in one worker worktree; verify its complete contract.
- [ ] [milestone-1] T2: Update capture gate, full-stream grading guidance, and schema documentation in an independent worker worktree.
- [ ] [milestone-2] T3: Integrate workers and verify the combined CLI, schema, shutdown, cleanup, and documentation contract.
- [ ] [milestone-3] T4: Run independent Standards and Spec reviews against the fixed repair baseline; repair and reverify findings in at most three review rounds.
- [ ] [milestone-3] T5: Reflect, persist durable guidance if needed, verify navigation, and remove this plan only after zero unresolved findings.

## Surprises & Discoveries

- `run_agent` currently streams into anonymous temporary text files, then returns decoded contents only on normal completion. `run_one` slices `result_text` at 4,000 characters and `stderr_tail` at 600. Exceptions bypass stream extraction, so timeout and cancellation lose their streams entirely.
- The pilot had two successful nonempty diffs, but both result previews stop at exactly 4,000 characters mid-JSONL. `/tmp/skills-ablation-coordination/pilot-gate-report.md` records the failed capture gate. That is a harness failure, not an arm finding.
- `run_one` already stages `git add -A` against a setup tree, so new/untracked files enter its diff and `files_changed`. Preserve and test that behavior rather than adding an unrelated file-manifest subsystem.
- `stop_group` verifies group disappearance even when its leader exits; `ShutdownUnconfirmed` retains the worktree. Raw capture changes must preserve this ownership boundary.
- Initial branch creation required normal Git metadata escalation because `.git` is outside writable scope; escalation succeeded. Main checkout started clean at `fd6059d37881dab58109cf1cff1429ad54ce9592`.

## Decision Log

- 2026-11-17, integration coordinator: Store binary stdout/stderr directly at resolved `--out` paths named `control-1.stdout`, `control-1.stderr`, and equivalents. Open these files before runner launch and leave them intact after every outcome. `--out` is never a disposable runner worktree. Existing result paths may be reused only deliberately; do not overwrite historical pilot output. Retaining bytes is the contract; parsing is optional convenience.
- 2026-11-17, integration coordinator: Keep `result_text` at at most 4,000 decoded characters and `stderr_tail` at at most 600. Add `stdout_path`, `stderr_path` (absolute strings), `stdout_bytes`, `stderr_bytes` (nonnegative integers), `result_text_truncated`, `stderr_tail_truncated` (booleans). A truncation flag describes the corresponding decoded preview, not whether the raw file is complete.
- 2026-11-17, integration coordinator: Preserve Claude JSON dictionary metadata (`is_error`, `result`, `total_cost_usd`, `num_turns`, `usage.output_tokens`) when well typed. For JSONL, malformed/partial JSON, non-dictionary JSON, or unknown text, use a bounded raw stdout preview and exit status; preserve bytes without guessing provider semantics. Invalid UTF-8 may be replaced only in previews. No new JSONL schema parser is necessary to retain and grade full transcripts.
- 2026-11-17, integration coordinator: Add `shutdown_confirmed` (boolean) and `cleanup_status` (`removed`, `retained`, `failed`, or `not_created`). `shutdown_confirmed` means no owned process group remains, including pre-launch failures with no group. Unconfirmed shutdown forces `ok=false`, `cleanup_status=retained`, and `worktree_kept`. Explicit `--keep-worktrees` also yields `retained`; removal errors yield `failed` and the retained path. Avoid claiming cleanup before its actual outcome.
- 2026-11-17, integration coordinator: Keep the probe repository baseline `fd6059d37881dab58109cf1cff1429ad54ce9592` fixed. The repaired harness can later run by absolute path against a temporary detached checkout of that baseline. Do not merge experiment patches into the repair branch or change approved runner configuration.

## Outcomes & Retrospective

Planning source inspection is complete; implementation and acceptance are pending. No model calls or implementation edits occurred during drafting. Current next action is T0 plan commit, then parent dispatches T1/T2. Stop and report unresolved findings after the bounded review process; never delete the plan while a required check or finding is unresolved. Experiment completion is a later parent-owned phase and cannot be claimed from repair tests.

## Context and Orientation

`skills/default/ablate-ai-layer/scripts/run_ablation.py` is a standalone standard-library Python CLI. `main()` creates the result directory, dispatches `run_one()` concurrently, writes per-run diffs and `summary.json`, and returns 0 for a usable comparison, 1 for an unusable experiment, 2 for usage/platform errors, 130 for SIGINT, and 143 for SIGTERM. `run_one()` creates an external detached Git worktree, strips configured instructions, records a setup Git tree, invokes the runner, stages changes, records a diff, and cleans up. `run_agent()` owns a new POSIX session and calls `stop_group()` before cleanup can occur. Cancellation is coordinated through the `CANCELLED` event. `ShutdownUnconfirmed` prevents unsafe removal.

`skills/default/ablate-ai-layer/scripts/test_ablation.py` is the maintained unittest suite. `AblationCliTests.cli()` launches the public scripts, `commit_fixture()` creates disposable commits with fixture identity, and `experiment()` runs one pair with a local fake runner. Existing tests cover nonzero JSON exits, setup stripping, timeout descendants, normal-exit descendants, and SIGTERM cancellation. Extend these seams rather than mocking internal functions for stream retention. `scripts/test-all.py` already registers this suite; registration needs no change.

Runtime instructions live in `skills/default/ablate-ai-layer/SKILL.md`; maintainer contracts live in its `README.md`; blind grading guidance lives in `references/comparison.md`. Relevant reusable guidance is in `brain/codebase/testing.md`, `brain/codebase/script-testing.md`, and `brain/codebase/repository-workflow.md`.

## Plan of Work

### Milestone 0: Establish a committed repair contract

Status: in progress
Acceptance: not met

Task T0 has no prerequisites. Its inputs are inspected source and the failed pilot gate. The integration coordinator creates branch `fix/ablation-full-transcripts` from the clean fixed baseline, commits only this plan and its curated index link, and records branch/base/plan commit in `/tmp/skills-ablation-coordination/harness-fix/readiness.md`. Acceptance is a clean plan-only commit before any source edit. No worker may implement until the parent confirms this checkpoint.

### Milestone 1: Deliver complete durable capture and its usage contract

Status: open
Acceptance: not met

Task T1 requires T0 and a parent dispatch under execplan-implement. One worker owns only `skills/default/ablate-ai-layer/scripts/run_ablation.py` and `scripts/test_ablation.py` within that bundle, in its own worktree. Activate tdd before source design/edits. Reproduce through the public CLI first: a disposable repo with AGENTS.md and a fake runner that creates a new result file, writes more than 4,000 characters to stdout, ends with a unique final marker, and writes stderr. Assert complete files exist and match emitted bytes. Before the fix this must fail because no durable raw files exist; retain the command, exit, and decisive assertion under external harness-fix evidence. This is the red gate, not an expected green test.

Then change `run_agent` to accept explicit stdout/stderr artifact paths, redirect `Popen` into binary durable handles, and return a process exit status rather than whole stream text. Keep prompt delivery, polling, cancellation, and `stop_group` semantics. Pass resolved output directory from `main` into `run_one`; prepare paths before launch. Finalize stream metadata and bounded summaries in `run_one` even when execution raises timeout/cancellation/shutdown errors. Isolate metadata parsing so malformed JSON structure, invalid usage shape, invalid UTF-8, or optional parsing failure cannot lose evidence, skip diff capture for otherwise successful runs, or falsely mark them unusable. `agent_error` continues to include nonzero exit and valid Claude `is_error`. Existing short valid Claude result preview remains compatible.

Public tests must verify byte equality, final markers beyond the preview boundary, exact byte counts and absolute paths outside all runner worktrees, bounded previews and correct flags, both arms, and preserved new files in diffs. Cover large valid Claude JSON with metadata; complete Codex-shaped JSONL; malformed JSON and a partial trailing JSONL record; plain binary output including invalid UTF-8; valid JSON arrays/scalars and malformed optional metadata; nonzero exit; empty streams; and successful worktree cleanup. Extend the existing timeout and SIGTERM cancellation tests to emit flushed output on both streams before waiting and assert durable evidence after shutdown/removal. Verify cancellation before launch has a coherent metadata record if represented. Preserve existing descendant non-survival assertions. Add a public retained-worktree case with `--keep-worktrees`, then clean it safely after assertions. For safety failure behavior, use a public fake runner that exits but leaves a descendant in-group as existing tests do; preserve any existing unconfirmed-shutdown coverage and add an isolated controlled failure fixture if necessary to establish `ok=false` and retention without changing real process policy.

Verification is `rtk proxy python3 skills/default/ablate-ai-layer/scripts/test_ablation.py` from the worker root, plus Python syntax checks listed below. Stop after the focused implementation and all its tests pass, record before/after evidence, and create a scoped commit. No paid runs or installed-copy edits.

Task T2 also requires T0 and may run alongside T1 because it owns only `skills/default/ablate-ai-layer/SKILL.md`, `README.md`, and `references/comparison.md`. Activate create-skill and writing-for-agents for runtime guidance edits. Use the schema in Decision Log as the shared contract. Step 4 must require a one-pair capture gate before remaining runs: full streams accessible and complete, expected final markers or provider terminal events present, usable diffs including new files, and confirmed shutdown/cleanup. Exit 0 or a nonempty diff alone does not pass this gate. On inadequate capture, stop before more spend. Step 5 and comparison guidance must require full raw streams for workflow claims; previews and diffs cannot substantiate unobserved tool outcomes. Preserve blinding and avoid arm-revealing instruction contents in grading copies while retaining originals. README documents artifact schema and binary retention on all outcomes, platform limits, tests, and scope of guarantees. Verify references and quick_validate, then commit only owned files. Stop before integration or model execution.

### Milestone 2: Prove the combined result

Status: open
Acceptance: not met

Task T3 requires T1 and T2. Integration coordinator cherry-picks scoped worker commits into the integration branch, resolves only overlapping contract issues, and runs the focused public suite on the integrated tree. Inspect retained external reproduction evidence and rerun its exact public fake-runner scenario against integrated source. Compare bytes, metadata, final markers, diff new-file behavior, and worktree/process absence after completion. Run quick_validate and syntax checks. Review documentation against actual field names and behavior, including timeout, cancellation, --keep-worktrees, failure diagnostics, and JSON parse fallback. Passing isolated worker tests or a clean merge does not establish this milestone. Record commands, counts, exits, and limitations here.

### Milestone 3: Review, preserve lessons, and close only on clean acceptance

Status: open
Acceptance: not met

Task T4 requires T3. Parent invokes code-review-biaxis with the fixed pre-repair baseline so independent Standards and Spec reviewers assess the integrated final patch. At most three review rounds, with scoped repairs and relevant revalidation after each changed implementation. Findings are not resolved by narrative dismissal without source/evidence. Stop and report any unresolved finding or required check after the limit, leaving this plan current. No ablation model calls until the repair is accepted and the parent explicitly advances experiment execution.

Task T5 requires T4 with zero unresolved findings. Activate reflect at code session wrap-up and brain before any durable note edit. Preserve reusable guidance in an existing indexed note or the bundle's maintainer docs, verify navigation, then remove this completed plan and its link from `brain/plans/index.md`. Commit final acceptance/cleanup through commit skill. Record final branch/base/commit/evidence in the external coordination directory so plan deletion cannot erase the repair audit trail. The parent then owns the remaining ablation, including a replacement capture pilot on the original baseline and stop/go decision before remaining approved runs.

## Concrete Steps

Next unfinished action: integration coordinator completes T0 by committing this plan and its index link using the commit skill, recording the resulting SHA externally, and notifying parent. Parent then dispatches the bounded T1 and T2 tasks with separate worktrees and explicit ownership. Workers are not alone and must preserve others' edits. Parent alone activates execplan-implement; workers activate relevant source/document skills.

From the repository or worker root, focused validation commands are:

    rtk proxy python3 skills/default/ablate-ai-layer/scripts/test_ablation.py
    rtk proxy python3 -m py_compile skills/default/ablate-ai-layer/scripts/run_ablation.py skills/default/ablate-ai-layer/scripts/test_ablation.py
    rtk proxy env PYTHONPATH=scripts/vendor python3 skills/default/skill-creator/scripts/quick_validate.py skills/default/ablate-ai-layer
    rtk git diff --check

Expected results are exit 0, unittest OK, and validator success. Actual results are pending. Aggregate test-all execution is unnecessary for an unchanged registry and isolated bundle; broaden only if integration reveals cross-bundle effects. Offline tests require Python 3, Git, and POSIX process groups. Missing prerequisites are reported as unverified failures, not passing skips.

## Validation and Acceptance

The fix is accepted only if the public red reproducer fails before source edits and passes afterward; every launched run retains byte-identical stdout/stderr in durable files; summary previews and flags are correct and bounded; valid short Claude metadata remains compatible; malformed/unknown streams retain evidence; nonzero, timeout, cancellation, retained worktree, and cleanup paths preserve streams and correct usability; and owned process groups stop before removal. Existing new-file diff capture and stripped setup exclusion must survive. Full stream paths must still exist after all disposable worktrees are removed. Documentation must make the one-pair gate and full-stream grading requirement explicit. Independent review must have zero unresolved findings before plan removal.

The fake tests cannot establish that a particular live Codex session emits all tool outcomes or billing metadata. That remains a replacement live capture gate in the later approved experiment, not a repair acceptance claim. Existing pilot pairs are retained as failed capture evidence and cannot be silently counted as adequately captured experiment runs.

## Idempotence and Recovery

Use fresh external output directories for reproductions and replacement model gates; never overwrite `/tmp/skills-ablation-coordination/results/pilot`. Keep run evidence outside worker and runner worktrees. Normal retries use fresh temporary repos and result paths. If a process group cannot be verified stopped, retain its worktree and raw artifacts, mark unusable, stop dependent model runs, and report exact diagnostic; never remove it just to make tests green. Cleanup-only fixture kills occur after assertions and cannot validate a leaked runner. Revert a repair commit rather than changing the original probe baseline. Do not reset unrelated work or remove unrelated worktrees. Cancellation evidence is retained on orderly SIGINT/SIGTERM; crash/power-loss durability and deliberately detached runner descendants are outside the contract.

## Interfaces and Dependencies

No external library is needed. Resolve `out` once in `main`, pass it to `run_one`, and derive unique arm/index filenames before launching. `run_agent(cmd, use_shell, wt, prompt, timeout, stdout_path, stderr_path)` redirects binary streams and returns the exit status on normal completion; exceptions preserve the opened files and trigger the existing verified shutdown path. `run_one(..., keep, out)` owns record assembly and evidence finalization, including failure paths. Existing `summary.json` top-level keys, diff naming, task.md, and public CLI flags remain compatible. New per-run fields and their exact types/enums are defined in Decision Log. Artifact byte counts are obtained from files after writer shutdown; preview decoding never rewrites raw bytes. Optional metadata parsing cannot replace or truncate the original files.

## Artifacts and Notes

Original experiment baseline: `fd6059d37881dab58109cf1cff1429ad54ce9592`. Integration branch: `fix/ablation-full-transcripts`. Failed pilot evidence: `/tmp/skills-ablation-coordination/pilot-gate-report.md`. Approved probe/config evidence: `/tmp/skills-ablation-coordination/preparation-report.md`, `task.md`, `pilot-invocation.txt`, and `remaining-invocation.txt`. Harness-fix readiness and future test/review evidence belong under `/tmp/skills-ablation-coordination/harness-fix/`. These external files supplement the inline contract and do not authorize extra spend or changes to approved runner settings.
