# Branch integration

Integrate one completed worker branch at a time. Preserve unfinished work, unrelated worktrees, and the base branch.

1. Confirm the implementer's worktree is clean, then rebase its branch onto the latest **base topic branch**.
2. Resolve conflicts and rerun affected tests. For a conflict-prone rebase, choose local resolution or a merger using the same cost rule. Stop the implementer's writes and transfer exclusive ownership of its worktree before rebasing. The resolver rebases that branch without mutating base. Even without conflicts, reuse evidence only when it covers the resulting tree and interactions; otherwise rerun affected checks.
   If affected tests fail, pause that branch's integration, record an unfinished repair, and return it to the execution loop in SKILL.md. Resume after the affected tests pass.
3. Update and commit any ExecPlan references to SHAs changed by the rebase, then confirm the implementer's worktree is clean.
4. Confirm the base worktree is clean, then fast-forward the base branch with `git merge --ff-only <implementer-branch>`.
5. Confirm the base branch tip matches the verified implementer branch tip. Once related prerequisites are integrated, execute the plan's composed-behavior proof on base, or delegate it as the named integration task. If it fails or remains unrun, keep milestone acceptance unmet and record the repair or blocker.
6. After each fast-forward, remove clean worktrees and local branches for the integrated node, including superseded repair/merger branches once their changes are verified on base. Preserve base and unrelated worktrees.

Create a new worker branch with `git worktree add -b <worker-branch> <path> <base-branch>`. After verified integration, remove its clean worktree with `git worktree remove <path>` and delete its local branch with `git branch -d <worker-branch>`.
