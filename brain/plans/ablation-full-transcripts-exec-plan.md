# Retain complete ablation runner transcripts

This living ExecPlan is `brain/plans/ablation-full-transcripts-exec-plan.md`. Follow the repository-local exec-plans skill and its annotated outline. Parent `/root` owns execplan-implement orchestration; persistent integration coordinator `/root/integration` owns integration and this plan. Read current source before dispatching. This plan authorizes harness repair and offline verification only; the separately approved experiment has its own execution gate.

## Purpose / Big Picture

An ablation user must be able to read every byte emitted by each runner after its disposable worktree is removed, including a final answer after a long Codex JSONL transcript. Keep complete stdout and stderr as durable per-run files under the result directory and keep `summary.json` small, compatible, and explicit about previews. Preserve evidence on nonzero exit, malformed output, timeout, and cancellation. Preserve the existing verified process-group shutdown before worktree removal. A public fake-runner experiment must reproduce the present capture failure before any implementation edit.

Scope is the canonical `skills/default/ablate-ai-layer/` bundle, focused tests and documentation, this plan, and a durable lesson if warranted. Installed skills are not source. No paid model calls, installation, experiment feature implementation, user rule edits, or unrelated cleanup belong to repair tasks. The user explicitly permits inspecting and fixing scripts despite the runtime skill's source-reading restriction.

## Progress

- [x] (2026-11-17) [milestone-0] Inspect canonical source, current tests, pilot evidence, and approved experiment records; select interfaces and bounded ownership.
- [x] (2026-11-17) [milestone-0] T0: Commit this plan on the integration branch before implementation.
- [x] (2026-11-17) [milestone-1] T1: Reproduce loss through the public CLI with a fake runner and retain failing evidence before code edits.
- [x] (2026-11-17) [milestone-1] T1: Implement durable raw streams and focused public CLI coverage in one worker worktree; verify its complete contract.
- [x] (2026-11-17) [milestone-1] T2: Update capture gate, full-stream grading guidance, and schema documentation in an independent worker worktree.
- [x] (2026-11-17) [milestone-2] T3: Integrate workers and verify the combined CLI, schema, shutdown, cleanup, and documentation contract.
- [x] (2026-11-17) [milestone-3] T4 round 1: Standards and Spec reviews completed successfully against pinned target `5126e6f9`; each reported the same P2 optional-metadata fixture coverage gap.
- [x] (2026-11-17) [milestone-3] T4-R1: Repair valid-JSON invalid-metadata fixtures and integrate commit `25f257d3`; targeted test, all 16 public CLI tests, syntax, and diff checks pass.
- [ ] [milestone-3] T4-R1 review closure: Repeat independent Standards and Spec axes against the pinned round-2 target; SF-1/SP-1 remain open until confirmed.
- [ ] [milestone-3] T4: Reach zero unresolved findings within at most three review rounds.
- [ ] [milestone-3] T5: Pending T4 zero-finding acceptance. Retain this plan; final reflection/removal and ablation execution follow only after required review is accepted.

## Surprises & Discoveries

- Round-1 Standards and Spec reviews both found that the intended invalid-metadata dictionary fixture is malformed JSON. Existing green tests therefore do not establish that coverage requirement; T4-R1 now repairs the fixture and adds valid-dictionary guards; integrated tests pass, with independent finding closure still pending.

- Before the repair, `run_agent` streamed into anonymous temporary text files, then returns decoded contents only on normal completion. `run_one` slices `result_text` at 4,000 characters and `stderr_tail` at 600. Exceptions bypass stream extraction, so timeout and cancellation lose their streams entirely.
- The pilot had two successful nonempty diffs, but both result previews stop at exactly 4,000 characters mid-JSONL. `/tmp/skills-ablation-coordination/pilot-gate-report.md` records the failed capture gate. That is a harness failure, not an arm finding.
- `run_one` already stages `git add -A` against a setup tree, so new/untracked files enter its diff and `files_changed`. Preserve and test that behavior rather than adding an unrelated file-manifest subsystem.
- `stop_group` verifies group disappearance even when its leader exits; `ShutdownUnconfirmed` retains the worktree. Raw capture changes must preserve this ownership boundary.
- Initial branch creation required normal Git metadata escalation because `.git` is outside writable scope; escalation succeeded. Main checkout started clean at `fd6059d37881dab58109cf1cff1429ad54ce9592`.

