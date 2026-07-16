---
name: subagent-model-router
description: Route subagent work to the narrowest capable agent type and cheapest capable model. Use before launching subagents, task tools, background agents, code reviewers, security reviewers, or parallel workers when agent_type or model must be selected.
---

# Subagent Model Router

Choose the narrowest capable `agent_type`, then the cheapest capable model that satisfies the required tier.

## Core rules

- Default cheap and narrow.
- Do not use Premium for bounded execution unless stakes/security require judgment.
- Keep execution cheap; route judgment-heavy review separately.
- Do not use Fast for normal code review.
- Security review starts at Premium.
- Escalate only for a concrete trigger.

## Agent-type floors

| Agent type        | Minimum tier | Use for                                                                       |
| ----------------- | -----------: | ----------------------------------------------------------------------------- |
| `task`            |         Fast | Tests, scripts, builds, lint, formatting, deterministic edits/checks.         |
| `explore`         |         Fast | Search, inspect, enumerate, gather evidence.                                  |
| `editor`          |         Fast | Mechanical edits. Use Standard for substantive rewrites or connected changes. |
| `debugger`        |     Standard | Bugs needing reasoning, especially across files.                              |
| `code-reviewer`   |     Standard | Diff/PR review. Fast only for tiny single-file style-only diffs.              |
| `security-review` |      Premium | Auth, permissions, secrets, sensitive data, policy/security controls.         |
| general agent     |     Standard | Only when no narrower type fits.                                              |

## Tier guide

- **Fast**: bounded, deterministic, repetitive, low-risk work; tiny single-file style-only review.
- **Standard**: normal coding, editing, debugging, analysis, and meaningful code review.
- **Premium**: security-sensitive, high-stakes, ambiguous, subtle correctness, cross-file contracts, false-pass tests, repeated failure, prior missed issue, or user-requested best quality.

## Workflow

1. Reuse a prior route only if work class, stakes, ambiguity, agent type, touched areas, review history, and model constraints are unchanged.
2. Pick the narrowest `agent_type`.
3. If this is code or security review, apply `reference/review-routing.md`.
4. Pick the lowest tier that satisfies:
   - the agent-type floor
   - task complexity and stakes
   - context size
   - review history
   - user/model constraints
5. Use `reference/model-catalog.md` to choose a capable model in the tier.
6. If several models fit, use `reference/pricing.md` to choose the cheapest for the token shape.
7. If unavailable, prefer a same-tier fallback. Change tier only if needed.
8. For large context, prefer a same-tier long-context model before escalating, unless reasoning difficulty also increases.

## Common defaults

- Simple bounded work: Fast, cheapest capable Fast model.
- Normal code review: `code-reviewer` + Standard + `gpt-5.4-mini`.
- Tiny single-file style-only review: `code-reviewer` + Fast + `gpt-5-mini`.
- Subtle correctness/auth/security review: Premium, often `gpt-5.3-codex` or stronger suitable model.

## Output format

Return:

- agent_type:
- tier:
- model:
- reason:
- escalation_trigger, if any:
- fallback, if any:

## References

Load only when needed:

- `reference/review-routing.md`: code-review/security-review routing.
- `reference/model-catalog.md`: models by routing tier.
- `reference/pricing.md`: token-cost optimization.
- `reference/escalation-policy.md`: escalation and missed-issue rules.
- `reference/patterns.md`: examples and edge cases.
