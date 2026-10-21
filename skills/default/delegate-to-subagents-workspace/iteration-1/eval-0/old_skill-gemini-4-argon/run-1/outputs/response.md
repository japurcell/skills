Shared canonical docs (`docs/file-map.md`, `docs/known-issues.md`) must never have concurrent write owners, even when source ownership is disjoint.

**Pre-dispatch ownership assignment**
- **Component A worker:** Write ownership of Component A source files and exclusive Component A area docs only. Read-only access to `docs/file-map.md` and `docs/known-issues.md`.
- **Component B worker:** Write ownership of Component B source files and exclusive Component B area docs only. Read-only access to `docs/file-map.md` and `docs/known-issues.md`.
- **Shared canonical docs (`docs/file-map.md`, `docs/known-issues.md`):** Assign one single integration owner (coordinator/orchestrator) or an explicit serial dependency (`doc-integration` wave after both workers complete) before dispatch.

**How verified findings reach final documents**
1. Both workers run in parallel on their disjoint source files and exclusive area docs.
2. Each worker retains scoped evidence and promptly notifies the integration owner of durable findings and critical guidance for `docs/file-map.md` and `docs/known-issues.md`.
3. After both tasks finish and outputs pass verification Criteria, the coordinator reconciles admitted claims from both workers and runs one serialized final documentation pass to update `docs/file-map.md` and `docs/known-issues.md`.