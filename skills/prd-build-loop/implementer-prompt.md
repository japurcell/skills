# Implement User Story: [title]

## Context
[All user story properties]

- `designGuidance`: [optional list of items with `description`, `rationale`, `source`]
- `filesLikelyTouched`: [optional list of likely relevant files]
- `progress_file`: [progress file path]
- `mode`: `initial_implementation` | `review_fix`
- `review_findings`: [only for `review_fix`]

## Workflow
1. Load the `tdd` skill if not loaded.
2. Read only what is needed:
   - Start with `filesLikelyTouched` if provided.
   - Read `progress_file` if it exists, especially `## Codebase Patterns`.
   - Read tests for the affected behavior.
   - Read the nearest applicable `AGENTS.md` for files you may change.
   - Read other files only as needed for dependencies, interfaces, or local patterns.
   - Avoid unrelated exploration.
3. For each `designGuidance` item, read `description` and `rationale` first. Read `source` only if needed to implement correctly.
4. If requirements are missing, ambiguous, or conflicting, return `NEEDS_CONTEXT`. Do not guess.
5. If `mode = initial_implementation`:
   - if behavior is clear and a targeted test is feasible, write or identify a failing test
   - implement the smallest change that makes it pass and follows relevant guidance
6. If `mode = review_fix`:
   - address all `review_findings` with the smallest necessary change
   - add or update tests if needed
7. Run required quality checks for the changed area based on project instructions, local patterns, and affected tests. If no broader checks are clearly required, run the most targeted relevant tests available.
8. Leave the working tree dirty and report back.

## Quality Requirements
- Keep changes minimal and focused.
- Follow existing code patterns.
- Follow all provided `designGuidance`.
- `progress_file` is read-only.

## Guardrails
- Do not create, amend, rewrite, push, or otherwise publish any commit, PR, or tag.

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
- **NEEDS_CONTEXT:** requirements are missing or conflicting; do not guess