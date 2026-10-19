Before dispatch, apply `delegate-to-subagents` ownership rules to the canonical file map and known-issues document, even across private worktrees. Serialize edits to shared canonical documents by assigning one integration owner (such as the coordinator) or an explicit serial dependency. Do not allow both workers to edit shared canonical docs concurrently.

Give each subtask an identifier, objective, context, constraints, deliverable, verification criteria, allowed resources, disjoint source write ownership, dependencies, and runtime limit. Each worker operates in its own private worktree and branch, retains scoped evidence for its findings, and promptly notifies the owner of durable findings for the canonical docs.

Integrate completed branches into the base topic branch one at a time (serialized):
1. Confirm the implementer worktree is clean and rebase its branch onto the latest base topic branch.
2. Resolve any conflicts (using a merger subagent with exclusive ownership of the implementer worktree if conflict-prone) and run affected checks covering the resulting tree and interactions.
3. Update and commit any ExecPlan SHA references changed by the rebase.
4. Confirm the base worktree is clean, fast-forward base (`git merge --ff-only`), verify the base tip matches, and remove the integrated worktree and branch.
5. Reconcile admitted canonical-doc findings in the designated owner pass and run the milestone composed-behavior proof on base.
