# Build the accepted foreground software factory

This living ExecPlan is `docs/software-factory/ExecPlan.md`, governed by `.agents/skills/exec-plans/SKILL.md`. Keep Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective current together. Created 2026-10-20 from the explicitly accepted specification. **The user's 2026-10-21 execplan-implement invocation authorizes implementation and disposable development verification. This includes the plan-defined harmless provider qualification in disposable repositories when credentials and native prerequisites are available. Release publication, installation into real user repositories, and applying learning changes are outside this implementation authorization. Destructive native qualification requires disposable machines and must never run on this workspace.**

## Purpose / Big Picture

A user installs the factory into a Git repository, selects an ordinary TypeScript workflow and explicit inputs, and runs it in the foreground. Every phase uses one isolated worktree. The workflow can plan from a prompt or external plan, ask an implementer to delegate internally, check the resulting candidate, review it independently, and make bounded corrections. A browser shows live and saved phases, sessions, prompts, outputs, questions, and cleanup uncertainty. Later explicit learning invocations inspect retained history and propose improvements without changing active configuration.

Success is an observable repository-change workflow and a differently shaped read-only audit, with truthful history through failures and interruption. A later invocation starts the current script from entry, with fresh native conversations. History, supplied context, and preserved workspace reuse never restore executable state. The accepted specification's 26 decision tickets remain closed; this task graph organizes future development, not factory-managed application tasks.

No durable workflow engine, checkpoint replay, factory task scheduler, per-task/integration worktree, managed PR publication, automatic infrastructure retry, profile fallback chain, live human approval bridge, automatic learning promotion, full purge, downgrade, or general database salvage belongs in this plan.

## Progress

Implementation is underway on `codex/research-agentic-workflow-prototypes`, initially clean. T1 is verified. T2 local macOS storage probes pass; Linux/Windows native evidence remains pending. T3 and T4 are verified locally, including their composed failure proof. T2-CI automation is integrated; actual hosted runs remain pending. T5 foreground invocation is in independent-review repair before integration. Milestone acceptance requires actual recorded evidence.

- [x] (2026-10-21) [milestone-1] T1: Established isolated package, fake harness/Git fixtures, explicit test dispatch and development CLI contract; six fixture tests pass.
- [x] (2026-10-21) [milestone-1] T2: Pinned official Node v24.22.1 artifacts/hashes and verified local darwin-arm64/APFS storage mechanisms.
- [x] (2026-10-21) [milestone-1] T2-CI: Integrated reviewed Linux/Windows/macOS Actions and failure reports at `764f559b`; actionlint and local integrated foundation checks pass.
- [ ] [milestone-1] T2-CI: Obtain actual hosted native evidence; no push or hosted execution has occurred.
- [ ] [milestone-1] T2: Qualify pinned runtime on native Linux/Windows; no support is claimed for unrun targets.
- [x] (2026-10-21) [milestone-1] Verified local build, six fixture checks and two storage/cancellation probes against v24.22.1.
- [ ] [milestone-1] Verify combined build/probes on remaining native targets.
- [x] (2026-10-21) [milestone-2] T3: Implemented transactional history, ownership and accounting. Eleven public store tests pass, including separate-process races and crash recovery; independent review repairs are verified.
- [x] (2026-10-21) [milestone-2] T4: Integrated reviewed bounded capture at `676ba5f1`; fifteen capture tests and adversarial escaped-secret probes pass.
- [x] (2026-10-21) [milestone-2] Combined proof on base: recorder failure under a competing SQLite write lock stops pending admission, retains one charged correction/occupied scope, and preserves committed filtered streams. All 27 store/capture/integration tests pass.
- [ ] [milestone-3] T5: Deliver worktree preparation, one build, and command-only workflow execution.
- [ ] [milestone-3] T6: Deliver finalization, interruption, and exact-claim manual clearance.
- [ ] [milestone-3] Verify interrupted work, retained allowances, and explicit fresh follow-up together.
- [ ] [milestone-4] T7: Deliver profile resolution and adapter conformance fixtures.
- [ ] [milestone-4] T8: Qualify and implement Codex, Copilot, Gemini, OpenCode, and Pi adapter modes in bounded provider tasks.
- [ ] [milestone-4] Verify the common runner against every declared supported adapter mode.
- [ ] [milestone-5] T9: Deliver change/audit workflows and bounded correction semantics.
- [ ] [milestone-5] Verify fresh reviews, stable candidates, optional UI verification, and exhaustion together.
- [ ] [milestone-6] T10: Deliver loopback history API and saved-before-display SSE.
- [ ] [milestone-6] T11: Deliver accepted UI with paging and accessibility.
- [ ] [milestone-6] Verify real recorder, SSE, reconnect, browser states, and scale together.
- [ ] [milestone-7] T12: Deliver bounded native notice code and deterministic reminder/helper tests; live desktop tests are deferred to final acceptance.
- [ ] [milestone-7] Verify needs-input, native failures, acknowledgment, and stopped-host behavior together.
- [ ] [milestone-8] T13: Deliver explicit extraction and comparative evaluation workflows.
- [ ] [milestone-8] T14: Record authorized adoption/revert evidence with changed-target checks.
- [ ] [milestone-8] Verify source preservation, inconclusive results, and approval/application distinctions together.
- [ ] [milestone-9] T15: Deliver skill installation and shared dependency environment.
- [ ] [milestone-9] T16: Deliver forward maintenance, uninstall, and selected cleanup in bounded operation tasks.
- [ ] [milestone-9] Verify installed startup/maintenance exclusion and interrupted operations together.
- [ ] [milestone-10] T17: Complete native support matrix and integrated release acceptance.
- [ ] [milestone-10] T17-desktop: Run the deferred live desktop notification qualification after all implementation tasks.
- [ ] [milestone-10] Verify packaged behavior and repository regressions; record remaining unsupported combinations.

## Surprises & Discoveries

T1 exposed the root NuGet ignore rule `**/[Pp]ackages/*`; an explicit authored-package exception now keeps factory source visible while package-local ignores exclude dependencies and generated output. The referenced `.agents/instructions/INDEX.md` is absent, so current brain testing routes supply repository guidance.

T5 independent review reproduced premature success when a workflow does not await `needsInput`, `progress`, `agent` or a delayed `scope` callback. Command-only promise tracking is insufficient: every asynchronous context operation must participate in invocation lifetime before final history or claim release. Review also reproduced wrong-repository selection from trimming opaque Git path whitespace and unbounded history capture materialization. T5 owns public E2E repairs for all three findings; the initial 45 passing checks do not establish T5 acceptance.

