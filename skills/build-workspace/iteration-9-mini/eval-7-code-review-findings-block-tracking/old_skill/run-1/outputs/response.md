The manager should **treat the reviewer findings as unresolved work**: re-dispatch the subagent that should own the fixes, then send the result back through the code-simplifier and the affected reviewer partitions until every reviewer returns `DONE`.

**Tracking does not stay done.** The task should **not be considered complete yet**; the plan/todo tracker must be updated to reflect the reopened/in-progress state, and only after all reviewers return `DONE` should the manager mark it `done` and record the verification performed.
