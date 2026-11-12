# Complete the scheduler comparison with a focused native harness

This living ExecPlan is `brain/plans/31-scheduler-reliability/ExecPlan.md`. Apply the repository-local exec-plans skill. Current checkpoint is 2026-11-12. Focused implementation is uncommitted in `/private/tmp/skills-scheduler-codex-auth`, branch `scheduler-codex-auth`. Independent [review 1](review-focused-1.md) reports Standards one P2 finding and Spec one P1 plus one P2 finding. The source worker is correcting them. Focused source acceptance remains pending. The user explicitly approved removing the added provider-conformance features so the original scheduler comparison can finish. The active contract below supersedes the preserved historical qualification contracts.

## Purpose / Big Picture

Compare frozen scheduler v2 with candidate v3 on the common deadline, extension, shutdown-gating, independent-progress and recorded parent-transfer behaviors through both Codex and GitHub Copilot. Report candidate ownership acknowledgment separately. A person should be able to inspect real helper execution, resulting state and the report for each fresh scored session. Synthetic shutdown facts remain synthetic. The plan finishes with retained results, durable lessons, cleanup and archive.

## Authorization and current budget

The user said “I agree with your recommendation. Remove these scope crept features so we can finish this task without unnecessary churn.” This approves implementation of this focused contract and continuing to completion. Existing provider login and ordinary supported native CLI sandbox/approval controls remain. Equivalent temporary project/setup paths for this plan purpose are already authorized. No repeated setup question is needed within these bounds.

P03 consumed two actual evaluation sessions from the approved eight-session budget. Copilot's seven model turns are recorded separately and establish no backend API-call count for the budget. Six sessions remain in total, serial, `gpt-6.1-sol` with `medium`, at most 600 seconds each. Allocate one neutral harness smoke per provider followed by four fresh scored sessions, baseline and candidate for each provider. Use each provider's baseline cell for its single neutral smoke. Candidate smoke slots are omitted in the fresh payload. A provider's one valid neutral smoke gates both of its scored sessions. No additional retries or expansion are authorized. Failed frozen P02/P03 artifacts stay unchanged. No live call runs until corrected source passes focused checks, independent review and fresh-payload verification. Parent owns final integration and live dispatch subject to actual tool policy.

Ordinary controls exclude all-tools/all-paths permission bypasses. Existing global Guardian, authentication and unrelated settings are outside the change. Remove harness-specific pinned hooks and forbidden probes. Retain source/prompt/session identity and the behavior evidence below. The requested outcome is a bounded diagnostic comparison. Claims of universal mediation, provider security conformance, general reliability or statistical significance are outside its evidence.

## Preserved history and accepted work

- The [complete pre-simplification plan](history-before-simplification-2026-11-12.md) was saved before replacement, byte-for-byte, 183736 bytes, SHA-256 `9f0cfdc3e1969a3bc5714c5be6717f2290c0a1d6f1fdc520cb43a3621a914519`. It retains every earlier unique contract, decision, approval, finding and evidence reference. Its superseded implementation instructions are historical.
- T1 ownership-transfer implementation and acceptance remain complete. Candidate v3 stores authorization separately from actual parent ownership update and explicit acknowledgment. Stop confirmation precedes transfer. Real parent update/readback and candidate acknowledgment evidence remain required. Commit `a873e2c125d56810328cf8ffb56e3efbfc2242a9` and later accepted scheduler corrections are retained in history.
- T3 retained-trace overhead analysis is accepted. Its results and limits remain in history. No optimization work is added.
- Latest accepted offline harness source is `3d5a2b5888adf77a49a000e80557bc655f19d8de`, integrated through `0f416340a39abe2398c86a7b50d94b6eed15e1ee`. All 55 then-maintained tests passed in 200.507 seconds and both [startup review axes](review-startup-1.md) found zero issues. These results describe that historical feature set.
- [P02 failed startup](pilot-startup-02.md) and [P03 invalid native smokes](pilot-smoke-03.md) remain immutable reports. P03 has two wrappers, two exclusive attempts, two actual evaluation sessions, zero eligible scored pairs and six gated slots. Both native processes exited 0 while qualification failed under the earlier contract.