Independent T1/T2 review reproduced SIGTERM leaving a SQLite qualification worker alive. Signal cleanup and worker IPC-disconnect handling now stop owned workers; public subprocess checks verify exits 130/143, dead workers and removed disposable directories. The reviewer approved the bounded foundation after repair.

The existing `docs/software-factory/ExecPlan.md` planned completed research prototypes, not a runtime. Its unique findings and verification were preserved in `docs/software-factory/ExecPlan.history-2026-10-20.md` before replacement. Its durable-graph recommendation is historical and must not influence current requirements.

Inspection on 2026-10-20 found no existing software-factory runtime package. The root publishes `skills/`, `agents/`, hooks, and installers. `scripts/install.sh:copy_skills` copies skill trees and removes evals/README/license files; the PowerShell installer documents matching behavior. Putting node_modules or development dependencies in a published skill would copy unnecessary state. Keep development source outside that bundle and package explicit release assets.

`scripts/test-all.py` uses an explicit suite registry and rejects native Windows as its coordinator platform. A new focused suite must be registered; Windows requires its own direct test commands. A guessed `scripts/test-install-skills.sh` does not exist; actual installer suites are `scripts/test-install.sh` and `scripts/test-install.ps1`.

No native adapter, notification helper, large SQLite stress, SSE performance, or full accessibility qualification has run. The T2 local storage probe and T3 transaction tests now exercise bounded contention and process loss; see current evidence below. Prototype browser evidence is design evidence only. The secret-scan incident remains documented in `docs/software-factory/hook-scan-limit-incident.md`; no scanner repair or clean security scan is claimed.

## Decision Log

- 2026-10-21, human: requested GitHub Actions qualification on Linux, Windows and macOS, deferred live desktop notification tests until the end, and directed implementation to continue. CI creation is authorized; checked-in workflows and local checks are not evidence of a hosted run. Live desktop proof belongs to T17-desktop, while T12 implements and deterministically verifies its packaging contract.

- 2026-10-21, human: invoked execplan-implement for this plan, superseding the authoring-only gate. Execute ready tasks and commit verified implementation when permitted. The plan's existing public CLI/store/host test boundaries are the accepted TDD seams.

- 2026-10-20, human: accepted the full specification and authorized plan authoring. The 2026-10-21 implementation invocation supersedes that earlier execution gate.
- 2026-10-20, human baseline: use SSSF-inspired foreground scripts, committed-only worktree creation, implementer-owned children, non-interactive steps, saved history, and explicit learning. Added machinery must solve an accepted requirement, not hypothetical future extensibility.
- 2026-10-20, plan author: place development code in `packages/software-factory/` and the published entry skill in `skills/software-factory/`. This separates test/dependency trees from generic skill copying. Release packaging assembles versioned runtime assets; the skill installs a pinned release explicitly into each target repository.
- 2026-10-20, plan author: use TypeScript, Node built-ins for processes/HTTP/files/SQLite, native ES modules, and plain browser modules/CSS. Use TypeScript and browser test tooling as development dependencies. No server framework, UI framework, broker, ORM, plugin SDK, or workflow-engine dependency is justified by this contract. Pin actual compatible versions during T1/T2 rather than fabricate current API facts.
- 2026-10-20, plan author: use Node's test runner for deterministic suites and Playwright for browser acceptance. Exact package versions and browser installation are future setup work, not performed here. Native tests are separate and may not silently pass by skipping missing prerequisites.
- 2026-10-20, plan author: keep all five desired harnesses in scope, with Codex/Copilot/Gemini first. A support claim is always an exact version/mode/platform claim. Optional child telemetry may be unavailable; unsupported required permissions or result channels must fail. A narrowed release requires a consequential human decision rather than silently deleting a provider.

## Outcomes & Retrospective

The accepted baseline has been translated into this self-contained delivery plan. Routine paths, module responsibilities, command shapes, dependencies, qualification gates, and task boundaries are specified. Authoring created no runtime artifacts. Implementation now adds the development package and dependencies; a verified runtime archive was extracted only into a temporary directory. No release or native registration was created. No new consequential product choice was needed during authoring. Native feasibility may later require a decision if an accepted requirement cannot be honored without expanding scope.

Execution is authorized. T1 is complete and T2 local storage prerequisites are verified. T3 storage and T4 capture are verified with a combined base proof. Reviewed CI automation is integrated and locally verified; T5 invocation remains in review repair; Linux/Windows and integrated release qualification remain pending. Development acceptance remains unmet until verification. Missing native targets remain visible qualification gates.

## Context and Orientation

Work from repository root `/Users/adam/.codex/worktrees/ea58/skills` (or the equivalent cloned checkout). Follow `AGENTS.md` and applicable source/testing routes before edits. `.agents/instructions/INDEX.md` is absent here; current routes are retained in `brain/codebase/testing.md` and `brain/codebase/script-testing.md`. Activate tdd for source design/implementation, skill-creator/create-skill for the published skill, dotnet if a Windows helper uses C#/.NET, and the relevant native-platform guidance. These instructions do not authorize dispatching agents. If work is later delegated, assign only bounded tasks with explicit file ownership and shared-state constraints.

The authoritative design is retained under `docs/software-factory/`: `map.md` indexes owning decisions, `lifecycle-specification.md` defines runtime mechanisms, `observability-ui-specification.md` defines presentation, and `tickets/specification-readiness-and-acceptance.md` traces requirements and qualification. The plan carries the current contract below so a worker need not reconstruct historical amendments. Resolve any actual conflict in favor of explicit accepted policy and reconcile this plan before coding.

A **run** groups related history and retained allowance. An **invocation** is one foreground execution from script entry. A **phase/operation** is a managed external action; an **attempt** is one execution of it. A **session** is a native harness conversation. An internal child session is observed when supported, not scheduled by the factory. A **claim** is exclusive ownership of a resource, with a fresh token to prevent stale release. **Clearance** records automatic or operator-confirmed cleanup; it does not rewrite execution success. **Capture** is saved supported text, not proof of every hidden harness action.

### Current behavioral contract

Workflow code controls conditions, reusable scopes, and bounded loops. Accept a prompt, external prose plan, or structured input without normalizing everything into an executable task graph. Declare expected phases without predicting future work. Both new worktree preparation and one workflow type-check/build precede all phases. A build failure launches no harness and creates no agent attempt. New worktrees use a resolved selected commit, never copied staged/unstaged/untracked/ignored changes; the source checkout/index stay untouched. Explicit reuse validates the existing worktree and preserves unfinished edits.

