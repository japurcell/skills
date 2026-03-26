# Feature-Dev Skill Improvement Proposal: Clean Handoff to Another Agent

## Outcome

Upgrade the `feature-dev` skill snapshot so it always leaves a reusable, file-backed planning artifact when work may continue in another turn or agent.

The reusable planning artifact should be:

- Path: `.agents/scratchpad/<feature-name>/handoff-plan.md`
- Source template: `references/handoff-plan-template.md`
- Purpose: let a new agent continue implementation without repeating discovery/design.

This directly addresses the gap in the snapshot skill, which currently has no explicit handoff artifact contract.

## What To Change

### 1. Update `skills/feature-dev-workspace/skill-snapshot/SKILL.md`

Add the following capabilities (mirroring successful patterns already present in `skills/feature-dev/SKILL.md`):

- Process calibration (`Light`, `Standard`, `Deep`) to avoid over-process while still requiring durable artifacts for multi-step work.
- Explicit "Handoff Artifact" section defining:
  - required path
  - required template
  - when artifact creation is mandatory
  - minimum required content
  - quality bar checks before stopping
- "Default Response Shape" section including `Artifact Status` so handoff visibility is always included in user responses.
- Relaxed gating in implementation phase:
  - proceed when intent is clear and blockers are resolved
  - still require artifact if stopping before full implementation

### 2. Add `skills/feature-dev-workspace/skill-snapshot/references/handoff-plan-template.md`

Create a template aligned with existing repo conventions (same style as `create-plan`, `create-spec`, and `create-tasks` templates):

Required sections:

1. Summary
2. Goal / Non-Goals
3. Relevant Findings (with concrete files + why)
4. Technical Context and Constraints
5. Assumptions / Open Questions
6. Recommended Design
7. Implementation Slices (ordered)
8. File-by-File Implementation Map
9. Validation Plan
10. Next-Agent Kickoff

### 3. Keep Reuse and Interop with Existing Planning Skills

In the handoff template and skill instructions, include a decision line:

- `Recommended Next Step: implement directly | ask blocking question | promote to plan.md/tasks.md`

This cleanly bridges to:

- `skills/create-plan/SKILL.md`
- `skills/create-tasks/SKILL.md`
- `skills/implement-plan/SKILL.md`

So a handoff can remain lightweight for small work or escalate into full planning artifacts when complexity increases.

## Reusable Planning Artifact (Explicit)

Use `handoff-plan.md` as the single source of truth for cross-agent continuity.

Why this artifact works:

- It is persistent and file-backed (not lost in chat history).
- It captures both architecture decisions and execution sequencing.
- It includes validation instructions so the next agent can verify work, not just code blindly.
- It is compact compared to full spec/plan/tasks flow, but upgradeable into that flow.

## Concrete Implementation Map

1. Edit `skills/feature-dev-workspace/skill-snapshot/SKILL.md`

- Expand frontmatter description to mention reusable handoff plan usage.
- Add **Process Selection** section (`Light/Standard/Deep`).
- Add **Default Response Shape** with `Artifact Status`.
- Update phases:
  - Discovery: scale todo depth by track.
  - Exploration: 1 vs 2 vs 2-3 explorer agents by track.
  - Clarification: ask only high-leverage questions; proceed with explicit assumptions when non-blocking.
  - Architecture: one approach for light, multi-option only when meaningful.
  - Implementation: remove blanket approval gate; proceed when user intent is clear.
  - Quality Review: scale reviewer-agent count by risk.
- Add full **Handoff Artifact** section:
  - required path `.agents/scratchpad/<feature-name>/handoff-plan.md`
  - template `references/handoff-plan-template.md`
  - required scenarios (standard/deep, likely handoff, stop-before-implement, user asks for plan/handoff)
  - minimum content checklist (goal/non-goals, findings, context, assumptions, design, slices, file map, validation, kickoff)
  - quality bar checklist (specific files, runnable validation, limited open questions)
- Add guidance in summary phase to point users to `handoff-plan.md`.

2. Create `skills/feature-dev-workspace/skill-snapshot/references/handoff-plan-template.md`

- Copy structure from the proven template in `skills/feature-dev/references/handoff-plan-template.md`.
- Preserve placeholders and section order so downstream tooling/agents can rely on stable shape.
- Include `Recommended Next Step` line for escalation into `plan.md/tasks.md` path.

3. Optional but recommended: align links in `skills/feature-dev-workspace/skill-snapshot/SKILL.md`

- Ensure references to `agents/code-explorer.md`, `agents/code-architect.md`, `agents/code-reviewer.md` exist or are removed if not part of snapshot packaging.
- If snapshot is meant to be portable, include a short fallback instruction when these agents are unavailable.

## Acceptance Criteria for This Improvement

- The skill produces a reusable handoff artifact path every time handoff conditions are met.
- Another agent can begin implementation from `handoff-plan.md` without repeating discovery.
- Artifact contains ordered implementation slices and file-by-file map.
- Artifact includes concrete validation commands/checks.
- The workflow remains lightweight for bounded tasks and deeper only when risk/ambiguity warrants it.

## Suggested Validation Run (for the skill author)

1. Run a feature request that stops after architecture design.
2. Confirm the agent writes `.agents/scratchpad/<feature-name>/handoff-plan.md`.
3. Start a second agent with only that artifact and repository access.
4. Verify second agent can execute implementation slices without re-asking baseline discovery questions.
5. Confirm it can either:
   - implement directly, or
   - escalate cleanly to `create-plan`/`create-tasks` when complexity requires.

This gives you a clean handoff architecture with a reusable planning artifact while staying consistent with patterns already established in this repository.
