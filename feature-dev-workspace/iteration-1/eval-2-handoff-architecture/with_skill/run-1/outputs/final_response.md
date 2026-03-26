# Understanding

Light track fits this task: the goal is a skill improvement for documentation/process, not a code implementation. The gap in `skills/feature-dev/SKILL.md` is not that it forgets handoff entirely; the gap is that the handoff is underspecified. The skill says to leave a handoff plan or implementation brief, but it does not define a file path, template, or consumer contract, so another agent still has to reconstruct the plan from conversational output.

# Relevant Findings

- `skills/feature-dev/SKILL.md` already contains the right intent: it mentions a reusable handoff plan in the description, an `Implementation Map` in the default response shape, and a `Handoff Artifact` section with the right high-level contents.
- `skills/create-plan/references/plan-template.md` shows the repo's preferred pattern for reusable design artifacts: a deterministic scratchpad location, lightweight metadata, technical context, project structure, and explicit readiness for the next phase.
- `skills/create-tasks/references/tasks-template.md` shows the repo's strongest implementation handoff pattern: phase-based execution, exact file paths, dependency ordering, independent checkpoints, and explicit validation.
- `skills/feature-dev/agents/code-architect.md` already asks for most of the content needed for a clean handoff: patterns found, architecture decision, component design, implementation map, build sequence, and critical details.
- The spec-kit agent templates in `spec-kit-template-copilot-sh-v0.4.2` use explicit handoffs and named downstream artifacts. That is the missing operational detail in `feature-dev` today.

# Recommendation

Introduce a deterministic reusable planning artifact named:

`.agents/scratchpad/<feature-name>/implementation-brief.md`

This should become the standard handoff output for `feature-dev` whenever discovery/design is completed by one agent and implementation will be performed by another agent or in a later turn. It should be lighter than the full `spec.md -> plan.md -> tasks.md` workflow, but structurally compatible with it.

The key change is to turn the current conversational handoff into a file-backed contract.

## Reusable Planning Artifact

The reusable planning artifact should contain these sections:

1. `Metadata`
   - feature name
   - process track
   - status (`draft`, `ready for implementation`, `blocked`)
   - originating skill/agent
   - recommended next agent or command
2. `Goal and Non-Goals`
3. `Relevant Findings and Source Files`
4. `Technical Context and Constraints`
5. `Decisions and Assumptions`
6. `Execution Slices`
   - setup
   - foundations
   - feature slices or user-story slices
   - polish
7. `File-by-File Implementation Map`
8. `Validation Plan`
9. `Next-Agent Contract`

That last section is the missing piece today. It should say what the next agent reads first, what order to implement in, what commands/tests to run, and when to stop and ask for clarification.

## Why this fits this repo

This proposal reuses existing patterns instead of inventing a new workflow:

- From `create-plan`: reuse stable scratchpad storage, metadata, technical context, and project structure.
- From `create-tasks`: reuse phase ordering, exact file-path discipline, checkpoints, and validation-oriented execution slices.
- From `code-architect`: reuse the expectation of a decisive architecture blueprint and implementation map.
- From spec-kit handoffs: reuse the idea that multi-agent continuation becomes reliable only when there is a named artifact and an explicit downstream contract.

The result is a bridge artifact: more structured than a prose answer, lighter than the full planning pipeline, and directly reusable by another agent.

# Proposed Skill Behavior

Update `feature-dev` so its handoff behavior is deterministic:

- `Light track`: create `implementation-brief.md` when the work is being handed off or paused after discovery/design. If the same agent will immediately implement, the artifact remains optional.
- `Standard track`: always create or update `implementation-brief.md` before implementation starts if another agent may take over.
- `Deep track`: always maintain `implementation-brief.md` as the canonical summary, refreshing it after exploration, architecture, and review.
- If `.agents/scratchpad/<feature-name>/` does not exist, create it.
- If `spec.md`, `plan.md`, or `tasks.md` already exist, the brief should link to them and avoid duplicating detail.

# Concrete Implementation Map

## 1. Update `skills/feature-dev/SKILL.md`

Make `implementation-brief.md` a first-class output instead of optional prose.

Changes to describe in the skill:

- In the description, keep the current handoff language but name the reusable planning artifact explicitly.
- In `Default Response Shape`, add guidance that when handoff applies, the response should point to the saved `implementation-brief.md` rather than only embedding the plan in chat.
- Replace the current `Handoff Artifact` section with a deterministic `Reusable Planning Artifact` section that defines:
  - the file path
  - when it is required
  - the required sections
  - the rule that another agent must be able to continue without repeating discovery
- In `Phase 5: Implementation`, add a rule that if implementation is deferred or delegated, refresh `implementation-brief.md` before stopping.
- In `Phase 7: Summary`, add a requirement to report the artifact path and readiness state.

## 2. Add `skills/feature-dev/references/implementation-brief-template.md`

Create a new template file for the reusable planning artifact.

The template should be a compact hybrid of `create-plan` and `create-tasks`:

- short metadata header
- technical context and constraints
- exact source files to read
- execution slices with file targets
- validation checklist
- next-agent contract

This keeps `SKILL.md` concise while giving the agent a canonical shape to follow.

## 3. Update `skills/feature-dev/agents/code-architect.md`

Align the architect agent's output with the new artifact so its result can be copied into `implementation-brief.md` with minimal cleanup.

Change the output guidance to use headings that map directly to the new template:

- Relevant Findings
- Architecture Decision
- Decisions and Assumptions
- Execution Slices
- File-by-File Implementation Map
- Validation Plan
- Next-Agent Notes

This reuses an existing agent rather than introducing a new one.

## 4. Optional follow-up: teach implementation flows to consume the artifact

A useful second step would be updating `skills/implement-plan/SKILL.md` so it can accept `implementation-brief.md` as a fallback input when `tasks.md` does not exist yet.

That is optional for v1. The artifact already improves handoff quality on its own because another agent can implement directly from it. But adding this fallback would complete the bridge between `feature-dev` and the repo's existing plan/tasks execution chain.

# Suggested Template Shape

```md
# Implementation Brief: [FEATURE]

**Status**: Ready for implementation
**Track**: Standard
**Origin**: feature-dev
**Next**: implementation agent

## Goal

## Non-Goals

## Relevant Findings and Source Files

- [path]: why it matters

## Technical Context and Constraints

## Decisions and Assumptions

## Execution Slices

### Slice 1: Setup

- [ ] Exact file change with path

### Slice 2: Foundations

- [ ] Exact file change with path

### Slice 3: Feature Slice / User Story

- [ ] Exact file change with path

## File-by-File Implementation Map

## Validation Plan

- automated checks
- manual verification
- review focus

## Next-Agent Contract

- Read these files first
- Implement slices in order
- Stop and ask if these assumptions fail
```

# Trade-offs

- This introduces some overlap with the full `create-plan` and `create-tasks` flow, but the overlap is intentional and useful: the brief is a lightweight bridge, not a replacement.
- Requiring the artifact on every tiny handoff would add overhead, so the requirement should be track-sensitive.
- Teaching downstream skills to consume the artifact directly is valuable, but can follow after the artifact itself is standardized.

# Outcome

The root fix is not “tell the model to write better handoff prose.” The root fix is to give `feature-dev` a named reusable planning artifact with a stable location, a repo-native structure, and a next-agent contract. That makes handoff clean, repeatable, and compatible with the planning patterns already used elsewhere in this repository.