Resolve Git common directory and put managed installation, database, backups, and maintenance state below its `factory/` child. Keep authored workflows/prompts/settings/dependency declarations in `.factory/` in the selected worktree, except explicit external inputs. A worktree is repository isolation, not a security sandbox. One invocation owns it, even for read-only work; other worktrees may run concurrently. One dashboard host per repository can coexist with invocations. Maintenance excludes all active or uncertain invocation/dashboard owners. Claims never expire; PID alone, endpoint failure, or old outcome never proves death. Known-live owners cannot be manually cleared. Unknown children block candidate handoff/reuse; informed manual cleanup is supported when reliable child control is unavailable. Never kill saved PIDs after restart.

One transaction must recheck admission, reserve capacity, record an attempt, and debit allowances before spawn. Record launch evidence as admitted/started/not_started/unknown. Confirmed non-launch can release its debit; uncertain launch retains it. Completion releases capacity only after relevant activity is quiescent. Manual cleanup reconciles capacity, not consumed allowances. Preserve operation and loop lineage across joined invocations; naming changes are not automatic allowance resets. Initial planned work differs from additional corrections/repeated reviews/follow-up work. Defaults: two managed agents and two commands concurrently per repository, two code corrections per loop, one format correction per invalid output, twenty additional agent attempts per run, sixty-minute agent/thirty-minute command timeouts excluding capacity waits, thirty-second shutdown grace. Explicit recorded increases are allowed. Opaque children are not counted or capped as managed attempts; avoid double-counting reported parent-inclusive usage.

Build current workflow code once per invocation without watchers or hot reload. Resolve settings, prompts and skills at each step start: repository defaults, selected profile, step settings, targeted explicit invocation overrides. Prompt and ordered skill list replace inherited values unless explicitly composed; omitted fields inherit and an empty skill list clears. Record actual supplied inputs and requested/effective settings. Native loading remains separately qualified. Required unsupported settings fail, with no substitution, broader permissions, or automatic retry. Optional telemetry remains unknown. Implementation and independent reviews start fresh; only compatible same-invocation corrections may reuse a conversation. Every later invocation starts fresh conversations.

Agent results controlling execution use an unambiguous validated final channel: normal workflow payload or `needs_input` with nonempty question/context. Do not scrape control JSON from arbitrary logs. Save questions before cleanup, stop admissions, interrupt peer calls, preserve received results and independent failures, then finalize. No live human wait or browser answer. Later answers are explicit new invocation inputs linked to saved questions. Failed infrastructure never relaunches automatically; bounded quality/format correction is distinct. Format correction cannot rerun implementation or gain edit authority. Checks/reviews inspect one stable candidate after delegated writers stop; repair follows stopped reviewers and requires relevant fresh checks.

Keep stage (starting/running/shutting_down/finalized), outcome (succeeded/failed/needs_input/interrupted/cancelled), cleanup (complete/required/unknown with basis), and capture (open/complete/partial/unknown/pruned) separate. No finalization means unknown outcome. Independent failure outranks needs-input, which outranks shutdown-only interruption; preserve all reasons. Success requires completed required work and cleanup. Exit 0 means success plus complete cleanup; 2 needs-input plus complete cleanup; 3 startup refusal; 1 other failure/unresolved cleanup; handled SIGINT/SIGTERM use 130/143. Forced exit may leave no final record. Notices never change execution exit status.

Use one local SQLite store, WAL/full synchronous/foreign keys, short transactions and durable unique operation identities. No transaction spans external execution, SSE waiting, or human action. Filter known/configured secrets before saving, notifications, or diagnostics, including chunk-split matches. Incrementally decode UTF-8; chunks at most 64 KiB, commit batches at most 256 KiB or 100 ms, total uncommitted buffer 4 MiB/invocation with backpressure, result parsing initially capped at 1 MiB. Preserve raw oversized output while rejecting its control result. Busy waits initially 100 ms up to five seconds total; uncertain commit acknowledgment resolves by identity, not duplicate debit. Disk/full recording failure stops admissions and requests shutdown, with stderr fallback. Retain all captured history by default, no automatic truncation or cleanup.

State/event rows commit together. SSE serves only committed facts, with decimal-string cursors, deduplication, applied-cursor reconnect, and bounded queries (200 events/1 MiB). Bound each slow viewer to 1 MiB then disconnect for resynchronization. Invalid/pruned cursor shows a gap and saved snapshot, not execution replay. Missing external output file is separate from corrupt essential ownership/accounting storage. The latter blocks launch without automatic reset. Use same-host local filesystems; reject unsupported placement.

Notifications are best effort: prominent needs-input/failure, configurable quiet success, routine progress in dashboard. Initial summary uses five-second bounded delivery; submission is not proven visibility. Optional links only inspect saved details. No sender residency, automatic dashboard start, or crash resend job. Reminders default off, grouped per repository, fifteen-minute interval, one dashboard host sender, full interval after startup, no missed-alert replay. Persist per-invocation acknowledgment without answering questions or clearing claims.

Full learning history survives extraction. Explicit extraction over selected ended invocations records sources, limitations, proposals or no-proposal findings. Separate explicit evaluation compares exact baseline/candidate inputs on cases/criteria, including contradictory cases and nondeterministic limits. Inconclusive is not passed. Human approval names exact change and target; recheck target before ordinary authoring/install action. Actual applied/reverting revision is evidence distinct from approval. No automatic mutation or promotion service.

Installation is explicit and repository-local, pinned Node LTS with built-in SQLite and one shared factory dependency environment. Startup never downloads or rewrites locks. Idle maintenance handles dependencies, upgrades, forward repair, selected history/backup cleanup and uninstall. Stage a self-sufficient temporary controller outside files being replaced. Record incomplete modification before mutation, consistent verified backup before migrations, migration markers transactionally, validate runtime/schema/files together before release. Preserve backups until explicit selected cleanup. Uninstall removes only owned installation/shortcut files and preserves history, authoring, backups and worktrees. Never recursively delete unexpected user files. Incomplete maintenance blocks new starts until explicit repair/completion; no automatic restore, downgrade, salvage, or full purge.

## Interfaces and Dependencies

The development package, fixture/build infrastructure, runtime qualification and T3 store modules now exist. Remaining module paths in this section are planned. Create `packages/software-factory/package.json`, lockfile, `tsconfig.json`, `src/`, `web/`, `test/`, `qualification/`, and `scripts/`. The development package produces `dist/cli.js`, library modules and web assets; generated `dist/`, dependency trees and test runs are ignored. Keep release artifacts outside installed skills until explicitly assembled. Add `skills/software-factory/SKILL.md`, `references/operations.md`, and a small `scripts/install.py` bootstrap for explicit release installation. Do not change provider hooks to drive the factory.

