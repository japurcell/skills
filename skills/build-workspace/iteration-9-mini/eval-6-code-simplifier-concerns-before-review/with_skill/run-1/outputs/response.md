The manager should **stop the downstream flow** and **treat the concern as unresolved work**.

Per the build workflow, `DONE_WITH_CONCERNS` from code-simplifier means: **read the concerns first**, and if they indicate a correctness/scope risk, **reopen any affected done task immediately**, then **re-dispatch the implementer/subagent that owns the fix**. **Do not update tracking yet** and **do not move to code-review** until the concern is resolved.
