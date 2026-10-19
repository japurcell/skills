Honor the user's commit prohibition strictly.

What can be marked complete:
- The local task's implementation and verification Progress entries (and the worker task's implementation/test verification steps, if verified) can be recorded as verified in the plan using their uncommitted diff and test output as evidence.
- However, any commit-dependent branch integration (`git merge --ff-only` onto base) and any milestone acceptance that depends on integrating the worker branch onto base must remain pending (`Acceptance: not met`).

What integration remains pending:
- Rebasing the worker branch onto base, updating/committing rebased SHA references, fast-forwarding base (`git merge --ff-only`), running the composed-behavior proof on the integrated base tree, and cleaning up the worker worktree/branch all depend on commits and must be reported as pending owner commit authorization.

What must be retained:
- All uncommitted changes in the base worktree and the worker's private worktree.
- The worker's private worktree and local branch.
- Verification evidence (test results, diffs, commands) and reconciled ExecPlan state recording that commit-dependent integration is blocked by the user's no-commit instruction.

What must not happen:
- Do not run `git commit` in base or worker worktrees.
- Do not rebase or fast-forward merge uncommitted worker work, and do not delete the worker worktree or branch.
