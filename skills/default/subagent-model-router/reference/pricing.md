# Pricing Reference

## Contents

- [Cost rule](#cost-rule)
- [Prices](#prices)
- [Notes](#notes)
- [Refresh](#refresh)

Source: [GitHub Copilot models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing). Source snapshot: **2026-10-08**.

Prices are USD per 1 million tokens for GitHub Copilot. They are not direct-provider API prices. Where GitHub AI Credits are used, 1 credit = $0.01 USD.

Pricing does not establish capability or availability. Compare only configurations that satisfy the capability floor and are accepted by the target runtime.

## Cost rule

Estimate:

```text
expected_cost =
    uncached_input
  + cached_input
  + cache_write
  + output
  + retries
  + verification
```

Also consider tool use and additional workers. Use a dominant token rate as a shortcut only when other factors are comparable.

Assume uncached input unless cache reuse is confirmed for the platform, model, and request shape. A higher token rate may cost less overall when it reduces retries, token volume, or verification.

| Token shape | Compare primarily |
| --- | --- |
| Large input, short output | Input and cached-input rates |
| Large output | Output rate |
| Reused context | Cache write plus confirmed cached-input savings |
| Uncertain task fit | Retries and verification |
| Input crossing a threshold | The matching long-context row |

## Prices

`default` in the `Condition` column identifies the ordinary pricing row. It is not a model or reasoning-effort dispatch value and does not authorize default-based routing.

`N/A` means not listed or not applicable.

| Provider | Model | Condition | Input | Cached input | Cache write | Output |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| OpenAI | `gpt-5.4-nano` | default | $0.20 | $0.02 | N/A | $1.25 |
| OpenAI | `gpt-5-mini` | default | $0.25 | $0.025 | N/A | $2.00 |
| OpenAI | `gpt-5.4-mini` | default | $0.75 | $0.075 | N/A | $4.50 |
| OpenAI | `gpt-5.3-codex` | default | $1.75 | $0.175 | N/A | $14.00 |
| OpenAI | `gpt-5.4` | ≤272K | $2.50 | $0.25 | N/A | $15.00 |
| OpenAI | `gpt-5.4` | >272K | $5.00 | $0.50 | N/A | $22.50 |
| OpenAI | `gpt-5.5` | ≤272K | $5.00 | $0.50 | N/A | $30.00 |
| OpenAI | `gpt-5.5` | >272K | $10.00 | $1.00 | N/A | $45.00 |
| OpenAI | `gpt-5.6-luna` | ≤200K | $0.20 | $0.02 | $0.25 | $1.20 |
| OpenAI | `gpt-5.6-luna` | >200K | $0.40 | $0.04 | $0.50 | $1.80 |
| OpenAI | `gpt-5.6-terra` | ≤272K | $2.00 | $0.20 | $2.50 | $12.00 |
| OpenAI | `gpt-5.6-terra` | >272K | $4.00 | $0.40 | $5.00 | $18.00 |
| OpenAI | `gpt-5.6-sol` | ≤272K | $4.00 | $0.40 | $5.00 | $20.00 |
| OpenAI | `gpt-5.6-sol` | >272K | $8.00 | $0.80 | $10.00 | $30.00 |
| OpenAI | `gpt-6-astra` | ≤272K | $10.00 | $1.00 | $12.50 | $50.00 |
| OpenAI | `gpt-6-astra` | >272K | $20.00 | $2.00 | $25.00 | $75.00 |
| OpenAI | `gpt-6-luna` | ≤272K | $0.10 | $0.01 | $0.125 | $0.50 |
| OpenAI | `gpt-6-luna` | >272K | $0.20 | $0.02 | $0.25 | $0.75 |
| OpenAI | `gpt-6-sol` | ≤272K | $2.00 | $0.20 | $2.50 | $10.00 |
| OpenAI | `gpt-6-sol` | >272K | $4.00 | $0.40 | $5.00 | $15.00 |
| OpenAI | `gpt-6.1-sol` | ≤272K | $2.00 | $0.10 | $2.50 | $10.00 |
| OpenAI | `gpt-6.1-sol` | >272K | $4.00 | $0.20 | $5.00 | $15.00 |
| Anthropic | `claude-haiku-4.5` | default | $1.00 | $0.10 | $1.25 | $5.00 |
| Anthropic | `claude-haiku-5.5` | ≤100K | $0.10 | $0.01 | $0.125 | $0.50 |
| Anthropic | `claude-haiku-5.5` | >100K | $0.50 | $0.05 | $0.625 | $2.50 |
| Anthropic | `claude-sonnet-4` | default | $3.00 | $0.30 | $3.75 | $15.00 |
| Anthropic | `claude-sonnet-4.6` | default | $3.00 | $0.30 | $3.75 | $15.00 |
| Anthropic | `claude-sonnet-5` | default | $2.00 | $0.20 | $2.50 | $10.00 |
| Anthropic | `claude-sonnet-5.5` | default | $2.00 | $0.10 | $2.50 | $10.00 |
| Anthropic | `claude-opus-4.8` | default | $5.00 | $0.50 | $6.25 | $25.00 |
| Anthropic | `claude-opus-4.8-fast` | default | $10.00 | $1.00 | $12.50 | $50.00 |
| Anthropic | `claude-fable-5` | default | $10.00 | $1.00 | $12.50 | $50.00 |
| Anthropic | `claude-opus-5` | default | $5.00 | $0.50 | $6.25 | $25.00 |
| Anthropic | `claude-opus-5.5` | default | $4.00 | $0.20 | $5.00 | $20.00 |
| Anthropic | `claude-fable-5.1` | default | $10.00 | $0.25 | $12.50 | $50.00 |
| Google | `gemini-3.7-flash` | promotional | $0.75 | $0.075 | N/A | $3.75 |
| Google | `gemini-3.8-flash` | promotional | $0.75 | $0.075 | N/A | $3.75 |
| Microsoft | `mai-code-1.1-flash` | default | $0.20 | $0.02 | N/A | $1.20 |
| xAI | `grok-4.5` | ≤200K | $2.00 | $0.50 | N/A | $6.00 |
| xAI | `grok-4.5` | >200K | $4.00 | $1.00 | N/A | $12.00 |
| xAI | `grok-4.6` | ≤200K | $2.00 | $0.50 | N/A | $6.00 |
| xAI | `grok-4.6` | >200K | $4.00 | $1.00 | N/A | $12.00 |
| xAI | `grok-4.7` | ≤200K | $2.00 | $0.50 | N/A | $6.00 |
| xAI | `grok-4.7` | >200K | $4.00 | $1.00 | N/A | $12.00 |
| Moonshot AI | `kimi-k3` | default | $3.00 | $0.30 | N/A | $15.00 |

## Notes

- Conditions are input-token thresholds, not necessarily context-window limits.
- Check [`model-catalog.md`](model-catalog.md) and the supported-models source before routing; this table may retain retired or restricted entries.
- Claude Sonnet 4 is retired; Claude Sonnet 4.6 has restricted legacy availability.
- GPT-5.4 Nano is limited to the Codex VS Code extension on Copilot Pro+.
- GPT-6.1 Sol matches GPT-6 Sol's input, output, and cache-write rates and has half its cached-input rate.
- Claude Sonnet 5.5 matches Sonnet 5's input, output, and cache-write rates and has half its cached-input rate.
- Claude Haiku 5.5 matches GPT-6 Luna's rates through 100K input tokens, then costs five times its own base rates. GPT-6 Luna's long-context threshold is 272K. Use each model's applicable row, including cache-write charges.
- Anthropic models and the listed GPT-5.6/GPT-6 families have published cache-write charges; earlier OpenAI models shown do not.
- Gemini 3.7 and 3.8 Flash promotional rates apply through **2026-12-31**.
- Legacy annual Copilot Pro or Pro+ plans may use [request multipliers](https://docs.github.com/en/copilot/reference/copilot-billing/request-based-billing-legacy/model-multipliers-for-annual-plans).
- If the platform selects models automatically, do not claim precise per-model cost control.
- Use the target platform's prices outside GitHub Copilot.

## Refresh

Fetch the live pricing source, reconcile all rows and thresholds, preserve cache charges and promotion dates, distinguish selectable from retired entries, verify the applicable billing model, bypass stale caches before claiming a price is absent, and update the snapshot date.
