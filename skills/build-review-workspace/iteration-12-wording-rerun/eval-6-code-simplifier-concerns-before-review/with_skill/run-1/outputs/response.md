**Next:** treat the simplifier concern as **unresolved work**, not as a finished review pass.

Because the extracted helper may have widened scope and hidden a behavior change, the manager should **reopen the affected task immediately in all active trackers together** (`.agents/scratchpad/auth/plan.md`, `.agents/scratchpad/auth/todo.md`, and SQL `todos`), then **re-dispatch the subagent that should own the fix** for that concern. **Do not proceed to code-review yet.**

After that fix returns `DONE`, rerun the affected simplifier partition, re-close the task across all trackers only when that downstream pass is clean, and only then continue to code-review.