Use these internal module interfaces; they are not a public plugin SDK. Names may be refined without changing behavior, but reconcile callers and tests in the same task:

- `src/store.ts`: `openRepositoryStore(commonDir)` returns claim/check/release, atomic `admitAttempt`, `settleAttempt`, `appendCapture`, `finalizeInvocation`, and bounded `readHistory`/`readEvents`/`readCapture` operations. `src/schema.ts` owns versioned migrations, foreign keys, unique claim/resource and capture sequence indexes. Tables: runs, invocations, attempts, operations, allowance_ledger, worktrees, owner_claims, clearances, captures, capture_chunks, questions, maintenance_operations, notification_preferences, notification_deliveries, notification_acknowledgments, observation_events. Learning results use versioned captured JSON, not a separate registry.
- `src/lifecycle.ts`: `invoke(request, dependencies)` owns startup/admission barrier/shutdown/finalization; `src/workspace.ts` prepares/validates worktrees; `src/build.ts` resolves the shared compiler environment and builds once; `src/accounting.ts` validates operation keys (1-256 UTF-8 bytes, case-sensitive, run-local lineage) and correction allowances through store transactions.
- `src/workflow.ts`: expose `WorkflowContext` with `scope`, `agent`, `command`, `needsInput`, and `progress`. A workflow exports `run(context, inputs): Promise<WorkflowResult>` plus an optional outline and input validator. Every managed call names its operation key and optional prior attempt/loop lineage. Commands accept executable/argument arrays and explicit cwd/environment, never shell-concatenated untrusted input. User-authored shell commands require explicit command-shell selection. Pure functions need no instrumentation. No `resume`, durable sleep, task queue, or checkpoint interface.
- `src/profiles.ts`: `resolveStepInputs` computes field-wise precedence and captures actual supplied instructions. `src/adapters/types.ts`: `validateProfile`, `start`, streamed supported events, `requestStop`, and final launch/exit/result/child-control facts. Concrete adapters live in `src/adapters/{codex,copilot,gemini,opencode,pi}.ts`. Use child-process argument arrays and closed stdin unless a qualified machine protocol requires it. Capability reports distinguish required failures from optional gaps.
- `src/capture.ts` and `src/redaction.ts` own bounded decoding/filtering/backpressure; `src/native/process.ts` inspects live identity and stops only owned scopes. Keep live process handles. POSIX groups cover only members remaining in them; Windows direct-child termination is not proof of descendants. Manual clearance lives in `src/clearance.ts` and calls exact-claim store transactions.
- `src/dashboard.ts` serves loopback HTTP, bounded read endpoints and SSE; `src/notifications.ts` owns notice records/reminders, with native senders in `src/native/notifications.ts`. Use fixed-data osascript on macOS, notify-send on Linux, and `native/windows-notify/` for the accepted inbox WinRT helper. Its owned Start Menu shortcut/AUMID and local handler require qualification. Do not add Windows App SDK dependency or post-exit click guarantee.
- `web/index.html`, `web/app.ts`, `web/timeline.ts`, `web/inspector.ts`, `web/styles.css`: accepted run index/timeline/inspector. Render captured content inertly. Mutation endpoints permit only notification preferences/acknowledgment; protect them with same-origin checks and an unguessable host session token. Loopback is not permission to accept cross-origin requests. No execution, answers, clearance, delete, or install endpoint.
- `src/maintenance.ts`: `performMaintenance(request)` uses the same gate for operation-specific sequences; `src/install.ts` validates release manifest, hashes, ownership and staging. `src/learning.ts` validates source/evaluation/adoption record shapes. `src/cli.ts` parses explicit verbs and produces machine-readable JSON on request, diagnostics on stderr, with no prompt dependency.

Workflow result payload schemas remain workflow-specific. Shared needs-input envelope has `kind`, `question`, `context`, optional `suggestions`; factory assigns question/source IDs on save. Extraction results carry `examinedSources`, `captureLimitations`, `proposals` with local keys, target/diff/evidence/counterexamples/cases, or `noProposalReason`. Evaluation records exact baseline/candidate input references, cases, criteria, settings, attempt results and limitations. Adoption records approved identity/target/expected current revision, human approval reference, action result and confirmed applied identity only after successful application. References identify captured bytes or an exact revision, not only a mutable filename.

## Plan of Work

Tasks below form the development dependency graph. Each task consumes the inline behavioral contract and named predecessor artifacts. Stop at its stated outcome; passing component tests alone does not meet milestone acceptance. Shared store/schema, CLI/package files, test registry and release manifest edits must be serialized even for otherwise independent tasks. No agents or tasks are dispatched by creating this plan.

### Milestone 1: Reproducible development and runtime feasibility
Status: in progress
Acceptance: not met

#### T1: Package and fixture boundary

Prerequisites: separate execution authorization. Own `packages/software-factory/package.json`, lockfile, TypeScript/build/test configuration, `test/fixtures/`, `scripts/test-software-factory.py`, and the focused registry entry in `scripts/test-all.py`. Establish a fake non-interactive harness executable with controlled launch, streams, exit, children, questions, permission errors and crash pauses. It must never call a live provider. Add a disposable Git repository fixture with a committed file and uncommitted changes. Expose test scripts named `typecheck`, `build`, `test:store`, `test:lifecycle`, `test:adapters`, `test:workflows`, `test:web`, `test:notifications`, `test:learning`, `test:maintenance`, `test:qualification`, and `test:all`; unfinished suites must report missing implementation, not a green empty run. Stop when fixtures/build infrastructure and a meaningful fixture smoke test run in isolation. Verify `rtk proxy npm --prefix packages/software-factory run build` and fixture CLI tests. Do not install a target factory yet.

#### T2: Pin and qualify local storage prerequisites

Prerequisites: T1. Own `qualification/runtime.ts`, `qualification/runtime-manifest.json`, `qualification/runtime.md`, and storage probe tests. Read current official Node/SQLite source/docs during execution; select an exact LTS patch/artifacts and integrity hashes. Exercise built-in SQLite transactions, backup API, WAL fixes, contention, foreign keys, local placement, process-loss persistence, and bounded synchronous latency on native macOS/Linux/Windows targets. Do not silently substitute an addon, alternate backend or network filesystem. Promote the runtime pin only with recorded native evidence for declared targets. A missing target remains unqualified; independent portable work can proceed, but native release claims cannot. If the chosen approach cannot satisfy required semantics, stop dependent deployment work and present the concrete tradeoff. Verify `run test:qualification -- --area runtime`; this command must fail on missing prerequisites. Combined milestone proof: build plus pinned-runtime storage probes, preserving platform-specific results and limits.

