# Restore one current VERSION2 scheduler and retain verified useful guidance

This living ExecPlan is `brain/plans/31-scheduler-current/ExecPlan.md`, saved before source edits. Apply exec-plans, brain, handoff and reflection workflows. The original clean integration HEAD was `504049f75ee93878af29341ddf8e41147ecd6209` on `scheduler-reliability`. The plan-only D1 commit is `ba782a3968bc40d6b9cfd4983a9d56dc46d0938b`; source work is isolated in `/private/tmp/skills-scheduler-current-cleanup`. D1 approved inventory is now recorded below. All audit/disposition prerequisites are resolved. The bounded source worker is active in the isolated clone. This is a new user-authorized cleanup. The previous completed task remains completed.

## Purpose / Big Picture

Leave scheduler VERSION2 as the only current implementation, with the guidance and deterministic checks that are verified successful and useful. Remove this session's unsuccessful or unproven scheduler/evaluation machinery, previous/v3 traces and obsolete evaluation archives from the working tree. Repair active references so users and installed skill links reach the one current implementation. Git history remains intact.

## Authorization and limits

- The user explicitly confirmed deletion of obsolete scheduler evaluation archives from the working tree. The earlier preserve-archive and promote-v3 contracts are superseded for this cleanup. Do not recreate deleted archive copies in the repository.
- Scope is this session's eval/scheduler changes, their guidance, references and obsolete archives. No Git history rewrite, unrelated main-branch edits, credentials, global authentication or unrelated installation changes.
- No paid/provider/model evaluation calls, broad suites, new framework, or new regression tests for deleted features. Existing focused deterministic v2 checks and an independent delta review establish restoration.
- The former Sol/medium subagent preference belonged only to the completed prior plan. It is not a global preference or a new requirement here.
- Parent owns disposition approval and integration. The initial coordinator assignment owns only this plan and curated navigation, with no source deletion, installation mutation or commit.

## Context and accepted evidence

Canonical v2 baseline commit is `5db7440017e081b4d391c92f28d325b2fccf95a0`. Relevant active bundle is `skills/default/delegate-to-subagents/`, including `scripts/scheduler.py`, `scripts/test_scheduler.py`, `SKILL.md`, `README.md` and session-added `evals/` machinery. Exact restore/delete/retain paths, archive references and installed symlink targets are the audit output, recorded before worker dispatch.

Prior manual Copilot inspection supported seven common assertions for both variants and an additional candidate acknowledgment. Candidate cost/latency was higher without demonstrated common reliability improvement. Codex comparison was inconclusive. Every original automatic P05 grade was invalid. The final harness correction was verified offline and never proved successful native evaluation. These facts do not establish a reason to keep the added machinery or promote v3.

Audit reports and non-source task evidence stay outside the repository at `/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-current-cleanup-mamlnvun`. No audit investigation is duplicated by this coordinator.

## Progress

- [x] (2026-11-12) [milestone-1] User approved VERSION2-only cleanup and working-tree archive deletion, with history intact.
- [x] (2026-11-12) [milestone-1] Save this current contract and curated plan entry before source edits.
- [x] (2026-11-12) [milestone-1] A1 evidence audit and separate generic-runner proof audit complete, retained externally.
- [x] (2026-11-12) [milestone-1] A2 baseline/reference/install inventory complete. Current installed/main behavior is v2, with no install/main edit required.
- [x] (2026-11-12) [milestone-1] A2-F resolved, installed scheduler is byte-identical to baseline SHA94f32f8b. Prior apparent difference came from filtered display bytes. Nested-index scan remains part of W1 cleanup.
- [x] (2026-11-12) [milestone-1] D1 parent-approved exact disposition and one-worker ownership recorded below. All dispatch prerequisites are resolved.
- [ ] [milestone-2] W1 (in progress) worker in `/private/tmp/skills-scheduler-current-cleanup` restores/deletes only approved paths and reconciles guidance/references. No worker result has been accepted or integrated.
- [ ] [milestone-2] V1 focused deterministic v2 verification and exact restoration evidence (pending W1).
- [ ] [milestone-2] R1 independent delta review and accepted integration.
- [ ] [milestone-3] C1 verify current durable guidance/navigation and remove this temporary plan on completion.

## Plan of Work and task graph

### Milestone 1 - Independent audit and approved disposition

Status: done
Acceptance: met

A1 has no source-write dependency. `/root/current_evidence_audit` examines retained success/failure evidence and distinguishes useful verified guidance from unsupported claims. Its report is `/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-current-cleanup-mamlnvun/evidence-audit.md`.

A2 runs independently. `/root/current_scheduler_audit` maps exact baseline files, current scheduler/test/skill/README and eval paths, provider-runner guidance, obsolete archives/references and installed symlink targets read-only. Its report is `/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-current-cleanup-mamlnvun/scheduler-audit.md`. Installed paths are observations at this stage. Existing symlink reachability does not imply a separate authorized global installation rewrite.

