# Handoff Plan: Stricter Handoff-Policy Enforcement for feature-dev

**Status**: ready for implementation
**Track**: Standard
**Origin**: feature-dev
**Feature Area**: skill workflow policy and artifact quality gates
**Recommended Next Step**: implement directly

## Summary

This handoff prepares a bounded change to the live feature-dev workflow so handoff behavior is enforced consistently when work stops before implementation or is expected to transfer to another agent. The recommended implementation keeps the current handoff artifact path and template, strengthens the policy language in the live skill, aligns supporting prompts, and tightens eval coverage so missing artifact creation or missing exact path reporting becomes an explicit failure.

## Goal / Non-Goals

- Goal: Require feature-dev to create or update `handoff-plan.md` whenever work is deferred before implementation or likely to continue with another agent.
- Goal: Require the user-facing response to include `Artifact Status` with the exact artifact path whenever the handoff artifact is required.
- Goal: Make the handoff quality bar explicit enough that another agent can continue without repeating discovery.
- Non-goal: Redesign the overall Light / Standard / Deep workflow beyond the handoff-policy surface.
- Non-goal: Introduce a new artifact type or replace `handoff-plan.md` with `plan.md` or `tasks.md`.

## Relevant Findings

- `skills/feature-dev/SKILL.md`: this is the primary implementation target because it already contains the live handoff contract, response-shape guidance, and quality bar that need stricter enforcement language rather than a parallel mechanism.
- `skills/feature-dev/references/handoff-plan-template.md`: this defines the canonical artifact structure, so enforcement should tighten around this template instead of drifting into ad hoc summaries.
- `skills/feature-dev/agents/code-architect.md`: this prompt already asks for architecture, implementation map, and phased sequencing, which can be aligned more directly with the handoff artifact to reduce translation work for follow-on agents.
- `skills/feature-dev/evals/evals.json`: this is where regression coverage already exists for handoff behavior, making it the right place to add stricter assertions around concrete artifact creation and exact path reporting.
- `skills/feature-dev-workspace/skill-snapshot/SKILL.md`: this older snapshot shows the gap clearly because it stops before implementation with no explicit file-backed handoff contract, which is useful as a contrast when tightening the live workflow.
- `skills/create-plan/references/plan-template.md`: this template shows stronger metadata discipline and scratchpad-first planning conventions that can be borrowed without turning feature-dev into a heavier planning workflow.
- `skills/create-tasks/references/tasks-template.md`: this template demonstrates the repository’s expected level of ordered execution detail and validation specificity for handoffs that another agent can execute reliably.

## Technical Context and Constraints

- Language / framework: markdown-based skill instructions, prompt files, and eval definitions.
- Runtime or platform constraints: there is no runtime code path to enforce this; behavior is driven by instruction clarity, artifact requirements, and benchmark expectations.
- Existing conventions to preserve: `.agents/scratchpad/<feature-name>/handoff-plan.md`, the current feature-dev response sections, and the existing handoff-plan template structure.
- Dependencies or interfaces affected: `skills/feature-dev/SKILL.md`, `skills/feature-dev/references/handoff-plan-template.md`, `skills/feature-dev/agents/code-architect.md`, and `skills/feature-dev/evals/evals.json`.
- Validation surface: benchmark execution for stop-before-implementation behavior, artifact existence at the contracted path, and response-level exact path reporting.

## Assumptions / Open Questions

- Assumption: The required artifact path remains `.agents/scratchpad/<feature-name>/handoff-plan.md` and should not gain alternate aliases.
- Assumption: The strictest enforcement should apply whenever implementation is deferred or another agent is likely to continue, even if the surrounding task is otherwise modest in scope.
- Open question: Should Standard-track work still require `handoff-plan.md` when implementation fully completes in the same turn?
- Risk if wrong: If enforcement is too broad, bounded work picks up unnecessary overhead; if it stays too narrow, cross-agent continuity remains inconsistent and the quality-gate benchmark can still be bypassed.

## Recommended Design

Tighten the live feature-dev skill with explicit MUST-level handoff triggers and a pre-stop readiness gate, while keeping the existing artifact path and template intact.

