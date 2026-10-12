# Software factory handoff

Updated: 2026-10-12. Scope: software-factory.

## Goal and progress

Produce an implementation-ready specification for the fully customizable factory using the [Customizable software factory map](map.md). The immediate Restate prototype was deferred in favor of planning.

- Done: initial source research, three interactive architecture documents, and capture of the user's confirmed requirements.
- Done: wayfinder map with thirteen tickets, comprising one imported requirements record and twelve open planning decisions. The map and tickets now live in `docs/software-factory/`.
- Current: no ticket is claimed. No new design decision has been resolved since charting, and runtime implementation has not started.
- Remaining: resolve the planning decisions and review specification readiness with the human. Ticket files own their statuses and resolutions; this handoff summarizes current progress.

## Next action

Resume wayfinder with directory `docs/software-factory/` and ticket [Workflow authoring and task contract](tickets/workflow-authoring-and-task-contract.md). Check its prerequisite is still closed, claim the ticket, then work through its question with the human. [Operating and installation model](tickets/operating-and-installation-model.md) is also unblocked.

The user approved grilling plus codebase-design as the substitute for the unavailable domain-modeling skill. No clarification or external blocker prevents the next session. Resolve one design ticket per session; use exact dependency files to determine readiness. After a resolution, update its ticket, the map's decision index and fog, and this handoff.

## Decisions, proposals, and limits

The [Confirmed factory requirements](tickets/confirmed-factory-requirements.md) record owns the accepted requirements. Critical constraints are code-owned deterministic behavior, full workflow customization, per-step harness/model/reasoning/prompt/skill choices, skill installation, and a UI showing all sessions and steps in real time.

The six-stage use case is a default recipe, not a fixed pipeline. Human review and interactive UI verification are configurable. Restate, TypeScript, nested task workflows, serialized integration, exact repair budgets, and the event transport remain proposals for the relevant tickets.

Keep crash recovery, stale approvals, and duplicate publication in the acceptance discussion. No working Restate or DBOS runtime, CLI adapter conformance, real-time transport, or recovery behavior has been verified.

This request maintains progress records only. It does not start an implementation, resolve a design ticket, or authorize publication.

## Evidence and verification

- [Initial research](research.md) and [review guide](README.md) contain the source studies and interactive documents. Their runs are simulations. The review guide includes the local preview command and prior UI validation scope.
- [Earlier prototype handoff](handoff.history-2026-10-12.md) preserves superseded workflow sketches, failure scenarios, runtime references, and the preview command. It is historical evidence, not a current instruction to implement.
- The user explicitly placed this handoff in `docs/software-factory/`; keep it here. Its history was moved alongside it, and scratchpad copies were removed. No commit or publication was performed; runtime source and HTML prototypes are unchanged.
- Charting and relocation checked filenames, dependency references and cycles, statuses, local links, and preservation of the original documents. This update rechecks current statuses, handoff links, and preserved history. Runtime and browser tests were not rerun for documentation maintenance.
