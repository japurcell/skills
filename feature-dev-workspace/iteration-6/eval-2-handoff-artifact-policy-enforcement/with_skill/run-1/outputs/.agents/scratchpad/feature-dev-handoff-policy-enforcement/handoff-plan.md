# Handoff Plan: Stricter Handoff-Policy Enforcement for feature-dev

**Status**: ready for implementation
**Track**: Standard
**Origin**: feature-dev iteration-6 eval-2
**Recommended Next Step**: implement directly

## Goal and Non-Goals
- Goal: Enforce artifact creation for deferred/delegated feature-dev work.
- Goal: Require exact artifact path reporting in Artifact Status.
- Non-goal: Redesign the full feature-dev workflow.

## Relevant Findings
- `skills/feature-dev/SKILL.md`: primary contract to tighten for handoff requirements.
- `skills/feature-dev/references/handoff-plan-template.md`: canonical artifact structure to preserve.
- `skills/feature-dev/evals/evals.json`: benchmark surface to harden for artifact existence/path checks.

## Recommended Design
- Add explicit MUST conditions in SKILL handoff section.
- Keep contracted path `.agents/scratchpad/<feature-name>/handoff-plan.md`.
- Fail evals when response claims artifact status without concrete artifact file.

## Implementation Slices
1. Tighten policy language in `skills/feature-dev/SKILL.md`.
2. Align template expectations in `skills/feature-dev/references/handoff-plan-template.md`.
3. Harden eval assertions in `skills/feature-dev/evals/evals.json`.

## File-by-File Implementation Map
- `skills/feature-dev/SKILL.md`: strengthen mandatory handoff criteria and readiness gate.
- `skills/feature-dev/references/handoff-plan-template.md`: preserve structure, add short compliance reminder.
- `skills/feature-dev/evals/evals.json`: add explicit artifact-file/path assertions.

## Validation Plan
- Run handoff eval and verify artifact file exists at reported path.
- Verify response includes exact artifact path.
- Verify open questions remain bounded to blocking issues only.

## Next-Agent Kickoff
1. Read the three files above.
2. Implement slice 1, then 2, then 3.
3. Re-run eval-2 benchmark and confirm strict pass/fail behavior.
