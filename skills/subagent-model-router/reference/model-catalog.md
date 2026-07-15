# Model Catalog

Use only when `SKILL.md` is not enough.

Routing tiers are for model selection. They may differ from a provider's marketing/category label.

Tables are grouped by routing tier, not strict price order. Use `reference/pricing.md` when exact cost or token-shape cost matters.

## Fast tier

Use for simple, bounded, repetitive, or low-risk work.

| Provider | Model | Status | Best for |
|---|---|---|---|
| OpenAI | GPT-5.4 nano | GA | cheapest lightweight OpenAI work |
| OpenAI | GPT-5 mini | GA | fast coding/writing help |
| OpenAI | GPT-5.4 mini | GA | lightweight OpenAI work |
| OpenAI | GPT-5.6 Luna | GA | lightweight work; has long-context pricing |
| Anthropic | Claude Haiku 4.5 | GA | simple/repetitive tasks |
| Google | Gemini 3 Flash | Public preview | fast simple work |
| Google | Gemini 3.5 Flash | GA | fast simple work |
| Microsoft | MAI-Code-1-Flash | GA | lightweight code work |

## Standard tier

Use for most coding, editing, analysis, review, research, and agent work.

| Provider | Model | Status | Best for |
|---|---|---|---|
| OpenAI | GPT-5.4 | GA | broad general work; has long-context pricing |
| OpenAI | GPT-5.6 Terra | GA | versatile work; has long-context pricing |
| Anthropic | Claude Sonnet 4 | GA | general coding and analysis |
| Anthropic | Claude Sonnet 4.5 | GA | general coding and agent tasks |
| Anthropic | Claude Sonnet 4.6 | GA | general coding and agent tasks |
| Anthropic | Claude Sonnet 5 | GA | preferred Anthropic standard model when available |
| Fine-tuned GitHub | Raptor mini | GA | low-cost versatile work |
| Moonshot AI | Kimi K2.7 Code | GA | code-oriented versatile work |

## Premium tier

Use for complex, ambiguous, high-stakes, or failure-sensitive work.

| Provider | Model | Status | Best for |
|---|---|---|---|
| OpenAI | GPT-5.3-Codex | GA | agentic software development |
| OpenAI | GPT-5.5 | GA | powerful reasoning; has long-context pricing |
| OpenAI | GPT-5.6 Sol | GA | powerful reasoning; has long-context pricing |
| Anthropic | Claude Opus 4.5 | GA | deep reasoning/debugging |
| Anthropic | Claude Opus 4.6 | GA | deep reasoning/debugging |
| Anthropic | Claude Opus 4.7 | GA | deep reasoning/debugging |
| Anthropic | Claude Opus 4.8 | GA | strongest normal Anthropic reasoning option |
| Anthropic | Claude Opus 4.8 fast mode preview | GA | premium reasoning when speed justifies cost |
| Anthropic | Claude Fable 5 | GA | long-horizon autonomous coding and knowledge work |
| Google | Gemini 2.5 Pro | GA | complex code generation, debugging, research |
| Google | Gemini 3.1 Pro | Public preview | deep reasoning; has long-context pricing |

## Selection notes

- Prefer fast tier for bounded execution and collection work.
- Prefer standard tier for normal agent work.
- Prefer premium tier only when complexity, stakes, or failures justify it.
- Public preview models may change behavior, pricing, or availability.
- If two models are close in cost, pick the better task fit.
