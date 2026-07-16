# Pricing Reference

All prices are per 1 million tokens. Use as a routing aid, not a permanent source of truth. Check current pricing when exact cost matters.

If prices are shown in GitHub AI Credits: 1 credit = $0.01 USD.

## Cost rules

1. First satisfy agent-type floor and task capability.
2. Then optimize for the dominant token cost.
3. Never choose Fast for normal code review only because it is cheaper.
4. Never pay Premium for bounded execution unless stakes require it.

| Token shape | Optimize for |
|---|---|
| Reads a lot, writes little | input cost |
| Writes a lot | output cost |
| Reuses large context | cached-input cost |
| Anthropic cached context | cache write + cached input |

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
| OpenAI | `gpt-5.6-luna` | ≤200K | $1.00 | $0.10 | — | $6.00 |
| OpenAI | `gpt-5.6-luna` | >200K | $2.00 | $0.20 | — | $9.00 |
| OpenAI | `gpt-5.6-terra` | ≤272K | $2.50 | $0.25 | — | $15.00 |
| OpenAI | `gpt-5.6-terra` | >272K | $5.00 | $0.50 | — | $22.50 |
| OpenAI | `gpt-5.6-sol` | ≤272K | $5.00 | $0.50 | — | $30.00 |
| OpenAI | `gpt-5.6-sol` | >272K | $10.00 | $1.00 | — | $45.00 |
| Anthropic | `claude-haiku-4.5` | default | $1.00 | $0.10 | $1.25 | $5.00 |
| Anthropic | `claude-sonnet-4` | default | $3.00 | $0.30 | $3.75 | $15.00 |
| Anthropic | `claude-sonnet-4.5` | default | $3.00 | $0.30 | $3.75 | $15.00 |
| Anthropic | `claude-sonnet-4.6` | default | $3.00 | $0.30 | $3.75 | $15.00 |
| Anthropic | `claude-sonnet-5` | default | $2.00 | $0.20 | $2.50 | $10.00 |
| Anthropic | `claude-opus-4.5` | default | $5.00 | $0.50 | $6.25 | $25.00 |
| Anthropic | `claude-opus-4.6` | default | $5.00 | $0.50 | $6.25 | $25.00 |
| Anthropic | `claude-opus-4.7` | default | $5.00 | $0.50 | $6.25 | $25.00 |
| Anthropic | `claude-opus-4.8` | default | $5.00 | $0.50 | $6.25 | $25.00 |
| Anthropic | `claude-opus-4.8-fast-mode-preview` | default | $10.00 | $1.00 | $12.50 | $50.00 |
| Anthropic | `claude-fable-5` | default | $10.00 | $1.00 | $12.50 | $50.00 |
| Google | `gemini-2.5-pro` | default | $1.25 | $0.125 | — | $10.00 |
| Google | `gemini-3-flash` | default | $0.50 | $0.05 | — | $3.00 |
| Google | `gemini-3.1-pro` | ≤200K | $2.00 | $0.20 | — | $12.00 |
| Google | `gemini-3.1-pro` | >200K | $4.00 | $0.40 | — | $18.00 |
| Google | `gemini-3.5-flash` | default | $1.50 | $0.15 | — | $9.00 |
| Fine-tuned GitHub | `raptor-mini` | default | $0.25 | $0.025 | — | $2.00 |
| Microsoft | `mai-code-1-flash` | default | $0.75 | $0.075 | — | $4.50 |
| Moonshot AI | `kimi-k2.7-code` | default | $0.95 | $0.19 | — | $4.00 |

## Notes

- Long-context pricing may differ from base rates.
- Cheapest model within a tier can vary by token mix.
- If platform auto-selects models, do not claim precise per-model cost control.
- Capability floors override price.
