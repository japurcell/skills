No — that is **not acceptable** in this workflow.

Before dispatching the next subagent, the manager must do a **full task-complete tracking sync immediately**: update Task 9 in every active tracker (`plan.md`, `todo.md`, and SQL `todos`) to the same status, record the verification actually performed, and confirm all trackers agree. Dispatching with `plan.md` still out of sync is incomplete work.
