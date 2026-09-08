# Model Catalog

Use when `SKILL.md` is not enough to choose a model.

Source: [GitHub Copilot models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing). Verified **2026-09-08**. This catalog covers models listed on that pricing page; absence does not establish retirement. IDs below are routing shorthand: use the exact identifier exposed by the runtime.

Routing tiers are local to this skill and may differ from provider labels. Use `reference/pricing.md` when exact cost matters.

## Fast

Use for simple, bounded, repetitive, or low-risk work. Not for normal code review.

| Provider | Model | Status | Best for |
|---|---|---|---|
| OpenAI | `gpt-5.4-nano` | GA | lightweight work without cache-write charges |
| OpenAI | `gpt-5-mini` | GA | fast coding/writing; tiny style-only reviews |
| OpenAI | `gpt-5.6-luna` | GA | lightweight long-context work |
| Anthropic | `claude-haiku-4.5` | GA | simple/repetitive tasks |
| Google | `gemini-3.5-flash` | GA | fast simple work |
| Microsoft | `mai-code-1-flash` | GA | lightweight code work |
| Microsoft | `mai-code-1.1-flash` | GA | lower-cost lightweight code work |

## Standard

Use for most coding, editing, analysis, debugging, agent work, and normal code review.

| Provider | Model | Status | Best for |
|---|---|---|---|
| OpenAI | `gpt-5.4-mini` | GA | bounded code review |
| OpenAI | `gpt-5.3-codex` | GA | agentic coding/review with demonstrated task fit |
| OpenAI | `gpt-5.6-terra` | GA | versatile work; long-context pricing |
| Anthropic | `claude-sonnet-4` | GA | general coding/analysis |
| Anthropic | `claude-sonnet-4.6` | GA | general coding/agent tasks |
| Anthropic | `claude-sonnet-5` | GA | general coding/agent tasks |
| Moonshot AI | `kimi-k2.7-code` | GA | code-oriented versatile work |
| Google | `gemini-3.6-flash` | GA | versatile work; promotional pricing |
| Google | `gemini-3.7-flash` | GA | versatile work; promotional pricing |
| Google | `gemini-3.8-flash` | GA | versatile work; promotional pricing |
| xAI | `grok-4.5` | GA | versatile work; long-context pricing |
| xAI | `grok-4.6` | GA | versatile work; long-context pricing |

## Premium

Use for complex, ambiguous, high-stakes, security-sensitive, or failure-sensitive work.

| Provider | Model | Status | Best for |
|---|---|---|---|
| OpenAI | `gpt-5.4` | GA | broad general work; long-context pricing |
| OpenAI | `gpt-5.5` | GA | powerful reasoning; long-context pricing |
| OpenAI | `gpt-5.6-sol` | GA | powerful reasoning; long-context pricing |
| Anthropic | `claude-opus-4.7` | GA | deep reasoning/debugging |
| Anthropic | `claude-opus-4.8` | GA | deep reasoning/debugging |
| Anthropic | `claude-opus-4.8-fast-mode-preview` | GA | premium reasoning when speed justifies cost |
| Anthropic | `claude-fable-5` | GA | long-horizon autonomous coding/knowledge work |
| OpenAI | `gpt-6-astra` | GA | powerful reasoning; long-context pricing |
| Anthropic | `claude-opus-5` | GA | powerful reasoning |
| Anthropic | `claude-fable-5.1` | GA | powerful reasoning; low cached-input rate |
| Moonshot AI | `kimi-k3` | GA | powerful reasoning |

## Task defaults

These are provisional starting candidates, not measured quality rankings. They follow [GitHub's task guidance](https://docs.github.com/en/copilot/reference/ai-models/model-comparison) and the pricing snapshot. Prefer demonstrated task fit when local evaluations disagree. Restrict every choice to the current runtime's models and exact IDs.

| Default | Tier | Starting candidate | Alternatives and conditions |
|---|---|---|---|
| Bounded work / tiny style review | Fast | `gpt-5.6-luna` | `mai-code-1.1-flash` when available and proven suitable; compare cache-write and context costs. |
| Budget review | Standard | `gpt-5.4-mini` | Ordinary bounded code diffs with clear scope; use general work default for broader review. |
| General work | Standard | `gpt-5.6-terra` | Implementation, debugging, broader review; retain `gpt-5.3-codex` for demonstrated task fit. |
| Demanding review | Premium | `gpt-5.6-sol` | Subtle correctness, security, complex contracts; choose the cheapest candidate demonstrated to meet the task's requirements. |
| Demanding autonomous work / repeated Premium misses | Premium | `gpt-6-astra` | Consider `claude-fable-5.1`; justify the added cost and verification approach. |

Newer names and provider categories alone do not demonstrate security-review accuracy. For unvalidated task classes, state uncertainty and require independent verification; do not describe a provisional default as proven.

## Notes

- Public preview models may change behavior, pricing, or availability.
- If two models are close in cost, pick the better task fit.
- Cost optimization never overrides agent-type floors.
