# Manifest intake

Read before any all-complete shortcut or selection. Load [task-schema.md](../../spec-to-tasks/references/task-schema.md) and [validation.md](../../spec-to-tasks/references/validation.md) for the complete manifest contract.

## Validate before execution

- Require a JSON object with a nonempty task array, unique nonempty IDs, boolean pass flags, and valid dependency graph. Reject unknown IDs, self/duplicate edges, cycles, and missing or non-array `dependsOn` fields. An empty array is blocked unless authoritative source explicitly defines a no-work result; never infer vacuous completion.
- Apply the producer's complete contract to every task, including completed tasks. Reject missing required fields, invalid reference/check shapes, invalid task types, and missing required outcome or explicit typecheck classification, even when every pass flag is true. Preserve existing IDs, pass flags, notes, and completion evidence; report invalid input without rewriting it.
- Validate all reference paths and check working directories as repository-relative, resolve them against the repository root, and reject escaping paths. Load each referenced section and confirm mapped requirements exist. For inline references, consume supplied content with both path and section null. Missing critical source/context or contradictory requirements blocks before execution.
- Before trusting a completed task, confirm its recorded evidence covers the current contract under [Updating existing tasks](../../spec-to-tasks/references/task-schema.md#updating-existing-tasks). Read task notes, existing progress evidence and relevant artifacts as needed. Resolve the supplied `progress_file` or default `<dirname(prd_file)>/progress.txt` before the completion shortcut; an absent progress file blocks only when needed evidence is unavailable elsewhere. If a retained pass lacks coverage, block before selection or all-complete detection and name the tasks needing reconciliation. Preserve the input flags and historical evidence; intake does not rewrite task history or treat new acceptance as already verified.

## Prerequisites and authority

Pass flags determine graph eligibility. Before dependent execution, inspect available notes, progress evidence, relevant durable artifacts and current state for the guarantees the selected task actually needs. A passed prerequisite's prose may contain a required decision, integration invariant, or owner condition; carry that constraint into execution. Missing critical evidence or an unmet current guarantee blocks. Report discrepancies without resetting earlier progress or inventing completion evidence.

Read every selected field, including inherited design guidance and acceptance criteria. Execute only one selected outcome, with source/context invariants and user scope/stop limits intact. Decisions outside delegated authority require owner approval and stay blocked.

## Read-only outcomes

Caller-supplied `commit: false` permits a verification or decision task to pass with real recorded evidence and no fabricated repository changes, subject to the normal zero-session-commit audit. Default `commit: true` still requires one real scoped commit. If no committable task changes exist, block; do not create an empty commit or silently disable commit. Durable evidence documents are valid only when actually required by the task.