D1 is approved by parent after the completed [evidence audit](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-current-cleanup-mamlnvun/evidence-audit.md), [generic runner proof audit](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-current-cleanup-mamlnvun/C-runner-proof-audit.md) and [baseline/reference/install audit](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-current-cleanup-mamlnvun/scheduler-audit.md). Where an audit suggests preserving an obsolete archive or generic runner, the explicit user-approved disposition below governs. There is no experiment to rescue unproven scripts.

#### D1 approved path disposition and worker ownership

One bounded worker on a separate worktree owns all paths below and directly required reference-only cleanup. Root coordinator owns progress/integration. Preserve unrelated edits and pre-existing supported tooling.

| Exact path or bounded group | Approved action |
| --- | --- |
| `skills/default/delegate-to-subagents/scripts/scheduler.py` | Restore byte-for-byte from `5db7440017e081b4d391c92f28d325b2fccf95a0`, VERSION2 only. |
| `skills/default/delegate-to-subagents/scripts/test_scheduler.py` | Restore exact matching baseline tests. |
| `skills/default/delegate-to-subagents/SKILL.md`, `README.md` | Restore matching v2 behavioral guidance, remove obsolete version-comparison prose, and preserve current version/help/I/O/host-ownership facts. No v3 acknowledgment contract. |
| `skills/default/delegate-to-subagents/evals/` | Delete entire tree, including harness, helper, tests, rubric, fixtures, registry and guidance. Remove direct registry/docs dependencies on it. |
| `skills/default/create-skill/scripts/eval_runner.py`, `scripts/test_eval_runner.py` | Delete offline-only unproven generic runner and its runner-specific tests. |
| `skills/default/create-skill/references/provider-runs.md` | Delete runner-specific procedure. |
| `skills/default/create-skill/SKILL.md`, `README.md`, `references/validation.md` | Surgically remove session-added runner prescriptions, runner commands/routing and the “Runner evidence and benchmark artifacts” section. Preserve pre-existing grading/evaluation tooling and supported baseline/artifact requirements. |
| `brain/plans/subagent-model-router-phase-1-exec-plan.md`, `subagent-model-router-phase-2-exec-plan.md` | Remove only runner prescriptions, dependencies and obsolete scheduler archive path mentions, including historical prose pointers to the removed experiments. Preserve both plans' independent requirements and verified outcomes. |
| `brain/archive/31-scheduler-reliability/` | Delete entire obsolete session archive, including history/reports and v3 traces. |
| `brain/archive/plans/31-scheduler-evaluation/` | Delete entire obsolete evaluation archive. |
| `brain/archive/plans/31-skill-workflow-hardening/` | Delete entire obsolete archive containing superseded runner instructions/older scheduler contracts. |
| `brain/archive/plans/index.md`, other affected curated indexes/direct links | Remove references to deleted trees and repair navigation. Scan nested indexes before deletion. |
| `brain/codebase/script-testing.md`, `live-hook-testing.md`, other directly affected session-added guidance | Remove deleted-pilot links/proof claims and speculative recipes. Retain concise factual distinctions about offline/native proof, actual model/child identity, original evidence and stopping repeated calls after clear validity failure. No new framework. |

Preserve `skills/default/create-skill/evals/grade_benchmark.py`, `evals/test_grade_benchmark.py`, `evals/evals.json` and unrelated supported tooling. The runner-proof audit found no central `scripts/test-all.py` registration for the generic runner. Remove only actual direct dependencies discovered by search, not unrelated registry behavior. Do not add feature-deletion regression tests.

Before deleting archives, scan nested curated indexes and reference targets, not only `brain/archive/index.md`. The prior archive is linked from `brain/archive/plans/index.md` as `../31-scheduler-reliability/ExecPlan.md`. A1/A2 initially missed this nested link, so index absence at a parent level is insufficient. Search all deleted path names, `eval_runner.py`, `test_eval_runner.py`, `provider-runs.md` and relevant v3 scheduler commands in the affected scope, then verify remaining Markdown targets after cleanup. Leave unrelated scheduler terminology and historical Git objects intact.

Installed `/Users/adam/.agents/skills/delegate-to-subagents` is a regular directory with current v2 behavior. Main `/Users/adam/dev/skills` also has v2 and is outside edits. The completed [installed-difference follow-up](/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-current-cleanup-mamlnvun/installed-difference-audit.md) establishes installed and pinned baseline bytes are identical, SHA-256 `94f32f8be95341e860cf30f88c9148ff1579f27494ef7189321748a5ea3c8bc7`, with empty raw diff and cmp exit 0. The earlier 62eb hash was filtered RTK display output, not Git blob content. No install/global/main mutation is needed.

Worker restoration and provenance must use raw Git bytes, such as `git show` via `subprocess` inside `rtk proxy python3`, or `rtk proxy git show`. Never restore or hash the output of display-filtered `rtk git show`. This is a narrowly observed snapshot identity correction, not a new tool or framework.

### Milestone 2 - Bounded restoration, verification and review

