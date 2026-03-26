# Handoff Plan: Stricter Handoff-Policy Enforcement for feature-dev

**Status**: ready for implementation
**Track**: Standard
**Origin**: feature-dev
**Feature Area**: skill workflow policy and artifact quality gates
**Recommended Next Step**: implement directly

## Summary

This handoff prepares a bounded improvement to the live feature-dev skill so handoff behavior is enforced instead of left to interpretation. The implementation should make artifact creation deterministic whenever work is paused before implementation or likely to transfer to another agent, while preserving the current feature-dev workflow shape and template-first approach. The next agent should update the skill contract, keep the handoff template aligned, and tighten eval coverage so the benchmark fails if artifact creation or exact path reporting is skipped.

## Goal / Non-Goals

- Goal: Require feature-dev to create or update `handoff-plan.md` in clearly defined deferred or delegated scenarios.
- Goal: Require the user-facing response to include `Artifact Status` with the exact artifact path whenever the artifact is required.
- Goal: Make the handoff quality gate explicit enough that another agent can continue without repeating discovery.
- Non-goal: Redesign the overall Light / Standard / Deep workflow beyond the handoff-policy surface.
- Non-goal: Introduce a new artifact type or replace `handoff-plan.md` with `plan.md`.

## Relevant Findings

- `skills/feature-dev/SKILL.md`: already defines a Handoff Artifact section, required path, minimum content, and quality bar; this is the primary file to tighten because current wording still leaves some edge-case interpretation.
- `skills/feature-dev/references/handoff-plan-template.md`: defines the canonical handoff shape and should stay the source of truth for required sections so enforcement does not drift from the artifact format.
- `skills/feature-dev/agents/code-architect.md`: already asks for architecture, implementation map, and build sequence details that map naturally into `handoff-plan.md`; aligning this output reduces translation work for follow-on agents.
- `skills/feature-dev/evals/evals.json`: already contains this benchmark prompt and expectations around concrete artifact creation and exact path reporting; it is the right place to harden regression coverage.
- `skills/create-plan/references/plan-template.md`: demonstrates stronger artifact metadata discipline and deterministic scratchpad conventions that can be borrowed without making feature-dev heavyweight.
- `skills/create-tasks/references/tasks-template.md`: shows the repo’s preferred level of ordered execution detail and validation specificity for reliable continuation by another agent.

## Technical Context and Constraints

- Language / framework: markdown-based skill instructions, prompt files, and eval definitions.
- Runtime or platform constraints: no runtime behavior changes; enforcement exists through instruction clarity, artifact requirements, and benchmark expectations.
- Existing conventions to preserve: `.agents/scratchpad/<feature-name>/handoff-plan.md`, the current feature-dev section ordering, and the existing handoff template structure.
- Dependencies or interfaces affected: `skills/feature-dev/SKILL.md`, `skills/feature-dev/references/handoff-plan-template.md`, `skills/feature-dev/agents/code-architect.md`, and `skills/feature-dev/evals/evals.json`.
- Validation surface: benchmark execution for stop-before-implementation behavior, artifact existence checks, and response-level exact path reporting.

## Assumptions / Open Questions

- Assumption: The artifact path contract stays as `.agents/scratchpad/<feature-name>/handoff-plan.md` rather than introducing aliases.
- Assumption: The strongest enforcement should apply whenever implementation is deferred or another agent is expected to continue, regardless of whether discovery/design work is otherwise lightweight.
- Open question: Should Standard track require artifact creation even when implementation is fully completed in the same turn?
- Risk if wrong: If enforcement is too broad, bounded work pays unnecessary overhead; if it stays too narrow, the benchmark gap remains and cross-agent continuity stays unreliable.

## Recommended Design

Tighten the live feature-dev skill with explicit MUST-level handoff conditions and a pre-stop readiness gate, while keeping the existing template and artifact path intact.

Why this fits this repo:

