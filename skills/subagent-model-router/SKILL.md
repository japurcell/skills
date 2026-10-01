---
name: subagent-model-router
description: Route subagent work to the cheapest capable model. Use before dispatching subagents, task tools, background agents, code reviewers, security reviewers, or parallel workers when a model must be selected.
---

# Subagent Model Router

Choose the lowest-cost model-and-effort configuration that satisfies the task's capability floor.

A route consists of:

- a capability tier
- a model
- a reasoning-effort setting, when applicable

Tiers describe task requirements, not price, latency, provider labels, or model families. The same model family may satisfy different tiers at different reasoning-effort settings.

## Tier guide

- **Fast**: bounded, low-risk work with clear requirements and straightforward verification. Examples include codebase exploration, mechanical transformations, and simple or repetitive tasks.
- **Standard**: work requiring substantive judgment, cross-file behavioral reasoning, interactive or agentic coding, deep debugging, or ordinary substantive code review.
- **Premium**: security-sensitive or high-stakes work, difficult long-horizon reasoning, complex work over large codebases, prior important review misses, repeated reasoning failures, or user-requested best quality.

File count, language mix, platform scope, and test count do not determine the tier by themselves.

## Decision order

1. Apply hard user, platform, and runtime constraints.
2. If the task is code review, PR review, auditing, or security review, determine its capability floor using [`reference/review-routing.md`](reference/review-routing.md).
3. Otherwise, determine the floor from the task's stakes, ambiguity, reasoning difficulty, and verification requirements.
4. Apply any escalation requirement from [`reference/escalation-policy.md`](reference/escalation-policy.md).
5. Use [`reference/model-catalog.md`](reference/model-catalog.md) to select a model-and-effort configuration that satisfies the resulting floor and is exposed by the current runtime.
6. If several configurations qualify, use [`reference/pricing.md`](reference/pricing.md) to minimize expected total cost of successful completion.
7. Select a same-tier fallback when one is available.
8. Confirm the exact runtime model ID and supported reasoning-effort setting before launching.

Capability floors override price and convenience. Availability may require a fallback, but it does not lower the floor.

## Selection guidelines

- Reuse a route only when the work class, stakes, ambiguity, affected behavior, review history, and runtime constraints are materially unchanged.
- Use the named task defaults in [`reference/model-catalog.md#task-defaults`](reference/model-catalog.md#task-defaults) as provisional starting points.
- For bounded, low-risk work, choose Fast unless a concrete reasoning, interaction, or risk factor requires a higher tier.
- Mechanical changes may remain Fast even when they affect multiple files, provided their correctness is straightforward to verify.
- Changes requiring cross-file behavioral reasoning are normally at least Standard.
- For large input context, first look for a same-tier configuration confirmed to support the required context. Escalate only if context or reasoning requirements cannot be met within the tier.
- Prefer a same-tier fallback when the first model is unavailable. Change tiers only when the task floor changes or no available same-tier configuration can satisfy it.
- If multiple supported versions of the same model fit the task, prefer the latest version unless an older version has a lower expected cost or demonstrated better task fit.
- Do not infer capability from price, recency, provider, or model name.
- When task-specific evaluation evidence is unavailable, use the named default, identify the choice as provisional, and require normal independent verification.
- Optimize expected cost to complete the task successfully, including input, output, cache writes and reads, retries, tool use, and verification—not token rates alone.

## Evidence expectations

Use the strongest available evidence in this order:

1. task-specific local evaluations
2. demonstrated success on materially similar work
3. platform or provider task guidance
4. provisional catalog defaults

When relying on provisional guidance, state the uncertainty. Do not describe a provisional default as proven.

## Output format

Return the following required fields:

- `tier`: `Fast`, `Standard`, or `Premium`
- `model`: exact runtime model ID
- `reason`: task fit, capability-floor rationale, cost assumptions, and evidence or uncertainty

Return these fields when applicable:

- `reasoning_effort`: exact runtime-supported effort setting
- `escalation_trigger`: concrete condition that caused or would cause escalation
- `fallback`: same-tier fallback model and effort, or an explanation that none is available

Example:

```yaml
tier: Standard
model: gpt-6.1-sol
reasoning_effort: default
reason: Substantive cross-file debugging requires behavioral reasoning. This is the provisional general-work default and is available in the current runtime.
escalation_trigger: Escalate if verification exposes an unresolved reasoning gap or the work becomes security-sensitive.
fallback: gpt-6-sol with the runtime-supported Standard effort setting
```

## Red flags

- Defaulting to Standard or Premium without identifying a concrete capability requirement.
- Using Fast for substantive code review, security-sensitive work, or high-stakes judgment.
- Using Premium for bounded execution when neither stakes nor reasoning difficulty requires it.
- Lowering a review or safety floor because the preferred model is unavailable.
- Escalating solely because tests fail, a dependency is missing, or the environment is misconfigured.
- Treating file count or language count as sufficient evidence for escalation.
- Selecting an older model version when a newer version has equal or lower expected cost and no demonstrated disadvantage.
- Claiming precise per-model cost control when the platform selects models automatically.
- Describing provider guidance or a catalog default as measured task-specific evidence.

## References

Load only when needed:

- [`reference/review-routing.md`](reference/review-routing.md): authoritative code-review and security-review floors.
- [`reference/escalation-policy.md`](reference/escalation-policy.md): authoritative escalation and failure-diagnosis rules.
- [`reference/model-catalog.md`](reference/model-catalog.md): model-and-effort configurations and task defaults.
- [`reference/pricing.md`](reference/pricing.md): Copilot pricing and expected-cost calculations.
- [`reference/patterns.md`](reference/patterns.md): non-authoritative examples and edge cases.

## Sources

Catalog and pricing references were verified against:

- [Supported AI models in GitHub Copilot](https://docs.github.com/en/copilot/reference/ai-models/supported-models)
- [AI model comparison](https://docs.github.com/en/copilot/reference/ai-models/model-comparison)
- [GitHub Copilot models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)

The sources were verified on **2026-09-29**. Recheck them when current availability or pricing is required because plans, runtimes, prices, and model availability can differ.

Use supported-models for availability and retirement, model-comparison for task guidance, and models-and-pricing for rates. A published price does not establish that a model is selectable.

For refreshes, fetch live sources directly. Reconcile supported models, pricing rows, context thresholds, cache charges, exclusions, and availability restrictions. If retrieval disagrees with a user's live page, bypass stale caches before claiming that an entry is absent.