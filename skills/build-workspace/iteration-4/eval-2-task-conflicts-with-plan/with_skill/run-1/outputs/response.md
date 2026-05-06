**Before dispatching any implementer, the manager should stop and resolve the conflict.** In the build skill, a task that is **ambiguous or conflicts with the plan is not clear enough to dispatch yet**. Here, “defer audit logging until phase 2” conflicts with “implement audit logging now,” so the workflow says to **resolve that inconsistency first** rather than send an implementer.

Per the build workflow, the sequence is:

1. Invoke **`addy-context-engineering`** and **`subagent-model-selection`**.
2. Pick the next pending task.
3. Because this task text conflicts with the plan, **clarify/update the requirement first**.
4. **Do not** pre-read a large file set, draft a solution, or dispatch the implementer until that conflict is resolved.

So the immediate action is **requirement clarification / plan-task reconciliation**, not implementation.
