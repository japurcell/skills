## Understanding

I’d treat this as a Standard Track request, with one Deep Track behavior added because the repository is unfamiliar and the work is product-sized: do enough discovery to ground the recommendation, ask a very small number of high-leverage questions, and stop with a concrete pre-edit plan rather than editing immediately.

## Relevant Findings

- The current [skills/feature-dev/SKILL.md](skills/feature-dev/SKILL.md) already calibrates between Light, Standard, and Deep tracks, but it does not explicitly require a repository-orientation pass for unfamiliar codebases before moving into clarifying questions or design.
- The current clarification guidance is directionally good, but still broad. It lists ambiguity categories, yet it does not cap or prioritize questions the way [skills/create-spec/SKILL.md](skills/create-spec/SKILL.md) does with a hard limit on critical clarifications.
- This repo already has stronger artifact-driven planning patterns in [skills/create-plan/SKILL.md](skills/create-plan/SKILL.md) and [skills/research/SKILL.md](skills/research/SKILL.md): they resolve unknowns, capture findings in reusable documents, and make the next phase explicit. The feature-dev skill only introduces a handoff artifact later, so pre-edit discovery can still feel loose.
- The helper prompts under [skills/feature-dev/agents/code-explorer.md](skills/feature-dev/agents/code-explorer.md) and [skills/feature-dev/agents/code-architect.md](skills/feature-dev/agents/code-architect.md) are strong on tracing and implementation detail, but weak on repo-orientation outputs that matter in unfamiliar repos: conventions, test entry points, extension seams, rollout risks, and where similar product workflows already live.
- For product-sized work, the main gap is not “more process” in general. The gap is earlier structure around unfamiliar-repo discovery, sharper question selection, and a reusable pre-edit brief that another agent could pick up without repeating discovery.

## Open Questions

1. When you say “work better for product-sized work,” is the main problem premature implementation, too many low-value questions, weak repo discovery, or weak handoff? I can tune the skill differently depending on which failure mode hurts most.
2. Do you want a hard question budget before editing, such as “ask at most 3 critical questions,” or do you want a softer cap where unfamiliar, cross-cutting work can ask a few more if each one is justified by a repo finding?
3. Should the skill stop after discovery plus recommendation for ambiguous work, or should it automatically continue into implementation once the critical questions are answered in the same turn?
4. Do you want a reusable planning artifact to be mandatory for all Standard and Deep runs, or only when another agent or a later turn is likely to continue the work?

## Recommendation

I would change the feature-dev skill in three coordinated ways before editing anything.

First, add an explicit unfamiliar-repo discovery checkpoint to the Standard and Deep tracks. Before clarifying questions, require a short “repo orientation” output that names the architecture boundaries, similar features, key files to read, test and validation commands, conventions to preserve, and the highest-risk integration seams. That keeps discovery focused on the information that actually reduces rework in unfamiliar repositories.

Second, tighten the clarification phase with a prioritized question budget. The model should only ask questions whose answers materially change scope, user-facing behavior, integration strategy, rollout constraints, or validation approach. Everything else should become stated assumptions. This repo already uses that discipline in create-spec, and feature-dev should borrow it instead of turning discovery into a broad interview.

Third, make the skill produce a lightweight pre-edit implementation brief for product-sized or ambiguous work. It does not need the full spec-to-plan-to-tasks pipeline, but it should capture: goal and non-goals, relevant findings, open questions or assumptions, recommended approach, likely files to touch, and the validation plan. That would make the skill much better at handing off work in unfamiliar repositories and would prevent repeating exploration on the next turn.

I would also tighten the helper-agent prompts so they explicitly return unfamiliar-repo details rather than only general analysis. In practice, that means updating the explorer prompt to report conventions, tests, extension points, and risks, and updating the architect prompt so it consumes the brief and recommends a pragmatic product-scale path rather than a generic implementation blueprint.

## Implementation Map

- Update [skills/feature-dev/SKILL.md](skills/feature-dev/SKILL.md) to add an unfamiliar-repo discovery step, a bounded clarification rubric, and a required pre-edit brief for Standard and Deep ambiguous work.
- Update [skills/feature-dev/agents/code-explorer.md](skills/feature-dev/agents/code-explorer.md) so its required output includes repo orientation, similar feature anchors, test commands, conventions, and risk hotspots.
- Update [skills/feature-dev/agents/code-architect.md](skills/feature-dev/agents/code-architect.md) so it can turn discovery findings into a concise implementation brief instead of only a full blueprint.
- Optionally update [skills/feature-dev/evals/evals.json](skills/feature-dev/evals/evals.json) after the skill changes land, so the evals explicitly check for unfamiliar-repo orientation, bounded questions, and a reusable pre-edit artifact.

If you confirm the preferred question budget and whether the implementation brief should be mandatory, I’d use that to draft the actual skill edits next.