## Progress

- [x] (2026-11-11) [milestone-1] T1 scheduler transfer behavior accepted.
- [x] (2026-11-11) [milestone-3] T3 retained-trace overhead analysis accepted.
- [x] (2026-11-12) [milestone-2] Historical startup source and offline review accepted at `3d5a2b58`.
- [x] (2026-11-12) [milestone-2] Preserve full prior plan and save the user-approved focused contract before source edits.
- [ ] [milestone-2] F1 implementation reduced the harness from about 1800 to 1070 lines. Initial frozen suite has 35/36 passing with one helper cleanup error. Final corrected-byte verification remains pending.
- [x] (2026-11-12) [milestone-2] F2 review 1 captured independently, Standards one P2 and Spec one P1 plus one P2 findings.
- [ ] [milestone-2] F2-C1 restore retained Copilot status SIGINT/exit-130/descendant coverage. Current serialized source worker is addressing it.
- [ ] [milestone-2] F2-C2 retain unknown non-authoritative telemetry with non-object data without schema invalidity. Current source worker is addressing it.
- [ ] [milestone-2] F2-C3 reproduce and bind canonical scenario state independently of result-selected copies. Current source worker is addressing it.
- [ ] [milestone-2] F2 final corrected-byte verification, independent finding/source acceptance and integration.
- [ ] [milestone-4] F3 prepare/verify a fresh six-session payload and execute its two neutral smokes and four scored sessions within gates.
- [ ] [milestone-4] F4 verify each result independently and retain the paired report and machine-readable results.
- [ ] [milestone-5] F5 persist durable lessons, reconcile all tasks, clean completed worker resources and archive the completed plan.

## Context and Orientation

Work from `/Users/adam/.codex/worktrees/48fd/skills` on `scheduler-reliability`. The public harness is `skills/default/delegate-to-subagents/evals/scheduler_pilot.py`, tests are `skills/default/delegate-to-subagents/evals/test_scheduler_pilot.py`, and operator guidance is `skills/default/delegate-to-subagents/evals/README.md`. The helper is `skills/default/delegate-to-subagents/evals/invoke_scheduler.py`. It runs frozen scheduler children and records commands, exits, before/after state and parent-update readbacks. The scenario rubric is `skills/default/delegate-to-subagents/evals/pilot-scenarios.json`.

Frozen v2 baseline is `/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/baseline-v2` from `5db7440017e081b4d391c92f28d325b2fccf95a0`. Reuse its pinned files. The candidate's scheduler and selected SKILL.md remain immutable for each new payload. Existing native login is provider-owned. An absent environment token is not proof of account logout. No credential extraction, copying, hashing or logging is allowed.

## Plan of Work and task graph

### Milestone 1 - Scheduler behavior

Status: done
Acceptance: met

T1 accepted implementation remains the scheduler under comparison. Preserve its atomic state, idempotent acknowledgment, real parent ownership evidence and independent assignment behavior.

### Milestone 3 - Retained overhead analysis

Status: done
Acceptance: met

T3 accepted observations remain historical evidence. Further retained-trace analysis or optimization is unnecessary for this contract.

### Milestone 2 - Focused usable harness

Status: in progress
Acceptance: not met

#### F1 - Implement focused native execution and behavioral grading

Prerequisites are this saved contract, accepted source `3d5a2b58` and the actual P03 evidence. One serialized implementer owns the harness, its tests and eval README, plus directly required small native fixture files and helper changes. No parallel source ownership. Activate TDD. Start with the public prepare/preflight/run/grade flow using actual retained native shapes and real helper children to reproduce retained-core failures. The provider diagnoses identify facts. Their maximal provider-schema and journal-repair proposals do not define this task.

Remove exhaustive provider event/protocol-schema validation, literal/effective provider-config shape equality, custom pinned-hook qualification, negative forbidden-probe qualification and duplicated permission/usage journal proof. Unknown non-authoritative telemetry is retained as raw evidence without automatic invalidity. Remove tests solely for these deleted features. The user authorized their deletion, and no new regression tests for deleted features are needed. Preserve all real-child, rubric, source/prompt/result immutability, state-chain and replay tests.

