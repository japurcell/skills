Sync **Task A** to completion across **all three active trackers now, together** before doing anything else:

1. Update `.agents/scratchpad/issues/plan.md` for Task A as done, including the verification that was actually run and the 4 files touched.
2. Update `.agents/scratchpad/issues/todo.md` with the same Task A status/identity and completion details.
3. Update the SQL `todos` state consistently (and keep `api-issues-pagination` aligned with its real status for Task B, which is still not dispatched).

After that, dispatch Task B’s implementer. **Do not start the code-simplifier wave yet**—it starts only after every task in the current wave is implemented and marked done across trackers.
