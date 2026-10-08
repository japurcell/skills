# Model Catalog

Use this catalog after determining the task's capability floor.

Sources:

- [Supported AI models in GitHub Copilot](https://docs.github.com/en/copilot/reference/ai-models/supported-models)
- [AI model comparison](https://docs.github.com/en/copilot/reference/ai-models/model-comparison)
- [GitHub Copilot models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)

Source snapshot: **2026-09-29**.

Pricing or comparison entries do not establish runtime availability. Absence from this catalog does not establish retirement. Model IDs are routing shorthand until confirmed against the dispatch interface.

## Using the catalog

Tiers apply to model-and-effort configurations, not necessarily whole model families.

Each table lists a local candidate effort for routing. Model status does not establish support for that effort. A configuration is available only if the dispatch interface accepts both the exact model ID and the listed effort value. If the model does not support that effort, remove the configuration rather than substituting another effort unless that alternative is separately listed for the required tier.

Before returning a route:

1. confirm the exact model IDs and effort values accepted by the dispatch interface
2. remove unavailable or below-floor configurations
3. resolve the selection and fallback to one exact model and effort each
4. return `dispatchable: false` if the selected values cannot be confirmed

Do not replace the listed effort with `default`, `auto`, a range, or another unresolved description.

Use [`pricing.md`](pricing.md) when exact cost matters.

## Fast

| Provider | Model | Effort | Status | Best for |
| --- | --- | --- | --- | --- |
| OpenAI | `gpt-5.4-nano` | `medium` | GA; Codex VS Code extension and Copilot Pro+ only | Lightweight work; unavailable in Copilot Chat |
| OpenAI | `gpt-5-mini` | `medium` | GA | Fast coding, writing, and mechanical review |
| OpenAI | `gpt-5.6-luna` | `medium` | GA | Bounded low-risk coding; GPT-6 Luna fallback |
| OpenAI | `gpt-6-luna` | `medium` | GA | Bounded low-risk coding |
| Anthropic | `claude-haiku-4.5` | `medium` | GA | Simple or repetitive tasks |
| Google | `gemini-3.5-flash` | `medium` | GA; retires 2026-10-02 | Fast simple work |
| Microsoft | `mai-code-1.1-flash` | `medium` | GA | Lightweight code work |

Fast review is limited to mechanical or non-semantic changes with straightforward verification.

## Standard

| Provider | Model | Effort | Status | Best for |
| --- | --- | --- | --- | --- |
| OpenAI | `gpt-5.6-luna` | `max` | GA | Cost-conscious agentic coding or bounded review |
| OpenAI | `gpt-6-luna` | `max` | GA | Cost-conscious agentic coding or bounded review |
| OpenAI | `gpt-5.4-mini` | `high` | GA | Bounded substantive review |
| OpenAI | `gpt-6.1-sol` | `medium` | GA | Connected or complex coding and broader analysis |
| OpenAI | `gpt-6-sol` | `medium` | GA | Interactive and agentic coding |
| OpenAI | `gpt-5.6-terra` | `medium` | GA | Connected coding and broader analysis |
| OpenAI | `gpt-5.3-codex` | `high` | GA | Agentic coding and review |
| Anthropic | `claude-sonnet-5.5` | `high` | GA | General coding and agent tasks; fallback to `claude-sonnet-5` |
| Anthropic | `claude-sonnet-5` | `high` | GA | General coding and agent tasks; fallback for `claude-sonnet-5.5` |
| Moonshot AI | `kimi-k2.7-code` | `high` | GA; retires 2026-10-02 | Versatile code work |
| Google | `gemini-3.6-flash` | `high` | GA; retires 2026-10-02 | Versatile work; promotional pricing |
| Google | `gemini-3.7-flash` | `high` | GA | Versatile work; promotional pricing |
| Google | `gemini-3.8-flash` | `high` | GA | Versatile work; promotional pricing |
| xAI | `grok-4.5` | `high` | GA | Versatile work; long-context pricing |
| xAI | `grok-4.6` | `high` | GA | Versatile work; long-context pricing |
| xAI | `grok-4.7` | `high` | GA | Agentic coding; long-context pricing |

## Premium

| Provider | Model | Effort | Status | Best for |
| --- | --- | --- | --- | --- |
| OpenAI | `gpt-6.1-sol` | `high` | GA | Demanding code or security review |
| OpenAI | `gpt-6-sol` | `high` | GA | Demanding code or security review |
| OpenAI | `gpt-5.6-terra` | `high` | GA | Demanding connected-code analysis |
| OpenAI | `gpt-5.3-codex` | `max` | GA | Demanding agentic coding or review |
| OpenAI | `gpt-5.4` | `max` | GA | Difficult general work; long-context pricing |
| OpenAI | `gpt-5.5` | `max` | GA | Powerful reasoning; long-context pricing |
| OpenAI | `gpt-6-astra` | `max` | GA | Demanding autonomous work; long-context pricing |
| Anthropic | `claude-opus-4.7` | `max` | GA; retires 2026-10-02 | Deep reasoning and debugging |
| Anthropic | `claude-opus-4.8` | `max` | GA | Deep reasoning and debugging |
| Anthropic | `claude-opus-4.8-fast` | `max` | GA | Premium reasoning when speed justifies cost |
| Anthropic | `claude-fable-5` | `max` | GA | Long-horizon autonomous work |
| Anthropic | `claude-opus-5` | `max` | GA | Powerful reasoning |
| Anthropic | `claude-opus-5.5` | `max` | GA | Long-running agentic work |
| Anthropic | `claude-fable-5.1` | `max` | GA | Long-horizon autonomous work; low cached-input rate |
| Moonshot AI | `kimi-k3` | `max` | GA | Multi-step agentic coding over large contexts |

Do not substitute a lower effort when the listed effort is unavailable. Treat that configuration as unavailable.

## Task defaults

These are provisional starting candidates, not measured quality rankings. Prefer task-specific evidence when available.

| Default | Tier | Starting configuration | Alternatives |
| --- | --- | --- | --- |
| Bounded work | Fast | `gpt-6-luna`, `medium` | `gpt-5.6-luna`, `medium`; then `mai-code-1.1-flash`, `medium` |
| Budget review | Standard | `gpt-6-luna`, `max` | `gpt-5.6-luna`, `max`; then another Standard review configuration |
| General work | Standard | `gpt-6.1-sol`, `medium` | `gpt-6-sol`, `medium`; `gpt-5.6-terra`, `medium`; then `gpt-5.3-codex`, `high` |
| Demanding review | Premium | `gpt-6.1-sol`, `high` | `gpt-6-sol`, `high`; `gpt-6-astra`, `max`; then another validated Premium review configuration |
| Demanding autonomous work | Premium | `gpt-6-astra`, `max` | Another validated Premium autonomous-work configuration |

Use bounded work for low-risk coding and mechanical review only. Substantive review is at least Standard; review floors are defined in [`review-routing.md`](review-routing.md).

Every default and fallback must be confirmed as an exact accepted dispatch configuration before being returned.

## Defaults, evidence, and availability

Persistent configuration does not override routing.

If the user explicitly requests configured defaults:

1. resolve them to exact model and effort values
2. verify that they satisfy the capability floor
3. return `dispatchable: false` if they cannot be resolved or do not satisfy the floor

Do not infer capability from model name, provider, recency, or price. For unvalidated task classes, identify the route as provisional and require verification appropriate to the stakes.

Availability notes:

- Public-preview behavior, pricing, and availability may change.
- Effort-based tier assignments are local routing choices, not provider guarantees.
- Published pricing does not establish selectability.
- Do not select a model scheduled to retire before the subtask is expected to run.
- Recheck runtime availability on or after a listed retirement date.
- Claude Opus 4.7, Gemini 3.5 Flash, Gemini 3.6 Flash, and Kimi K2.7 Code are scheduled to retire on **2026-10-02**. Listed replacements are Claude Opus 5, Gemini 3.8 Flash, and Kimi K3.
- Claude Sonnet 4.6 has restricted legacy availability.
- Claude Sonnet 4 retired on **2026-05-01** and is not a routing candidate.
- Qwen2.5 lacks both a supported-models entry and a published Copilot rate in the cited snapshot.

## Refresh

When refreshing:

1. fetch live sources directly
2. reconcile availability, restrictions, retirement dates, and intentionally excluded models
3. do not infer availability from pricing or comparison pages alone
4. verify exact runtime IDs and effort values separately
5. bypass stale caches before claiming an entry is absent
6. update the snapshot date
