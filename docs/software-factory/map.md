# Customizable software factory

## Destination

An implementation-ready specification for a fully customizable, code-controlled agentic factory: its workflow and task contracts, execution model, skill installation, live session UI, and improvement process are decided well enough to implement and test.

## Notes

- This is a planning map. The user chose this destination on 2026-10-12. The earlier Restate prototype is superseded by the current executor direction; implementation remains outside this planning session.
- Consult wayfinder and the narrow skills needed for the selected ticket. Use grilling plus codebase-design for design conversations. The user explicitly approved this substitute for the unavailable domain-modeling skill on 2026-10-12.
- Consult prototype for a prototype ticket and research for a research ticket. Research tickets require an assigned research directory and a delegated researcher. No new research was launched merely to repeat the retained studies.
- Work one decision ticket per session, except delegated research. Claim its file before work. Check the exact filenames in Blocked By; only closed prerequisites unblock it. Human decisions require a live exchange.
- Closed requirements imported below come from the prior conversation. Before asking a question, reconcile it against prior human answers and the owning tickets. Record an established answer without asking the user to decide it again. Assistant recommendations and examples are not human decisions; only ask about unresolved choices or an actual conflict. This standing instruction was explicit on 2026-10-12.
- Discover open sessions by searching the tickets directory. The map deliberately does not duplicate the open-ticket list.
- Preserve quality, simplicity, robustness, scalability, and long-term maintainability over development cost.
- Evidence entry points: [initial research](research.md) and [reviewable architecture documents](README.md). Source studies and simulations have different evidentiary limits.
- The user promoted this map and its tickets to `docs/software-factory/` on 2026-10-12 for version control. Resume wayfinder in this directory; do not recreate a scratchpad map.
- The [handoff](handoff.md) tracks current progress, verification limits, and the next session. Keep decision details in their owning tickets.

## Decisions so far

- [Confirmed factory requirements](tickets/confirmed-factory-requirements.md): code-owned deterministic flows, fully customizable workflows, per-step agent choices, skill installation, and real-time session visibility.
- [Workflow authoring and task contract](tickets/workflow-authoring-and-task-contract.md): TypeScript routines use managed steps; prose and structured plans become validated task graphs; declared outlines expand with discovered work.
- [Local runtime prerequisites](tickets/local-runtime-prerequisites.md): Restate requires its server; DBOS TypeScript requires Postgres. Neither establishes an embedded-only TypeScript setup or proven native Windows packaging.
- [Embedded graph runtime fit](tickets/embedded-graph-runtime-fit.md): LangGraph Functional API best matches the accepted authoring interface; Mastra is a graph-builder alternative. Local storage, crash recovery, and native Windows still require proof.
- [Embedded workflow runtime fit](tickets/embedded-workflow-runtime-fit.md): Effect offers an explicitly embedded SQL-backed composition with unstable APIs; TanStack needs a local durable store. Workflow DevKit Local World is development/testing infrastructure, and Resonate's default SDK is not persistent.
- [Restate and DBOS operating fit](tickets/service-engine-operating-fit.md): Restate retains a server and native Windows gap; DBOS TypeScript retains Postgres and packaging constraints. DBOS Python supports SQLite but changes the workflow-language contract. The [combined comparison](research/embedded-runtime-comparison.md) retains the research that preceded the user's executor decision.
- [Operating and installation model](tickets/operating-and-installation-model.md): per-repository SQLite executor, foreground invocations, human-triggered Continue, skill-managed runtime, retained versions for unfinished runs, resumable Stop, and explicit cleanup with data-preserving uninstall.

## Not yet specified

<!-- FOG START -->
- The accepted contract covers repository changes and read-only audits. Other concrete workflow patterns may expose extension pressures beyond these examples; no separate question is sharp enough to ticket yet.
- Known native-platform, upgrade, shutdown, retention, and recovery mechanisms have owners in the existing tickets. Additional deployment/harness interactions may still expose narrower process or permission questions that cannot yet be stated precisely.
- Observed improvement proposals may expose evaluation domains or ownership conflicts that need their own decisions after the core learning contract is set.
<!-- FOG END -->

## Out of scope

- Building or deploying the factory, installing a runtime into target repositories, and executing the earlier Restate prototype during this map's charting session.
- Performing application changes, creating PRs, or applying skill/prompt improvements as a side effect of planning.
- Implementation task decomposition and rollout scheduling; these follow the specification unless the user explicitly changes this map's destination.

