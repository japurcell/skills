# Software factory handoff

Updated: 2026-10-12. Scope: software-factory.

## Goal and progress

Produce an implementation-ready specification for the fully customizable factory using the [Customizable software factory map](map.md). The earlier Restate prototype is superseded by the selected executor direction; implementation has not started.

- Done: initial source research, three interactive architecture documents, and capture of the user's confirmed requirements.
- Done: wayfinder map with seventeen tickets in `docs/software-factory/`. Eight are closed: the requirements record, authoring contract, operating contract, execution profiles, local runtime prerequisites, and three delegated runtime comparisons linked from the map.
- Current: [Agent execution profiles](tickets/agent-execution-profiles.md) is closed. Its final choices are accepted: replacement by default with explicit composition, and per-step schemas required for agent outputs that control execution while reports may use text/artifacts. Eight tickets are closed, none is claimed, and nine are open. The user requested stopping after recording these decisions; no new ticket was started.
- Remaining: resolve the planning decisions and review specification readiness with the human. Ticket files own their statuses and resolutions; this handoff summarizes current progress.

## Next action

Stop after this documentation update, as explicitly requested on 2026-10-12. Wait for the user to resume planning. On a future explicit resume, discover the first open, unclaimed frontier ticket and verify every exact `Blocked By` file is closed before claiming it. Do not restart the resolved execution-profiles exchange. Verify new CLI facts through delegated research when needed.

Do not repeat accepted platform, per-repository installation, foreground invocation, dependency ownership, trust, offline, TypeScript-authoring, SQLite-executor, Continue, runtime-provisioning, upgrade-retention, Stop, history-retention, uninstall, configuration-precedence, fallback-default, session-default, skill-delivery, minimum-telemetry, configured fresh-session recovery, instruction-composition, or structured-result policy questions. The user's primary and additional harness choices and per-step model/reasoning/skill/prompt configurability are already recorded.

The user approved grilling plus codebase-design as the substitute for the unavailable domain-modeling skill. Read prior conversation decisions before asking questions; record settled answers without asking again. Distinguish human decisions from assistant proposals. Resolve one design ticket per session; use exact dependency files to determine readiness. After a resolution, update its ticket, the map's decision index and fog, and this handoff.

## Decisions, proposals, and limits

The [Confirmed factory requirements](tickets/confirmed-factory-requirements.md) record owns the accepted requirements. Critical constraints are code-owned deterministic behavior, full workflow customization, per-step harness/model/reasoning/prompt/skill choices, skill installation, and a UI showing all sessions and steps in real time.

The closed [Workflow authoring and task contract](tickets/workflow-authoring-and-task-contract.md) owns the accepted TypeScript/managed-step interface, prose and structured plan intake, minimum task record, graph validation, ambiguity policy, nested scopes, and dynamically expanded outline. These answers are settled; do not ask them again.

The six-stage use case is a default recipe, not a fixed pipeline. Human review and interactive UI verification are configurable. Serialized integration, exact repair budgets, and the event transport remain proposals for the relevant tickets. Clarification of ambiguous plans is not mandatory approval of every valid plan. Code-level nesting does not choose a runtime mechanism.

The [selected executor and continuation record](tickets/operating-and-installation-model.md#selected-executor-and-continuation) owns the latest decisions. A separate workflow server or database service is not part of the initial execution architecture. The factory owns durable execution and reconciliation. Continue selects an unfinished run; it does not implicitly approve a checkpoint or reset a repair budget.

The closed [operating resolution](tickets/operating-and-installation-model.md#resolution) owns skill-managed pinned runtime provisioning, retaining compatible runtime/workflow versions for unfinished runs, graceful interruption with resumable Stop, history retained until explicit cleanup, and data-preserving uninstall with separate purge. Exact mechanisms remain with the linked downstream tickets. Do not convert those mechanism questions into renewed policy choices.

Keep crash recovery, stale approvals, and duplicate publication in the acceptance discussion. [Recovery guarantees and runtime selection](tickets/recovery-and-runtime-selection.md) remains open and blocked for detailed mechanisms and acceptance; its engine-choice question is already answered. The illustrative method names, SQLite binding/layout, replay mechanism, fencing, and version migration are not finalized. No executor, CLI adapter conformance, real-time transport, native Windows support, or recovery behavior has been verified. Runtime implementation and publication remain outside scope.

## Evidence and verification

- [Initial research](research.md) and [review guide](README.md) contain the source studies and interactive documents. Their runs are simulations. The review guide includes the local preview command and prior UI validation scope.
- [Local runtime findings](research/local-runtime-prerequisites/findings.md) cite current official documentation for engine/storage prerequisites and packaging constraints. This was source research, not an installation, recovery test, or native-platform validation.
- [Combined runtime comparison](research/embedded-runtime-comparison.md) links three completed delegated reports and primary sources. Its earlier library recommendations are historical, not the selected direction. The research distinguishes SDK language from engine language and Continue selection from recovery mechanics; it proves no full platform/lifecycle contract.
- [Earlier prototype handoff](handoff.history-2026-10-12.md) preserves superseded workflow sketches, failure scenarios, runtime references, and the preview command. It is historical evidence, not a current instruction to implement.
- The user explicitly placed this handoff in `docs/software-factory/`; keep it here. Its history was moved alongside it, and scratchpad copies were removed. No commit or publication was performed; runtime source and HTML prototypes are unchanged.
- Documentation validation covers ticket statuses, prerequisite references, changed local links/anchors, dependency cycles, and whitespace. Runtime and browser tests were not run for this planning update. The end-of-session knowledge review keeps feature decisions in their owning tickets; no canonical KB addition is warranted.
