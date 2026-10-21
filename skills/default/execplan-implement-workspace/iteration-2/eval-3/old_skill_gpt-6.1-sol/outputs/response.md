**Resolve shared-document ownership before dispatch.** Private worktrees do not make canonical file-map and known-issues edits independent.

Assign each canonical document one integration owner, or impose explicit serial dependencies between its editors. Keep disjoint source work parallel. Each assignment needs explicit source/document ownership, prerequisites, current plan context, verification, and a stopping boundary.

Workers retain scoped evidence and promptly send durable findings to the document owner. The coordinator reconciles admitted findings and completes the final documentation pass.

Integrate branches serially: confirm the worker worktree is clean, rebase onto latest base, resolve conflicts, and verify affected behavior. Repair failures through step 5 before continuing. Update and commit changed SHA references, confirm both worktrees are clean, then fast-forward base. Confirm matching tips and run the composed-behavior proof when prerequisites are integrated. Remove only verified clean integrated worktrees and branches.
