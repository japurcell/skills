# Recovery guarantees and runtime selection

**Type:** grilling
**Status:** open
**Blocked By:** operating-and-installation-model.md, task-scheduling-and-integration.md, human-control-and-publication.md, session-events-and-live-progress.md, workflow-versioning-and-run-changes.md
**Research Dir:** not applicable

## Question

Which recovery guarantees and mechanisms must the selected factory-owned SQLite executor provide within the chosen operating model?

The user selected the executor and human-triggered Continue on 2026-10-12; [Operating and installation model](operating-and-installation-model.md#selected-executor-and-continuation) owns those decisions. Do not reopen runtime selection or the recovery trigger as an unanswered question. Retained engine research supplies comparisons and failure scenarios for the custom executor.

Specify ownership after a controller or worker crash, reconciliation of already-running CLI work, attempt identity and fencing, replay of completed work, durable human waits, shutdown, and external publication ambiguity. Separate engine-provided guarantees from factory responsibilities.

Resolution should specify the executor's guarantees and identify precisely scoped unresolved proofs, with acceptance scenarios for crash recovery, stale approvals, and duplicate publication. The SQLite binding, ownership/fencing protocol, database layout, control-flow replay mechanism, and external-effect rules remain to be decided. Any new external fact-finding must become a delegated research ticket; a behavioral proof needing execution requires a separately authorized prototype ticket. Do not claim simulations or code sketches prove durability.

---

<!-- Resolution will be appended after this ticket is claimed and worked with the human. -->

