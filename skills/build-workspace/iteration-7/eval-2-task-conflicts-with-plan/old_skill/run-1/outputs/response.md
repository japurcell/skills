**No implementer should be dispatched yet.** The build workflow says that if a task “**conflicts with the plan**,” it is **not clear enough to dispatch yet** and the manager must **resolve that before dispatch**.

So in this case the manager should:
1. Invoke `addy-context-engineering` and `subagent-model-selection`.
2. Surface the audit-logging conflict, get it resolved/update the plan or task text, and **only then** dispatch an implementer.

If the contradiction means the plan itself is wrong, the workflow says to **escalate to the human** rather than guess.
