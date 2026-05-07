I’ll answer from the specified local skill file only, without changing or validating the repository.

The manager should **not patch inline** and should **not rerun code-simplifier or code-reviewer**. For `DONE_WITH_FINDINGS`, they must reopen each affected done task immediately across every active tracker, route the two correctness fixes to the appropriate owning subagent, and have that subagent fix and verify them.

Tracking changes from “done/final-reviewed candidate” back to visibly unresolved/not-final-reviewed everywhere: `plan.md`, `todo.md`, and SQL todo state if active. After the fixes, the manager records the exact verification performed, but **the final reviewed sync does not happen yet**; the post-review fixes are handed off as unreviewed, and another build-review wave is the fresh quality gate if desired.
