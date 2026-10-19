Assign coordinator as sole integration owner for `docs/file-map.md` and `docs/known-issues.md` (or set explicit serial dependency between tasks). Both workers run in parallel on disjoint source files only.

### Assignments

**`task-comp-a` / `task-comp-b` (parallel workers)**
- **Identifier:** `task-comp-a` / `task-comp-b`
- **Objective:** Implement component A / component B changes and capture durable doc findings.
- **Necessary context:** Component A / B specs and relevant interfaces.
- **Constraints:** No nested delegation. Preserve others' edits. Do not edit shared canonical docs (`docs/file-map.md`, `docs/known-issues.md`).
- **Deliverable:** Component code changes, exclusive area docs (if any), and scoped evidence/durable findings (including critical guidance) for `docs/file-map.md` and `docs/known-issues.md`.
- **Verification criteria:** Component tests pass; no writes outside owned paths; findings backed by scoped evidence.
- **Allowed resources:** Assigned component source/test directories and read access to needed interfaces.
- **Write ownership:** Disjoint component A / B source and exclusive area doc paths only (`docs/file-map.md` and `docs/known-issues.md` excluded).
- **Dependencies:** `none`
- **Runtime limit:** Explicit warning threshold (e.g., `15m`).

### How Findings Reach Final Documents

1. Workers keep scoped evidence and promptly notify coordinator (integration owner) of durable findings and critical guidance for `docs/file-map.md` and `docs/known-issues.md`.
2. Coordinator verifies both workers' outputs against acceptance criteria.
3. After all tasks finish, coordinator reconciles admitted findings from both workers and completes the final documentation pass on `docs/file-map.md` and `docs/known-issues.md`.