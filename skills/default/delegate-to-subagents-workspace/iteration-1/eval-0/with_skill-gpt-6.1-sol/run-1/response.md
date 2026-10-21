**Coordinator owns both shared documents:** `docs/file-map.md` and `docs/known-issues.md`. Neither component worker edits them.

| Assignment | Scope and ownership | Deliverable and verification | Dependencies |
|---|---|---|---|
| `component-a` | Complete component A. Write only its explicitly enumerated source/test files, disjoint from B. Read relevant source and docs. | Changes plus scoped findings: affected paths, file-map updates, known issues, and supporting test results or reproducible evidence. Verify component acceptance criteria and existing behavior. | None; independent of B. |
| `component-b` | Complete component B under the same constraints, using its own enumerated source/test files. | Same deliverables and verification for B. | None; independent of A. |
| `docs-integration` | Coordinator alone edits both shared documents. Reconcile verified findings from A and B without overwriting unrelated content. | Accurate file-map entries and deduplicated, evidence-backed known issues. Check paths against completed changes and trace each admitted finding to worker evidence. | Both component assignments complete and their findings verified. |

Before any future dispatch, bind each component assignment to exact file lists and acceptance criteria. Workers share the codebase, preserve others’ edits, and cannot delegate further. External resources: none unless specifically required.

Each component assignment gets a **30-minute warning threshold**, monitored by coordinator elapsed time. An overrun triggers a non-interrupting status request, not cancellation.

Workers retain scoped evidence and promptly notify the coordinator of durable findings, especially critical guidance. Coordinator records both sets, resolves conflicts or unsupported claims, then performs one final documentation pass after both finish. **Both workers contribute findings; only the coordinator writes shared docs.** No dispatch occurs here.