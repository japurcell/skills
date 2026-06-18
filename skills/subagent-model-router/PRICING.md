# Pricing Reference

All prices below are **per 1 million tokens**.

Pricing may include:

- input
- output
- cached input
- Anthropic cache write

If prices are shown in **GitHub AI Credits**, use:

```text
1 credit = $0.01 USD
```

Pricing changes. Treat this file as a routing aid, not a permanent source of truth. Check the current pricing source when exact cost matters.

## Cost Heuristics

Prefer the lowest combined cost that still meets the task’s reasoning needs.

Use token shape:

| Token shape | Optimize for |
| --- | --- |
| Reads a lot, writes little | Input cost |
| Writes a lot | Output cost |
| Reuses large context | Cached input cost |
| Anthropic with cached context | Cache write plus cached input |

Do not pay premium rates for bounded execution work.

When two models are close in price, prefer the one that better fits the task.

## OpenAI

| Model | Status | Input | Cached input | Output |
| --- | --- | ---: | ---: | ---: |
| GPT-4.1 | GA | $2.00 | $0.50 | $8.00 |
| GPT-5 mini | GA | $0.25 | $0.025 | $2.00 |
| GPT-5.3-Codex | GA | $1.75 | $0.175 | $14.00 |
| GPT-5.4 | GA | $2.50 | $0.25 | $15.00 |
| GPT-5.4 mini | GA | $0.75 | $0.075 | $4.50 |
| GPT-5.4 nano | GA | $0.20 | $0.02 | $1.25 |
| GPT-5.5 | GA | $5.00 | $0.50 | $30.00 |

## Anthropic

| Model | Status | Input | Cached input | Cache write | Output |
| --- | --- | ---: | ---: | ---: | ---: |
| Haiku | GA | $1.00 | $0.10 | $1.25 | $5.00 |
| Sonnet | GA | $3.00 | $0.30 | $3.75 | $15.00 |
| Opus | GA | $5.00 | $0.50 | $6.25 | $25.00 |

## Google

| Model | Status | Input | Cached input | Output |
| --- | --- | ---: | ---: | ---: |
| Gemini 3 Flash | Public preview | $0.50 | $0.05 | $3.00 |
| Gemini 3.1 Pro | Public preview | $2.00 | $0.20 | $12.00 |
| Gemini 3.5 Flash | GA | $1.50 | $0.15 | $9.00 |

## Practical Notes

- Public preview models may change behavior, pricing, or availability more often than GA models.
- Long-context pricing may differ from base rates.
- The cheapest model within a tier can vary by token mix.
- If the platform auto-selects the model, do not pretend precise per-model cost control is available.
