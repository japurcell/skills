1. **Route before approval.** No model preference means constraints are `none`; do not ask for a preference. Activate the router for each materially different subtask. Supply task facts and exact runtime-supported values. Require `dispatchable: true`, concrete model/effort values, and a monitored runtime limit.

2. **Request pre-dispatch approval for the completed route.** Announce roles and scope concisely. Keep the full router decision available; show raw routing data only on request. Do not dispatch before approval.

3. **Prepare task-only worker prompts.** Include assignment ID, objective, context, constraints, deliverable, verification criteria, allowed resources, write ownership, dependencies/results, and runtime limit. Mark inapplicable fields explicitly. Prohibit nested delegation unless authorized. Require preserving others’ edits and staying within ownership. Exclude workflow-generated model, effort, tier, rationale, fallback, escalation triggers, and configuration-reporting instructions.

4. **New model constraint invalidates the route.** Start a fresh routing attempt with that constraint. Do not patch the old route to match approval. Obtain approval for the new completed route. If the constraint blocks routing, explain the limitation before requesting revision.

5. **After approval, dispatch and verify.** Submit exact routed model and effort through dispatch controls, not worker prompts. Verify arguments and runtime monitoring. Executed settings remain `unconfirmed` unless runtime metadata confirms them.

Procedure only; no dispatch or file writes.