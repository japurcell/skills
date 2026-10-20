# Customizable software factory

## Destination

An implementation-ready specification for a fully customizable, code-controlled agentic factory: its workflow and task contracts, execution model, skill installation, live session UI, and improvement process are decided well enough to implement and test.

## Notes

- Completed on 2026-10-20 after explicit final specification acceptance. All twenty-six tickets are closed; no planning frontier remains. The accepted SSSF-inspired baseline and qualification obligations are retained. Implementation requires a separate request.

- This is a planning map. The user chose this destination on 2026-10-12. The earlier Restate prototype and durable SQLite executor direction are superseded by the SSSF-style foreground runner; implementation remains outside this planning session.
- Consult wayfinder and the narrow skills needed for the selected ticket. Use grilling plus codebase-design for design conversations. The user explicitly approved this substitute for the unavailable domain-modeling skill on 2026-10-12.
- Consult prototype for a prototype ticket and research for a research ticket. Research tickets require an assigned research directory and a delegated researcher. No new research was launched merely to repeat the retained studies.
- Work one decision ticket per session, except delegated research. Claim its file before work. Check the exact filenames in Blocked By; only closed prerequisites unblock it. Human decisions require a live exchange.
- Closed requirements imported below come from the prior conversation. Before asking a question, reconcile it against prior human answers and the owning tickets. Record an established answer without asking the user to decide it again. Assistant recommendations and examples are not human decisions; only ask about unresolved choices or an actual conflict. This standing instruction was explicit on 2026-10-12.
- Discover open sessions by searching the tickets directory. The map deliberately does not duplicate the open-ticket list.
- Preserve quality, simplicity, robustness, scalability, and long-term maintainability over development cost.
- On 2026-10-15 the user explicitly directed: prefer removing optional complexity over designing more machinery. Test whether a capability is needed before refining its mechanisms. Present consequential scope changes explicitly; do not silently revoke accepted behavior. Derive routine record fields, command names, and exit codes from accepted contracts rather than turning every implementation detail into another feature decision.
- On 2026-10-15 the user clarified that proposed simplifications must actually reduce complexity. Evaluate the complete replacement and retained correctness requirements against available evidence; similarity to SSSF alone is not a reason to replace an accepted mechanism. The polling proposal was rejected and SSE reaffirmed in [Session events and live progress](tickets/session-events-and-live-progress.md#live-ui-reliability-unchanged-pending-discussion).
- Evidence entry points: [initial research](research.md) and [reviewable architecture documents](README.md). Source studies and simulations have different evidentiary limits.
- The user promoted this map and its tickets to `docs/software-factory/` on 2026-10-12 for version control. Resume wayfinder in this directory; do not recreate a scratchpad map.
- The [handoff](handoff.md) tracks current progress, verification limits, and the next session. Keep decision details in their owning tickets.

## Decisions so far

- [Specification readiness and acceptance](tickets/specification-readiness-and-acceptance.md#resolution): completed design baseline accepted, all twenty-six decisions closed, qualification obligations preserved, and no implementation authorized.

- [Detailed observability UI design](tickets/detailed-observability-ui-design.md#resolution): refined prototype and detailed interaction/accessibility/scale contract accepted; outcome, cleanup, and capture remain distinct, with observation-only controls and supported child visibility.

- [Invocation lifecycle and interrupted work](tickets/recovery-and-runtime-selection.md#resolution): concrete foreground lifecycle, retained accounting/history, shared ownership and idle maintenance, honest manual cleanup, and the older inbox Windows notification API. The [lifecycle specification](lifecycle-specification.md) defines mechanisms and future qualification gates; no durable resume or implementation is added.

- [Lifecycle platform constraints](tickets/lifecycle-platform-constraints.md): source research bounds process-group/direct-child control, Windows basic-alert deployment alternatives, and local SQLite recording/backup/compaction. Native tests remain pending; notification adoption stays in the lifecycle decision.

- [Confirmed factory requirements](tickets/confirmed-factory-requirements.md): code-owned deterministic flows, fully customizable workflows, per-step agent choices, skill installation, and real-time session visibility.
- [Workflow authoring and task contract](tickets/workflow-authoring-and-task-contract.md): TypeScript routines [build once per invocation](tickets/recovery-and-runtime-selection.md#accepted-workflow-build-and-loading) and use managed steps; prose and structured plans feed implementation phases; managed operations and observed child sessions expand declared outlines without a task scheduler.
- [Local runtime prerequisites](tickets/local-runtime-prerequisites.md): Restate requires its server; DBOS TypeScript requires Postgres. Neither establishes an embedded-only TypeScript setup or proven native Windows packaging.
- [Embedded graph runtime fit](tickets/embedded-graph-runtime-fit.md): LangGraph Functional API best matches the accepted authoring interface; Mastra is a graph-builder alternative. Local storage, crash recovery, and native Windows still require proof.
- [Embedded workflow runtime fit](tickets/embedded-workflow-runtime-fit.md): Effect offers an explicitly embedded SQL-backed composition with unstable APIs; TanStack needs a local durable store. Workflow DevKit Local World is development/testing infrastructure, and Resonate's default SDK is not persistent.
- [Restate and DBOS operating fit](tickets/service-engine-operating-fit.md): Restate retains a server and native Windows gap; DBOS TypeScript retains Postgres and packaging constraints. DBOS Python supports SQLite but changes the workflow-language contract. The [combined comparison](research/embedded-runtime-comparison.md) retains the research that preceded the user's executor decision.
- [Managed runtime and SQLite packaging fit](tickets/runtime-and-sqlite-packaging-fit.md): source research compares Node built-in SQLite, better-sqlite3, and Bun; Node built-in SQLite avoids a native addon but remains release candidate. The subsequent [Node LTS and built-in SQLite decision](tickets/recovery-and-runtime-selection.md#accepted-node-lts-and-built-in-sqlite) is accepted; native qualification remains pending.
- [Operating and installation model](tickets/operating-and-installation-model.md): per-repository foreground runner, skill-managed pinned Node LTS with built-in SQLite, SQLite observability history, interruption without durable resume, idle-only managed upgrades under the [accepted shared maintenance gate](tickets/recovery-and-runtime-selection.md#accepted-shared-repository-maintenance-gate), [explicit backup retention/cleanup](tickets/recovery-and-runtime-selection.md#accepted-upgrade-backup-retention), [explicit shared dependency installation](tickets/recovery-and-runtime-selection.md#accepted-workflow-dependency-installation), [shared ownership mechanics](tickets/recovery-and-runtime-selection.md#accepted-shared-ownership-mechanism), and [idle, data-preserving uninstall](tickets/recovery-and-runtime-selection.md#accepted-uninstall-through-the-maintenance-gate) without built-in full purge.
- [Agent execution profiles](tickets/agent-execution-profiles.md): non-interactive calls with explicit permissions/configuration and selected-profile-or-failure behavior, visible sessions and compatible correction reuse within an invocation, fresh sessions for later invocations, replacement with explicit instruction composition, and schemas for agent outputs that control execution.
- [Live progress transport fit](tickets/live-progress-transport-fit.md): protocol research supporting SSE observation; saved-event catch-up, applied cursors, and deduplication concern the UI, not workflow replay. The live-progress ticket owns adoption.
- [Session events and live progress](tickets/session-events-and-live-progress.md): saved-before-display SSE updates, an independent repository dashboard, full captured history retained for traceable learning with exceptional idle-only cleanup, supported nested child activity, custom progress events, and interruption on recording failure; one-second display target remains to be tested.
- [Run workspace and implementer delegation](tickets/task-scheduling-and-integration.md): one run worktree before all phases, created only from committed revisions, with one active invocation per worktree; implementer-owned subagents; stable candidate handoff, conditional child visibility, and no factory task scheduling or integration.
- [Verification and review policy](tickets/verification-and-review-policy.md): structured results, checks, review phases, and bounded corrections on one stable candidate; generic reviewer aggregation and criterion-evidence machinery removed; managed-attempt limits retained.
- [Codex permission feasibility](tickets/codex-permission-feasibility.md): historical native approval-bridge feasibility; superseded as a product requirement by non-interactive calls. Platform behavior still needs tests.
- [Copilot and Gemini permission feasibility](tickets/copilot-gemini-permission-feasibility.md): historical structured approval-route research; live mediation is no longer required. Non-interactive policy equivalence still needs proof.
- [OpenCode and Pi permission feasibility](tickets/opencode-pi-permission-feasibility.md): historical approval-route research; dialogs alone do not prove permission enforcement. Non-interactive profiles require separate validation.
- [Human input and execution controls](tickets/human-control-and-publication.md): non-interactive permissions, structured needs-input exits, human decisions between invocations, and attention notifications; no live approval bridge or managed publication.
- [Desktop notification delivery fit](tickets/desktop-notification-delivery-fit.md): source research distinguishes basic alerts from optional hyperlinks and registered app activation after sender exit. Research adopts no native delivery mechanism. The subsequent [optional-link decision](tickets/recovery-and-runtime-selection.md#accepted-optional-notification-links) retains CLI/dashboard access to saved details; native behavior remains untested.

- [Swimlane interaction design](tickets/swimlane-interaction-design.md): accepted run cards, owner/session timelines, and phase details beneath the timeline; detailed visual and interaction design has a separate follow-up ticket.

- [Workflow versioning and run changes](tickets/workflow-versioning-and-run-changes.md): current-script entry-point invocation, optional history and saved-input reuse with fresh native conversations, and step-start resolution of settings/prompts/skill inputs; no durable resume or retained executable versions.

- [SSSF approvals and lifecycle comparison](tickets/sssf-lifecycle-comparison.md): pinned-source study confirms no live human question/approval round trip, polling-based observation, limited child cleanup, and template-stamping installation; the later human-input amendment adopts non-interactive calls; other differences remain explicit.

- [Skill and prompt improvement](tickets/skill-and-prompt-improvement.md): explicit source-linked extraction, bounded comparative evaluation through existing workflows, human approval of the exact change/target, ordinary revision/revert history, and preserved learning evidence.

## Not yet specified

<!-- FOG START -->
None within the accepted specification scope. Concrete future qualification conflicts or extension requests may require new decisions; they do not keep this completed map open.
<!-- FOG END -->

## Out of scope

- Built-in full repository factory purge, removed by [the accepted full-purge decision](tickets/recovery-and-runtime-selection.md#accepted-removal-of-built-in-full-purge). Data-preserving uninstall and exceptional selected history/backup cleanup remain; complete removal is documented manual operator work.

- Built-in installation downgrade migrations and general database salvage, excluded by [forward-only explicit upgrade repair](tickets/recovery-and-runtime-selection.md#accepted-forward-only-upgrade-repair). Backups remain available for informed manual recovery; no automatic history restoration.

- Factory-level automatic infrastructure retries for managed agent calls and commands, removed by [Verification and review policy](tickets/verification-and-review-policy.md#no-factory-level-automatic-infrastructure-retries). Bounded quality/format corrections and explicit follow-up invocations remain.

- Factory-managed automatic profile fallback chains, including preconfigured harness/model/skill-delivery substitutions, removed by [Agent execution profiles](tickets/agent-execution-profiles.md#selected-profile-or-failure). Explicit per-step selection and later-invocation changes remain.

- Factory-managed native conversation reuse across invocations and separate native-resume recovery configuration, removed by [Agent execution profiles](tickets/agent-execution-profiles.md#invocation-scoped-correction-conversations). Supported compatible corrections may reuse conversations within one invocation.

- Capturing uncommitted source-checkout changes when creating a worktree, including file/hunk selection and dirty-content snapshot machinery, removed by [Run workspace and implementer delegation](tickets/task-scheduling-and-integration.md#committed-revision-only-worktree-creation). Existing factory-worktree reuse still preserves unfinished work.


- Live human waits, native question/approval callback mediation, live response/grant/withdrawal machinery, and routine human review gates, removed by [Human input and execution controls](tickets/human-control-and-publication.md#resolution). Explicit permissions and human decisions through later invocation inputs remain.

- Managed push/PR publication and its intent/reconciliation machinery, removed in [Human input and execution controls](tickets/human-control-and-publication.md#resolution). Custom workflows remain ordinary authorized code without a factory publication guarantee.
- Immutable registered-evidence capture/archival, removed in [Session events and live progress](tickets/session-events-and-live-progress.md#resolution); save traces, prompts, and outputs instead.
- Generic reviewer aggregation/adjudication, criterion-evidence registries, and evidence-reuse policy engines, removed in [Verification and review policy](tickets/verification-and-review-policy.md#resolution); structured results, checks, review phases, and bounded corrections remain.

- Factory-managed parallel implementation tasks, task dependency scheduling, per-task/integration worktrees, integration queues, and automatic dependency refresh, removed by [Run workspace and implementer delegation](tickets/task-scheduling-and-integration.md#resolution). Implementer-owned parallel subagents and their supported visibility remain in scope.

- Durable workflow resume, execution checkpoints/replay, old executable-version retention for unfinished runs, and suspended-run migration, explicitly removed by [Workflow versioning and run changes](tickets/workflow-versioning-and-run-changes.md#resolution). Durable observation history remains in scope.

- Building or deploying the factory, installing a runtime into target repositories, and executing the earlier Restate prototype during this map's charting session.
- Performing application changes, creating PRs, or applying skill/prompt improvements as a side effect of planning.
- Implementation task decomposition and rollout scheduling; these follow the specification unless the user explicitly changes this map's destination.

