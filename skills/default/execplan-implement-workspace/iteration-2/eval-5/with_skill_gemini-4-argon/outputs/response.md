Choose local execution by the coordinator in the base worktree with exclusive file ownership.

Cost and correctness tradeoff:
- Expected completion cost must be minimized without reducing correctness across context loading, startup, routing, tool calls, handback review, integration, and verification.
- The coordinator already holds all required current context, and the task is a bounded single edit with a known verification check. Executing locally avoids copying context into a task packet, running `subagent-model-router`, creating/rebasing/removing a private worktree, and reviewing a worker handback—all of which cost more than doing the edit and check directly.
- Correctness is fully preserved: no independent review or context isolation is required, the coordinator applies the exact current contract directly without handoff loss, uses task-appropriate documentation verification evidence (without inventing product tests), skips unnecessary worktree rebase/merge, and verifies on the base branch before reconciling the ExecPlan.
