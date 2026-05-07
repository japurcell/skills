Sync **Task A’s completion now**, not the review wave: update `.agents/scratchpad/issues/plan.md`, `.agents/scratchpad/issues/todo.md`, and the **SQL todo state** row `api-issues-pagination` to the same done status, record the verification that actually passed, and confirm all three trackers agree **before dispatching Task B**.

**Do not start code-simplifier yet.** Task B is still in the current wave, so downstream review waits until **every task in the wave** is implemented and marked done. The four touched files do **not** trigger `review_scope_files` yet.
