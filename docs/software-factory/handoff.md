# Software factory handoff

Updated: 2026-10-12. Scope: software-factory.

## Goal and progress

Produce an implementation-ready specification for the fully customizable factory using the [Customizable software factory map](map.md). The immediate Restate prototype was deferred in favor of planning.

- Done: initial source research, three interactive architecture documents, and capture of the user's confirmed requirements.
- Done: wayfinder map with thirteen tickets in `docs/software-factory/`. Two are closed: the imported requirements record and [Workflow authoring and task contract](tickets/workflow-authoring-and-task-contract.md).
- Current: the user accepted all remaining authoring contract details on 2026-10-12. Eleven planning tickets remain open; none is claimed. Runtime implementation has not started.
- Remaining: resolve the planning decisions and review specification readiness with the human. Ticket files own their statuses and resolutions; this handoff summarizes current progress.

## Next action

In the next wayfinder session, resume `docs/software-factory/` with [Operating and installation model](tickets/operating-and-installation-model.md). Recheck its exact prerequisite, claim it, and resolve only its unanswered operating and installation choices with the human. [Verification and review policy](tickets/verification-and-review-policy.md) is also unblocked. This session closed one design ticket and does not start another.

The user approved grilling plus codebase-design as the substitute for the unavailable domain-modeling skill. Read prior conversation decisions before asking questions; record settled answers without asking again. Distinguish human decisions from assistant proposals. Resolve one design ticket per session; use exact dependency files to determine readiness. After a resolution, update its ticket, the map's decision index and fog, and this handoff.

## Decisions, proposals, and limits

The [Confirmed factory requirements](tickets/confirmed-factory-requirements.md) record owns the accepted requirements. Critical constraints are code-owned deterministic behavior, full workflow customization, per-step harness/model/reasoning/prompt/skill choices, skill installation, and a UI showing all sessions and steps in real time.

The closed [Workflow authoring and task contract](tickets/workflow-authoring-and-task-contract.md) owns the accepted TypeScript/managed-step interface, prose and structured plan intake, minimum task record, graph validation, ambiguity policy, nested scopes, and dynamically expanded outline. These answers are settled; do not ask them again.

The six-stage use case is a default recipe, not a fixed pipeline. Human review and interactive UI verification are configurable. Restate, runtime-specific child workflows, serialized integration, exact repair budgets, and the event transport remain proposals for the relevant tickets. Clarification of ambiguous plans is not mandatory approval of every valid plan. Code-level nesting does not choose a runtime mechanism.

Keep crash recovery, stale approvals, and duplicate publication in the acceptance discussion. No working Restate or DBOS runtime, CLI adapter conformance, real-time transport, or recovery behavior has been verified.

The current request resumes planning and records prior answers. Implementation and publication remain outside the authorized scope.

## Evidence and verification

- [Initial research](research.md) and [review guide](README.md) contain the source studies and interactive documents. Their runs are simulations. The review guide includes the local preview command and prior UI validation scope.
- [Earlier prototype handoff](handoff.history-2026-10-12.md) preserves superseded workflow sketches, failure scenarios, runtime references, and the preview command. It is historical evidence, not a current instruction to implement.
- The user explicitly placed this handoff in `docs/software-factory/`; keep it here. Its history was moved alongside it, and scratchpad copies were removed. No commit or publication was performed; runtime source and HTML prototypes are unchanged.
- Charting and relocation checked filenames, dependency references and cycles, statuses, local links, and preservation of the original documents. This closure checks ticket counts and dependencies, the next frontier, local links, and diff whitespace. Runtime and browser tests were not rerun for documentation changes.