Keep ordinary supported native sandbox and approval settings, disposable physical repos and provider-owned existing login. Freeze the actual chosen launch inputs symmetrically for baseline/candidate. Do not inventory and compare entire provider configuration or sandbox profile schemas. Keep controls that directly bind execution inputs and source/results.

For Copilot, the actual helper commands were denied because native shell command identity was `python3`, while the frozen rule included Python plus helper path. Implement the narrow candidate of a directly executable frozen helper with a pinned absolute interpreter shebang and literal helper-path command grant. Freeze executable mode and bytes before manifest hashes. Render prompt commands and helper execution from one prefix. Preserve helper resolved output/state scope validation and exact child receipts. Do not grant unrestricted Python or construct a general permission framework. Actual native neutral smoke must prove permission acceptance and real helper operations. Offline fixture acceptance is insufficient for this permission result.

For Codex, stdout completed helper commands and results supply authoritative execution evidence. Use only the exact session's raw rollout for required model/effort/session/cwd proof. Normalize cwd semantically across an absolute filesystem path and a local file URI. Keep missing or contradictory required identity invalid. Full sandbox/permission profile equality and inventories are removed. Use the minimal grounded actual native shapes. Do not reconstruct permission journals, streaming parent chains or accounting streams.

Both providers must establish the frozen fresh session, selected skill body and requested model/effort, required helper commands/argv and actual completed child outputs. Match required actions one-to-one, reject duplicate/replayed/fabricated receipts and require a consistent independent before/after state chain with output readbacks. Wrong model, wrong skill, missing execution, contradictory identity and unmatched required actions remain invalid. Harmless incidental read-only inspection is not a sole invalidity reason. Compromised source, state or results remain invalid. Missing required semantic evidence invalidates behavior even if a native process exits 0.

Retain raw stdout/stderr, exact session context needed for identity, helper receipts, authored outputs, source/prompt hashes, exit status and timing. Run and grade must use the same core validation so later mutation, replay or missing evidence cannot turn valid behavior into a trusted result. Optional usage fields may be missing or unknown without invalidating behavior. Preserve provider-defined raw usage fields separately, avoid estimates and zero substitutions, and distinguish wrapper elapsed from provider execution plus evidence collection elapsed.

Preserve the public `prepare`, `preflight`, `run` and `grade` commands, prompt stdin transport, normal stdout/stderr contracts and exit semantics. Help exits 0 without provider calls. Setup/invocation errors exit 2, timeout 124 and interruption 130. Grade exits 0 when it writes a valid grading artifact, including behavioral failures, whose fields determine the result. No fresh model session is part of F1. No provider-interface or SDK rewrite is required.

Verification covers only retained/new core behavior. Use actual native samples for minimal authoritative parsers, real scheduler/helper children for positive receipts, and negatives for wrong/missing identity, source/prompt mutation, duplicate/replay, missing execution, command/argv mismatch, state-chain inconsistency and incorrect rubric results. Keep CLI boundary/exit/cleanup checks. Run focused checks and the maintained affected test command from the worker root, `rtk proxy python3 skills/default/delegate-to-subagents/evals/test_scheduler_pilot.py`, with expected exit 0. Retain exact tested hashes and results. At final source acceptance, reconcile the scheduler fixture description in `brain/codebase/script-testing.md` with the retained core contract, replacing obsolete auth-mode/metadata-drift promises. No historical test-count target applies after authorized feature deletion. Stop at the implemented/tested checkpoint and review inputs.

#### F2 - Independent source acceptance

Depends on F1 exact final bytes. Obtain independent Standards and Spec review against this focused contract, retain both axes without reranking, and integrate only accepted tested bytes. The closed original EOF review cycle stays closed. Native qualification remains F3.

##### F2 correction tasks from focused review 1

Status: in progress
Acceptance: not met

