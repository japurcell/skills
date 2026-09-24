# Model Catalog

Use when `SKILL.md` is not enough to choose a model.

Sources: [Supported AI models in GitHub Copilot](https://docs.github.com/en/copilot/reference/ai-models/supported-models), [AI model comparison](https://docs.github.com/en/copilot/reference/ai-models/model-comparison), and [GitHub Copilot models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing). Verified **2026-09-22**. This catalog covers routable models listed on those pages; absence does not establish retirement. IDs below are routing shorthand: use the exact identifier exposed by the runtime.

Routing tiers are local to this skill and may differ from provider labels. Use `reference/pricing.md` when exact cost matters.

## Fast

Use for bounded, low-risk work with clear requirements, codebase exploration, fast help with simple or repetitive tasks, and small file reviews. Not for normal code review.

| Provider | Model | Status | Best for |
| --- | --- | --- | --- |
| OpenAI | `gpt-5.4-nano` | GA | lightweight work without cache-write charges |
| OpenAI | `gpt-5-mini` | GA | fast coding/writing; tiny style-only reviews |
| OpenAI | `gpt-6-luna` with `medium` effort | GA | bounded, low-risk coding with clear requirements; verify output; fallback to `gpt-5.6-luna` when not available |
| Anthropic | `claude-haiku-4.5` | GA | simple/repetitive tasks |
| Google | `gemini-3.5-flash` | GA; retires 2026-10-02 | fast simple work |
| Microsoft | `mai-code-1.1-flash` | GA | lower-cost lightweight code work |

## Standard

Use for general purpose and interactive coding, agentic tasks, substantive rewrites, deep reasoning and debugging, and meaningful code review.

| Provider | Model | Status | Best for |
| --- | --- | --- | --- |
| OpenAI | `gpt-6-luna` with `max` effort | GA | agentic coding/review with demonstrated task fit; fallback to `gpt-5.6-luna` with `max` effort when not available |
| OpenAI | `gpt-5.4-mini` | GA | bounded code review |
| OpenAI | `gpt-6-sol` | GA | connected coding and broader analysis; long-context pricing |
| OpenAI | `gpt-5.6-terra` | GA | connected coding and broader analysis; long-context pricing |
| OpenAI | `gpt-5.3-codex` | GA | agentic coding/review with demonstrated task fit |
| Anthropic | `claude-sonnet-4.6` | annual Pro/Pro+ only | general coding/agent tasks |
| Anthropic | `claude-sonnet-5` | GA | general coding/agent tasks |
| Moonshot AI | `kimi-k2.7-code` | GA; retires 2026-10-02 | code-oriented versatile work |
| Google | `gemini-3.6-flash` | GA; retires 2026-10-02 | versatile work; promotional pricing |
| Google | `gemini-3.7-flash` | GA | versatile work; promotional pricing |
| Google | `gemini-3.8-flash` | GA | versatile work; promotional pricing |
| xAI | `grok-4.5` | GA | versatile work; long-context pricing |
| xAI | `grok-4.6` | GA | versatile work; long-context pricing |
| xAI | `grok-4.7` | GA | agentic coding; long-context pricing |

## Premium

Use for complex reasoning over large codebases and long-running agentic work, long-horizon autonomous coding, high-stakes, repeated failure, prior missed issue, or user-requested best quality

| Provider | Model | Status | Best for |
| --- | --- | --- | --- |
| OpenAI | `gpt-5.4` | GA | broad general work; long-context pricing |
| OpenAI | `gpt-5.5` | GA | powerful reasoning; long-context pricing |
| Anthropic | `claude-opus-4.7` | GA; retires 2026-10-02 | deep reasoning/debugging |
| Anthropic | `claude-opus-4.8` | GA | deep reasoning/debugging |
| Anthropic | `claude-opus-4.8-fast` | GA | premium reasoning when speed justifies cost |
| Anthropic | `claude-fable-5` | GA | long-horizon autonomous coding/knowledge work |
| OpenAI | `gpt-6-astra` | GA | powerful reasoning; long-context pricing |
| Anthropic | `claude-opus-5` | GA | powerful reasoning |
| Anthropic | `claude-opus-5.5` | GA | powerful reasoning |
| Anthropic | `claude-fable-5.1` | GA | powerful reasoning; low cached-input rate |
| Moonshot AI | `kimi-k3` | GA | powerful reasoning |

## Task defaults

These are provisional starting candidates, not measured quality rankings. They follow [GitHub's task guidance](https://docs.github.com/en/copilot/reference/ai-models/model-comparison) and the pricing snapshot. Prefer demonstrated task fit when local evaluations disagree. Restrict every choice to the current runtime's models and exact IDs.

| Default | Tier | Starting candidate | Alternatives and conditions |
| --- | --- | --- | --- |
| Bounded work / small file review | Fast | `gpt-6-luna` | Includes low-risk coding changes with clear requirements. If GPT-6 Luna is unavailable, use `gpt-5.6-luna` as the first fallback; use `mai-code-1.1-flash` if neither Luna model is available. |
| Budget review | Standard | `gpt-6-luna` with `max` effort | Ordinary bounded code diffs with clear scope; use general work default for broader review. |
| General work | Standard | `gpt-6-sol` | Interactive and agentic coding, substantive rewrites, debugging, and broader review. Route small self-contained coding changes through the bounded-work default; retain `gpt-5.6-terra`, then `gpt-5.3-codex` for demonstrated task fit. |
| Demanding review | Premium | `gpt-6-sol` with `high` or greater effort | High stakes, repeated failures/misses; retain `gpt-5.6-terra`, then `gpt-5.3-codex` for demonstrated task fit. |
| Demanding autonomous work / repeated Premium misses | Premium | `gpt-6-astra` | justify the added cost and verification approach. |

Newer names and provider categories alone do not demonstrate security-review accuracy. For unvalidated task classes, state uncertainty and require independent verification; do not describe a provisional default as proven.

## Notes

- Public preview models may change behavior, pricing, or availability.
- GitHub publishes GPT-6 Luna and GPT-6 Sol token rates. The official model comparison describes Luna for fast/simple tasks and Sol for interactive/agentic coding. Verify results from the bounded-work Luna default before expanding its scope further.
- GitHub schedules Claude Opus 4.7, Gemini 3.5 Flash, Gemini 3.6 Flash, and Kimi K2.7 Code for retirement on **2026-10-02**. Prefer listed replacements after retirement: Claude Opus 5, Gemini 3.8 Flash, and Kimi K3.
- Claude Sonnet 4.6 is available only to individual annual Pro/Pro+ subscribers after its September 1, 2026 retirement; confirm runtime availability before routing.
- If two models are close in cost, pick the better task fit.
