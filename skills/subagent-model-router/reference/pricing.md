# Pricing Reference

All prices are per 1 million tokens.

Use this as a routing aid, not a permanent source of truth. Check current pricing when exact cost matters.

If prices are shown in GitHub AI Credits: 1 credit = $0.01 USD.

## Cost heuristics

Prefer the lowest combined cost that still meets the task's reasoning needs.

| Token shape | Optimize for |
|---|---|
| Reads a lot, writes little | input cost |
| Writes a lot | output cost |
| Reuses large context | cached-input cost |
| Anthropic with cached context | cache write + cached input |

Do not pay premium rates for bounded execution work.

## OpenAI

| Model | Status | Category | Tier | Threshold | Input | Cached input | Output |
|---|---|---|---|---|---:|---:|---:|
| GPT-5 mini | GA | Lightweight | Default | N/A | $0.25 | $0.025 | $2.00 |
| GPT-5.3-Codex | GA | Powerful | Default | N/A | $1.75 | $0.175 | $14.00 |
| GPT-5.4 | GA | Versatile | Default | ≤272K | $2.50 | $0.25 | $15.00 |
| GPT-5.4 | GA | Versatile | Long context | >272K | $5.00 | $0.50 | $22.50 |
| GPT-5.4 mini | GA | Lightweight | Default | N/A | $0.75 | $0.075 | $4.50 |
| GPT-5.4 nano | GA | Lightweight | Default | N/A | $0.20 | $0.02 | $1.25 |
| GPT-5.5 | GA | Powerful | Default | ≤272K | $5.00 | $0.50 | $30.00 |
| GPT-5.5 | GA | Powerful | Long context | >272K | $10.00 | $1.00 | $45.00 |
| GPT-5.6 Luna | GA | Lightweight | Default | ≤200K | $1.00 | $0.10 | $6.00 |
| GPT-5.6 Luna | GA | Lightweight | Long context | >200K | $2.00 | $0.20 | $9.00 |
| GPT-5.6 Sol | GA | Powerful | Default | ≤272K | $5.00 | $0.50 | $30.00 |
| GPT-5.6 Sol | GA | Powerful | Long context | >272K | $10.00 | $1.00 | $45.00 |
| GPT-5.6 Terra | GA | Versatile | Default | ≤272K | $2.50 | $0.25 | $15.00 |
| GPT-5.6 Terra | GA | Versatile | Long context | >272K | $5.00 | $0.50 | $22.50 |

## Anthropic

| Model | Status | Category | Input | Cached input | Cache write | Output |
|---|---|---|---:|---:|---:|---:|
| Claude Haiku 4.5 | GA | Versatile | $1.00 | $0.10 | $1.25 | $5.00 |
| Claude Sonnet 4 | GA | Versatile | $3.00 | $0.30 | $3.75 | $15.00 |
| Claude Sonnet 4.5 | GA | Versatile | $3.00 | $0.30 | $3.75 | $15.00 |
| Claude Sonnet 4.6 | GA | Versatile | $3.00 | $0.30 | $3.75 | $15.00 |
| Claude Opus 4.5 | GA | Powerful | $5.00 | $0.50 | $6.25 | $25.00 |
| Claude Opus 4.6 | GA | Powerful | $5.00 | $0.50 | $6.25 | $25.00 |
| Claude Opus 4.7 | GA | Powerful | $5.00 | $0.50 | $6.25 | $25.00 |
| Claude Opus 4.8 | GA | Powerful | $5.00 | $0.50 | $6.25 | $25.00 |
| Claude Sonnet 5 | GA | Versatile | $2.00 | $0.20 | $2.50 | $10.00 |
| Claude Opus 4.8 fast mode preview | GA | Powerful | $10.00 | $1.00 | $12.50 | $50.00 |
| Claude Fable 5 | GA | Powerful | $10.00 | $1.00 | $12.50 | $50.00 |

## Google

| Model | Status | Category | Tier | Threshold | Input | Cached input | Output |
|---|---|---|---|---|---:|---:|---:|
| Gemini 2.5 Pro | GA | Powerful | Default | N/A | $1.25 | $0.125 | $10.00 |
| Gemini 3 Flash | Public preview | Lightweight | Default | N/A | $0.50 | $0.05 | $3.00 |
| Gemini 3.1 Pro | Public preview | Powerful | Default | ≤200K | $2.00 | $0.20 | $12.00 |
| Gemini 3.1 Pro | Public preview | Powerful | Long context | >200K | $4.00 | $0.40 | $18.00 |
| Gemini 3.5 Flash | GA | Lightweight | Default | N/A | $1.50 | $0.15 | $9.00 |

## Fine-tuned GitHub

| Model | Status | Category | Input | Cached input | Output |
|---|---|---|---:|---:|---:|
| Raptor mini | GA | Versatile | $0.25 | $0.025 | $2.00 |

## Microsoft

| Model | Status | Category | Input | Cached input | Output |
|---|---|---|---:|---:|---:|
| MAI-Code-1-Flash | GA | Lightweight | $0.75 | $0.075 | $4.50 |

## Moonshot AI

| Model | Status | Category | Input | Cached input | Output |
|---|---|---|---:|---:|---:|
| Kimi K2.7 Code | GA | Versatile | $0.95 | $0.19 | $4.00 |

## Practical notes

- Public preview models may change behavior, pricing, or availability more often than GA models.
- Long-context pricing may differ from base rates.
- The cheapest model within a tier can vary by token mix.
- If the platform auto-selects the model, do not pretend precise per-model cost control is available.