#### T2-CI: Native qualification automation

Prerequisites: T1 and verified local T2. Authorized 2026-10-21. Add `.github/workflows/software-factory-qualification.yml` and qualification helpers/evidence for native Linux, Windows and macOS. Pin the reviewed Node/artifact/tool versions, use disposable repositories, preserve logs and JSON evidence even on failure, fail on missing prerequisites, and keep untrusted pull requests credential-free. Current foundation checks must remain explicit about unfinished product suites. Extend the workflow as later tasks land; final T17 requires the complete supported suite, not only foundation smoke tests. Add separately triggered authenticated-provider qualification only with explicit configured CI credentials and bounded harmless cases; never expose credentials to fork code or run live desktop notices early.

Native filesystem detection and signal semantics must be qualified honestly on each host; update portable mechanisms from evidence instead of excluding a failing platform or weakening tests. Windows/POSIX-specific resource tests require equivalent native evidence or visible pending qualification. Creating workflows does not establish a hosted pass. Hosted execution requires these commits on a remote branch; no push has yet been requested or performed. Implementation evidence: reviewed commits `3c86993d` and `764f559b` fast-forwarded onto base. Actionlint 1.7.12 passed. After shared placement/store and registry integration, pinned Node 24.22.1 typecheck/build, 29 store/capture/placement/composed checks, six fixtures and four runtime/CI contract checks passed. Windows WAL byte-lock write denial remains a candidate native fixture until hosted execution proves it; POSIX file-size failure coverage remains intact. Details are in `packages/software-factory/qualification/ci.md`.

### Milestone 2: Durable facts without durable execution
Status: done
Acceptance: met

#### T3: Store, ownership and accounting

Prerequisites: T1 and T2's validated storage mechanism on the development host; other targets remain qualification gates. Own `src/schema.ts`, `src/store.ts`, `src/accounting.ts`, `test/store.test.ts`. Implement the table/transaction contract, installation/worktree identity, resource-specific admission, exact-token release, lineage and initial/additional debits. Tests must use separate processes contending for the last capacity slot, same worktree, dashboard and maintenance gate. Crash before/after admission and uncertain commit acknowledgment cannot double debit or fabricate unused allowance. Clearances atomically save basis and release only inspected ownership; known-live refusal remains. Stop at transaction-level functionality. Verify `run test:store`.

#### T4: Bounded saved capture

Prerequisites: T3. Own `src/capture.ts`, `src/redaction.ts`, `test/capture.test.ts`. Preserve text/JSON chunks and explicit completeness; implement state/event atomicity and bounded readers. Exercise split UTF-8, split secrets, huge lines, oversized control JSON, slow writers, disk-full failure, duplicate sequence and missing/pruned references. Capture may backpressure managed streams but never silently truncate or delete history. Stop at recorder/read APIs; no browser or harness protocol. Verify `run test:store` with capture coverage. Combined proof: concurrent writers with failure injection maintain bounded memory, single debits, committed-only events and preserved evidence.

### Milestone 3: Foreground commands, interruption and explicit follow-up
Status: in progress
Acceptance: not met

#### T5: Workspace and current-script invocation

Prerequisites: T3, T4. Own `src/workspace.ts`, `src/build.ts`, `src/workflow.ts`, startup paths in `src/lifecycle.ts`/`src/cli.ts`, `test/startup.test.ts`. Implement committed-only new worktree and explicit existing-worktree reuse, shared toolchain validation, one invocation build and command operations. Missing dependencies instruct explicit installation without downloading; conflicting resolution scaffolding refuses replacement. Validate selected question/context references and same-run operation lineage. A command-only workflow records output and completes in its worktree. Verify `run test:lifecycle`, including relative imports, selected worktree authoring inputs, untouched dirty source, no phase after build failure, and no reset on reuse. Stop before real harness adapters.

#### T6: One shutdown path and manual clearance

Prerequisites: T5. Own finalization in `src/lifecycle.ts`, `src/native/process.ts`, `src/clearance.ts`, `test/shutdown.test.ts`. Serialize stop/admission; save questions before cleanup; retain peer results and distinguish independent failure from requested interruption. Bound grace and stop only verified live owned scopes. Finalize uncertainty with blocked ownership/capacity rather than waiting indefinitely. Add explicit `inspect-owner` and `clear-owner` CLI paths requiring exact claim and operator note/confirmation, with machine versus operator basis retained. Verify `run test:lifecycle` through separate-process kill points, escaped children, PID reuse/inaccessible identity, manual release races, failed save/release, SIGINT/SIGTERM statuses and preserved files. Stop after command/fake-harness lifecycle proofs. Combined proof starts a fresh invocation after explicit safe clearance, verifies current script entry and retained additional allowance, and proves no automatic restart.

### Milestone 4: Honest non-interactive harness adapters
Status: open
Acceptance: not met

#### T7: Input resolution and shared conformance

Prerequisites: T6. Own `src/profiles.ts`, `src/adapters/types.ts`, fake adapter and `test/adapters.test.ts`. Implement the field replacement/composition rules, effective-input capture, required capabilities, unambiguous result channel, and fresh-versus-correction session policy. Permission denial or unexpected interaction cannot widen permissions, inherit a terminal or become fabricated needs-input. Test launch counts proving no retry/fallback, fresh review/later sessions, compatible correction reuse and fresh fallback only for unsupported conversation reuse. Verify `run test:adapters`. Stop at the common contract and fixture proof.

#### T8: Provider-specific modes

Prerequisites: T7. Split before assignment into T8-codex, T8-copilot, T8-gemini, T8-opencode, T8-pi; each owns only its adapter, provider fixtures, and `qualification/<provider>.md`. No provider depends on another; each consumes the same T7 conformance contract. For each, inspect current official CLI protocols/version, choose the non-interactive machine mode and record exact arguments/permissions/schema/stop semantics. Implement parsing, stream mapping, native session identity and reported child parentage only where reliable. Qualify an explicitly authorized harmless live call in a disposable repository, permission denial, malformed result, stop, unknown telemetry, and same-invocation correction. Never infer loaded skills from requested filenames or expose private reasoning not emitted by the provider. Verify `run test:adapters -- --provider NAME`, then `run test:qualification -- --area adapter --provider NAME` with credentials supplied outside code/logs. Missing credentials are a blocked native proof, not a passing adapter. Stop each task at its exact mode evidence. Combined milestone proof runs common scenarios through each supported mode and records unsupported combinations without silently dropping desired harnesses.

