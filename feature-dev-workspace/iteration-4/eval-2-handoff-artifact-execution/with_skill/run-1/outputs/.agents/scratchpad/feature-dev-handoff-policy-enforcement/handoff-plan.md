# Handoff Plan: Stricter Handoff-Policy Enforcement for feature-dev

**Status**: ready for implementation
**Track**: Standard
**Origin**: feature-dev
**Feature Area**: skill orchestration and artifact policy
**Recommended Next Step**: implement directly

## Summary

This change tightens handoff-policy enforcement in the feature-dev workflow so artifact creation is deterministic and auditable when work is handed to another agent or paused before implementation. The request is to stop before implementation and provide a concrete handoff that another agent can execute. The implementation should preserve current feature-dev structure and strengthen policy requirements around when, where, and how handoff artifacts are written and reported.

## Goal / Non-Goals

- Goal: Make handoff artifact behavior explicit, mandatory in defined cases, and consistently reported in responses.
- Goal: Ensure artifact path rules are deterministic and easy to validate in evals.
- Non-goal: Rework overall feature-dev process tracks beyond what is needed for handoff-policy enforcement.
- Non-goal: Implement downstream automation scripts beyond minimal policy/eval updates in this pass.

## Relevant Findings

- skills/feature-dev/SKILL.md: already defines a Handoff Artifact section, required path, minimum content, and quality bar, but wording still relies on interpretation in edge cases.
- skills/feature-dev/references/handoff-plan-template.md: provides canonical structure for handoff-plan.md and should remain source of section shape.
- skills/feature-dev/agents/code-architect.md: already emits architecture and implementation-map material that can be mapped into handoff artifacts.
- skills/create-plan/references/plan-template.md: demonstrates deterministic scratchpad artifact conventions and metadata discipline useful for stricter enforcement language.
- skills/create-tasks/references/tasks-template.md: shows concrete execution ordering and validation detail level expected for reliable continuation by another agent.

## Technical Context and Constraints

- Language / framework: markdown-based skill instructions and agent prompts.
- Runtime or platform constraints: no runtime code path; enforcement is via instruction clarity and eval expectations.
- Existing conventions to preserve: feature-dev response shape (including Artifact Status), .agents/scratchpad path convention, and template-first artifact guidance.
- Dependencies or interfaces affected: feature-dev instruction text, handoff template references, and eval assertions that check artifact behavior.
- Validation surface: manual prompt simulation against feature-dev behavior plus benchmark eval expectations for artifact path/reporting.

## Assumptions / Open Questions

- Assumption: Existing required artifact path remains `.agents/scratchpad/<feature-name>/handoff-plan.md`.
- Assumption: Enforcement should be strongest for Standard/Deep and for any stop-before-implementation flow.
- Open question: Should Standard track require artifact creation even when implementation completes in the same turn?
- Risk if wrong: Over-enforcement could add overhead for bounded tasks; under-enforcement keeps current ambiguity.

## Recommended Design

Adopt strict, condition-based MUST rules inside skills/feature-dev/SKILL.md without changing the template location or overall workflow phases.

Design details:

1. Add explicit enforcement rules under Handoff Artifact:

- MUST create/update handoff-plan.md when stopping before implementation.
- MUST create/update handoff-plan.md when another agent is expected to continue.
- MUST include Artifact Status in user-facing response with exact artifact path.
- MUST ensure artifact has all required minimum content sections.

2. Clarify track behavior:

- Light: artifact optional only when implementation is completed in the same turn.
- Standard/Deep: artifact required whenever implementation is deferred or delegation is likely.

3. Add failure-prevention wording:

- If required context is missing, artifact must still be written with explicit assumptions and bounded open questions.
- Do not end the turn with recommendation-only prose when policy requires a file-backed artifact.

4. Keep template coupling explicit:

- Continue requiring skills/feature-dev/references/handoff-plan-template.md structure unless stronger repo standard exists.

This approach is minimal, compatible with current repo patterns, and directly testable in evals.

## Implementation Slices

### Slice 1: Tighten policy language in feature-dev skill

- Outcome: deterministic handoff-policy rules documented with clear MUST conditions.
- Files: skills/feature-dev/SKILL.md
- Dependencies: none

### Slice 2: Align template and response contract

- Outcome: template usage and Artifact Status requirements are unambiguous and traceable.
- Files: skills/feature-dev/SKILL.md, skills/feature-dev/references/handoff-plan-template.md
- Dependencies: Slice 1

### Slice 3: Protect behavior with eval coverage

- Outcome: benchmark catches missing artifact creation or missing exact path reporting.
- Files: skills/feature-dev/evals/evals.json (and/or eval prompt assets used in this benchmark harness)
- Dependencies: Slice 1 and Slice 2

## File-by-File Implementation Map

- skills/feature-dev/SKILL.md: add explicit MUST-level enforcement bullets in Handoff Artifact and tighten track-specific rules around deferred implementation.
- skills/feature-dev/SKILL.md: strengthen Summary guidance so responses must include Artifact Status path whenever artifact is required.
- skills/feature-dev/references/handoff-plan-template.md: keep section list stable; optionally add short compliance checklist header used by agents before stop.
- skills/feature-dev/evals/evals.json: add/adjust assertions for exact artifact path mention and presence of Artifact Status section in final response.
- skills/feature-dev-workspace/iteration-_/eval-_/... (if benchmark fixtures are versioned): add at least one fixture expecting physical artifact creation and explicit path echo.

## Validation Plan

- Automated: run feature-dev benchmark eval that requires stop-before-implementation handoff behavior and verify pass on artifact existence + exact path reporting.
- Automated: check eval assertions fail when artifact file is omitted or Artifact Status path is missing.
- Manual: prompt feature-dev with "stop before implementation" request and verify it writes handoff-plan.md and cites exact path in response.
- Review focus: false positives where model reports artifact path without creating file, and edge cases between Light and Standard policy branches.

## Next-Agent Kickoff

1. Read skills/feature-dev/SKILL.md and locate Handoff Artifact plus Phase 5/Phase 7 text.
2. Implement Slice 1 first, keeping wording concise and RFC-2119 clear.
3. Update template/eval assets per Slice 2 and Slice 3.
4. Re-run the target benchmark scenario and confirm artifact file is actually created and path is echoed in Artifact Status.
5. If behavior conflicts with desired track overhead, pause and request decision on Standard-track always-on artifact policy.