All three tasks depend on the [immutable review 1](review-focused-1.md) snapshot rooted at `35c31ab9782c293a8777b2145892c31b8aa0c6ae`. The current serialized source worker owns them in `/private/tmp/skills-scheduler-codex-auth`, branch `scheduler-codex-auth`, within F1's existing file scope. The corrections share source/tests and are serialized. Final acceptance depends on all three corrections and exact final-byte verification, then independent review and integration before F3.

- F2-C1, Standards P2, is in progress. Restore standalone public Copilot status cancellation coverage from the mixed deleted test. Keep SIGINT, exit 130 and status-child/descendant disappearance assertions for the surviving status path. Retire only obsolete layer checks. The finding is static coverage loss, with no claimed observed cancellation defect. Reconcile the test-disposition inventory with retained coverage.
- F2-C2, Spec P2, is in progress. The reviewer directly reproduced unknown `future.telemetry` with array-valued data yielding `malformed-native-line:1`. Retain unknown non-authoritative telemetry without imposing the deleted schema gate. Required execution/identity records remain strict. Keep a public retained-core reproduction and correction proof for this contract.
- F2-C3, Spec P1, is in progress. Start with a public E2E reproduction of detached final-state copy plus later canonical-state mutation. The reviewer identified this statically, without full-session reproduction. Independently bind the fixed `outputs/scenario-state.json` used by required helper commands to the actual final receipt/state chain. An agent-selected copied artifact cannot hide changes to the canonical scheduler state. Preserve parent ownership binding, immutable inputs and the full rubric.

The first frozen 36-test suite had 35 passing and one helper cleanup success-subcase failure, `[Errno 1] Operation not permitted`, in 136.981 seconds. The isolated same-byte cleanup check passed in 1.123 seconds. No full-suite success or root-cause conclusion follows yet. The current test-disposition inventory reports 37 after cancellation coverage was restored, while the worker continues correcting and verifying source. Treat mutable inventory counts as bookkeeping. Retain final-byte hashes/results before acceptance. No source or native acceptance is established by these preliminary checks.

### Milestone 4 - Fresh paired pilot and report

Status: open
Acceptance: not met

#### F3 - Fresh six-session payload and execution

Depends on F2. Parent prepares a new explicitly identified source archive/manifest with disposable repos, exact skill/prompt bytes, real helper paths/grants, session IDs, requested Sol/medium, timeouts and ordinary native controls. Retain and verify the fresh payload before launch. Equivalent temporary setup paths for this plan purpose already have authorization. Do not backfill P03 or silently reuse its failed receipts.

Execute exactly one neutral baseline-cell harness smoke per provider. It must prove login/session/selector identity and required helper write/readback execution under the ordinary native controls. No harness hook, forbidden probe or exhaustive telemetry inventory is required. A provider's failed smoke gates its two scored sessions without retry. After valid smokes, run four fresh scored sessions, baseline/candidate for each provider, serially. Deliver each selected skill body verbatim with equivalent synthetic facts, control conditions, command granularity and output requirements. Record all authorized slots and any gated remainder. Six remaining sessions total is the ceiling.

#### F4 - Independent behavioral results and report

Depends on available F3 evidence. Independently inspect each state chain and rubric assertion, including deadline/checkpoint handling, one extension, valid second-extension rejection, stop-before-transfer, real parent ownership change and independent C progress. Candidate explicit acknowledgment is reported separately. Compare common behavioral assertions per eligible pair. Retain invalid/missing-output/setup results transparently, raw usage availability and timing with their meanings. One pair per provider supplies diagnostic evidence with no variance/significance claim. A behavioral failure is a result and grants no retry. No efficacy claim follows from incomplete pairs.

Write `pilot-report.md` and `pilot-benchmark.json` beside this plan with source/manifest/session identities, complete six-slot ledger, assertion citations, provider/version/selectors, raw evidence links/hashes, optional native usage and independent review. Preserve [P02](pilot-startup-02.md) and [P03](pilot-smoke-03.md) reports separately as immutable history.

### Milestone 5 - Durable closeout, cleanup and archive

Status: open
Acceptance: not met

