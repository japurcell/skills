## Understanding

I used the feature-dev workflow on a Standard track and intentionally stopped before implementation, as requested. I prepared a concrete handoff for adding stricter handoff-policy enforcement to feature-dev and created the required file-backed handoff artifact.

## Relevant Findings

- skills/feature-dev/SKILL.md already contains a Handoff Artifact section, required path convention, minimum content, and quality bar.
- skills/feature-dev/references/handoff-plan-template.md provides the baseline structure this change should preserve.
- skills/create-plan/references/plan-template.md and skills/create-tasks/references/tasks-template.md show stronger deterministic artifact and execution conventions that can be reused for stricter enforcement language.
- skills/feature-dev/agents/code-architect.md already outputs architecture and implementation-map details compatible with the handoff artifact shape.

## Open Questions

- Should Standard track require artifact creation even when implementation is completed in the same turn?

## Recommendation

Implement stricter MUST-level enforcement in skills/feature-dev/SKILL.md for deferred/delegated work:

1. Require handoff-plan.md creation or update whenever stopping before implementation.
2. Require handoff-plan.md creation or update whenever another agent is likely to continue.
3. Require an Artifact Status section in the user-facing response with the exact artifact path.
4. Keep template coupling to skills/feature-dev/references/handoff-plan-template.md and require all minimum sections.

## Implementation Map

- skills/feature-dev/SKILL.md: tighten Handoff Artifact and track-specific enforcement wording.
- skills/feature-dev/references/handoff-plan-template.md: optional compliance checklist to reduce omissions.
- skills/feature-dev/evals/evals.json: add assertions for physical artifact creation behavior and exact path reporting.

## Artifact Status

Created: /home/adam/.agents/skills/feature-dev-workspace/iteration-4/eval-2-handoff-artifact-execution/with_skill/run-1/outputs/.agents/scratchpad/feature-dev-handoff-policy-enforcement/handoff-plan.md

## Completion Note

Wrote the required handoff artifact and benchmark output files under the requested outputs directory.
