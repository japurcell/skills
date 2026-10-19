Delegate a **single shared exploration/investigation task** to the cheaper capable worker first, before running the three source tasks. Activate `delegate-to-subagents` and route through `subagent-model-router`. Because the investigation is read-only, the worker does not need product code changes, `tdd`, an empty commit, or an unnecessary worktree.

**Shared context handling:**
- Send the exploration worker a minimal, sufficient task packet containing the current requirements, shared invariants, required negative cases, current authorization boundaries, source/log entry points, and stop condition. Never trim facts required for correctness or authorization.
- Keep the large log searches and raw transcripts out of the coordinator's near-limit context.
- Retain the reusable findings beside the ExecPlan (or in a linked artifact) with exact source locations and verification evidence.

**Handback and next steps:**
- Require the worker to return only concise conclusions, evidence paths, relevant findings for positive and negative cases, and any blockers.
- The coordinator verifies the retained evidence, reconciles the ExecPlan (`Surprises & Discoveries` / `Decision Log`), and references that concise artifact in the task packets for the three ready source tasks (preserving all authorization rules and negative cases without forwarding raw logs).