### Milestone 5: Useful customizable workflows
Status: open
Acceptance: not met

#### T9: Change and audit recipes

Prerequisites: T7 and at least one qualified T8 mode for live acceptance; fake-mode checks can proceed after T7. Own `templates/workflows/change.ts`, `templates/workflows/audit.ts`, prompt/profile templates, and `test/workflows.test.ts`. Support prompt/prose/structured plan inputs, optional planning, implementation, configured commands, independent review, and bounded corrections in ordinary code. Audit must demonstrate different scopes/branches without implementation assumptions. Keep agent-led browser verification off unless explicitly enabled; deterministic selected E2E commands remain ordinary checks. Stable candidate checks gate review and repairs cannot overlap reviewers. Invalid control output permits one format correction without code-edit rights; valid needs-input never triggers format correction. Infrastructure failure never becomes quality correction. Verify `run test:workflows`, including two corrections then exhaustion, twenty additional attempts across joined history, changed later-step inputs, no-op repairs, optional skipped work and fresh reviews. Combined proof completes one harmless live change and read-only audit, with check/review evidence and no publication. Stop before learning workflows.

### Milestone 6: Accepted live and historical UI
Status: open
Acceptance: not met

#### T10: Observation host

Prerequisites: T4, T6. Own `src/dashboard.ts`, history routes and `test/dashboard.test.ts`. Claim/publish a verified loopback endpoint, reuse only matching repository/claim host, serve committed cursor pages and capture chunks, handle slow clients/gaps/disconnection. Do not keep SQLite read transactions open while waiting on clients. Reject cross-origin mutation requests and require host session credentials for notification writes. Browser reads cannot execute workflows. Verify `run test:web -- --suite server`; stop at server/API proof.

#### T11: UI implementation

Prerequisites: T10; fixtures use T9 scenario shapes but do not require live T9 execution. Own `web/` and `test/browser/`. Rebuild the accepted dark layout from `docs/software-factory/prototypes/observability-prototype.html` as production modules; do not copy its synthetic timers, alert dialogs or local feedback tools into runtime behavior. Run cards select invocations; timeline nests supported children; inspector shows request/result/events and collapsed inputs/accounting/files. Keep outcome, cleanup basis, capture and connection separate. Preserve focus, selection/text and reading position under updates, Back/Forward and collapse; invalid links show an error rather than another record. Provide equivalent keyboard/screen-reader text navigation and inert captures. Freeze pins a saved cursor; scrolling away suspends follow with a new-events count.

Use system sans, 14px body, 24px main heading, 18px sections, 12px compact metadata, 8px spacing increments and 16-24px panel padding. Preserve colors `#0e1622`, `#162130`, `#e4ebf5`, `#adbbcd`, `#75d5e1`, `#e7c47d`. Cards use three columns above 1150px, two above 650px, one below; inspector stacks below 850px. Enforce 4.5:1 text/3:1 meaningful controls contrast and visible focus, minimum 24px targets or spacing. At 390px and 200% zoom, only the labeled timeline may scroll horizontally. Respect reduced motion.

Use 30 cards, 50 lane rows and lifecycle-bounded event/capture pages, not an unbounded DOM or new search service. Explicitly show loading, no runs, empty filter, unreadable store, partial/pruned capture, missing external file, disconnected maintenance and stale uninstalled host. Storage displays measured sizes/time/growth without a collector daemon. Verify `run test:web -- --suite browser` plus manual keyboard/screen-reader/zoom and visual inspection. Combined proof uses real recorder/SSE data, reconnect duplicates/gaps, 10,000 runs, 1,000 sessions/invocation, 100,000 events, nested children and multi-MB output. Measure p95 display latency against the accepted one-second target under recorded load; failure cannot be hidden by weakening data/acceptance. Stop with browser evidence; no execution controls.

### Milestone 7: Attention without interactive workflows
Status: open
Acceptance: not met

#### T12: Notification delivery and metadata

Prerequisites: T6, T10; browser controls integrate after T11. Own `src/notifications.ts`, `src/native/notifications.ts`, `native/windows-notify/`, and `test/notifications.test.ts`. Implement runner initial summary, five-second bounded sender, saved submission/failed/timeout/unknown states, and host-only opt-in grouped reminders. Implement fixed-data macOS/Linux senders and the older inbox Windows WinRT executable with owned shortcut/AUMID and any required local handler. Defer their live desktop qualification to T17-desktop, as requested on 2026-10-21. Windows helper language/toolchain is selected from verified native feasibility, not an implied App SDK dependency. Native tests need desktop sessions; headless success cannot establish visible delivery. Record manual visible-delivery evidence separately from submission.

Verify deterministic `run test:notifications` now; run native `run test:qualification -- --area notifications` only at T17-desktop, including XML/shell-special text as data, missing service, timeout, denied delivery, five-second helper exit, host restart full interval, multiple tabs one sender, acknowledgment persistence and no workflow mutation. Combined proof causes needs-input plus cleanup uncertainty, retains both in CLI/UI despite unavailable desktop delivery, and sends no repeated reminder by default. Stop at bounded basic alerts; no click activation service.

### Milestone 8: Traceable learning through existing workflows
Status: open
Acceptance: not met

#### T13: Extraction and evaluation

Prerequisites: T9 and T4; UI integration after T11. Own `src/learning.ts`, `templates/workflows/learn.ts`, `templates/workflows/evaluate.ts`, `test/learning.test.ts`. Implement explicit ended-source selection and the captured JSON shapes above. Evaluation uses exact candidate/baseline inputs in isolated work without changing active configuration. Record examined versus unexamined sources, no proposals, contradictory cases, partial data and inconclusive results. No schedule, automatic hook, replay, registry or global trial count. Verify `run test:learning`; stop at reports and reviewable candidate diffs.

#### T14: Adoption and revert provenance

Prerequisites: T13. Own adoption validators/evidence in `src/learning.ts` and operations documentation/templates. Use ordinary explicitly authorized authoring/install paths; validate approved candidate, target scope and expected target content before application. Record approval independently from observed applied revision and failures. Revert is explicit version control plus recorded provenance, not a rollback daemon. Test changed target, broader scope without authorization, approved-but-not-applied, failed/uncertain action and actual revert. Verify `run test:learning`. Combined proof follows extraction, inconclusive evaluation, revised evaluation, explicit test-fixture approval/application and revert while preserving sources. Do not adopt a real user prompt or skill as part of qualification.

