### Routing and approval order

Route first, record second, request approval third, dispatch last:

1. Do not ask the user to choose, confirm, or restate a model or reasoning effort before routing; absent preferences are not ambiguity.
2. Activate `subagent-model-router` with `none` for model/effort constraints, plus task facts (objective, stakes, security sensitivity, ambiguity, expected context size, review history, verification plan) and exact runtime-supported models and effort values. Do not use configured, inherited, or runtime defaults.
3. Obtain a complete route (`dispatchable`, `tier`, exact `model`, exact `reasoning_effort`, `reason`, `escalation_trigger`, exact `fallback` or `none`).
4. Record the complete route decision in one session artifact outside maintained source before requesting approval, and announce roles/scope in one concise chat sentence.
5. Request pre-dispatch approval for the completed, recorded route.
6. After approval, dispatch with the recorded `model`, `reasoning_effort`, and explicit runtime-limit enforcement passed as dispatch arguments outside the prompt.

### Worker prompt contents

**Include:**
- Objective and necessary context
- Task constraints
- Expected deliverable
- Verification criteria
- Allowed resources and write ownership (plus shared-doc integration owner notification rules if applicable)
- Required dependency results
- Explicit nested-delegation prohibition (default) or intentional authorization

**Exclude** (pass via external dispatch parameters or keep in orchestrator session artifact):
- Selected model, reasoning effort, or tier
- Route, rationale, fallback, or escalation trigger
- Instructions to identify or report model, effort, runtime configuration, or dispatch arguments
- Dispatch-compliance or orchestration-audit instructions

### If approval adds a new model constraint

1. Do not edit the existing route to match the approval response and do not dispatch.
2. Invalidate the current route.
3. Begin a fresh routing attempt via `subagent-model-router` using the original task facts and runtime capabilities plus the newly added user model constraint.
4. Record the new route in the same session artifact:
   - If `dispatchable: true`, request approval for the revised route (if pre-dispatch approval still applies) and dispatch only after approval with the new exact values.
   - If the constraint prevents a valid route (`dispatchable: false`), record the non-dispatchable route, explain the limitation in chat, and ask the user to revise the constraint.