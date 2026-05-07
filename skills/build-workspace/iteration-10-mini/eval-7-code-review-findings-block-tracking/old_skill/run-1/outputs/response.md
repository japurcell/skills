Reopen the affected done task(s) immediately, then dispatch the fix to the implementer for those correctness issues. After the fix lands, run the affected slice back through code-simplifier and the code-reviewer partitions as needed, and only then close the tasks again.

Tracking should not stay stale: the reopened task(s) move out of done in the tracker/plan/todo state until the downstream passes return DONE, then the manager syncs everything to the final reviewed state.
