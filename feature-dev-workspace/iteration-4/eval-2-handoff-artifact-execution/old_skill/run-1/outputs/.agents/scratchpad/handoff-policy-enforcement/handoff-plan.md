# Handoff Plan: Stricter Handoff-Policy Enforcement for feature-dev

**Status**: ready for implementation
**Track**: Standard
**Origin**: feature-dev
**Feature Area**: skills workflow policy and artifact quality gates
**Recommended Next Step**: implement directly

## Summary

This handoff prepares a targeted improvement to the feature-dev workflow so handoff behavior is enforced, not merely suggested. The goal is to ensure that when work stops before implementation or is likely to transfer across agents, the workflow must produce a concrete, file-backed handoff artifact and report explicit artifact status in the user response. The recommended implementation updates skill rules, aligns supporting templates/agent output, and adds a readiness gate for consistent handoff quality.

## Goal / Non-Goals

- Goal: Add stricter, explicit handoff-policy enforcement to feature-dev so required handoff artifacts are always produced in qualifying scenarios.
- Goal: Make handoff output implementation-ready for another agent without repeating discovery.
- Non-goal: Refactor unrelated workflow phases or redesign the full feature-dev process architecture.

## Relevant Findings

- skills/feature-dev-workspace/skill-snapshot/SKILL.md: Current snapshot workflow has no explicit Handoff Artifact contract section and no required artifact path/template guidance.
- skills/feature-dev/SKILL.md: Live feature-dev already includes a strong Handoff Artifact contract, required path, minimum content, and quality bar that can be reused as the baseline pattern.
- skills/feature-dev/references/handoff-plan-template.md: Existing reusable template structure is implementation-ready and maps directly to handoff requirements.
- skills/feature-dev/agents/code-architect.md: Architect output already contains most handoff-critical sections (findings, architecture decision, implementation map, sequence).
- skills/feature-dev/evals/evals.json: Eval #2 expects actual artifact creation and exact artifact status path in response; this should guide enforcement wording and expected behavior.

## Technical Context and Constraints

- Language / framework: Markdown-based skill instructions and agent prompt files.
- Runtime or platform constraints: Must work in Copilot/agent execution context where skill docs govern behavior; no runtime code changes required.
- Existing conventions to preserve: RFC-style mandatory language in skill docs, phased workflow structure, and repository scratchpad artifact paths.
- Dependencies or interfaces affected: feature-dev top-level skill instructions, optional alignment to code-architect output guidance, and handoff template references.
- Validation surface: Eval prompt compatibility, artifact-path correctness, and response-level Artifact Status reporting.

## Assumptions / Open Questions

- Assumption: The implementation target is the snapshot skill path for benchmarking behavior, while using live feature-dev files as reference patterns.
- Assumption: Enforcing one required handoff artifact (`handoff-plan.md`) is preferable to introducing multiple new artifact types.
- Open question: Should stricter enforcement apply to Light track when implementation is deferred, or only to Standard/Deep plus explicit handoff requests?
- Risk if wrong: Over-enforcement may add friction for quick, low-risk tasks; under-enforcement will keep handoffs inconsistent.

## Recommended Design

Adopt a strict Handoff Mode contract in feature-dev with mandatory artifact output and a pre-stop readiness gate.

Why this approach:

- It is low-risk because the repository already contains a proven pattern in `skills/feature-dev/SKILL.md` and `skills/feature-dev/references/handoff-plan-template.md`.
- It directly addresses the benchmark requirement that artifact creation must be executed, not just described.
- It balances rigor and usability by tying enforcement to concrete trigger conditions rather than making every turn heavy.

Main alternative considered:

- Reusing `plan.md`/`tasks.md` from create-plan/create-tasks for all handoffs.
- Rejected for this change because it introduces heavier process coupling and drifts from the existing feature-dev handoff artifact contract.

## Implementation Slices

### Slice 1: Add explicit handoff-policy contract in snapshot skill

- Outcome: The snapshot skill has concrete trigger rules, required artifact path, and mandatory artifact-status response behavior.
- Files: skills/feature-dev-workspace/skill-snapshot/SKILL.md
- Dependencies: None.

### Slice 2: Add/align snapshot handoff template and references

- Outcome: Snapshot skill has a local, reusable handoff template that defines required sections for implementation-ready transfer.
- Files: skills/feature-dev-workspace/skill-snapshot/references/handoff-plan-template.md (new), skills/feature-dev-workspace/skill-snapshot/SKILL.md (reference link update)
- Dependencies: Slice 1 contract text finalized.

### Slice 3: Align architect output to handoff artifact headings

- Outcome: Architecture output can be transferred directly into handoff-plan with minimal translation.
- Files: skills/feature-dev-workspace/skill-snapshot/agents/code-architect.md (if present in snapshot) or skills/feature-dev/agents/code-architect.md (if enforcement is applied in live skill path)
- Dependencies: Slice 2 template shape finalized.

### Slice 4: Add readiness gate and eval-facing response requirements

- Outcome: Skill enforces quality checks before stopping and always reports Artifact Status with exact path when artifact is created/updated.
- Files: skills/feature-dev-workspace/skill-snapshot/SKILL.md
- Dependencies: Slices 1-3 complete.

## File-by-File Implementation Map

- skills/feature-dev-workspace/skill-snapshot/SKILL.md: Add `Default Response Shape` section including required `Artifact Status`; add `Handoff Artifact` section with required path `.agents/scratchpad/<feature-name>/handoff-plan.md`, template requirement, mandatory creation conditions, minimum content, and quality bar; add explicit rule that stopping before implementation requires artifact creation.
- skills/feature-dev-workspace/skill-snapshot/references/handoff-plan-template.md: Create template mirroring proven structure (status, track, summary, goals, findings, constraints, assumptions, design, slices, file map, validation, next-agent kickoff).
- skills/feature-dev-workspace/skill-snapshot/agents/code-architect.md (or equivalent active architect prompt): Require output headings to match template so handoff docs are easy to populate.
- skills/feature-dev/evals/evals.json (optional hardening): Add/retain assertion language that requires created artifact evidence and exact artifact path in final response.

## Validation Plan

- Automated:
  - Run benchmark/eval prompt for handoff artifact execution against snapshot skill and verify output includes a physically created artifact file.
  - Check generated output folder contains: `final_response.md`, `user_notes.md`, `metrics.json`, and `outputs/.agents/scratchpad/<feature-name>/handoff-plan.md`.
- Manual:
  - Confirm handoff plan can be handed to another agent without rediscovery.
  - Confirm response explicitly includes `Artifact Status` and exact artifact path.
  - Confirm open questions are limited to materially blocking policy decisions.
- Review focus:
  - Trigger conditions are neither too broad nor too narrow.
  - Template coverage supports implementation execution.
  - Path contract consistency across skill text and benchmark artifacts.

## Next-Agent Kickoff

1. Read `skills/feature-dev-workspace/skill-snapshot/SKILL.md` and identify exact insertion points for Handoff Artifact and Artifact Status rules.
2. Create `skills/feature-dev-workspace/skill-snapshot/references/handoff-plan-template.md` using the existing feature-dev template as baseline.
3. Update architect prompt file to output template-aligned sections.
4. Re-run the eval that requires real artifact creation and verify the exact artifact path appears in final response.
5. If the Light-track enforcement scope remains unresolved, apply conservative default (enforce when implementation is deferred) and flag for follow-up decision.
