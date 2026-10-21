Reuse the existing parser worker for the closely related ready parser node, and dispatch a fresh worker for the unrelated payments node.

Parser node (compact, current context):
- Under the execution cost rules, reuse a worker for closely related nodes when retained useful context outweighs contamination and reload costs.
- Before dispatch, revalidate routing (`subagent-model-router`) and explicit file/worktree ownership, and give the second parser node its own explicit task packet, requirements, negative cases, acceptance criteria, stop boundary, and separate result/verification evidence. Integrate one completed branch at a time.

Payments node (unrelated context):
- Use a fresh worker with its own routed model/effort, isolated private worktree/branch, and minimal sufficient task packet. Reusing the parser worker would carry irrelevant parser context and risk cross-task contamination without saving reload cost.

If the parser worker's context is stale or crowded:
- Do not reuse that worker. Before replacing or compacting, retain the completed parser node's state, decisions, verification evidence, and next action in the ExecPlan or linked task notes.
- Dispatch a fresh worker for the second parser node using a clean task packet that references the retained evidence and current contract.
