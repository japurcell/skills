## Notes for Human Review

- The strongest repo-native pattern to borrow is from `skills/create-spec/SKILL.md`: limit clarifications, prioritize only the highest-impact unknowns, and prefer explicit assumptions over broad question lists.
- There is a product decision hiding inside this skill change: whether `feature-dev` should remain a lightweight conversational orchestrator or become the front door to artifact-heavy planning via `create-spec` and `create-plan`.
- A hard cap of 3 clarifying questions is probably right for this repo because `create-spec` already uses that pattern, but it may feel too strict for very large features unless the skill also tells the agent to surface assumptions clearly.
- I do not think the first pass needs edits to `skills/feature-dev/agents/code-explorer.md`, `code-architect.md`, or `code-reviewer.md`. The gap appears to be in the parent skill instructions rather than the specialized agent prompts.
- If this change is implemented later, adding eval coverage is important; otherwise the skill may regress back toward generic exploration or over-questioning.
