# Failure and Concurrency Contract

**Type:** grilling
**Status:** open
**Blocked By:** context-organization-and-skill-boundary.md, maintenance-scheduling-and-pruning.md
**Research Dir:** not applicable

## Question

What happens when retrieval or maintenance fails, a session ends unexpectedly, or multiple agents change the same repository knowledge?

Define pending-work ownership, duplicate trigger handling, partial-write recovery, retries, cancellation, and visibility of incomplete maintenance. Establish a durable completion record and recovery behavior that meets the agreed lifecycle guarantees. Determine which failures block agent work and which permit continued work with an explicit outstanding obligation.

Preserve [Context Retrieval Contract](context-retrieval-contract.md): attempt focused recovery automatically, expose incomplete delivery, and pause only work dependent on missing policy or a material unresolved fact while independent work continues. Choose retry, recovery, publication, and concurrency mechanisms within that boundary; do not reopen it as a blanket task-stop policy.

Implement the verified-completion, visible-incomplete, pending-work, and next-eligible-event semantics in [Lifecycle Guarantees](lifecycle-guarantees.md). Respect explicit pauses/cancellation without restarting canceled user work, keep retries bounded, and do not equate provider termination with successful completion. Define how automatically invoked maintenance agents avoid recursively scheduling themselves. Choose ownership and records without weakening those agreed boundaries.

---

<!-- Resolution will be appended here. -->