## Decision Log

- 2026-11-17, integration coordinator: User explicitly approved private source transmission and ordered completion of all work. The authorization blocker is resolved; both exact independent reviewer launches succeeded. Their round-1 reports now establish the active repair requirement. Preserve the original blocker record as historical evidence only, and retain the plan until review acceptance.

- 2026-11-17, integration coordinator: Store binary stdout/stderr directly at resolved `--out` paths named `control-1.stdout`, `control-1.stderr`, and equivalents. Open these files before runner launch and leave them intact after every outcome. `--out` is never a disposable runner worktree. Existing result paths may be reused only deliberately; do not overwrite historical pilot output. Retaining bytes is the contract; parsing is optional convenience.
- 2026-11-17, integration coordinator: Keep `result_text` at at most 4,000 decoded characters and `stderr_tail` at at most 600. Add `stdout_path`, `stderr_path` (absolute strings), `stdout_bytes`, `stderr_bytes` (nonnegative integers), `result_text_truncated`, `stderr_tail_truncated` (booleans). A truncation flag describes the corresponding decoded preview, not whether the raw file is complete.
- 2026-11-17, integration coordinator: Preserve Claude JSON dictionary metadata (`is_error`, `result`, `total_cost_usd`, `num_turns`, `usage.output_tokens`) when well typed. For JSONL, malformed/partial JSON, non-dictionary JSON, or unknown text, use a bounded raw stdout preview and exit status; preserve bytes without guessing provider semantics. Invalid UTF-8 may be replaced only in previews. No new JSONL schema parser is necessary to retain and grade full transcripts.
- 2026-11-17, integration coordinator: Add `shutdown_confirmed` (boolean) and `cleanup_status` (`removed`, `retained`, `failed`, or `not_created`). `shutdown_confirmed` means no owned process group remains, including pre-launch failures with no group. Unconfirmed shutdown forces `ok=false`, `cleanup_status=retained`, and `worktree_kept`. Explicit `--keep-worktrees` also yields `retained`; removal errors yield `failed` and the retained path. Avoid claiming cleanup before its actual outcome.
- 2026-11-17, integration coordinator: Keep the probe repository baseline `fd6059d37881dab58109cf1cff1429ad54ce9592` fixed. The repaired harness can later run by absolute path against a temporary detached checkout of that baseline. Do not merge experiment patches into the repair branch or change approved runner configuration.

## Outcomes & Retrospective

T0 plan commit `e901eda0df0b7923cd088b23a45ec840e4d23f3c` preceded implementation. T1 source commit `ecf94b11ed517da7777a5b13e367083c085fbda5` and T2 documentation commit `c51ea10a2c9b12e9b698df174f6f3f4464ab4141` are integrated as `0a02aa14` and `d1e3cd74`. Workers passed their scoped checks. T1 red evidence records the public `test_full_streams_survive_cleanup` failing with missing `stdout_path` before the fix. T3 integrated proof passed: the exact red reproducer now passes, all 16 CLI tests pass, syntax/skill/diff checks pass, and retained external artifacts prove byte equality, final markers, and lifecycle completion. The user explicitly approved private source transmission and ordered completion of all work. Both independent round-1 external reviews completed with exit 0 against target `5126e6f9b4098ad93b47d3896c7899075794ad8d`. Each found one P2 test-coverage issue: the invalid-optional-metadata fixture is malformed JSON because the opening quote before `total_cost_usd` is missing, so it never reaches metadata type validation. The shared T4-R1 repair is implemented and integrated as `25f257d3` (worker commit `820d63bdf033dbda57303d0d6cdff4dcdc3c76c1`). The targeted test passes in 2.698s and all 16 CLI tests pass in 7.754s; syntax/diff checks pass. Both review axes must still confirm SF-1/SP-1 closure against the new pinned round-2 target. T3 is complete; T4 acceptance and T5 remain pending. No experiment model runs occurred. Stop and report unresolved findings after the bounded review process; never delete the plan while a required check or finding is unresolved. Experiment completion is a later parent-owned phase and cannot be claimed from repair tests.

## Context and Orientation

