# Save Session

## Goal
- Ship CSV + JSON export flow.

## Current Status
- Done: Spec drafted at `.agents/scratchpad/feature-export/spec.md`.
- In progress: No implementation or plan started.
- Next up: Create `.agents/scratchpad/feature-export/plan.md` with acceptance criteria and break the work into small, testable tasks.

## Decisions and Constraints
- Export formats: CSV and JSON only (per spec).
- Keep the /save-session feature-scoped under `.agents/scratchpad/feature-export/`.
- Preserve only durable context relevant to continuing work (rules, spec, blockers).

## Relevant Files
- `/home/adam/dev/personal/skills/skills/save-session-workspace/iteration-2/eval-2-feature-export-spec/with_skill/run-2/sandbox/.agents/scratchpad/feature-export/spec.md` — current spec and goal.
- `/home/adam/dev/personal/skills/skills/save-session/SKILL.md` — local /save-session workflow guidance (follow when creating/resuming /save-sessions).
- `/home/adam/dev/personal/skills/skills/addy-context-engineering/SKILL.md` — guidance for what context to keep; minimal durable context only.

## Open Questions or Blockers
- No technical blockers recorded; work has not started beyond the draft spec.
- Clarify desired acceptance criteria (rows, headers, field ordering) if not already in spec.

## Recommended Next Step
- Create `plan.md` in the same folder with clear acceptance criteria and one minimal failing test for CSV export; then implement the CSV path to make the test pass, followed by JSON.