### Milestone 9: Explicit installation and safe idle maintenance
Status: open
Acceptance: not met

#### T15: Release bundle and initial installation

Prerequisites: T2, T6, T9, T10, T11 and T12's helper packaging contract. Own `src/install.ts`, bootstrap parts of `src/maintenance.ts`, `packages/software-factory/scripts/package-release.ts`, `skills/software-factory/`, and `test/install.test.ts`. Package only built runtime/web/helper/templates with versioned manifests and integrity hashes; do not copy development node_modules into a published skill. The bootstrap explicitly obtains/verifies selected release and pinned Node platform asset, initializes the Git-common-directory factory store with a bootstrap exclusion marker, and creates authoring templates only when absent. Refuse symlink/mismatched/unowned collisions; never overwrite user customization. Distribution URL/version must be supplied by an actual release manifest, not guessed here. No release publication occurs without separate authorization.

Use one isolated installed dependency environment per repository. Explicit dependency maintenance installs declared packages/lock under the idle gate; startup merely validates compatibility. Keep application dependencies separate. Verify `run test:maintenance -- --operation install` on disposable homes/repos, offline/missing artifacts, interrupted bootstrap, dirty source, and template preservation. Test generic skill copy through existing installer suites in their disposable fixtures; do not run account-wide installers on the user's home. Stop at repeatable initial install and startup.

#### T16: Maintenance operations

Prerequisites: T15, T3, T4. Split before assignment into T16-upgrade (upgrade/dependencies/forward repair), T16-uninstall, and T16-cleanup. Serialize all edits to `src/maintenance.ts`; each consumes shared admission/controller staging and contributes operation-specific `test/maintenance-*.test.ts`.

T16-upgrade owns consistent verified backup, preparation/modifying/validating markers, transactional migration markers, intended-version reinstall, and validation before gate release. Preserve untrusted/corrupt data and block without salvage or downgrade. T16-uninstall depends on T16-upgrade's controller survival/incomplete-operation mechanism, removes manifest-owned installation and native shortcut files only, marks absent, and supports explicit interrupted completion. T16-cleanup depends on T16-upgrade and T14's learning reference shapes; show exact history/backup selections, space estimates and learning dependencies; confirm exceptional deletion under idle exclusion; batch prune with operational facts/questions/lineage retained; protect recovery backups; compact only with sufficient temporary space. A failed compaction cannot recreate storage or automatically delete more files.

Verify each with `run test:maintenance -- --operation upgrade`, `uninstall`, or `cleanup`. Stop each at its operation evidence. Combined proof races each operation against runner/dashboard/other maintenance starts, injects failures around database/file transitions, and verifies explicit forward recovery, preserved data and no gate release on incomplete state.

### Milestone 10: Integrated qualification and delivery readiness
Status: open
Acceptance: not met

#### T17: Native and packaged acceptance

Prerequisites: every preceding task and integration check. Own `qualification/support-matrix.json`, `qualification/report.md`, release acceptance fixtures, and final documentation reconciliation. Exercise installed packages on native macOS/Linux/Windows with exact runtime/OS/harness/helper versions and capabilities. Test real process stop/identity limits, manual unsupported-child cleanup, SQLite process-loss/contended writes and backups, native helper install/update/uninstall, user-facing CLI/UI history and bounded load. Destructive power-loss tests require disposable machines; never perform them on this workspace. Missing native access/credentials is blocked evidence and must remain visible.

T17-desktop runs the deferred live notification tests last, on suitable desktop sessions, after T12/helper packaging and other implementation acceptance. Headless CI submission cannot establish visible delivery.

Run the complete local deterministic suite, browser suite, native qualification, existing affected installer suites and root registered checks. Record outputs and retained limitations in the support matrix. No adapter/platform is supported merely because a fake test passes. If a desired mode cannot meet required permissions/result/stop behavior, return that specific consequential conflict; do not silently downgrade or reintroduce removed machinery. Stop at reviewable release readiness. Publishing, installing into real user repositories, or applying learning changes still requires authorization appropriate to those actions.

## Concrete Steps

**Current next action: finish the independently reproduced T5 asynchronous-context repair, review and integrate invocation startup, then implement T6 shutdown/manual clearance.** T2-CI workflows are integrated; hosted execution remains pending, with no push performed. Commands below remain expected instructions until evidence is recorded. Paths and npm script names are task deliverables.

Completed T1 setup: the package and lockfile exist, with development dependencies explicitly installed using `npm ci --ignore-scripts`. Repeat setup only when needed with `rtk proxy npm --prefix packages/software-factory ci --ignore-scripts`; startup never installs. Typecheck/build commands now produce `packages/software-factory/dist/cli.js`. Exact dependency versions are in the lockfile.

Observed T1/T2 evidence (2026-10-21): `rtk proxy python3 scripts/test-software-factory.py --suite fixtures` passed typecheck, build and six fixture/CLI checks. `rtk proxy python3 scripts/test_test_all.py` passed 14 checks. The official darwin-arm64 archive SHA256 matched the downloaded release checksum list; extracted v24.22.1 reports SQLite 3.53.4. Pinned-runtime `run test:qualification -- --area runtime` passed. See `packages/software-factory/qualification/runtime.md` for exact commands, metrics and native limitations. `run test:all` fails at the first unimplemented suite (now `lifecycle`); aggregate acceptance remains unmet. T3 verification: pinned-runtime `rtk proxy python3 scripts/test-software-factory.py --suite store` passed typecheck/build and eleven store tests. Public cross-process tests cover final slot/allowance, worktree/dashboard/maintenance exclusion, and process loss before/after admission. Independent review reproduced two post-clearance recovery bugs; fresh follow-up now accepts cleared unknown outcomes, and stale settlement cannot resurrect occupancy. Both repairs passed independent re-review. Native process inspection remains T6, not a claim of T3.

Observed T4 integration evidence: clean worker branch `codex/factory-capture` rebased without changes and fast-forwarded onto base at `676ba5f1`. Pinned-runtime `rtk proxy python3 scripts/test-software-factory.py --suite store` passed typecheck/build and all 27 registered storage/capture/composed tests. Capture documentation is `packages/software-factory/qualification/capture.md`; schema is now version 2 and older stores require explicit future maintenance. No automatic migration ran. Local milestone-2 acceptance is met; Linux/Windows and final native release acceptance remain unmet.