`skills/default/ablate-ai-layer/scripts/run_ablation.py` is a standalone standard-library Python CLI. `main()` creates the result directory, dispatches `run_one()` concurrently, writes per-run diffs and `summary.json`, and returns 0 for a usable comparison, 1 for an unusable experiment, 2 for usage/platform errors, 130 for SIGINT, and 143 for SIGTERM. `run_one()` creates an external detached Git worktree, strips configured instructions, records a setup Git tree, invokes the runner, stages changes, records a diff, and cleans up. `run_agent()` owns a new POSIX session and calls `stop_group()` before cleanup can occur. Cancellation is coordinated through the `CANCELLED` event. `ShutdownUnconfirmed` prevents unsafe removal.

`skills/default/ablate-ai-layer/scripts/test_ablation.py` is the maintained unittest suite. `AblationCliTests.cli()` launches the public scripts, `commit_fixture()` creates disposable commits with fixture identity, and `experiment()` runs one pair with a local fake runner. Existing tests cover nonzero JSON exits, setup stripping, timeout descendants, normal-exit descendants, and SIGTERM cancellation. Extend these seams rather than mocking internal functions for stream retention. `scripts/test-all.py` already registers this suite; registration needs no change.

Runtime instructions live in `skills/default/ablate-ai-layer/SKILL.md`; maintainer contracts live in its `README.md`; blind grading guidance lives in `references/comparison.md`. Relevant reusable guidance is in `brain/codebase/testing.md`, `brain/codebase/script-testing.md`, and `brain/codebase/repository-workflow.md`.

## Plan of Work

### Milestone 0: Establish a committed repair contract

Status: done
Acceptance: met

Completed T0 contract and proof: plan-only commit `e901eda0df0b7923cd088b23a45ec840e4d23f3c`, verified before workers began; readiness evidence is retained externally. The following describes completed work, not a pending instruction.

Task T0 has no prerequisites. Its inputs are inspected source and the failed pilot gate. The integration coordinator creates branch `fix/ablation-full-transcripts` from the clean fixed baseline, commits only this plan and its curated index link, and records branch/base/plan commit in `/tmp/skills-ablation-coordination/harness-fix/readiness.md`. Acceptance is a clean plan-only commit before any source edit. No worker may implement until the parent confirms this checkpoint.

### Milestone 1: Deliver complete durable capture and its usage contract

Status: done
Acceptance: met

Completed T1/T2 contract: public red reproduction failed before source edits; T1 passed 16 CLI tests and syntax/diff checks, and T2 passed quick_validate and link/schema checks. Commits are recorded in Outcomes. Evidence: `/tmp/skills-ablation-coordination/harness-fix/t1/red.txt`, `t1/commit.txt`, and `t2/report.md`. The following is the completed delivery contract retained for integration/review, not pending worker instructions.

Task T1 requires T0 and a parent dispatch under execplan-implement. One worker owns only `skills/default/ablate-ai-layer/scripts/run_ablation.py` and `scripts/test_ablation.py` within that bundle, in its own worktree. Activate tdd before source design/edits. Reproduce through the public CLI first: a disposable repo with AGENTS.md and a fake runner that creates a new result file, writes more than 4,000 characters to stdout, ends with a unique final marker, and writes stderr. Assert complete files exist and match emitted bytes. Before the fix this must fail because no durable raw files exist; retain the command, exit, and decisive assertion under external harness-fix evidence. This is the red gate, not an expected green test.

Then change `run_agent` to accept explicit stdout/stderr artifact paths, redirect `Popen` into binary durable handles, and return a process exit status rather than whole stream text. Keep prompt delivery, polling, cancellation, and `stop_group` semantics. Pass resolved output directory from `main` into `run_one`; prepare paths before launch. Finalize stream metadata and bounded summaries in `run_one` even when execution raises timeout/cancellation/shutdown errors. Isolate metadata parsing so malformed JSON structure, invalid usage shape, invalid UTF-8, or optional parsing failure cannot lose evidence, skip diff capture for otherwise successful runs, or falsely mark them unusable. `agent_error` continues to include nonzero exit and valid Claude `is_error`. Existing short valid Claude result preview remains compatible.

