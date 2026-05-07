# Save Session

## Goal
- Ship CSV + JSON export flow.

## Current Status
- Done: Spec drafted at `.agents/scratchpad/feature-export/spec.md`.
- In progress: None — implementation not started.
- Next up: Create a minimal plan and implement backend export endpoints, add tests, and wire a UI trigger.

## Decisions and Constraints
- Follow project conventions and rules (see skill-snapshot SKILL.md).
- Prefer a backend-first approach with endpoints like `/api/export?format=csv|json` and stream CSV responses to avoid large memory use.
- Reuse existing auth and pagination patterns where applicable.

## Relevant Files
- `/home/adam/dev/personal/skills/skills/save-session-workspace/iteration-2/eval-2-feature-export-spec/old_skill/run-1/sandbox/.agents/scratchpad/feature-export/spec.md` — active feature spec; primary reference for expected CSV/JSON fields and UX.
- `/home/adam/dev/personal/skills/skills/save-session-workspace/skill-snapshot/SKILL.md` — /save-session workflow and template; dictates path and structure for this artifact.
- `/home/adam/dev/personal/skills/skills/addy-context-engineering/SKILL.md` — context selection rules used to decide what to preserve.

## Open Questions or Blockers
- CSV header ordering and exact field selection (use spec defaults unless instructed otherwise).
- Confirm whether exports must respect current user scoping/filters (likely yes).

## Recommended Next Step
- Write a short plan (3–5 steps): add endpoints, implement streaming CSV generator, add tests, and a minimal UI action to trigger export. Then implement and run tests.
