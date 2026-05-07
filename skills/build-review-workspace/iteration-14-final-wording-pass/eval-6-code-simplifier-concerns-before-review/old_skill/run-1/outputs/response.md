Do **not** proceed to code-review yet.

Treat that `DONE_WITH_CONCERNS` as unresolved scope/correctness risk: reopen the affected task immediately in `.agents/scratchpad/auth/plan.md`, `.agents/scratchpad/auth/todo.md`, and the SQL `todos` table, then re-dispatch the implementer with the simplifier’s concern about the extracted helper possibly widening scope and hiding a behavior change. Only after that fix is back to `DONE` should the affected simplifier pass return `DONE`, then continue into code-review and re-close tracking to the final reviewed state.