- It reuses the handoff contract already present in `skills/feature-dev/SKILL.md` instead of inventing a parallel process.
- It keeps `handoff-plan.md` as the single lightweight continuity artifact, which matches the direction already established in prior feature-dev iterations.
- It borrows stronger discipline from `create-plan` and `create-tasks` only where it improves determinism: metadata clarity, ordered slices, and validation specificity.

Main trade-off:

- Stronger MUST rules increase consistency and benchmarkability, but they also narrow the model’s discretion for borderline Light-track cases. The recommended implementation keeps that trade-off contained by only making deferred or delegated work mandatory.

## Implementation Slices

### Slice 1: Tighten handoff-policy contract in the skill

- Outcome: `skills/feature-dev/SKILL.md` clearly states when `handoff-plan.md` is mandatory and when ending the turn without it is not allowed.
- Files: `skills/feature-dev/SKILL.md`
- Dependencies: none

### Slice 2: Align artifact and agent-output requirements

- Outcome: the handoff template and architect output are aligned closely enough that another agent can populate `handoff-plan.md` with minimal interpretation.
- Files: `skills/feature-dev/references/handoff-plan-template.md`, `skills/feature-dev/agents/code-architect.md`
- Dependencies: Slice 1

### Slice 3: Harden eval coverage for artifact quality gate

- Outcome: the benchmark fails when the artifact is missing, the path is omitted, or the response reports a path without a concrete file-backed artifact.
- Files: `skills/feature-dev/evals/evals.json`
- Dependencies: Slice 1, Slice 2

## File-by-File Implementation Map

- `skills/feature-dev/SKILL.md`: add explicit MUST rules that require creating or updating `handoff-plan.md` when stopping before implementation, when another agent is expected to continue, and when the user explicitly asks for a handoff or reusable plan.
- `skills/feature-dev/SKILL.md`: strengthen `Artifact Status` guidance so the exact artifact path is required in the user-facing response whenever the handoff artifact is created or updated.
- `skills/feature-dev/SKILL.md`: add a concise readiness gate that requires concrete files in Relevant Findings, a specific file map, a runnable validation plan, and only truly blocking open questions.
- `skills/feature-dev/references/handoff-plan-template.md`: keep the current section order, but optionally add a short compliance reminder near the header so agents do not omit status, track, or next-step fields.
- `skills/feature-dev/agents/code-architect.md`: update output guidance so headings map more directly to `Relevant Findings`, `Recommended Design`, `Implementation Slices`, `File-by-File Implementation Map`, `Validation Plan`, and `Next-Agent Kickoff`.
- `skills/feature-dev/evals/evals.json`: tighten the eval expectations so they explicitly require a file-backed artifact, exact path reporting, and bounded open questions with risk framing.

## Validation Plan

- Automated: run the feature-dev benchmark prompt for stop-before-implementation handoff behavior and confirm a passing result only when the artifact file exists at the contracted path.
- Automated: add a regression expectation that fails if the final response contains `Artifact Status` without a corresponding file-backed artifact.
- Automated: verify the final response includes the exact artifact path, not a relative description without the file location.
- Manual: simulate a deferred Standard-track feature request and confirm the agent writes `handoff-plan.md` before stopping.
- Review focus: borderline Light-track cases, false positives where a path is reported without a file, and template drift between `SKILL.md` and `handoff-plan-template.md`.

## Next-Agent Kickoff

1. Read `skills/feature-dev/SKILL.md`, `skills/feature-dev/references/handoff-plan-template.md`, `skills/feature-dev/agents/code-architect.md`, and `skills/feature-dev/evals/evals.json`.
2. Implement Slice 1 first so the policy contract becomes explicit before updating supporting files.
3. Apply Slice 2 to keep the artifact template and architect output synchronized with the stricter contract.
4. Apply Slice 3 and re-run the handoff-artifact benchmark to confirm the quality gate catches missing artifact creation or path reporting.
5. Pause for human input only if the Standard-track same-turn completion question materially changes the desired enforcement boundary.
