---
name: subagent-model-router
description: Route subagent work to the narrowest capable agent type and cheapest capable model. Use before launching subagents, task tools, background agents, or parallel workers when agent_type or model must be selected.
---

# Subagent Model Router

Pick the cheapest model likely to complete the task well.

## Core rule

Default cheap and narrow. Escalate only for:

- harder reasoning
- context too large for the current model
- higher stakes
- failed verification
- user-requested tier
- model unavailability

Do not use premium models for bounded execution work.

## Workflow

1. Reuse an earlier route if work class, stakes, ambiguity, and model constraints are unchanged.
2. Otherwise classify the work:
   - **Fast**: simple, bounded, repetitive, low-risk.
   - **Standard**: normal coding, editing, review, debugging, analysis.
   - **Premium**: hard reasoning, broad ambiguity, high stakes, repeated lower-tier failure.
3. Pick the narrowest agent type:
   - `task`: run tests, scripts, checks, deterministic work.
   - `explore`: search, inspect, list candidate files.
   - reviewer/debugger/editor agent: when the work needs that specialty.
   - general agent: only when no narrower type fits.
4. Use `reference/model-catalog.md` to find capable models in the selected tier.
5. If cost matters or several models fit, use `reference/pricing.md` to pick the cheapest for the token shape.
6. If the model is unavailable, stay in the same tier when possible.
7. For large context, prefer a suitable same-tier long-context model before escalating tiers.

## Output format

Return:

- agent_type:
- tier:
- model:
- reason:
- fallback, if any:

## Tier guide

| Tier     | Use for                                                                                         |
| -------- | ----------------------------------------------------------------------------------------------- |
| Fast     | tests, builds, lint, search, extraction, formatting, logs, small isolated edits                 |
| Standard | multi-file debugging, normal code edits, meaningful reviews, design tradeoffs                   |
| Premium  | high-stakes work, broad architecture/security analysis, hard failures, best-available reasoning |

## Token-shape guide

| Task shape                    | Prefer low                         |
| ----------------------------- | ---------------------------------- |
| Reads a lot, writes little    | input cost                         |
| Writes a lot                  | output cost                        |
| Reuses large context          | cached-input cost                  |
| Anthropic with cached context | cache-write plus cached-input cost |

## Load references only when needed

- `reference/patterns.md`: examples and edge cases.
- `reference/model-catalog.md`: all models by routing tier.
- `reference/pricing.md`: pricing and token-cost tradeoffs.
- `reference/escalation-policy.md`: when and how to escalate.