Public tests must verify byte equality, final markers beyond the preview boundary, exact byte counts and absolute paths outside all runner worktrees, bounded previews and correct flags, both arms, and preserved new files in diffs. Cover large valid Claude JSON with metadata; complete Codex-shaped JSONL; malformed JSON and a partial trailing JSONL record; plain binary output including invalid UTF-8; valid JSON arrays/scalars and malformed optional metadata; nonzero exit; empty streams; and successful worktree cleanup. Extend the existing timeout and SIGTERM cancellation tests to emit flushed output on both streams before waiting and assert durable evidence after shutdown/removal. Verify cancellation before launch has a coherent metadata record if represented. Preserve existing descendant non-survival assertions. Add a public retained-worktree case with `--keep-worktrees`, then clean it safely after assertions. For safety failure behavior, use a public fake runner that exits but leaves a descendant in-group as existing tests do; preserve any existing unconfirmed-shutdown coverage and add an isolated controlled failure fixture if necessary to establish `ok=false` and retention without changing real process policy.

Verification is `rtk proxy python3 skills/default/ablate-ai-layer/scripts/test_ablation.py` from the worker root, plus Python syntax checks listed below. Stop after the focused implementation and all its tests pass, record before/after evidence, and create a scoped commit. No paid runs or installed-copy edits.

Task T2 also requires T0 and may run alongside T1 because it owns only `skills/default/ablate-ai-layer/SKILL.md`, `README.md`, and `references/comparison.md`. Activate create-skill and writing-for-agents for runtime guidance edits. Use the schema in Decision Log as the shared contract. Step 4 must require a one-pair capture gate before remaining runs: full streams accessible and complete, expected final markers or provider terminal events present, usable diffs including new files, and confirmed shutdown/cleanup. Exit 0 or a nonempty diff alone does not pass this gate. On inadequate capture, stop before more spend. Step 5 and comparison guidance must require full raw streams for workflow claims; previews and diffs cannot substantiate unobserved tool outcomes. Preserve blinding and avoid arm-revealing instruction contents in grading copies while retaining originals. README documents artifact schema and binary retention on all outcomes, platform limits, tests, and scope of guarantees. Verify references and quick_validate, then commit only owned files. Stop before integration or model execution.

### Milestone 2: Prove the combined result

Status: done
Acceptance: met

Completed integrated proof: the exact red test passes (1 test), all 16 public CLI tests pass in 7.169s, syntax checks pass, quick_validate reports Skill is valid!, and diff checks pass. Retained public-case artifacts prove exact 5,013-byte stdout and 710-byte stderr in both arms, both final markers, 4,000-character previews with flags, new.txt in each diff, absent runner groups, removed worktrees, and a clean fixture repository. Integrated documentation schema and local links/anchors pass. Evidence: `/tmp/skills-ablation-coordination/harness-fix/t3/checks.json`, `docs-contract.json`, and `public-case/proof.json`. The following is the completed integration contract, not pending instructions.

Task T3 requires T1 and T2. Integration coordinator cherry-picks scoped worker commits into the integration branch, resolves only overlapping contract issues, and runs the focused public suite on the integrated tree. Inspect retained external reproduction evidence and rerun its exact public fake-runner scenario against integrated source. Compare bytes, metadata, final markers, diff new-file behavior, and worktree/process absence after completion. Run quick_validate and syntax checks. Review documentation against actual field names and behavior, including timeout, cancellation, --keep-worktrees, failure diagnostics, and JSON parse fallback. Passing isolated worker tests or a clean merge does not establish this milestone. Record commands, counts, exits, and limitations here.

### Milestone 3: Review, preserve lessons, and close only on clean acceptance

Status: in progress
Acceptance: not met

Current review state: T4-R1 implementation and integrated verification are complete; independent round-2 review is next. Transmission authorization is resolved by explicit user approval. Both planned independent reviewers completed round 1 with exit 0. The reviewed code target remains `5126e6f9b4098ad93b47d3896c7899075794ad8d`; this plan-only reconciliation does not repin it. Reports are `/tmp/skills-ablation-coordination/harness-fix/review/standards-report.md` and `spec-report.md`. The earlier `approval-blocker.txt` is historical evidence, not a current permission requirement.

Standards finding SF-1 (P2), round-1 evidence, closure pending: `skills/default/ablate-ai-layer/scripts/test_ablation.py:96` omits the opening quote before `total_cost_usd`, so `json.loads` raises at column 60. This violates the required malformed optional-metadata coverage because only malformed-JSON fallback runs. No production runtime defect or other standards finding was reported.

