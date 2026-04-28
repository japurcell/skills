# Prompt

You are executing /prd-implement for PRD #9000. All AFK child issues are complete and already synchronized in the parent task graph. The only remaining child issue is HITL #9005, "Approve rollout checklist," so the parent PRD issue must stay open. In the same user request, the user said: `implement PRD #9000 and open a PR when you're done.` Show the controller's exact final response.

# Response

PRD execution status for #9000

Completed this run:

- none

Blocked / waiting:

1. #9005 Approve rollout checklist - HITL; waiting for the required human approval.

Next ready work:

- none

Landing status:

- Local changes only; no commit, push, or PR actions performed in this run.

Notes:

- All AFK child issues are complete and synchronized in the parent task graph.
- The parent PRD issue remains open because #9005 is HITL.
- `prd-implement` stops here; landing work is out of scope for this run and would require a separate `commit` or `commit-to-pr` request after this skill finishes.
