**Before any implementer is dispatched, the coordinator should stop and resolve the conflict.** In the local build workflow, a task that is *ambiguous or conflicts with the plan* is an explicit **do not dispatch yet** case.

So the sequence is:

1. Invoke `addy-context-engineering` and `subagent-model-selection`.
2. Notice that “defer audit logging until phase 2” conflicts with “implement audit logging now.”
3. Resolve or escalate that ambiguity first.
4. Only after it is clarified, dispatch an implementer with a **lean handoff**.

The manager should **not** pre-read repo files or draft a solution while waiting; the linked implementer prompt says discovery and first-pass design belong to the implementer once the task is clear.
