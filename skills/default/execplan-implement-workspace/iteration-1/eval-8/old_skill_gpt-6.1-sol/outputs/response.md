**Keep verified edits uncommitted and preserve the worker worktree.** Implementation authorization does not override the explicit no-commit instruction.

Mark only demonstrably completed local implementation and verification entries complete. Retain commands, results, tested-tree identity, and limitations. Do not mark branch integration, base verification, or delivery acceptance complete merely because local checks passed. If task completion includes those outcomes, the task remains partially complete.

The prescribed integration sequence remains blocked: the worker has uncommitted edits, and no new committed branch tip carries them. Do not rebase the dirty worktree or substitute an unapproved integration method.

Retain the worktree, branch, edits, evidence, prerequisites, and current plan state. Report actual base state and the pending commit/integration gate. Preserve any existing approval boundaries.

Do not commit, create an empty commit, discard edits, or remove the dirty worktree. Resume commit-based integration only when the no-commit restriction is lifted.
