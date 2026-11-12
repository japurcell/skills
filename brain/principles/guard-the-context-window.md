# Guard the Context Window

**Principle:** The context window is finite and non-renewable within a session. Every token that enters should earn its place.

## Why

Context overflow degrades reasoning quality, causes compression artifacts, and halts progress. Unlike compute or time, context consumed within a session cannot be reclaimed.

## Pattern

- **Isolate large payloads.** Route DOM snapshots, screenshots, and verbose tool outputs to subagents. The main context gets summaries, not raw data.
- **Don't read what you won't use.** Read selectively based on relevance: use plans for the current task contract and indexed brain topics for applicable durable guidance.
- **Keep frequently-used content inline.** Skill templates used on every invocation belong in SKILL.md, not in references/. Every file read costs tokens - only split to references when content is truly conditional.
- **Place guidance by task applicability.** Before persisting a rule, distinguish what it covers from when it is needed. Repository-wide coverage does not imply every-task applicability: CLI standards cover all scripts but belong in an indexed brain topic loaded for script work. Reserve `AGENTS.md` for universally applicable instructions and shared navigation; use existing brain indexes for conditional guidance.
- **Keep durable guidance outside plans.** Plans are temporary and may be deleted. Persist reusable lessons and rules in canonical indexed brain topics when identified. Plans retain task-specific status, decisions, and evidence, and link to durable guidance instead of storing it.
- **Size phases and cap scope.** See [principles/cost-aware-delegation](cost-aware-delegation.md) for specific numbers (2-3 files, turn budgets, mechanism costs).

## Relationship to Other Principles

[principles/cost-aware-delegation](cost-aware-delegation.md) treats delegation as economics. This principle treats the context window itself as the scarce resource - it applies to both delegated and self-directed work.

See also [principles/cost-aware-delegation](cost-aware-delegation.md)
