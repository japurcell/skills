## Understanding

I would treat this as a Standard Track change. It is not a tiny wording tweak, but it also does not need a deep multi-option architecture exercise. The goal is to make `feature-dev` behave better before implementation when the repo is unfamiliar and the work is product-sized.

## Relevant Findings

- The current `feature-dev` skill has already improved over the older snapshot in this repo: it now calibrates Light/Standard/Deep tracks, avoids mandatory approval gates, and includes a handoff artifact.
- The main gap is in unfamiliar-repo startup behavior. Phase 2 says to explore the codebase and read files returned by agents, but it does not explicitly require a repo-orientation pass that maps entry points, similar features, integration seams, validation paths, and local constraints before questions are asked.
- Phase 3 is directionally right, but still underspecified for product-sized work. It says to ask only material questions, yet it does not cap or prioritize them. In this repo, `create-spec` handles ambiguity more cleanly: make informed defaults, limit clarifications to the highest-impact unknowns, and prioritize by impact.
- This repo already has adjacent skills for heavier planning: `create-spec`, `create-plan`, and `research`. That means `feature-dev` should probably get better at discovery and targeted clarification rather than turning into a second planning framework.
- The supporting agent prompts under `skills/feature-dev/agents/` are already strong at tracing code and proposing architectures. The weak point is the orchestration in `skills/feature-dev/SKILL.md`, not the agent files.

## Open Questions

1. Do you want `feature-dev` to stay primarily conversational, or should Standard/Deep runs produce a required pre-edit artifact such as a short discovery brief or handoff plan?
2. When product-sized work is still somewhat ambiguous after exploration, should the skill stop after questions and recommendation, or proceed on explicit assumptions when the remaining gaps are non-blocking?
3. Should `feature-dev` escalate into `create-spec` / `create-plan` for larger work, or should it keep all discovery and planning inline in one response?
4. Do you want a hard cap on clarifying questions? My recommendation is `max 3 critical questions`, then document assumptions for the rest.
5. Is the target mostly application/product repos, or should this also optimize for unfamiliar internal tooling repos like this skills repository?

## Recommendation

I would keep the first change set focused on `skills/feature-dev/SKILL.md`.

What I would change there:

- Add an explicit unfamiliar-repo discovery step for Standard and Deep tracks. Before clarifying questions, require the agent to map entry points, identify 1-2 similar features or adjacent workflows, inspect validation/build/test paths, and list likely file targets plus repo-specific risks.
- Tighten Phase 3 using the pattern already present in `create-spec`: ask only high-impact questions, cap them, group them by scope/integration/validation, and state assumptions for everything else.
- Make the pre-edit response shape stronger for Standard and Deep work. Before touching code, require: findings, open questions, recommendation, implementation map, and validation plan.
- Add an escalation rule instead of overloading this skill. If discovery still leaves major product ambiguity, route into `create-spec` or `create-plan` rather than forcing `feature-dev` to invent a full planning workflow.

Why this helps in unfamiliar repos: the common failure mode is not lack of architecture options; it is missing repo constraints too early. A stronger orientation pass plus capped, prioritized questions should produce better recommendations and less rework.

## Implementation Map

If we decide to edit the repo next, I would start here:

- `skills/feature-dev/SKILL.md`
  - Strengthen the description and process-selection language around product-sized work in unfamiliar repos.
  - Add a repo-orientation checklist in Phase 2.
  - Revise Phase 3 to cap and prioritize clarifying questions.
  - Require a pre-edit discovery brief for Standard/Deep work.
  - Add an escalation note pointing to `create-spec`, `create-plan`, and `research` when ambiguity remains high.

Optional follow-up after that:

- `skills/feature-dev/evals/evals.json`
  - Add coverage for unfamiliar-repo orientation and capped clarification behavior so the change is protected by evals.
