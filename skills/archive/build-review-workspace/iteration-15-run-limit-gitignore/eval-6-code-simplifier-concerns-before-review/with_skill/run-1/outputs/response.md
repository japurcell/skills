I’ll read the exact benchmark skill file and answer from that source only.

read the code-simplifier's concerns before continuing to code-reviewer.

Because the concern is about widened scope and possible behavior change, the manager should treat it as unresolved work: immediately reopen the affected done task in `.agents/scratchpad/auth/plan.md`, `.agents/scratchpad/auth/todo.md`, and SQL todo state, then re-dispatch the owning implementer/subagent to fix and verify that helper’s scope/behavior.

Do **not** proceed to code-reviewer yet. After the owning subagent fixes and verifies it, do **not** run another code-simplifier wave; continue directly to the single code-reviewer wave over the same review partitions.
