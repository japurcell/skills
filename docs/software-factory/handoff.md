# Software factory handoff

Updated: 2026-10-14. Scope: software-factory.

## Goal and progress

Produce an implementation-ready specification for the fully customizable factory using the [Customizable software factory map](map.md). The earlier Restate prototype is superseded by the selected executor direction; implementation has not started.

- Done: initial source research, three interactive architecture documents, and capture of the user's confirmed requirements.
- Done: twelve closed tickets establish the requirements record, authoring contract, operating contract, execution profiles, local runtime prerequisites, three delegated runtime comparisons, the transport study, the live-progress contract, task scheduling/integration, and verification/review policy. The map has eighteen tickets: twelve closed, one claimed, and five open.
- Current: [Human control and publication](tickets/human-control-and-publication.md) is claimed by `subagent-h6p9k2`. All five first-round choices are accepted: no default checkpoint deadline, feedback routed to bounded repair, explicit recorded limit increases, GitHub first, and terminal Cancel alongside resumable Pause/Continue. The human renamed Stop to Pause; its interrupt-and-preserve behavior and Ctrl+C semantics are unchanged. Verification and review policy remains closed.
- Remaining: resolve the planning decisions and review specification readiness with the human. Ticket files own their statuses and resolutions; this handoff summarizes current progress.

## Next action

On the next planning continuation, resume the remaining branches of [Human control and publication](tickets/human-control-and-publication.md). All five first-round choices and the Pause rename are settled; no question is pending. Both exact prerequisites were verified closed on 2026-10-14. Checkpoint authorization and stale/duplicate responses, UI Continue reaching a foreground invocation, process-control mechanisms, and GitHub publication/reconciliation behavior remain unresolved. Do not silently turn the dashboard into a workflow supervisor or claim unverified remote guarantees. The latest naming question is answered without starting another question round or research dispatch.

Do not repeat accepted platform, per-repository installation, foreground invocation, dependency ownership, trust, offline, TypeScript-authoring, SQLite-executor, Continue, runtime-provisioning, upgrade-retention, Pause, Cancel, history-retention, uninstall, configuration-precedence, fallback-default, session-default, skill-delivery, minimum-telemetry, configured fresh-session recovery, instruction-composition, structured-result, save-before-display, one-second latency, recording-failure, independent-dashboard, retained-evidence, SSE-transport, or custom-progress-event questions. The user's primary and additional harness choices and per-step model/reasoning/skill/prompt configurability are already recorded.

The user approved grilling plus codebase-design as the substitute for the unavailable domain-modeling skill. Read prior conversation decisions before asking questions; record settled answers without asking again. Distinguish human decisions from assistant proposals. Resolve one design ticket per session; use exact dependency files to determine readiness. After a resolution, update its ticket, the map's decision index and fog, and this handoff.

## Decisions, proposals, and limits

The [Confirmed factory requirements](tickets/confirmed-factory-requirements.md) record owns the accepted requirements. Critical constraints are code-owned deterministic behavior, full workflow customization, per-step harness/model/reasoning/prompt/skill choices, skill installation, and a UI showing all sessions and steps in real time.

The closed [Workflow authoring and task contract](tickets/workflow-authoring-and-task-contract.md) owns the accepted TypeScript/managed-step interface, prose and structured plan intake, minimum task record, graph validation, ambiguity policy, nested scopes, and dynamically expanded outline. These answers are settled; do not ask them again.

