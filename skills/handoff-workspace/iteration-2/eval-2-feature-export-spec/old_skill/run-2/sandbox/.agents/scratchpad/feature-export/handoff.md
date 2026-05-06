# Handoff

## Goal
- Ship CSV + JSON export flow for the feature in this scratchpad.

## Current Status
- Done: Spec drafted (`.agents/scratchpad/feature-export/spec.md`).
- In progress: None — plan not started.
- Next up: Create a short plan.md with acceptance criteria and the first implementation task.

## Decisions and Constraints
- Follow local handoff and context-engineering rules (see skill-snapshot and addy-context-engineering SKILLs).
- Keep the handoff minimal: only durable files and the single next action.

## Relevant Files
- `.agents/scratchpad/feature-export/spec.md` — active feature spec; source of truth for goals and acceptance criteria.
- `/home/adam/dev/personal/skills/skills/handoff-workspace/skill-snapshot/SKILL.md` — handoff workflow rules; explains template and placement.
- `/home/adam/dev/personal/skills/skills/addy-context-engineering/SKILL.md` — context-selection rules used to decide what to preserve.

## Open Questions or Blockers
- No technical blockers recorded; plan not started so implementation details remain to be decided.

## Recommended Next Step
- Write `.agents/scratchpad/feature-export/plan.md` that breaks the work into: (1) acceptance criteria; (2) implement export serializers (CSV/JSON) and unit tests; (3) add export endpoint and integration test; (4) manual verification instructions.

- Single best next action for the next agent: create `plan.md` and open a PR with the first commit implementing serializer unit tests.
