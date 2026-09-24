---
name: subagent-model-router
description: Route subagent work to the cheapest capable model. Use before launching subagents, task tools, background agents, code reviewers, security reviewers, or parallel workers when model must be selected.
---

# Subagent Model Router

Choose the cheapest capable model that satisfies the required tier.

## Tier guide

- **Fast**: bounded, low-risk work with clear requirements, codebase exploration, fast help with simple or repetitive tasks.
- **Standard**: general purpose and interactive coding, agentic tasks, deep reasoning and debugging, and meaningful code review.
- **Premium**: complex reasoning over large codebases and long-running agentic work, long-horizon autonomous coding, high-stakes, repeated failure, prior missed issue, or user-requested best quality.

## Selection Guidelines

- If this is code or security review, apply `reference/review-routing.md`.
- Use `reference/model-catalog.md` to choose a capable model in the tier, restricted to models exposed by the current runtime. Confirm its exact model ID before launching.
- If several models fit, use `reference/pricing.md` to compare Copilot costs for the token shape, including cache writes, long-context rates, retries, and verification. Optimize expected cost to complete the task successfully, not just token rates. For other platforms, use their pricing.
- If unavailable, prefer a same-tier fallback. Change tier only if needed.
- For large context, prefer a same-tier long-context model before escalating, unless reasoning difficulty also increases.

## Common defaults

Use the single [task defaults table](reference/model-catalog.md#task-defaults): bounded work, budget review, general work, demanding review, or demanding autonomous work. Examples describe task classes; that table owns model preferences.

Tiers describe capability requirements, not expense or latency. Choose the cheapest model demonstrated to meet the requirement; a higher price is not evidence of better review quality.

## Output format

Return:

- tier:
- model:
- effort, if specified:
- reason (task fit, cost assumptions, and evidence or uncertainty):
- escalation_trigger, if any:
- fallback, if any:

## References

Catalog and pricing references were verified against [Supported AI models in GitHub Copilot](https://docs.github.com/en/copilot/reference/ai-models/supported-models), [AI model comparison](https://docs.github.com/en/copilot/reference/ai-models/model-comparison), and [GitHub Copilot models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing) on **2026-09-22**. Recheck those sources when current pricing is required; plan and runtime availability can differ.

Load only when needed:

- `reference/review-routing.md`: code-review/security-review routing.
- `reference/model-catalog.md`: models by routing tier.
- `reference/pricing.md`: token-cost optimization.
- `reference/escalation-policy.md`: escalation and missed-issue rules.
- `reference/patterns.md`: examples and edge cases.
