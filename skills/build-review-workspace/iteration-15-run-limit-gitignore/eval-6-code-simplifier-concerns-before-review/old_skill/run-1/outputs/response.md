I’ll read the specified snapshot skill file and answer from that source only.

**Read the code-simplifier's concerns before continuing to code-reviewer.**

Because the concern is about widened scope / possible behavior change, the manager should treat it as unresolved work: immediately reopen the affected task across `.agents/scratchpad/auth/plan.md`, `.agents/scratchpad/auth/todo.md`, and SQL todo state, then re-dispatch the appropriate subagent to resolve the helper/scope issue. Do **not** proceed to code-reviewer until that concern is fixed, the affected task is re-closed consistently across all active trackers, and the relevant simplifier pass returns `DONE`.
