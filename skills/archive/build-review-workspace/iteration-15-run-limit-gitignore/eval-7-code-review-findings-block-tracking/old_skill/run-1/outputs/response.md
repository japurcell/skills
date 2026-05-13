I’ll read the specified snapshot skill file and answer from that source only.

The manager should **not end the wave**. For `DONE_WITH_FINDINGS`, they must address the two correctness issues first: immediately reopen the affected done task(s) across every active tracker, route the fixes to the appropriate subagent, then rerun the affected code-simplifier and code-reviewer partitions as needed.

Tracking stays synchronized: any reopened task is reopened everywhere (`plan.md`, `todo.md`, and SQL todo state if active), and it is only re-closed everywhere after the affected downstream passes return `DONE`. The final reviewed tracking sync happens only after every reviewer returns `DONE`.
