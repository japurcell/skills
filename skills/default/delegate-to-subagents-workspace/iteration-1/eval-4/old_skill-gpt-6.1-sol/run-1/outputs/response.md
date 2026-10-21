1. **Route before approval.** Start with model and effort constraints set to `none`. Use task facts and exact runtime-supported values with `subagent-model-router`. Do not ask for model preferences or inherit defaults.

2. **Record, then request approval.** In actual execution, record the complete route in one session artifact before requesting approval. Require exact model and effort values and `dispatchable: true`. If routing fails, explain the blocker; do not dispatch. Here, describe only—no artifact or dispatch.

3. **Keep worker prompts task-focused.** Include objective, necessary context, constraints, deliverable, verification criteria, allowed resources, write ownership, and dependency results. Prohibit nested delegation unless intentionally authorized. Exclude workflow-generated routing, dispatch, and audit metadata. Configure model, effort, and runtime-limit enforcement outside the prompt.

4. **Wait for approval.** Once approved, explicitly submit the recorded model and effort with enforced runtime limits. Audit actual dispatch arguments and runtime-control state.

5. **New model constraint means fresh routing.** Invalidate the old route. Reroute using the new constraint, record the complete revised decision, then request approval again. Never edit routed values merely to match the approval response.