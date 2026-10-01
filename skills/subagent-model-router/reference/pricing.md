# Pricing Reference

Source: [GitHub Copilot models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing).

Verified **2026-09-29**.

All prices are USD per 1 million tokens for GitHub Copilot. These are not direct-provider API prices and do not apply automatically to other platforms.

If prices are shown in GitHub AI Credits:

> 1 credit = $0.01 USD

Pricing does not establish model availability or capability. Determine the task floor using `SKILL.md` and, for review, [`review-routing.md`](review-routing.md). Then compare only configurations that satisfy that floor and are available in the target runtime.

## Expected-cost calculation

Minimize expected total cost of successful completion, including:

- uncached input
- cached input
- cache writes
- output
- retries
- tool use
- verification
- additional workers or reviewers

A simplified estimate is:

```text
expected_cost =
    uncached_input_cost
  + cached_input_cost
  + cache_write_cost
  + output_cost
  + expected_retry_cost
  + expected_verification_cost
```

Use the dominant token cost as a shortcut only when the other factors are materially comparable.

Shared repository context across workers does not guarantee cache hits. Verify cache behavior for the platform, model, and request shape. If cache reuse is uncertain, budget uncached input.

A configuration with a somewhat higher token rate can be cheaper overall if it reduces retries, tool calls, output volume, or verification effort.

## Token-shape guidance

| Token shape | Primary comparison |
| --- | --- |
| Reads much more than it writes | Input and cached-input cost |
| Writes a large response | Output cost |
| Reuses a large context | Confirmed cached-input savings plus cache-write cost |
| Uses a model with cache-write charges | Cache-write cost and expected number of later cache hits |
| Has uncertain task fit | Retry and verification cost as well as token rates |
| Crosses a long-context threshold | The matching long-context pricing row |

## Prices

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
| Anthropic | `claude-sonnet-4` | default | $3.00 | $0.30 | $3.75 | $15.00 |
| Anthropic | `claude-sonnet-4.6` | default | $3.00 | $0.30 | $3.75 | $15.00 |
| Anthropic | `claude-sonnet-5` | default | $2.00 | $0.20 | $2.50 | $10.00 |
| Anthropic | `claude-sonnet-5.5` | default | $2.00 | $0.20 | $2.50 | $10.00 |
| Anthropic | `claude-opus-4.7` | default | $5.00 | $0.50 | $6.25 | $25.00 |
| Anthropic | `claude-opus-4.8` | default | $5.00 | $0.50 | $6.25 | $25.00 |
| Anthropic | `claude-opus-4.8-fast` | default | $10.00 | $1.00 | $12.50 | $50.00 |
| Anthropic | `claude-fable-5` | default | $10.00 | $1.00 | $12.50 | $50.00 |
| Anthropic | `claude-opus-5` | default | $5.00 | $0.50 | $6.25 | $25.00 |
| Anthropic | `claude-opus-5.5` | default | $4.00 | $0.20 | $5.00 | $20.00 |
| Anthropic | `claude-fable-5.1` | default | $10.00 | $0.25 | $12.50 | $50.00 |
| Google | `gemini-3.5-flash` | default | $1.50 | $0.15 | N/A | $9.00 |
| Google | `gemini-3.6-flash` | promotional | $0.75 | $0.075 | N/A | $3.75 |
| Google | `gemini-3.7-flash` | promotional | $0.75 | $0.075 | N/A | $3.75 |
| Google | `gemini-3.8-flash` | promotional | $0.75 | $0.075 | N/A | $3.75 |
| Microsoft | `mai-code-1.1-flash` | default | $0.20 | $0.02 | N/A | $1.20 |
| xAI | `grok-4.5` | ≤200K | $2.00 | $0.50 | N/A | $6.00 |
| xAI | `grok-4.5` | >200K | $4.00 | $1.00 | N/A | $12.00 |
| xAI | `grok-4.6` | ≤200K | $2.00 | $0.50 | N/A | $6.00 |
| xAI | `grok-4.6` | >200K | $4.00 | $1.00 | N/A | $12.00 |
| xAI | `grok-4.7` | ≤200K | $2.00 | $0.50 | N/A | $6.00 |
| xAI | `grok-4.7` | >200K | $4.00 | $1.00 | N/A | $12.00 |
| Moonshot AI | `kimi-k2.7-code` | default | $0.95 | $0.19 | N/A | $4.00 |
| Moonshot AI | `kimi-k3` | default | $3.00 | $0.30 | N/A | $15.00 |

## Notes

- Conditions represent input-token thresholds. Select the matching row before comparing costs.
- Pricing thresholds are not necessarily context-window limits. Confirm the actual context limit in the target runtime.
- This table preserves published rates for some retired or restricted models. Check [`model-catalog.md`](model-catalog.md) and the supported-models source before routing.
- Claude Sonnet 4 is retired.
- Claude Sonnet 4.6 has restricted legacy availability.
- GPT-5.4 Nano is limited to the Codex VS Code extension on Copilot Pro+.
- GPT-6.1 Sol matches GPT-6 Sol's input, output, and cache-write rates, with half the cached-input rate.
- Anthropic models, GPT-5.6 Luna, GPT-5.6 Sol, GPT-5.6 Terra, GPT-6 Astra, GPT-6 Luna, GPT-6 Sol, and GPT-6.1 Sol have published cache-write charges.
- Earlier OpenAI models in this table do not have listed cache-write charges.
- Gemini 3.6, 3.7, and 3.8 Flash promotional rates apply through **2026-12-31**; recheck afterward.
- Existing annual Copilot Pro or Pro+ subscriptions still using request-based billing have [legacy model multipliers](https://docs.github.com/en/copilot/reference/copilot-billing/request-based-billing-legacy/model-multipliers-for-annual-plans).
- The cheapest configuration within a tier varies by input/output mix, cache behavior, context threshold, retries, and verification.
- If the platform automatically selects models, do not claim precise per-model cost control.
- Copilot rates do not apply to other platforms. Use the target platform's pricing.

## Refresh procedure

When refreshing prices:

1. fetch the live pricing source directly
2. reconcile every published row
3. preserve context thresholds and cache charges
4. record promotional expiration dates
5. distinguish retired pricing entries from selectable routing candidates
6. verify the target billing model, including legacy request multipliers
7. bypass stale caches before claiming that a price is absent
8. update the verification date
