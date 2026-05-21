# Implement User Story: [title]

## Context

[All user story properties]

- `progress_file`: [progress file path]
- `mode`: `initial_implementation` | `review_fix`
- `review_findings`: [present only for `review_fix`]

## Workflow

1. Load `context-engineering`, `karpathy-guidelines`, and `tdd` if not already loaded.
2. Read only the files needed:
   - if provided, start with `filesLikelyTouched`
   - if `progress_file` exists, read it, especially `## Codebase Patterns`
   - read relevant tests and nearby `AGENTS.md`
   - avoid unrelated exploration
3. If requirements are ambiguous or conflicting, return `NEEDS_CONTEXT`. Do not guess.
4. If `mode = initial_implementation`:
   - write or identify a failing test for the expected behavior when practical
   - implement the minimum change to make it pass
5. If `mode = review_fix`:
   - address all `review_findings` with the minimum necessary change
   - add or update tests when needed
6. Run required quality checks for the changed area.
7. Leave the working tree dirty and report back.

## Report Format

- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- What you implemented
- Files changed
- Concise verification results
- **Learnings for future iterations:**
  - Patterns discovered
  - Gotchas encountered
  - Useful context
- Any issues or concerns

## Status Definitions

- **DONE:** task completed and required checks passed
- **DONE_WITH_CONCERNS:** completed, but correctness or completeness is uncertain
- **BLOCKED:** cannot complete due to external dependency or issue
- **NEEDS_CONTEXT:** missing or conflicting requirements; do not guess

## Quality Requirements

- Keep changes focused and minimal.
- Follow existing code patterns.

## Guardrails

- Do not create, amend, rewrite, push, or otherwise publish any commit, PR, or tag.
- `progress_file` is read-only.
