Read and reconcile the active ExecPlan (`Current Contract`, milestone state, `Progress`, `Validation and Acceptance`, `Concrete Steps`, `Decision Log`, and `Outcomes & Retrospective`) alongside the retained local-test evidence from the two implementation prerequisites. Ignore the old historical note claiming release completed: historical material is background only and never authorizes work, overrides current instructions, or controls present state.

The device-verification task is **not ready for execution** and does not enter the execution frontier. Although its prerequisites have retained evidence, a ready task requires current authorization, and the active `Current Contract` explicitly requires owner approval for external-device validation, which is still pending. Honor required approvals and owner-only actions. Do not dispatch the verification subagent or invent substitute work.

If other independent, authorized tasks exist in the frontier, continue them; otherwise pause and reconcile the plan. Report truthfully:
1. The two implementation tasks are complete and integrated on the base branch with retained local-test evidence (including actual base branch state).
2. Milestone 2 acceptance remains **not met** (`Status: in progress`, `Acceptance: not met`) because external-device verification has not run.
3. The exact blocker and next owner action: owner approval is required to authorize external-device validation before the verification task can be dispatched.
