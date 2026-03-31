Understanding
- Goal: improve `feature-dev` for product-sized work in unfamiliar repositories before editing.
- Chosen track: Standard.

Relevant Findings
- `skills/feature-dev/SKILL.md` already supports track calibration, but unfamiliar-repo + product-sized risk deserves stronger default toward Standard/Deep.
- `skills/feature-dev/SKILL.md` exploration phase asks for code-explorer agents but can more explicitly require dependency and integration mapping.
- `skills/feature-dev/references/handoff-plan-template.md` supports continuity, but risk-register style guidance could be clearer for high-uncertainty work.

Open Questions
- What failures hurt most today: missed dependencies, unclear domain assumptions, or rollout risk?
- Should unfamiliar+product-sized requests always avoid Light track unless user asks otherwise?
- Do you want explicit rollback/feature-flag planning in the design phase by default?

Recommendation
- Add a short orientation checkpoint before deep discovery (domain, key systems, known pitfalls).
- Expand exploration guidance to explicitly map integration points and dependency blast radius.
- Add a product-risk checklist to clarifying/design phases (rollout, reversibility, monitoring).
- Keep question count small and high leverage.

Implementation Map
1. Update process-selection heuristics in `skills/feature-dev/SKILL.md`.
2. Extend Phase 2 exploration guidance for integration/dependency mapping.
3. Add concise product-risk checklist in clarifying/design phases.
4. Validate on existing eval prompts in `skills/feature-dev/evals/evals.json`.
