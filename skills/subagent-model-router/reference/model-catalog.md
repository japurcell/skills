# Model Catalog

Use when `SKILL.md` is not enough to choose a model.

Routing tiers are local to this skill and may differ from provider labels. Use `reference/pricing.md` when exact cost matters.

## Fast

Use for simple, bounded, repetitive, or low-risk work. Not for normal code review.

| Provider | Model | Status | Best for |
|---|---|---|---|
| OpenAI | `gpt-5.4-nano` | GA | cheapest lightweight OpenAI work |
| OpenAI | `gpt-5-mini` | GA | fast coding/writing; tiny style-only reviews |
| OpenAI | `gpt-5.6-luna` | GA | lightweight long-context work |
| Anthropic | `claude-haiku-4.5` | GA | simple/repetitive tasks |
| Google | `gemini-3-flash` | Public preview | fast simple work |
| Google | `gemini-3.5-flash` | GA | fast simple work |
| Microsoft | `mai-code-1-flash` | GA | lightweight code work |

## Standard

Use for most coding, editing, analysis, debugging, agent work, and normal code review.

| Provider | Model | Status | Best for |
|---|---|---|---|
| OpenAI | `gpt-5.4-mini` | GA | default normal code review |
| OpenAI | `gpt-5.3-codex` | GA | subtle code correctness, cross-file contracts, false-pass tests, auth-flow review |
| OpenAI | `gpt-5.6-terra` | GA | versatile work; long-context pricing |
| Anthropic | `claude-sonnet-4` | GA | general coding/analysis |
| Anthropic | `claude-sonnet-4.5` | GA | general coding/agent tasks |
| Anthropic | `claude-sonnet-4.6` | GA | general coding/agent tasks |
| Anthropic | `claude-sonnet-5` | GA | preferred Anthropic standard model when available |
| Fine-tuned GitHub | `raptor-mini` | GA | low-cost versatile work |
| Moonshot AI | `kimi-k2.7-code` | GA | code-oriented versatile work |

## Premium

Use for complex, ambiguous, high-stakes, security-sensitive, or failure-sensitive work.

| Provider | Model | Status | Best for |
|---|---|---|---|
| OpenAI | `gpt-5.4` | GA | broad general work; long-context pricing |
| OpenAI | `gpt-5.5` | GA | powerful reasoning; long-context pricing |
| OpenAI | `gpt-5.6-sol` | GA | powerful reasoning; long-context pricing |
| Anthropic | `claude-opus-4.5` | GA | deep reasoning/debugging |
| Anthropic | `claude-opus-4.6` | GA | deep reasoning/debugging |
| Anthropic | `claude-opus-4.7` | GA | deep reasoning/debugging |
| Anthropic | `claude-opus-4.8` | GA | strongest normal Anthropic reasoning option |
| Anthropic | `claude-opus-4.8-fast-mode-preview` | GA | premium reasoning when speed justifies cost |
| Anthropic | `claude-fable-5` | GA | long-horizon autonomous coding/knowledge work |
| Google | `gemini-2.5-pro` | GA | complex code generation, debugging, research |
| Google | `gemini-3.1-pro` | Public preview | deep reasoning; long-context pricing |

## Review defaults

| Situation | Preferred model |
|---|---|
| Tiny style-only diff | `gpt-5-mini` |
| Normal code review | `gpt-5.4-mini` |
| Tests/guards, backend + frontend, or >3 files | `gpt-5.4-mini` |
| Subtle correctness, false-pass tests, cross-file contracts | `gpt-5.3-codex` |
| Auth/security-sensitive review | `gpt-5.3-codex` or stronger Premium model |
| Security review | Premium model; never cheapest |

## Notes

- Public preview models may change behavior, pricing, or availability.
- If two models are close in cost, pick the better task fit.
- Cost optimization never overrides agent-type floors.
