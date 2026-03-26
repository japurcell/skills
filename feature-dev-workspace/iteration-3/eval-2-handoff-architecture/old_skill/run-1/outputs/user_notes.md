# User Notes

## Uncertainties

- The snapshot skill references agent files (`agents/code-explorer.md`, `agents/code-architect.md`, `agents/code-reviewer.md`), but this eval did not verify whether those files exist inside the snapshot package itself. If missing, add fallback behavior text.
- The exact trigger threshold between `Light` and `Standard` tracks may still need tuning from real usage data (task size, ambiguity, and risk are partly judgment-based).

## Trade-Offs

- Requiring `handoff-plan.md` for standard/deep work adds overhead, but it significantly improves multi-agent continuity and reduces repeated discovery.
- Keeping handoff artifact lightweight preserves speed, but may under-specify very large features unless escalated to `plan.md` + `tasks.md`.
- Allowing implementation without a hard approval gate improves throughput, but relies on stronger assumption logging and explicit blocker handling.

## Human Review Focus

- Validate that the proposed handoff template is not duplicating too much of existing `create-plan` outputs.
- Confirm naming/path conventions for `.agents/scratchpad/<feature-name>/` are accepted across your current workflow.
- Decide whether to enforce artifact creation on all tracks or keep it optional for completed light-track requests.
