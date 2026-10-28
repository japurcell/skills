# Model Catalog

## Contents

- [Using the catalog](#using-the-catalog)
- [Fast](#fast)
- [Standard](#standard)
- [Premium](#premium)
- [Task defaults](#task-defaults)
- [Availability](#availability)

Use this catalog after determining the task's capability floor.

Sources:

- [Supported AI models in GitHub Copilot](https://docs.github.com/en/copilot/reference/ai-models/supported-models)
- [AI model comparison](https://docs.github.com/en/copilot/reference/ai-models/model-comparison)
- [GitHub Copilot models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)

Source snapshot: **2026-10-28**. The supported-models source owns status, restrictions, and retirement dates; the comparison source informs task fit; the pricing source owns rates. Capability tiers and candidate efforts below are local, provisional routing policy.

Pricing or comparison entries do not establish runtime availability. Absence from this catalog does not establish retirement. Model IDs are routing shorthand until confirmed against the dispatch interface.

## Using the catalog

Tiers apply to model-and-effort configurations, not necessarily whole model families.

Each table lists a local candidate effort for routing. Model status does not establish support for that effort. A configuration is available only if the dispatch interface accepts both the exact model ID and the listed effort value. Remove unsupported configurations. Do not substitute another effort unless its capability at the required tier is separately established by higher-priority task evidence or an explicit catalog entry.

Apply the [dispatch contract](../SKILL.md#dispatch-contract) and compare eligible candidates using [pricing.md](pricing.md).

## Fast

| Provider | Model | Effort | Status | Best for |
| --- | --- | --- | --- | --- |
| OpenAI | `gpt-5.4-nano` | `medium` | GA; Codex VS Code extension and Copilot Pro+ only | Lightweight work; unavailable in Copilot Chat |
| OpenAI | `gpt-5.6-luna` | `medium` | GA | Bounded low-risk coding; GPT-6 Luna fallback |
| OpenAI | `gpt-6-luna` | `medium` | GA | Bounded low-risk coding |
| Anthropic | `claude-haiku-4.5` | `medium` | GA | Simple or repetitive tasks |
| Anthropic | `claude-haiku-5.5` | `medium` | GA | Simple or repetitive tasks; price increases above 100K input tokens |
| Google | `gemini-3.8-flash` | `medium` | GA | Lightweight coding questions; promotional pricing |
| Microsoft | `mai-code-1.1-flash` | `medium` | GA | Lightweight code work |

Fast review is limited to mechanical or non-semantic changes with straightforward verification.

## Standard

| Provider | Model | Effort | Status | Best for |
| --- | --- | --- | --- | --- |
| OpenAI | `gpt-5.6-luna` | `max` | GA | Cost-conscious agentic coding or bounded review |
| OpenAI | `gpt-6-luna` | `max` | GA | Cost-conscious agentic coding or bounded review |
| OpenAI | `gpt-6.1-sol` | `medium` | GA | Connected or complex coding and broader analysis |
| OpenAI | `gpt-6.1-terra` | `medium` | GA | Everyday agentic coding and terminal work |
| OpenAI | `gpt-6-sol` | `medium` | GA | Interactive and agentic coding |
| OpenAI | `gpt-5.6-terra` | `medium` | GA | Connected coding and broader analysis |
| OpenAI | `gpt-5.3-codex` | `medium` | GA | Agentic coding and review |
| Anthropic | `claude-sonnet-5.5` | `medium` | GA | General coding and agent tasks; fallback to `claude-sonnet-5` |
| Anthropic | `claude-sonnet-5` | `medium` | GA | General coding and agent tasks; fallback for `claude-sonnet-5.5` |
| Anthropic | `claude-sonnet-4.6` | `medium` | Legacy annual Copilot Pro/Pro+ only | General coding and agent tasks when legacy access is confirmed |
| Google | `gemini-4-argon` | `medium` | GA | Complex coding, agentic work, and reasoning; provisional candidate; promotional pricing |
| xAI | `grok-4.5` | `medium` | GA | Versatile work; long-context pricing |
| xAI | `grok-4.6` | `medium` | GA | Versatile work; long-context pricing |
| xAI | `grok-4.7` | `medium` | GA | Agentic coding; long-context pricing |

## Premium

| Provider | Model | Effort | Status | Best for |
| --- | --- | --- | --- | --- |
| OpenAI | `gpt-6.1-sol` | `high` | GA | Demanding code or security review |
| OpenAI | `gpt-6-sol` | `high` | GA | Demanding code or security review |
| OpenAI | `gpt-5.6-terra` | `high` | GA | Demanding connected-code analysis |
| OpenAI | `gpt-5.6-sol` | `high` | GA | Complex codebase reasoning and long-running agentic work |
| OpenAI | `gpt-5.3-codex` | `high` | GA | Demanding agentic coding or review |
| OpenAI | `gpt-6-astra` | `medium` | GA | Demanding autonomous work; long-context pricing |
| Anthropic | `claude-opus-4.8` | `medium` | GA | Deep reasoning and debugging |
| Anthropic | `claude-opus-4.8-fast` | `medium` | GA | Premium reasoning when speed justifies cost |
| Anthropic | `claude-fable-5` | `medium` | GA | Long-horizon autonomous work |
| Anthropic | `claude-opus-5` | `medium` | GA | Powerful reasoning |
| Anthropic | `claude-opus-5.5` | `medium` | GA | Long-running agentic work |
| Anthropic | `claude-fable-5.1` | `medium` | GA | Long-horizon autonomous work; low cached-input rate |
| Google | `gemini-4-argon` | `high` | GA | Complex coding, agentic work, and reasoning; provisional candidate; promotional pricing |
| Moonshot AI | `kimi-k3` | `medium` | GA | Multi-step agentic coding over large contexts |

## Task defaults

These are provisional starting candidates, not measured quality rankings. Alternatives are unordered; compare all eligible candidates using the evidence and cost rules in SKILL.md.

| Default | Tier | Starting configuration | Alternatives |
| --- | --- | --- | --- |
| Bounded work | Fast | `gpt-6-luna`, `medium` | `claude-haiku-5.5`, `medium`; `gpt-5.6-luna`, `medium`; `mai-code-1.1-flash`, `medium` |
| Budget review | Standard | `gpt-6-luna`, `max` | `gpt-5.6-luna`, `max`; another Standard review configuration |
| General work | Standard | `gpt-6.1-sol`, `medium` | `gpt-6.1-terra`, `medium`; `gpt-6-sol`, `medium`; `gemini-4-argon`, `medium`; `gpt-5.6-terra`, `medium`; `gpt-5.3-codex`, `medium` |
| Demanding review | Premium | `gpt-6.1-sol`, `high` | `gpt-6-sol`, `high`; `gemini-4-argon`, `high`; `gpt-6-astra`, `medium`; another validated Premium review configuration |
| Demanding autonomous work | Premium | `gpt-6-astra`, `medium` | Another validated Premium autonomous-work configuration |

Use bounded work for low-risk coding and mechanical review only. Substantive review is at least Standard; review floors are defined in [`review-routing.md`](review-routing.md).

## Availability

- Public-preview behavior, pricing, and availability may change.
- Claude Fable 5 and 5.1 have special retention and enablement conditions; check the [supported-models footnotes](https://docs.github.com/en/copilot/reference/ai-models/supported-models#footnotes). Fable models and Kimi K3 are excluded from enterprise default enablement; confirm administrator policy.
- Claude Sonnet 4.6 retired for most users on **2026-09-01** but remains available to individual subscribers on annual Copilot Pro and Pro+ plans. Monthly plans do not qualify.
- GPT-5 mini, GPT-5.4, GPT-5.4 mini, GPT-5.5, and Gemini 3.7 Flash retired on **2026-10-19** and are excluded from routing candidates.
- Recheck runtime availability on or after a listed retirement date.

For snapshot refreshes and historical exclusions, see [maintenance.md](maintenance.md).