Why this fits this repo:

- It reuses the live handoff contract already established in `skills/feature-dev/SKILL.md` rather than inventing a second process.
- It keeps `handoff-plan.md` as the single lightweight continuity artifact, which matches the current feature-dev direction and the benchmark’s expectations.
- It borrows only the useful parts of the stronger plan/task templates: concrete metadata, ordered slices, and validation specificity.

Main trade-off:

- Stronger MUST rules improve determinism and eval reliability, but they reduce discretion for borderline Light-track cases. The recommended implementation contains that cost by making the requirement explicit only for deferred, delegated, or explicitly requested handoffs.

## Implementation Slices

### Slice 1: Tighten handoff-policy rules in the live skill

- Outcome: `skills/feature-dev/SKILL.md` clearly states when `handoff-plan.md` is mandatory and when ending the turn without it is not allowed.
- Files: `skills/feature-dev/SKILL.md`
- Dependencies: none

### Slice 2: Align supporting template and architect output

- Outcome: the handoff template and code-architect prompt line up closely enough that another agent can populate `handoff-plan.md` with minimal interpretation.
- Files: `skills/feature-dev/references/handoff-plan-template.md`, `skills/feature-dev/agents/code-architect.md`
- Dependencies: Slice 1

### Slice 3: Harden eval coverage for the quality gate

- Outcome: the benchmark fails when the artifact is missing, the path is omitted, or the response reports a path without a concrete file-backed artifact.
- Files: `skills/feature-dev/evals/evals.json`
- Dependencies: Slice 1, Slice 2

## File-by-File Implementation Map

- `skills/feature-dev/SKILL.md`: strengthen the Handoff Artifact section so creating or updating `handoff-plan.md` is mandatory when stopping before implementation, when another agent is likely to continue, and when the user explicitly asks for a handoff or reusable implementation guidance.
- `skills/feature-dev/SKILL.md`: tighten the `Artifact Status` response guidance so the exact artifact path must be present whenever the handoff artifact is created or updated.
- `skills/feature-dev/SKILL.md`: add a concise readiness gate that requires concrete files in Relevant Findings, a specific implementation map, a runnable validation plan, and only materially important open questions.
- `skills/feature-dev/references/handoff-plan-template.md`: keep the current section order, but add a brief compliance reminder if needed so status, track, and next-step fields are never left as placeholders.
- `skills/feature-dev/agents/code-architect.md`: update output guidance so headings map directly to the handoff artifact’s Findings, Recommended Design, Implementation Slices, File-by-File Implementation Map, Validation Plan, and Next-Agent Kickoff sections.
- `skills/feature-dev/evals/evals.json`: strengthen the relevant eval expectations so missing artifact files, missing exact path reporting, or unbounded open questions are explicit failures.

## Validation Plan

- Automated: run the stop-before-implementation handoff benchmark and confirm it only passes when a concrete artifact file exists at the contracted path.
- Automated: add a regression expectation that fails if the final response includes `Artifact Status` without a corresponding file-backed artifact.
- Automated: verify the final response includes the exact artifact path, not just a relative description of where the file should exist.
- Manual: simulate a deferred Standard-track feature request and confirm the workflow writes `handoff-plan.md` before stopping.
- Review focus: borderline Light-track cases, false positives where a path is reported without a file, and drift between `skills/feature-dev/SKILL.md` and `skills/feature-dev/references/handoff-plan-template.md`.

## Next-Agent Kickoff

1. Read `skills/feature-dev/SKILL.md`, `skills/feature-dev/references/handoff-plan-template.md`, `skills/feature-dev/agents/code-architect.md`, and `skills/feature-dev/evals/evals.json`.
2. Implement Slice 1 first so the policy contract becomes explicit before updating supporting files.
3. Apply Slice 2 to keep the artifact template and architect prompt synchronized with the stricter contract.
4. Apply Slice 3 and re-run the handoff-artifact benchmark to verify that missing artifact creation or missing exact path reporting now fails.
5. Pause for human input only if the Standard-track same-turn completion question materially changes the desired enforcement boundary.
