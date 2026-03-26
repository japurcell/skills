# Improvement design for feature-dev handoff

The strongest improvement is to make `feature-dev` produce a first-class reusable planning artifact instead of a short freeform handoff note. I would add an `implementation-brief.md` artifact at `.agents/scratchpad/<feature-name>/implementation-brief.md` and make the skill require it whenever work is likely to be handed to another agent, paused for a later turn, or promoted into deeper planning.

This fits the repo better than inventing a separate workflow. The current `feature-dev` skill already defines a concise handoff shape. `create-plan` already defines durable technical planning structure in `plan.md`, and `create-tasks` defines execution ordering in `tasks.md`. The gap is the missing bridge between exploratory architecture work and implementable execution. `implementation-brief.md` should be that bridge: lighter than the full spec/plan/tasks pipeline, but structured so another agent can implement directly or expand it into `plan.md` and `tasks.md` without repeating discovery.

## Repo patterns to reuse

Reuse these existing patterns rather than creating a completely new format:

1. From `skills/feature-dev/SKILL.md`: keep the current handoff sections as the backbone: goal, findings, open questions or assumptions, recommendation, file-by-file implementation map, validation plan.
2. From `skills/create-plan/references/plan-template.md`: borrow `Technical Context`, `Project Structure`, and explicit constraints so the next agent does not have to rediscover stack, boundaries, and expected layout.
3. From `skills/create-tasks/references/tasks-template.md`: borrow phased sequencing, dependency notes, and validation checkpoints so the brief is actionable instead of purely descriptive.
4. From `skills/feature-dev/agents/code-explorer.md` and `skills/feature-dev/agents/code-architect.md`: standardize agent outputs so they can be assembled into the artifact with minimal synthesis loss.

## Proposed reusable planning artifact

Use `.agents/scratchpad/<feature-name>/implementation-brief.md` with these sections:

1. `Summary`
   One-paragraph restatement of the feature request, selected track (`Light`, `Standard`, or `Deep`), and whether this brief is for direct implementation or later expansion.
2. `Goals and Non-Goals`
   Explicit scope boundary so the implementer does not widen the task.
3. `Relevant Findings`
   Key repo patterns, abstractions, and source files to read first.
4. `Technical Context`
   Language, primary dependencies, testing approach, constraints, and any environment assumptions. This mirrors the useful parts of `plan.md` without forcing a full planning pass.
5. `Open Questions or Assumptions`
   Only unresolved decisions that materially affect implementation. If proceeding without answers, list the chosen assumptions.
6. `Recommended Design`
   The chosen approach and why it fits this codebase. This should be decisive, not a menu of options.
7. `Implementation Map`
   File-by-file change list with responsibilities, sequencing notes, and clear dependency edges.
8. `Validation Plan`
   Tests, manual checks, review checkpoints, and expected evidence of completion.
9. `Promotion Path`
   State whether the next step is:
   - implement directly from this brief
   - expand into `plan.md`
   - expand into `tasks.md`
   - stop for clarification

That artifact is reusable because it works in both directions: `feature-dev` can hand it to a coding agent immediately, and the same artifact can seed the repo's richer planning flow when the work turns out to be larger than expected.

## Skill behavior changes

I would change `feature-dev` so handoff is an explicit mode, not an optional afterthought.

1. Add a `Delegated Handoff` rule near `Process Selection`.
   - `Light`: create the brief only when implementation is deferred, another agent will continue, or the change surface spans several files.
   - `Standard`: create or update the brief before implementation starts and keep it current if the plan changes.
   - `Deep`: always create the brief, and recommend promotion to `plan.md` and `tasks.md` before coding.
2. Replace the current vague `Leave reusable artifacts` guidance with a hard requirement:
   - If the skill is not implementing immediately, it MUST produce `implementation-brief.md`.
   - If another agent is likely to continue, responses should summarize the brief and point to it as the source of truth.
3. Add a short `Artifact Quality Bar` section:
   - every referenced file must have a reason to be read
   - implementation map must name concrete files or directories
   - validation plan must be specific enough for another agent to execute
   - assumptions must be explicit when questions are left unresolved
4. Update `Default Response Shape` to include `Implementation Brief Status` when relevant.

## Concrete implementation map

If I were implementing this repo change, I would make these edits:

1. `skills/feature-dev/SKILL.md`
   - Add a `Delegated Handoff` subsection after `Process Selection`.
   - Make `implementation-brief.md` a required output when implementation is deferred or delegated.
   - Add track-specific rules for when to create only the brief versus when to recommend promotion to `plan.md` and `tasks.md`.
   - Expand the `Handoff Artifact` section into a concrete schema aligned with the new template.
2. `skills/feature-dev/references/implementation-brief-template.md` (new)
   - Add the reusable artifact template with the sections listed above.
   - Keep it compact enough for light work but structured enough to seed `create-plan` and `create-tasks`.
3. `skills/feature-dev/agents/code-explorer.md`
   - Require a final block with `Essential files`, `Change surface`, and `Open unknowns`.
   - This makes explorer output directly reusable in `Relevant Findings` and `Open Questions or Assumptions`.
4. `skills/feature-dev/agents/code-architect.md`
   - Require a final block with `Recommended design`, `Implementation map`, `Build sequence`, and `Validation checkpoints`.
   - This makes architect output drop cleanly into the brief with less lossy synthesis.
5. Optional follow-up: `skills/implement-plan/SKILL.md`
   - Add support for consuming `implementation-brief.md` directly for smaller tasks, or at minimum document that larger delegated work should promote the brief into `plan.md` plus `tasks.md` before `/implement-plan`.

## Expected handoff flow

The resulting flow would be:

1. `feature-dev` explores the codebase and resolves high-leverage questions.
2. `feature-dev` chooses a recommendation and writes `.agents/scratchpad/<feature-name>/implementation-brief.md`.
3. If the task is still medium or large, the next step is promotion into `plan.md` and optionally `tasks.md` using the existing repo patterns.
4. Another agent starts by reading the brief, then the referenced source files, then implements against the validation plan.

This is the key improvement: the reusable planning artifact is no longer an informal summary in chat. It becomes a durable file, shaped by patterns the repo already uses, that cleanly separates discovery and architecture from implementation while preserving enough specificity for a second agent to continue without redoing the work.