The six-stage use case is a default recipe, not a fixed pipeline. Human review and interactive UI verification are configurable. The closed [scheduling resolution](tickets/task-scheduling-and-integration.md#resolution) owns task isolation, repository capacity, shared-resource policy, integration ordering, freshness, and review/repair write ownership. The closed [verification resolution](tickets/verification-and-review-policy.md#resolution) owns all fourteen accepted verification/review policies, including repair routing, format correction, elapsed-time limits, criterion-level evidence, and derived accounting/outcome obligations. Do not re-ask these choices. Clarification of ambiguous plans is not mandatory approval of every valid plan. Code-level nesting does not choose a runtime mechanism.

Preserve the limits' distinctions: code repairs have per-loop caps and additional agent attempts share a run-wide allowance; these do not promise a hard token/cost ceiling or bound all initial planned work. Attempt timeouts do not select human-checkpoint deadlines. Continue does not extend budgets, renew the same attempt's timer, or satisfy missing evidence. Detailed enforcement and authorized changes retain their downstream owners.

Preserve the scheduling distinction: a parked unintegrated candidate allows other eligible integrations; a combined result containing invalidated content pauses ordinary task starts and integrations until refresh establishes a current result. Unaffected active work may finish and queue. Refresh preserves work and evidence, observes existing budgets, and does not replace human-triggered Continue after interruption of the runner.

The [selected executor and continuation record](tickets/operating-and-installation-model.md#selected-executor-and-continuation) owns the latest decisions. A separate workflow server or database service is not part of the initial execution architecture. The factory owns durable execution and reconciliation. Continue selects an unfinished run; it does not implicitly approve a checkpoint or reset a repair budget.

The closed [operating resolution](tickets/operating-and-installation-model.md#resolution) owns skill-managed pinned runtime provisioning, retaining compatible runtime/workflow versions for unfinished runs, graceful interruption with resumable Pause, history retained until explicit cleanup, and data-preserving uninstall with separate purge. The [control decision](tickets/human-control-and-publication.md#accepted-pause-and-cancel-controls) owns the rename and terminal Cancel. Exact mechanisms remain with the linked downstream tickets. Do not convert those mechanism questions into renewed policy choices.

The closed [execution-profiles resolution](tickets/agent-execution-profiles.md#resolution) owns explicit configuration/fallback and session policies, required live output with optional rich telemetry, explicit skill delivery, instruction replacement with deliberate composition, and schemas for agent outputs controlling execution. Apply these without renewed questions.

The closed [live-progress resolution](tickets/session-events-and-live-progress.md#resolution) owns how sessions, events, and retained evidence are recorded and delivered through the independent repository dashboard. Human policies are explicit in its confirmed-answer sections; derived engineering obligations and acceptance cases support implementation. Exact recovery transactions, compatibility mechanisms, control authorization, and UI presentation retain their downstream owners.

Keep crash recovery, stale approvals, and duplicate publication in the acceptance discussion. [Recovery guarantees and runtime selection](tickets/recovery-and-runtime-selection.md) remains open and blocked for detailed mechanisms and acceptance; its engine-choice question is already answered. The illustrative method names, SQLite binding/layout, replay mechanism, fencing, and version migration are not finalized. No executor, CLI adapter conformance, real-time transport, native Windows support, or recovery behavior has been verified. Runtime implementation and publication remain outside scope.

## Evidence and verification

- [Initial research](research.md) and [review guide](README.md) contain the source studies and interactive documents. Their runs are simulations. The review guide includes the local preview command and prior UI validation scope.
- [Local runtime findings](research/local-runtime-prerequisites/findings.md) cite current official documentation for engine/storage prerequisites and packaging constraints. This was source research, not an installation, recovery test, or native-platform validation.
- [Combined runtime comparison](research/embedded-runtime-comparison.md) links three completed delegated reports and primary sources. Its earlier library recommendations are historical, not the selected direction. The research distinguishes SDK language from engine language and Continue selection from recovery mechanics; it proves no full platform/lifecycle contract.
- [Live progress transport findings](research/live-progress-transport-fit/findings.md) compare current browser protocol contracts using primary sources. Parent review corrected the latency measurement origin to factory receipt, including persistence/batching delay. The human subsequently selected SSE with separate controls; browser behavior, native packaging, and performance remain untested.
- [Earlier prototype handoff](handoff.history-2026-10-12.md) preserves superseded workflow sketches, failure scenarios, runtime references, and the preview command. It is historical evidence, not a current instruction to implement.
- The user explicitly placed this handoff in `docs/software-factory/`; keep it here. Its history was moved alongside it, and scratchpad copies were removed. No commit or publication was performed; runtime source and HTML prototypes are unchanged.
- Documentation validation covers ticket statuses, prerequisite references, changed local links/anchors, dependency cycles, and whitespace. Runtime and browser tests were not run for this planning update. The end-of-session knowledge review keeps feature decisions in their owning tickets; no canonical KB addition is warranted.