For each verification shorthand `run NAME` above, execute `rtk proxy npm --prefix packages/software-factory run NAME` from repository root, appending supplied `--` options. T1's test dispatch must forward filters consistently and fail when a selected suite/provider/operation has no tests. `test:all` runs deterministic and browser tests; `test:qualification` is explicitly separate because it requires native machines, credentials/desktop access and potentially paid harmless calls. Do not run live qualification without its prerequisites and authorization.

The development CLI example below uses the qualified Node on PATH. Installed scripts instead invoke their manifest-owned absolute Node path and never depend on a global runtime. In a disposable fixture repository created by T1, the intended surface is:

    node /absolute/source/packages/software-factory/dist/cli.js invoke --repository /absolute/fixture --workflow .factory/workflows/audit.ts --input /absolute/fixture-input.json --new-worktree --ref HEAD --json
    node /absolute/source/packages/software-factory/dist/cli.js history --repository /absolute/fixture --invocation INVOCATION_ID --json
    node /absolute/source/packages/software-factory/dist/cli.js dashboard --repository /absolute/fixture

Input example: `{"request":"Report tracked files without editing them"}`. Expect structured run/invocation/worktree identities, saved command/harness results and a verified loopback dashboard URL. A clean audit exits 0. A fixture needs-input returns exit 2 only with complete cleanup and saves question/context. Follow-up uses `invoke --run RUN_ID --worktree WORKTREE_ID --input ANSWER_FILE` with explicit current workflow selection, starts fresh from entry and retains accounting. IDs come from previous output, never guessed. `inspect-owner` prints exact claims; `clear-owner --claim CLAIM_ID --operator-confirmed --note NOTE` refuses positively live owners and saves operator basis. No automatic clearance occurs merely from invoking again.

Maintenance commands are explicit `install`, `dependencies`, `upgrade`, `repair`, `uninstall`, and `cleanup` verbs. Mutating selection commands first describe exact owned targets and accept explicit supplied confirmation, supporting non-interactive invocation without implicit destructive defaults. Runtime `invoke` has no automatic install/repair side effects. Exact argument help must be covered by CLI tests before documenting installed commands as working.

## Validation and Acceptance

Task checks use disposable repositories/homes and public CLI/store/host interfaces. Required negative cases are in the milestone prose and shared contract, not optional stretch work. Use fake harnesses for deterministic state races and real native calls only to prove adapter capability. Each integrated milestone records version, command, exit status, important output and artifact location. Store bulky logs in ignored `packages/software-factory/test-results/`; retain concise sanitized findings under `qualification/`. Never record credentials or assert that submitted desktop alerts were seen without evidence.

The final end-to-end scenario begins from a dirty source checkout with a committed tiny project. Install explicitly into a disposable repository. Start a prompt/prose-plan change, see the pre-phase isolated workspace, implementation children where supported, stable-candidate checks and independent review, bounded repair, then saved final report. Confirm source edits/index untouched and local candidate preserved without a PR. In separate scenarios, end on a saved question, interrupt before finalization, lose recorder storage, and expose unsupported child shutdown. The UI must show questions/unknowns/cleanup separately; explicit operator clearance and a fresh invocation preserve evidence and allowance. A second same-worktree invocation is refused, while separate worktrees share capacity. Learning uses these ended records, does not discard them or change active inputs, and records exact authorized adoption provenance only in fixtures.

Repository regression commands after affected code exists: `rtk proxy python3 scripts/test-software-factory.py` (T1 adds it), `rtk proxy bash scripts/test-install.sh`, and `rtk proxy pwsh -NoProfile -File scripts/test-install.ps1` for installer impacts. Run `rtk proxy python3 scripts/test-all.py` on supported macOS/Linux coordinator hosts after integration. On native Windows run the focused package and PowerShell suites directly. Missing Python, PowerShell, Node, browser or native desktop prerequisite is an environmental block, not an ignored test. Activate required source/skill validation routes when those files are actually changed. Complete one coordinated update-agent-docs pass at the end of implementation; canonical KB edits require their OKF/link checks.

Historical plan-authoring evidence on 2026-10-20: inspected the accepted baseline, lifecycle/UI contracts, profile/review/learning requirements, existing research ExecPlan and installer/test-registry entry points. At authoring time no implementation test had run. Structural task-dependency, required-section, status/progress, local-document link and whitespace checks validate this document only.

## Idempotence and Recovery

For development, rerun build/tests against disposable fixture directories, never user repositories. Test cleanup removes only fixture paths created and recorded by that test. Do not reset the working tree or delete user files to repair a failed run. Preserve failed outputs and reproduce the specific public behavior before fixing bugs. Never weaken a test or requirement to make a milestone green.

For factory invocations, repeat means a new explicit invocation with current inputs and fresh conversations, not replay. Unknown launches retain charges and block unsafe capacity/worktree reuse until established quiescence or accepted operator clearance. Known-live owners refuse clearance. Capture/store failure stops work without resetting history. Retain partial worktrees and required source facts.

For maintenance, only failed preparation with a still-validated original installation may release admission for continued use. Interrupted modification remains blocked. The operator explicitly runs repair/completion against the recorded intended operation after clearing an inactive/confirmed owner. Replay only missing migration steps by committed markers; never replay external workflow actions. Incompatible/corrupt schema or unavailable intended installer preserves data and requires a consequential recovery decision outside automatic salvage. Backups survive until selected idle cleanup, including after success. Uninstall preserves user history/worktrees and leaves staged controller files for later explicit cleanup if the running executable cannot remove itself.

For this plan, the historical research snapshot is retained unchanged except its explicit historical wrapper. Future scope changes must reconcile active contract, task dependencies, Progress, milestone states, commands and recovery together. A link to an old plan is never authorization.

## Artifacts and Notes

- Accepted baseline: [final specification acceptance](tickets/specification-readiness-and-acceptance.md#resolution), [decision map](map.md), [lifecycle mechanisms](lifecycle-specification.md), [detailed UI](observability-ui-specification.md).
- Visual reference only: [accepted prototype](prototypes/observability-prototype.html). Synthetic browser checks do not establish runtime performance, native behavior, accessibility certification or SSE correctness.
- Historical records: [research plan snapshot](ExecPlan.history-2026-10-20.md) retains completed research/prototype evidence and superseded recommendations. It is not an execution dependency.
- Resume state: [feature handoff](handoff.md). Implementation is authorized; T1, local T2, T3 and T4 are verified; CI automation is integrated and T5 is in review repair; native milestone acceptance remains unmet.
