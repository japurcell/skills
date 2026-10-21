# PRD handling

Use this reference only for `/prd`-style PRDs.

## Canonical sections

When present, treat these as canonical:

1. Functional Requirements
2. Technical Decisions
3. Definition of Done
4. Execution Sequence
5. Testing Plan
6. Out of Scope

## Rules

- Do not create tasks for Out of Scope items.
- Preserve IDs such as `US-*` and `FR-*` in `sourceRefs.requirements` and, where useful, in descriptions or acceptance criteria. Each label must resolve to actual PRD content.
- Mandatory execution order controls task order and priority, and each real prerequisite is represented by a `dependsOn` edge.
- Recommended order affects priority only when safe. Do not turn a recommendation into a dependency, and do not treat priority as authorization to bypass a prerequisite.
- Use relevant Definition of Done and Testing Plan items to seed task acceptance criteria.
- Do not copy irrelevant criteria into every task.
- Assume canonical definitions are intentional unless they conflict with workspace rules or are internally inconsistent.
- If a conflict cannot be safely resolved, ask the user and stop before writing `tasks.json`.
- Carry shared invariants into `requiredContext` for each affected task. When work is split across tasks, add an integration task or check with source references and a dependency on its contributing work; individual task passes do not prove combined behavior.
