## Understanding

I used the feature-dev skill instructions and selected a Standard track design pass. The improvement is to make handoff execution deterministic by treating one reusable planning artifact as the source of truth for the next agent, instead of leaving handoff quality to free-form prose.

## Relevant Findings

- skills/feature-dev/SKILL.md already requires a handoff artifact and defines minimum content, but the workflow does not fully enforce when to write it, how to keep it implementation-ready, or how to validate handoff completeness before stopping.
- skills/feature-dev/references/handoff-plan-template.md is a strong base artifact with sections that already map to implementation needs.
- skills/create-plan/references/plan-template.md shows a proven repository pattern: stable sectioned artifact, explicit context fields, and structure that downstream steps can consume.
- skills/create-tasks/references/tasks-template.md contributes another reusable pattern: ordered slices, dependency-aware sequencing, and explicit validation/checkpoints.
- skills/feature-dev/agents/code-architect.md already emits most of what handoff needs (architecture decision, implementation map, build sequence), so alignment work is low risk.

## Recommendation

Promote handoff-plan.md to a strict reusable planning artifact contract in feature-dev and introduce a lightweight handoff readiness gate.

Reusable planning artifact: .agents/scratchpad/<feature-name>/handoff-plan.md

This keeps feature-dev lighter than spec-first workflows while giving a follow-on implementation agent a concrete, low-ambiguity plan that can be executed without repeating discovery.

## Improvement Design

### 1) Add a Handoff Mode contract to feature-dev

In skills/feature-dev/SKILL.md, add explicit behavior:

- Enter Handoff Mode when any of the following are true:
  - track is Standard or Deep and implementation will continue in another turn
  - another agent is likely to implement or review
  - the response stops before implementation
  - the user asks for plan, handoff, or implementation map
- In Handoff Mode, writing handoff-plan.md is mandatory before ending the turn.
- The user-facing response must point to handoff-plan.md as source of truth.

### 2) Strengthen handoff-plan template with execution-oriented fields

In skills/feature-dev/references/handoff-plan-template.md, keep current sections and add these repository-proven elements:

- Metadata block (inspired by create-plan):
  - Date, Status, Track, Owner, Blockers, Recommended Next Step
- Slice dependency markers (inspired by create-tasks):
  - each slice includes Depends On and Parallelizable
- Validation checklist (inspired by implement-plan expectations):
  - command list, expected outputs, and stop conditions

This preserves one artifact while making it implementation-grade.

### 3) Align code-architect output to artifact sections

In skills/feature-dev/agents/code-architect.md, require headings that map 1:1 to handoff-plan.md:

- Relevant Findings
- Recommended Design
- Implementation Slices
- File-by-File Implementation Map
- Validation Plan
- Next-Agent Kickoff

Result: architect output can be copied into handoff-plan.md with minimal transformation.

### 4) Add a readiness gate in feature-dev before completion

In skills/feature-dev/SKILL.md, add a pre-stop gate:

- Every file in Relevant Findings has a clear reason.
- Every implementation slice has a concrete outcome and dependencies.
- File-by-file map includes exact files or directories.
- Validation plan includes at least one automated or manual verification path.
- Open questions are only truly blocking items, otherwise converted to assumptions.

If gate fails, the skill must revise handoff-plan.md before final response.

## Concrete Implementation Map

### Proposed file changes

1. skills/feature-dev/SKILL.md

- Add a new Handoff Mode subsection under Process Selection or Handoff Artifact.
- Add explicit trigger rules and mandatory artifact creation rule.
- Add handoff readiness gate checklist.
- Update Default Response Shape so Artifact Status always includes path and readiness state.

2. skills/feature-dev/references/handoff-plan-template.md

- Add metadata header fields.
- Extend Implementation Slices with dependency and parallelization fields.
- Extend Validation Plan with command table and expected outcomes.
- Keep existing section order to avoid migration friction.

3. skills/feature-dev/agents/code-architect.md

- Update output guidance to mirror handoff-plan headings.
- Require explicit file paths and ordered slices to reduce downstream ambiguity.

### Suggested rollout sequence

- Step 1: Update template first (defines target structure).
- Step 2: Update code-architect output guidance to target the new template.
- Step 3: Update feature-dev skill contract and readiness gate.
- Step 4: Run eval-2-handoff-architecture benchmark and compare with prior iteration on handoff completeness and implementation readiness.

## Why This Reuses Repo Patterns Well

- Artifact-first planning from create-plan
- Ordered, dependency-aware execution from create-tasks
- Implementation validation discipline from implement-plan

This avoids inventing a new planning system and instead makes feature-dev a lighter but reliable handoff path centered on one reusable planning artifact: handoff-plan.md.

## Outcome

The recommended improvement is to harden feature-dev around a required, quality-gated handoff-plan.md contract, with template and agent-output alignment so another agent can implement directly from that artifact without repeating discovery.
