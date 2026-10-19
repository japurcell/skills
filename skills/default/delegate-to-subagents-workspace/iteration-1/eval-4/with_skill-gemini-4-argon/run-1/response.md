### Routing and Approval Order
1. **Define assignment:** Specify all required fields (`identifier`, `objective`, `context`, `constraints`, `deliverable`, `verification criteria`, `allowed resources`, `write ownership`, `dependencies`, `runtime limit`), marking inapplicable fields `none` or `not applicable`.
2. **Route first (before approval):** Do not ask the user for a model or effort preference. Missing preference is not ambiguity; pass `none` for user model/effort constraints along with task facts and exact runtime-supported values to `subagent-model-router`. Do not apply configured defaults unless explicitly requested.
3. **Announce and pause for approval:** Announce roles and scope in one concise sentence (omit raw routing/audit data unless requested). Because the user requested pre-dispatch approval, pause after completing the route and wait for approval.
4. **Dispatch after approval:** If approved without changes and all dispatch requirements pass (`dispatchable: true`, exact supported `model` and `reasoning_effort` submitted via dispatch controls outside the prompt, explicit runtime limit + monitor, satisfied dependencies), dispatch the completed route.

### Worker Prompt Contents
**Include:**
- Full assignment fields (`identifier`, `objective`, `necessary context`, `constraints`, `deliverable`, `verification criteria`, `allowed resources`, `write ownership`, `dependencies`, `runtime limit`).
- Required dependency results.
- Nested-delegation policy (prohibit nested delegation unless intentionally authorized).
- Shared-codebase rules: preserve others' edits, stay within assigned write ownership, retain scoped evidence, and promptly notify the integration owner of durable findings/critical guidance for shared canonical docs.

**Exclude (prompt isolation):**
- All workflow-generated routing and audit metadata: `model`, `reasoning_effort`, tier, rationale, fallback, escalation triggers, and any instructions to identify or self-report execution settings or dispatch compliance. (Submit `model` and `reasoning_effort` exclusively via external dispatch controls.)

### If Approval Adds a New Model Constraint
- **Invalidate the route:** Do not patch or edit the existing route to match the approval response.
- **Start a fresh routing attempt:** Re-run `subagent-model-router` from scratch using the new user model constraint, task facts, and runtime-supported values.
- **Handle blockers if incompatible:** If the new constraint prevents a valid route (`dispatchable: false` or unsupported value), do not dispatch; explain the limitation to the user before asking them to revise the constraint.