Spec finding SP-1 (P2), round-1 evidence, closure pending: the same fixture cannot establish behavior for a valid dictionary with `usage: []`, boolean `num_turns`, nonnumeric cost, and other invalid metadata types. Read-only AST extraction and `json.loads` confirmed JSONDecodeError at character 59. No additional spec/scope finding was reported. SF-1 and SP-1 share one repair; retain both axis findings separately until independently re-reviewed.

Completed T4-R1 implementation contract: worker commit `820d63bdf033dbda57303d0d6cdff4dcdc3c76c1` is integrated as `25f257d3`. Both invalid-metadata cases are generated with json.dumps and explicitly guarded with json.loads returning a dictionary; a short string result distinguishes parsed metadata handling from raw fallback. The public test also asserts invalid metadata omitted, string is_error ignored, exit 0 usable, and new-file diff retained. Existing malformed JSON fixtures remain. Evidence: `/tmp/skills-ablation-coordination/harness-fix/r1-fix/red.txt` proves the pre-fix guard failed at column 60; `r1-integration/checks.json` records integrated targeted/full/syntax/diff exit 0. The following describes completed worker instructions for audit, not pending implementation.

Task T4-R1 requires the completed round-1 reviews. Parent dispatches the existing implementation worker on its existing worktree after merging/rebasing the current integration branch. That worker owns only `skills/default/ablate-ai-layer/scripts/test_ablation.py` for this fix and must preserve other edits. Activate tdd. First prove the current optional-metadata case cannot parse as JSON; then make it syntactically valid JSON while retaining intentionally invalid optional field types. Assert or construct valid JSON so the case actually exercises dictionary type validation; preserve raw-byte equality, usable-run, and absent-invalid-metadata assertions through the public CLI. Run the focused `AblationCliTests.test_stream_formats_preserve_bytes_and_optional_metadata`, the full public CLI suite, syntax, and diff checks. Commit only the scoped fixture repair and return evidence. Stop before broader changes or review launches.

The fix is integrated and verified. Parent now repeats independent Standards and Spec reviews against the unchanged base `fd6059d37881dab58109cf1cff1429ad54ce9592`. Round 2 is next; at most three total review rounds are allowed. Findings are not resolved by narrative dismissal without source/evidence. Stop and report any unresolved finding or required check after the limit, leaving this plan current. No ablation model calls until the repair is accepted and parent advances experiment execution.

Task T5 requires T4 with zero unresolved findings. Activate reflect at code session wrap-up and brain before any durable note edit. Preserve reusable guidance in an existing indexed note or the bundle's maintainer docs, verify navigation, then remove this completed plan and its link from `brain/plans/index.md`. Commit final acceptance/cleanup through commit skill. Record final branch/base/commit/evidence in the external coordination directory so plan deletion cannot erase the repair audit trail. The parent then owns the remaining ablation, including a replacement capture pilot on the original baseline and stop/go decision before remaining approved runs.

## Concrete Steps

Next authorized action: parent dispatches round-2 independent Standards and Spec reviewers using `/tmp/skills-ablation-coordination/harness-fix/review-round2/` and detached worktree `/tmp/ablation-fix-review-round2`, with exact target recorded in `review-metadata.json`. T4-R1 source/test repair is already integrated and validated; no further fixture edits are pending. Both SF-1 and SP-1 await independent closure. The user explicitly approved private source transmission and ordered completion of all work. T3 remains complete; T5 and plan deletion wait for zero unresolved findings. Review base remains `fd6059d37881dab58109cf1cff1429ad54ce9592`. Preserve original round-1 packet and worktree pinned at `5126e6f9b4098ad93b47d3896c7899075794ad8d`, and unrelated todo commit `31fa1cc03667e795639dd5199974caba0c3be2cf`. No reviewers or experiments were launched during this integration task.

From the repository or worker root, focused validation commands are:

    rtk proxy python3 skills/default/ablate-ai-layer/scripts/test_ablation.py
    rtk proxy python3 -m py_compile skills/default/ablate-ai-layer/scripts/run_ablation.py skills/default/ablate-ai-layer/scripts/test_ablation.py
    rtk proxy env PYTHONPATH=scripts/vendor python3 skills/default/skill-creator/scripts/quick_validate.py skills/default/ablate-ai-layer
    rtk git diff --check

