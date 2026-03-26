# User Notes

## Uncertainties

- The main naming decision is whether the reusable planning artifact should be `implementation-brief.md`, `handoff.md`, or reuse `plan.md`. I recommended `implementation-brief.md` because it is lighter than the full planning pipeline while remaining implementation-oriented.
- It is not yet clear whether the team wants downstream implementation skills to consume this artifact directly in v1, or whether the artifact is mainly for human-guided handoff. The recommendation assumes direct agent consumption is desirable.

## Trade-offs

- Standardizing a reusable planning artifact reduces handoff ambiguity, but it adds process overhead if used on small tasks. The recommendation keeps it track-sensitive to avoid turning every light task into a formal planning exercise.
- Reusing the scratchpad pattern keeps the design consistent with this repo, but it also nudges `feature-dev` closer to the `create-plan` / `create-tasks` family. That is useful if the goal is interoperability; it is less useful if the goal is to keep `feature-dev` totally standalone.
- Updating `code-architect.md` is low-risk and improves consistency. Updating `implement-plan/SKILL.md` to consume the new artifact would provide a stronger end-to-end handoff, but it is a larger behavioral change and can be deferred.

## Human Review Needed

- Confirm the artifact name.
- Confirm whether `feature-dev` should always write the artifact on Standard/Deep tracks, or only when the user explicitly asks for a handoff.
- Decide whether to add v1 support in `implement-plan/SKILL.md` for reading `implementation-brief.md` when `tasks.md` is absent.

## Scope Note

- No repository files were modified for this benchmark run. The proposal describes changes to make, but leaves the repo untouched outside the output directory.
