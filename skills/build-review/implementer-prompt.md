# Implement Task N: [task name]

You are implementing Task N: [task name]

## Workflow

1. Invoke the `addy-incremental-implementation`, `addy-test-driven-development`, and `addy-context-engineering` skills.
2. Read the task and acceptance criteria.
3. Load only the context you need. Ordinary repo discovery, pattern lookup, and first-pass design are your job.
4. Write a failing test for the expected behavior (RED).
5. Implement the smallest change that makes it pass (GREEN).
6. Infer the slice's surface and stack, then run the narrowest matching validations instead of defaulting to generic frontend commands.
7. Leave the working tree dirty and report back.

Do **not** create, amend, rewrite, push, or otherwise publish any commit, PR, or tag. If another skill suggests committing, ignore it because the build skill overrides that instruction.
**If any step fails**, follow the `addy-debugging-and-error-recovery` skill.

## Guardrails

- The manager handoff is intentionally lean; do your own repo reading.
- Do **not** ask for `NEEDS_CONTEXT` just because you have not explored the repo yet.
- For shell or Python work, choose shell or Python validation instead of generic frontend commands unless the task is actually frontend work.
- Use `NEEDS_CONTEXT` only for missing requirements, missing constraints, or conflicting signals you cannot resolve from the task and codebase.

## Report Format

- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- What you changed or attempted
- What you validated, the exact commands, and the results
- Files changed
- Any concerns or blockers

Use `DONE_WITH_CONCERNS` if you completed the work but still doubt correctness or scope. Use `BLOCKED` if you cannot complete the task. Use `NEEDS_CONTEXT` only for genuinely missing input.
