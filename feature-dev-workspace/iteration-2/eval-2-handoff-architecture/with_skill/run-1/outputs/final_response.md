## Understanding

I used the `feature-dev` skill in `Standard` track mode. The improvement I would make is to turn the current vague “handoff artifact” guidance in `skills/feature-dev/SKILL.md` into a first-class, reusable planning artifact that another agent can consume directly without repeating discovery.

## Relevant Findings

- `skills/feature-dev/SKILL.md` already expects a reusable handoff artifact, but it only defines the contents at a high level and does not give a template, path, or readiness criteria.
- `skills/create-plan/SKILL.md` and `skills/create-plan/references/plan-template.md` show the strongest reusable pattern in this repo: a planning command becomes reliable when it writes a concrete artifact with a stable structure.
- `skills/create-tasks/SKILL.md` adds the missing execution detail: ordered phases, per-story slices, explicit file targets, and validation checkpoints.
- `skills/implement-plan/SKILL.md` shows what the downstream consumer actually needs: clear execution order, dependency rules, test expectations, and stop/go checkpoints.
- `skills/feature-dev/agents/code-architect.md` already produces most of the raw material needed for a handoff artifact: patterns, architecture decision, implementation map, and build sequence.

## Recommendation

Add a reusable planning artifact named `handoff-plan.md` to the `feature-dev` workflow.

The key change is not more process. The key change is giving `feature-dev` one explicit artifact that sits between discovery/design and implementation, similar to how this repo uses `plan.md` and `tasks.md`. The artifact should be required whenever:

- the work is `Standard` or `Deep` track,
- implementation will be deferred to another agent or later turn,
- or the response stops at design rather than code changes.

### Proposed Artifact

Runtime output path:

`.agents/scratchpad/<feature-name>/handoff-plan.md`

Template source path inside the skill:

`skills/feature-dev/references/handoff-plan-template.md`

### Required Sections

1. `Summary`
   - feature goal, user-visible outcome, chosen track
2. `Goal / Non-Goals`
   - tighten scope for the implementation agent
3. `Relevant Findings`
   - high-signal repo patterns and exact source files to read first
4. `Assumptions / Open Questions`
   - only unresolved items that can change implementation
5. `Recommended Design`
   - one chosen approach, why it fits, and rejected alternatives only if material
6. `Implementation Slices`
   - ordered phases or increments, modeled after the repo’s `create-tasks` and `implement-plan` flow
7. `File-by-File Implementation Map`
   - exact files to create or modify, responsibility of each change, and key integration points
8. `Validation Plan`
   - tests, review checkpoints, and success criteria
9. `Next-Agent Kickoff`
   - the first concrete steps the implementation agent should take without repeating discovery

This `handoff-plan.md` is the reusable planning artifact. It is specific enough to drive implementation, but lighter than the full `create-plan -> create-tasks -> implement-plan` stack.

## Why This Fits This Repo

This repo already favors artifact-driven workflows:

- `create-plan` establishes a stable `plan.md` structure.
- `create-tasks` turns planning into executable slices.
- `implement-plan` assumes those slices exist and uses them to coordinate implementation.

`feature-dev` currently stops short of that reliability. It asks for a handoff artifact, but not in a way that guarantees another agent can pick up the work. A dedicated `handoff-plan.md` closes that gap while preserving `feature-dev` as the lighter-weight, flexible option.

## Concrete Implementation Map

1. Update `skills/feature-dev/SKILL.md`
   - In `Core Principles`, replace the generic reusable-artifact guidance with a required artifact rule for handoff scenarios.
   - In `Default Response Shape`, add a `Reusable Planning Artifact` section so the output format matches the new behavior.
   - In `Phase 4: Architecture Design`, require the chosen design to be normalized into `handoff-plan.md` before stopping.
   - In `Phase 5: Implementation`, clarify that if implementation is deferred, the command must write `handoff-plan.md` rather than only summarizing recommendations.
   - Replace the current `Handoff Artifact` section with a stricter contract: path, required headings, and readiness criteria.

2. Add `skills/feature-dev/references/handoff-plan-template.md`
   - Base the top of the template on `skills/create-plan/references/plan-template.md`: summary, scope, technical context, source files, and structure.
   - Borrow execution concepts from `skills/create-tasks/SKILL.md`: ordered slices, file targets, and validation checkpoints.
   - Keep it shorter than `plan.md` plus `tasks.md`; this should be one artifact, not a mini-framework.

3. Update `skills/feature-dev/agents/code-architect.md`
   - Align the architect output headings with the new template so the agent can draft most of `handoff-plan.md` directly.
   - Add required output for `Implementation Slices`, `Validation Plan`, and `Next-Agent Kickoff`.
   - Keep the single-approach bias; another agent should receive one decisive plan, not a menu.

4. Optional follow-on refinement in `skills/feature-dev/SKILL.md`
   - Add a simple readiness test before handoff:
     - every implementation slice has a concrete outcome,
     - every referenced file has a purpose,
     - validation covers the main risk,
     - unresolved questions are either explicitly blocked or turned into assumptions.

## Suggested Template Shape

```md
# Handoff Plan: <feature>

## Summary

## Goal / Non-Goals

## Relevant Findings

## Assumptions / Open Questions

## Recommended Design

## Implementation Slices

## File-by-File Implementation Map

## Validation Plan

## Next-Agent Kickoff
```

## Outcome

The improvement is to make `feature-dev` emit a reusable planning artifact explicitly: `handoff-plan.md`. That keeps the skill aligned with the repo’s artifact-first planning patterns while giving a downstream implementation agent a concrete, low-ambiguity starting point.
