# Implement User Story: [title]

## Context

[All user story properties]

- `story_id`: [id]
- `designGuidance`: [optional items with `description`, `rationale`, `source`]
- `filesLikelyTouched`: [optional likely relevant files]
- `prd_file`: [PRD file path]
- `progress_file`: [progress file path]
- `mode`: `implementation` | `review_fix`
- `current_wave`: [active `parallelBatch` story IDs/titles]
- `parallel_siblings`: [sibling story IDs/titles and `filesLikelyTouched`]
- `ownership_boundaries`: [owned files/surfaces and sibling-owned files/surfaces]
- `review_findings`: [required for `review_fix`; include code-review and security-audit findings plus required fix scope]

## Workflow

1. Invoke `tdd` and `context-engineering`.
2. Read only what is needed:
   - Start with `filesLikelyTouched` if provided.
   - Read `progress_file` if it exists, especially `## Codebase Patterns`.
   - Read nearest applicable `AGENTS.md` for files you may change.
   - Read tests for affected behavior.
   - Read other non-ignored files only as needed for dependencies, interfaces, or local patterns.
   - Avoid unrelated exploration.
3. For each `designGuidance` item, read `description` and `rationale` first. Read `source` only if needed and not ignored.
4. Treat this story as exclusive scope. Do not implement sibling stories, prerequisite work, or work owned by another story.
5. If requirements are missing/conflicting, a dependency appears unfinished, or required work overlaps sibling-owned files/surfaces, return `NEEDS_CONTEXT` or `BLOCKED`. Do not guess or widen scope.
6. If `mode = implementation`:
   - If behavior is clear and a targeted test is feasible, write or identify a failing test.
   - Implement the smallest change satisfying the story and relevant guidance.
7. If `mode = review_fix`:
   - Address all `review_findings` with the smallest necessary change.
   - Add or update tests if needed.
8. Run required checks for the changed area based on project instructions, local patterns, and affected tests. If no broader checks are clearly required, run the most targeted relevant tests available.
9. Leave the working tree dirty and report back.

## Rules

- Keep changes minimal and focused.
- Follow existing code patterns and all provided `designGuidance`.
- `filesLikelyTouched` is starting scope. If a change outside it is unavoidable, explain why.
- If an unavoidable change collides with a sibling-owned file or surface, stop and report overlap instead of proceeding.
- Do not modify `prd_file` or `progress_file`.
- Do not read, analyze, or change `.gitignore`-ignored files. If required scope appears ignored, return `NEEDS_CONTEXT`.
- Do not create, amend, rewrite, push, or publish any commit, PR, or tag.
- Always include a `Progress block`, even for `BLOCKED` or `NEEDS_CONTEXT`.
- `DONE` means implementer work is done; it does not mean the story is complete or `passes: true`.

## Report Format

- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- **What changed:** [concise summary]
- **Files changed/reviewed:** [list]
- **Verification:** [commands/checks and results]
- **Issues or concerns:** [none, or concise list]
- **Progress block:**

```text
## [Date/Time] - [Story ID]
- Role: implementer
- Summary
- Files changed/reviewed
- Issues or concerns
- Verification or outcome
- **Learnings for future iterations:**
  - Patterns discovered
  - Gotchas encountered
  - Useful context
---
```

## Status Definitions

- **DONE:** Story implementation or review fix completed and required checks passed. Finalization is still required.
- **DONE_WITH_CONCERNS:** Work completed, but correctness/completeness has explicit non-blocking uncertainty.
- **BLOCKED:** Cannot complete due to external dependency, tooling failure, unresolved prerequisite, or unavoidable blocked overlap.
- **NEEDS_CONTEXT:** Requirements are missing, ambiguous, conflicting, or overlap decisions are needed.