Observed T3 results: exit 0 for all listed commands, exact reproducer OK (1 test), full suite OK (16 tests), and Skill is valid! from quick_validate. Evidence is retained under external `harness-fix/t3/`. Aggregate test-all execution is unnecessary for an unchanged registry and isolated bundle; broaden only if integration reveals cross-bundle effects. Offline tests require Python 3, Git, and POSIX process groups. Missing prerequisites are reported as unverified failures, not passing skips.

## Validation and Acceptance

The fix is accepted only if the public red reproducer fails before source edits and passes afterward; every launched run retains byte-identical stdout/stderr in durable files; summary previews and flags are correct and bounded; valid short Claude metadata remains compatible; malformed/unknown streams retain evidence; nonzero, timeout, cancellation, retained worktree, and cleanup paths preserve streams and correct usability; and owned process groups stop before removal. Existing new-file diff capture and stripped setup exclusion must survive. Full stream paths must still exist after all disposable worktrees are removed. Documentation must make the one-pair gate and full-stream grading requirement explicit. Independent review must have zero unresolved findings before plan removal.

The fake tests cannot establish that a particular live Codex session emits all tool outcomes or billing metadata. That remains a replacement live capture gate in the later approved experiment, not a repair acceptance claim. Existing pilot pairs are retained as failed capture evidence and cannot be silently counted as adequately captured experiment runs.

## Idempotence and Recovery

Use fresh external output directories for reproductions and replacement model gates; never overwrite `/tmp/skills-ablation-coordination/results/pilot`. Keep run evidence outside worker and runner worktrees. Normal retries use fresh temporary repos and result paths. If a process group cannot be verified stopped, retain its worktree and raw artifacts, mark unusable, stop dependent model runs, and report exact diagnostic; never remove it just to make tests green. Cleanup-only fixture kills occur after assertions and cannot validate a leaked runner. Revert a repair commit rather than changing the original probe baseline. Do not reset unrelated work or remove unrelated worktrees. Cancellation evidence is retained on orderly SIGINT/SIGTERM; crash/power-loss durability and deliberately detached runner descendants are outside the contract.

## Interfaces and Dependencies

No external library is needed. Resolve `out` once in `main`, pass it to `run_one`, and derive unique arm/index filenames before launching. `run_agent(cmd, use_shell, wt, prompt, timeout, stdout_path, stderr_path)` redirects binary streams and returns the exit status on normal completion; exceptions preserve the opened files and trigger the existing verified shutdown path. `run_one(..., keep, out)` owns record assembly and evidence finalization, including failure paths. Existing `summary.json` top-level keys, diff naming, task.md, and public CLI flags remain compatible. New per-run fields and their exact types/enums are defined in Decision Log. Artifact byte counts are obtained from files after writer shutdown; preview decoding never rewrites raw bytes. Optional metadata parsing cannot replace or truncate the original files.

## Artifacts and Notes

Original experiment baseline: `fd6059d37881dab58109cf1cff1429ad54ce9592`. Integration branch: `fix/ablation-full-transcripts`. Failed pilot evidence: `/tmp/skills-ablation-coordination/pilot-gate-report.md`. Approved probe/config evidence: `/tmp/skills-ablation-coordination/preparation-report.md`, `task.md`, `pilot-invocation.txt`, and `remaining-invocation.txt`. Harness-fix readiness and future test/review evidence belong under `/tmp/skills-ablation-coordination/harness-fix/`. These external files supplement the inline contract and do not authorize extra spend or changes to approved runner settings.

Integration evidence note: an extra external fixture verifier initially compared literal `/tmp` against resolved `/private/tmp`; correcting the verifier to resolve the base path established containment without a product change or rerun. The public harness itself returned 0 on that first invocation. This was an evidence-check path alias issue, not a harness failure.

Round-2 integration evidence: `/tmp/skills-ablation-coordination/harness-fix/r1-integration/checks.json`, `targeted.stderr`, and `suite.stderr`. Targeted metadata test OK (1 test, 2.698s), full CLI suite OK (16 tests, 7.754s), syntax/diff exit 0. Only the scoped fixture repair and plan status changed.