F5 depends on F4 and resolution of all remaining plan tasks. Keep reusable behavior in the maintained helper, tests and eval README, with concise links to existing indexed brain topics when useful. Verify no lessons remain only in this temporary plan. Confirm workers stopped, worktrees clean and fully merged before removing only completed task worktrees/branches. Preserve external evidence and root integration branch. Update current outcome and navigation, then archive the completed plan through the repository's existing archive structure. No main merge or push is authorized by this task. Never mark a task complete without its evidence.

## Concrete Steps

The current source worker finishes F2-C1/C2/C3 with retained public reproduction evidence and unchanged core invariants, then records final corrected-byte checks and hashes. Parent obtains independent finding/source acceptance and integrates only accepted bytes. Review 1 and the preliminary suite chronology remain linked in [review-focused-1.md](review-focused-1.md). No fresh payload or live dispatch precedes F2 acceptance. The remaining six-session budget and F3/F4/F5 dependencies stay unchanged.

## Validation and Acceptance

T1 and T3 acceptance stay met. M2 requires focused core tests, independent review and accepted bytes. M4 requires the bounded six-slot attempt accounting, native helper smoke proof and transparent paired behavioral results/report with independent state/rubric checks. M5 requires durable lessons, verified cleanup and archive with no incomplete tasks. The user goal of a meaningful both-provider baseline/candidate comparison stays explicit. If required execution or state proof fails, record it and diagnose within authorized work, preserving the no-retry ceiling. Never substitute a schema-conformance project for scheduler behavior evidence.

## Idempotence and Recovery

Read current manifests, receipts and the live ledger before dispatch. Never retry a consumed session automatically or overwrite frozen evidence. Public local preparation/tests can use fresh disposable roots. Repeated grade reads the same immutable evidence and core validation. After partial helper mutation, inspect actual saved state before taking further action. Parent acknowledgment retries must read the existing ownership update and use the same receipt, avoiding a second reassignment. Remove only unaccepted scoped source edits when recovery requires it, preserving others' work and all retained failures.

## Surprises & Discoveries

Focused review 1 found retained cancellation coverage removed with an obsolete layer test, a remaining unknown-telemetry schema gate and a canonical-state binding gap. The initial full-suite cleanup error and isolated same-byte pass do not establish a diagnosis or accepted suite result. [Review and verification chronology](review-focused-1.md).

P03 provider processes exited 0 while added conformance checks made both smokes invalid. Copilot's actual command identifier explains helper permission denial. Codex's actual context includes a file URI cwd and semantically different sandbox representation. The complete [Codex diagnosis](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-phase-codex/findings.md) and [Copilot diagnosis](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-phase-copilot/findings.md) are evidence inputs for minimal parsing and the narrow helper candidate. Their broader proposed schema/journal repair designs are superseded by this approved scope. Optional telemetry and usage do not establish scheduler behavior.

## Decision Log

- 2026-11-12. User approved removing the added provider-conformance features and finishing the original scheduler task. Preserve real execution, identity, immutable inputs and independent state/rubric evidence.
- 2026-11-12. Preserve the complete prior plan byte-for-byte before simplifying the active plan, with historical reports and exact external evidence reachable.
- 2026-11-12. Use six remaining sessions, one baseline-cell neutral smoke per provider and four fresh scored sessions. Existing task-specific equivalent-path authorization applies. No automatic retries or budget expansion.
- 2026-11-12. Keep direct executable helper permissions narrow and require native smoke proof, without constructing a provider permission framework.

## Outcomes & Retrospective

Focused F1 work is uncommitted and F2 corrections are active. Three findings and preliminary test results are retained without an accepted-source claim. No native calls occurred in this documentation checkpoint.

Original scheduler implementation and retained-trace analysis are accepted. Historical startup fixes have offline acceptance. The focused harness, its new source acceptance, fresh paired pilot/report and closeout remain unfinished. Reusable native-login, fixture-authority and input/evidence lessons already have maintained locations in [eval README](../../../skills/default/delegate-to-subagents/evals/README.md), [live provider checks](../../codebase/live-hook-testing.md) and [script testing](../../codebase/script-testing.md). F1 owns structural encoding of the new focused invariants. No general model preference or new generic framework is added.
