Delegate one shared, read-only exploration/investigation task to the cheaper capable worker first, then execute the three source tasks after its findings return.

Why and how:
- Under the execution cost and context rules, share exploration when several tasks need the same context, and delegate when a cheaper capable worker and context isolation save more than dispatch overhead. Keeping the large log investigation out of the coordinator's nearly full context avoids repeated reads and context compaction/overflow.
- Activate `delegate-to-subagents` and route via `subagent-model-router`.
- Because the investigation is read-only, the worker does not need a private worktree, branch, or product code/test changes, and must not create an empty commit.
- Send the smallest sufficient task packet: bounded investigation objective, log/source entry points, current authorization boundaries, shared invariants, required negative cases, deliverable format, verification criteria, and stop condition. Never trim facts required for correctness or authorization.

Handback and shared context handling:
- Request only concise conclusions, exact source/log evidence paths, relevant negative-case findings, and blockers—no raw large logs or full transcripts.
- Retain the reusable findings beside the ExecPlan (or linked task notes) with source and verification evidence, reconcile the plan, and reference or include those verified findings in the task packets for the three ready source tasks.
