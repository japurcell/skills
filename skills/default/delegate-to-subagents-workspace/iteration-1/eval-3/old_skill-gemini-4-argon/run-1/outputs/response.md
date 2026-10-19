**Before approval or dispatch**
- Plan for each subtask with defined `subtask_id`, objective/context, constraints/deliverable, verification criteria, allowed resources/write ownership (`none` for read-only), dependencies (`none`), and explicit `runtime_limit`.
- Complete router decision for each subtask (`dispatchable: true`, `tier`, exact `model`, exact `reasoning_effort`, `reason`, `escalation_trigger`, exact `fallback` or `none`) recorded in one session artifact outside maintained source.

**What goes in chat**
- One concise sentence naming the reviewer roles and scope.
- Do not show raw routing or audit data unless the user requests it, or a material routing/compliance failure occurs.
- Proceed directly to parallel dispatch without pausing for confirmation unless preexisting user-requested or runtime-required approval applies.

**Where submitted, executed, and completion data belong**
- Keep all workflow-generated routing, model/effort, and audit metadata out of subagent prompts; pass `model`, `reasoning_effort`, and `runtime_limit` explicitly via dispatch parameters/runtime controls.
- Record submitted arguments (`subtask_id`, `submitted.model`, `submitted.reasoning_effort`, `runtime_limit.value`, `runtime_limit.mechanism`), runtime-observed executed settings, and final completion results (`status`, `output_verified`, `routing_compliant`) in the same session artifact under `dispatches:`.

**When execution metadata is unavailable**
- Record `executed.model: unconfirmed` and `executed.reasoning_effort: unconfirmed` in the session artifact.
- Never infer executed values or use a subagent's self-report as confirmation.