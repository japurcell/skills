# Fan-out evaluations

Run each [scenario](evals.json) in a fresh Codex project with the candidate and its router under `.agents/skills/`. Copy each fixture relative to `files/`, preserving directories. Ask Codex to activate the project copy of `fan-out`. For live dispatch cases, ask it to quote the worker briefs after completion so reviewers can inspect their scope and acceptance criteria.

Grade dispatch from the router results, native spawn calls, child models and first wait. Check the produced files or answer independently. For read-only work, compare the project tree before and after. The two tabletop cases exercise capacity, fallback, ownership transfer and the portable instructions themselves.

## Codex results, 2026-11-19

The original body contained 283 whitespace-delimited words. The shortest body to pass the seven scenarios contained 44. Codex CLI 0.170.0 ran the coordinator on `gpt-6.2-sol` at low effort. In the four live parallel cases, the worker sessions recorded `gpt-6-luna` and every spawn preceded the first wait. The directory and list cases used three and two workers respectively.

| Cut from the 44-word body | Observed failure |
| --- | --- |
| Remove “even unlisted” | The first directory inventory dispatched all three workers. A repeat did everything locally after inferring the routed model was unavailable. |
| Remove “local” from “Explain local fallback” | The coordinator reported Birch's missing effort control and left the chunk undispatched without assigning it to the parent. |
| Remove “inputs” | The inline-list case still passed. In the portable-specification case, Codex found no requirement to make parent-only inputs available to workers. |

## Sources for the wording

- OpenAI's Codex documentation describes separate scopes with a parent collecting results. Its SDK example launches independent tasks together and consumes their outputs in a later step. [Subagents](https://developers.openai.com/codex/subagents/) · [Parallelization example](https://github.com/openai/openai-agents-python/blob/main/examples/agent_patterns/parallelization.py)
- Anthropic's research team describes how vague assignments led to duplicate work. Its feature-development command assigns distinct areas of investigation and requests concrete file references. [Research system](https://www.anthropic.com/research/multi-agent-research-system) · [Feature development command](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/feature-dev/commands/feature-dev.md)
- Superpowers groups parallel assignments by independent problem and checks the combined changes. This repository's delegation skill supplies the wording for scope, ownership, acceptance criteria, completion evidence and exact-model dispatch. [Superpowers](https://github.com/obra/superpowers/blob/main/skills/dispatching-parallel-agents/SKILL.md) · [Delegate to subagents](../../delegate-to-subagents/SKILL.md)
