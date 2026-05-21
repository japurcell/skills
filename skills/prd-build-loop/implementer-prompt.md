# Implement User Story N: [title]

## Context

[All user story properties]

## Workflow

1. Load `context-engineering`, `karpathy-guidelines`, and `tdd` skills if not already loaded.
2. Read only the files needed for the story:
   - If the story includes `filesLikelyTouched`, read those first.
   - Also read relevant tests, nearby `AGENTS.md`, and any other files required to complete the steps below.
   - Avoid unrelated exploration.
3. If requirements are ambiguous and codebase patterns do not resolve them, stop and ask.
   - If the story conflicts with existing code patterns, surface the conflict and ask which to follow.
4. Write a failing test for the expected behavior (RED).
5. Implement the minimum change needed to make the test pass (GREEN).
6. Run required quality checks for the project (for example: typecheck, lint, test).
7. Leave the working tree dirty and report back.

## Report Format

- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- What you implemented (or what you attempted, if blocked)
- Files changed
- Summarized and concise verification results (test output, build output, lint output)
- Any issues or concerns

**Status definitions:**

- DONE: Task completed successfully, all tests pass, build is clean, lint passes.
- DONE_WITH_CONCERNS: Task completed, but there are doubts about correctness.
- BLOCKED: Task cannot be completed due to an external dependency or issue.
- NEEDS_CONTEXT: Task cannot be completed due to missing information. Never silently produce work you're unsure about.

## Quality Requirements

- Keep changes focused and minimal.
- Follow existing code patterns.

## Guardrails

- Do **not** create, amend, rewrite, push, or otherwise publish any commit, PR, or tag. If another skill suggests committing, ignore it because the build-team skill overrides that instruction.