Status: in progress
Acceptance: not met

W1 depends on D1. The assigned worker is active in the isolated clone `/private/tmp/skills-scheduler-current-cleanup`; the coordinator owns only this plan/index and integration. No source delta, verification result or review has been accepted yet. One serialized worker owns source restoration/deletion and directly coupled documentation according to the approved inventory. It is not alone and must preserve others' edits. Restore the designated current source/test/skill/README from exact commit `5db7440017e081b4d391c92f28d325b2fccf95a0` where approved. Remove obsolete alternate/previous/v3 implementations, failed/unproven eval harness and provider guidance, and confirmed obsolete scheduler evaluation archives and their navigation. Keep genuinely verified useful guidance in existing indexed topics. Do not carry forward the old archive-preservation contract or create replacement archives.

V1 depends on W1's exact bytes. From the worker repository root run the focused existing v2 suite identified by A2, expected `rtk proxy python3 skills/default/delegate-to-subagents/scripts/test_scheduler.py`, and relevant public v2 CLI checks. Expected result is exit 0 with existing baseline semantics, help/stream/exit behavior and retained supported inputs intact. Audit findings determine any exact applicable command adjustment before execution. Verify restored file identities against the pinned baseline, VERSION2 as the sole current scheduler implementation, removed obsolete paths and repaired references. Check installed symlink targets read-only against the resulting current files. No paid/provider call, broad suite or feature-deletion regression test is added.

R1 depends on exact W1/V1 output. An independent reviewer compares the bounded delta against the approved disposition and this contract, checking accidental retained v3/eval references, deleted verified useful obligations and unrelated edits. Parent integrates only accepted exact verified bytes. Retain source hashes, focused results and review evidence externally in the task evidence directory.

### Milestone 3 - Current guidance and task cleanup

Status: open
Acceptance: not met

C1 depends on accepted R1. Reflect on retained guidance and leave only verified successful useful content in maintained code/docs or appropriate existing indexed topics. Check curated navigation and all affected links after archive removal. Preserve Git history, external evidence and unrelated worktrees/settings. Remove this temporary plan and its active index entry once all tasks are complete. Do not archive it or recreate obsolete evaluation archives. Record concise completion evidence outside the repository and return the accepted source/commit and verification result.

## Concrete Steps

A1/A2/A2-F and parent D1 disposition are complete. The bounded W1 worker is active in `/private/tmp/skills-scheduler-current-cleanup`; no output is accepted yet. The coordinator waits for the worker commit, focused verification evidence and independent R1 review, then integrates only accepted bytes. Finish C1 and remove this temporary plan after final exact-hash/reference/navigation checks. This coordinator assignment is limited to the plan/index and external integration checklist; no source edits/deletions or installation actions occur here.

## Validation and Acceptance

The intended observable outcome is one current VERSION2 scheduler with consistent current documentation and installed-link reachability, no obsolete session eval/v3/previous implementation or evaluation archives in the working tree, and no historical rewrite. Acceptance needs the approved inventory, exact v2 restoration evidence, focused existing deterministic checks, independent delta acceptance and clean affected navigation. Verified useful guidance survives outside this temporary plan. No acceptance is inferred from the prior offline harness tests or invalid native pilot grades.

## Idempotence and Recovery

Read current Git status before each owned change. Use exact pinned baseline files and path-scoped edits without resetting unrelated work. If a disposition contradicts an actual reference or symlink, report that specific fact to parent and reconcile the inventory before mutating installation state. Git history supplies recovery without repository archive copies. Do not rerun model/provider evaluations to decide what to keep.

## Surprises & Discoveries

A1/A2/A2-F establish v2 as current installed/main behavior and byte-identical to the pinned baseline. A filtered display hash caused the apparent source discrepancy. The generic runner has fake-provider tests only and no actual successful native proof. The nested curated archive index contained a link missed by the initial audit. Parent approved removal rather than preserving unproven generic machinery or obsolete archives.

## Decision Log

- 2026-11-12. Parent approved the exact D1 restore/delete/retain inventory, including all three obsolete archive directories and the generic unproven runner. Preserve the pre-existing create-skill grader/evals and router task scopes. Installed-difference follow-up is resolved and source dispatch is ready.

- 2026-11-12. User selected VERSION2 as the only current scheduler and explicitly included obsolete evaluation archive deletion in working-tree cleanup. History remains intact.
- 2026-11-12. Parent delegated two independent audits before a single bounded restoration worker. This initial assignment changes only the current plan/index.
- 2026-11-12. Retain verified useful durable lessons in existing indexed topics. The new temporary plan will be removed after completion.

## Outcomes & Retrospective

Planning contract and approved inventory are saved before source work. Audits and D1 are complete. Installed-difference follow-up is resolved. The isolated worker has the approved source scope; restoration, focused verification, independent review and cleanup remain pending. Coordinator preparation records only the current owner, commit boundary and final integration checks. No global model preference or general framework is introduced.
