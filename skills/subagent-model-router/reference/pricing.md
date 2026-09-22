# Pricing Reference

Source: [GitHub Copilot models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing). Verified **2026-09-22**. All prices are USD per 1 million tokens for GitHub Copilot. Check the source when exact cost matters; these are not direct-provider API or other-platform prices.

If prices are shown in GitHub AI Credits: 1 credit = $0.01 USD.

## Cost rules

1. First satisfy agent-type floor and task capability.
2. Then minimize expected total cost of successful completion: input, output, cache writes/reads, retries, and verification. Use dominant token cost only as a shortcut when other factors are comparable.
3. Never choose Fast for normal code review only because it is cheaper.
4. Never pay Premium for bounded execution unless stakes require it.

| Token shape | Optimize for |
|---|---|
| Reads a lot, writes little | input cost |
| Writes a lot | output cost |
| Reuses large context | confirmed cache hits plus any cache-write charges |
| Models with cache-write charges | cache write + cached input |

Shared repo context across workers does not guarantee cache hits. Verify cache behavior for the platform, model, and request shape; otherwise estimate uncached input. A slightly higher token rate can be cheaper overall if it avoids retries or reduces token volume.

## Prices

`—` means not listed or not applicable.

| Provider | Model | Condition | Input | Cached input | Cache write | Output |
|---|---|---|---:|---:|---:|---:|
| OpenAI | `gpt-5.4-nano` | default | $0.20 | $0.02 | — | $1.25 |
| OpenAI | `gpt-5-mini` | default | $0.25 | $0.025 | — | $2.00 |
| OpenAI | `gpt-5.4-mini` | default | $0.75 | $0.075 | — | $4.50 |
| OpenAI | `gpt-5.3-codex` | default | $1.75 | $0.175 | — | $14.00 |
| OpenAI | `gpt-5.4` | ≤272K | $2.50 | $0.25 | — | $15.00 |
| OpenAI | `gpt-5.4` | >272K | $5.00 | $0.50 | — | $22.50 |
| OpenAI | `gpt-5.5` | ≤272K | $5.00 | $0.50 | — | $30.00 |
| OpenAI | `gpt-5.5` | >272K | $10.00 | $1.00 | — | $45.00 |
| OpenAI | `gpt-5.6-luna` | ≤200K | $0.20 | $0.02 | $0.25 | $1.20 |
| OpenAI | `gpt-5.6-luna` | >200K | $0.40 | $0.04 | $0.50 | $1.80 |
| OpenAI | `gpt-5.6-terra` | ≤272K | $2.00 | $0.20 | $2.50 | $12.00 |
| OpenAI | `gpt-5.6-terra` | >272K | $4.00 | $0.40 | $5.00 | $18.00 |
| OpenAI | `gpt-5.6-sol` | ≤272K | $4.00 | $0.40 | $5.00 | $20.00 |
| OpenAI | `gpt-5.6-sol` | >272K | $8.00 | $0.80 | $10.00 | $30.00 |
| OpenAI | `gpt-6-astra` | ≤272K | $10.00 | $1.00 | $12.50 | $50.00 |
| OpenAI | `gpt-6-astra` | >272K | $20.00 | $2.00 | $25.00 | $75.00 |
| Anthropic | `claude-haiku-4.5` | default | $1.00 | $0.10 | $1.25 | $5.00 |
| Anthropic | `claude-sonnet-4` | default | $3.00 | $0.30 | $3.75 | $15.00 |
| Anthropic | `claude-sonnet-4.6` | default | $3.00 | $0.30 | $3.75 | $15.00 |
| Anthropic | `claude-sonnet-5` | default | $2.00 | $0.20 | $2.50 | $10.00 |
| Anthropic | `claude-opus-4.7` | default | $5.00 | $0.50 | $6.25 | $25.00 |
| Anthropic | `claude-opus-4.8` | default | $5.00 | $0.50 | $6.25 | $25.00 |
| Anthropic | `claude-opus-4.8-fast` | default | $10.00 | $1.00 | $12.50 | $50.00 |
| Anthropic | `claude-fable-5` | default | $10.00 | $1.00 | $12.50 | $50.00 |
| Anthropic | `claude-opus-5` | default | $5.00 | $0.50 | $6.25 | $25.00 |
| Anthropic | `claude-opus-5.5` | default | $4.00 | $0.20 | $5.00 | $20.00 |
| Anthropic | `claude-fable-5.1` | default | $10.00 | $0.25 | $12.50 | $50.00 |
| Google | `gemini-3.5-flash` | default | $1.50 | $0.15 | — | $9.00 |
| Google | `gemini-3.6-flash` | promotional | $0.75 | $0.075 | — | $3.75 |
| Google | `gemini-3.7-flash` | promotional | $0.75 | $0.075 | — | $3.75 |
| Google | `gemini-3.8-flash` | promotional | $0.75 | $0.075 | — | $3.75 |
| Microsoft | `mai-code-1.1-flash` | default | $0.20 | $0.02 | — | $1.20 |
| xAI | `grok-4.5` | ≤200K | $2.00 | $0.50 | — | $6.00 |
| xAI | `grok-4.5` | >200K | $4.00 | $1.00 | — | $12.00 |
| xAI | `grok-4.6` | ≤200K | $2.00 | $0.50 | — | $6.00 |
| xAI | `grok-4.6` | >200K | $4.00 | $1.00 | — | $12.00 |
| xAI | `grok-4.7` | ≤200K | $2.00 | $0.50 | — | $6.00 |
| xAI | `grok-4.7` | >200K | $4.00 | $1.00 | — | $12.00 |
| Moonshot AI | `kimi-k2.7-code` | default | $0.95 | $0.19 | — | $4.00 |
| Moonshot AI | `kimi-k3` | default | $3.00 | $0.30 | — | $15.00 |

## Notes

- Conditions are input-token thresholds; choose the matching row before comparing costs.
- GitHub lists GPT-6 Luna and GPT-6 Sol as supported but does not publish their token rates on the linked pricing page. Their Copilot cost remains unverified.
- Anthropic, GPT-5.6 Luna/Sol/Terra, and GPT-6 Astra have published cache-write charges. Earlier OpenAI models do not; GPT-6 Luna/Sol cache-write rates are unknown.
- Gemini 3.6/3.7/3.8 Flash promotional rates apply through **2026-12-31**; recheck afterward.
- Existing annual Copilot Pro/Pro+ subscriptions still using request-based billing have [legacy model multipliers](https://docs.github.com/en/copilot/reference/copilot-billing/request-based-billing-legacy/model-multipliers-for-annual-plans). Verify the applicable billing model before estimating usage.
- Cheapest model within a tier can vary by token mix.
- If platform auto-selects models, do not claim precise per-model cost control.
- Capability floors override price.
