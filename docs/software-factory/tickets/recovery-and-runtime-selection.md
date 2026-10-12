# Recovery guarantees and runtime selection

**Type:** grilling
**Status:** open
**Blocked By:** operating-and-installation-model.md, task-scheduling-and-integration.md, human-control-and-publication.md, session-events-and-live-progress.md, workflow-versioning-and-run-changes.md
**Research Dir:** not applicable

## Question

Which recovery guarantees does the factory require, and which runtime best satisfies them within the chosen operating model?

Compare Restate, DBOS, and a custom runner using the agreed workflow, installation, session, and versioning contracts. Restate is the current candidate; earlier discussion did not settle the production choice.

Specify ownership after a controller or worker crash, reconciliation of already-running CLI work, attempt identity and fencing, replay of completed work, durable human waits, shutdown, and external publication ambiguity. Separate engine-provided guarantees from factory responsibilities.

Resolution should select the runtime or identify a precisely scoped unresolved proof, with acceptance scenarios for crash recovery, stale approvals, and duplicate publication. Any new external fact-finding must become a delegated research ticket; a behavioral proof needing execution requires a separately authorized prototype ticket. Do not claim simulations or code sketches prove durability.

---

<!-- Resolution will be appended after this ticket is claimed and worked with the human. -->

