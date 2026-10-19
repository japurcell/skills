Before dispatch, assign each task explicit disjoint source write ownership, private worktree, and unpushed branch (`git worktree add -b <worker-branch> <path> <base-branch>`). Shared canonical documents (file map and known-issues document) cannot have concurrent writers, even across private worktrees. Give each shared canonical document one integration owner (such as the coordinator) or an explicit serial dependency between tasks. Exclusive area documentation stays worker-owned.

During execution, workers retain scoped evidence and promptly notify the integration owner of durable findings and critical guidance instead of concurrently editing shared canonical docs.

Integrate one completed worker branch at a time (`references/integration.md`):
1. Confirm worker worktree is clean, stop worker writes, and rebase its branch onto latest base topic branch.
2. Resolve conflicts and rerun affected tests if interactions or tree changed.
3. Update and commit any ExecPlan SHA references changed by rebase; confirm clean worker worktree.
4. Confirm clean base worktree, then run `git merge --ff-only <worker-branch>` and verify base tip matches worker tip.
5. Run composed-behavior proof on base once related prerequisites integrate.
6. Remove verified clean worker worktree (`git worktree remove`) and branch (`git branch -d`).
7. Reconcile admitted findings and complete one final documentation pass after all active tasks finish.
