**Do not commit.** Implementation authorization does not override the explicit commit restriction.

The local task may be marked complete if its full task acceptance is verified. Local changes skip rebase/merge, but milestone acceptance still requires the plan’s composed-behavior proof on base.

The worker’s implementation and verification may be recorded as complete. Its commit-dependent integration remains pending: verified uncommitted edits are not integrated changes. Keep any integration-dependent task or milestone acceptance unmet.

Retain local edits, the worker’s private worktree and branch, verification evidence, current task state, and remaining integration steps. Reconcile the plan with actual base state. Report precisely which changes exist on base and which remain only in the worker worktree.

Do not commit, claim the worker changes are integrated, or remove its dirty worktree. Record permission to commit as the required owner action before commit-dependent integration can proceed.
