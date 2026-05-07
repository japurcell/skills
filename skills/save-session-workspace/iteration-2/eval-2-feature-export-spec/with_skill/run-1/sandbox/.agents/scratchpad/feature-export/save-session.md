# Save Session

## Goal
- Continue and finalize the "feature export" spec so a follow-up agent can produce a small, actionable implementation plan (acceptance criteria, tasks, and minimal file edits) and a compact context bundle to run with.

## Current Status
- Done: An initial spec exists at `.agents/scratchpad/feature-export/spec.md` describing the export feature intent and basic behavior.
- In progress: No acceptance criteria, tasks, or implementation steps have been written.
- Next up: Flesh out acceptance criteria, break the work into small tasks, and collect the minimal set of files/tests the implementer will need.

## Decisions and Constraints
- Follow addy-context-engineering: keep only durable rules, the active spec, and the specific files that will be edited or tested.
- Place continuation work in this feature-scoped scratchpad (`.agents/scratchpad/feature-export/`).
- Do not include full repository dumps or transcripts—keep context focused (<2,000 lines).

## Relevant Files
- `.agents/scratchpad/feature-export/spec.md` — current spec to continue; primary source of truth for goals and assumptions.
- `.agents/scratchpad/feature-export/` — feature scratchpad folder (holds spec and future plan/save-session).
- `/home/adam/dev/personal/skills/skills/save-session/SKILL.md` — /save-session skill rules used to create this artifact (guides formatting and scope).
- `/home/adam/dev/personal/skills/skills/addy-context-engineering/SKILL.md` — context-selection rules that determine what to include in the follow-up session.

## Open Questions or Blockers
- None technical. The only open decision is whether the next agent should (A) produce runnable implementation tasks now, or (B) first produce acceptance criteria and get human confirmation. Default: produce tasks and tests to be implemented.

## Recommended Next Step
- Start a new, feature-scoped agent session that: (1) reads `spec.md`, (2) generates 3–6 acceptance criteria, (3) produces a small task list with files to edit, and (4) returns a compact context bundle (rules + spec excerpt + 2–4 relevant files) for the implementer.
