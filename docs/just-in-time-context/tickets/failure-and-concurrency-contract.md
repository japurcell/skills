# Failure and Concurrency Contract

**Type:** grilling
**Status:** open
**Blocked By:** context-organization-and-skill-boundary.md, maintenance-scheduling-and-pruning.md
**Research Dir:** not applicable

## Question

What happens when retrieval or maintenance fails, a session ends unexpectedly, or multiple agents change the same repository knowledge?

Define pending-work ownership, duplicate trigger handling, partial-write recovery, retries, cancellation, and visibility of incomplete maintenance. Establish a durable completion record and recovery behavior that meets the agreed lifecycle guarantees. Determine which failures block agent work and which permit continued work with an explicit outstanding obligation.

Preserve [Context Retrieval Contract](context-retrieval-contract.md): attempt focused recovery automatically, expose incomplete delivery, and pause only work dependent on missing policy or a material unresolved fact while independent work continues. Choose retry, recovery, publication, and concurrency mechanisms within that boundary; do not reopen it as a blanket task-stop policy.

Implement the verified-completion, visible-incomplete, pending-work, and next-eligible-event semantics in [Lifecycle Guarantees](lifecycle-guarantees.md). Respect explicit pauses/cancellation without restarting canceled user work, keep retries bounded, and do not equate provider termination with successful completion. Define how foreground stage callbacks and compatible skill/source-ingestion entries avoid recursive scheduling and duplicate semantic work. Choose ownership and records without weakening those agreed boundaries.

Implement [Context Organization and Skill Boundary](context-organization-and-skill-boundary.md): bind invocation context to workspace/worktree, task, agent, and stage; define issuance, validation, expiry, and restoration without trusting a provider-named environment variable. Invalid learn/dream context fails before mutation. Separate CLI dispatch/process success from validated completed, no-change, or incomplete stage outcomes. Choose actual outcome checks, publication/rollback, and durable ignored-state records. Preserve stable unit references and context availability when knowledge moves or changes during active, resumed, or delegated work, without detailed usage attribution.

Implement [Maintenance Scheduling and Pruning](maintenance-scheduling-and-pruning.md): distinguish the due review cycle, assigned required batch, reviewed coverage, and remaining routine work. Choose durable ownership and progress records across concurrent agents/worktrees, interruption, source revisions, and repeated native events. Verify scoped no-change without claiming full-cycle completion; only verified cycle completion resets its clock. Preserve pending obligations, unresolved candidates, active recovery records, and required evidence through cleanup. Completed unreferenced operational records expire after 30 days unless still needed for recovery or validation. Keep foreground execution and respect existing pause/cancellation rules; do not add idle model jobs.

---

<!-- Resolution will be appended here. -->
