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
- Preserve IDs such as `US-*` and `FR-*` in descriptions or acceptance criteria.
- Mandatory execution order controls task order and priority.
- Recommended order affects priority only when safe.
- Use relevant Definition of Done and Testing Plan items to seed task acceptance criteria.
- Do not copy irrelevant criteria into every task.
- Assume canonical definitions are intentional unless they conflict with workspace rules or are internally inconsistent.
- If a conflict cannot be safely resolved, ask the user and stop before writing `tasks.json`.
