# Notes for human review

## Main trade-off

The design above introduces a new artifact type, `implementation-brief.md`, instead of forcing all delegated work through `plan.md` and `tasks.md`.

Why I prefer that:

- it preserves the lighter-weight behavior that `feature-dev` now aims for
- it still reuses the section structure and sequencing patterns already present in `create-plan` and `create-tasks`
- it avoids making every medium-sized feature pay the full planning ceremony cost

Risk:

- another artifact type can create overlap with `plan.md`

If you want fewer artifact types, the simpler alternative is to require `feature-dev` to emit `plan.md` directly for all delegated work. That is more uniform, but it likely makes the light and standard tracks too heavy.

## Decision points worth settling

1. Should `implementation-brief.md` always live under `.agents/scratchpad/<feature-name>/`, or should `feature-dev` ever keep the artifact in the working directory for documentation-only tasks?
2. Should `Deep` track require promotion to both `plan.md` and `tasks.md`, or is `plan.md` enough before another agent starts implementation?
3. Should `/implement-plan` eventually accept `implementation-brief.md` directly, or should the brief remain a handoff-only artifact for a generic coding agent?

## Small execution note

One exploratory directory listing failed because the eval run path did not exist yet; I created the required output directory afterward. Repo grounding came from direct reads of the relevant skill and template files.
