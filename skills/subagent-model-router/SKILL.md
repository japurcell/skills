---
name: subagent-model-router
description: Route subagent work to the cheapest capable model. Use before dispatching subagents, task tools, background agents, code reviewers, security reviewers, or parallel workers when a model must be selected.
---

# Subagent Model Router

Choose the lowest-cost dispatchable model-and-effort configuration that satisfies the task's capability floor.

A dispatchable route consists of:

- a capability tier
- an exact model identifier accepted by the current dispatch interface
- an exact reasoning-effort value accepted by the current dispatch interface

Do not return an implicit, inherited, conditional, or unresolved model or effort value as dispatchable.

Values or phrases such as the following are not dispatchable unless the dispatch interface accepts that exact literal value and the user explicitly requested it:

- `runtime-selected`
- `runtime default`
- `default`
- `auto`
- “runtime-supported effort”
- “high or greater”
- “strongest available”
- “if applicable”
- an unexpanded placeholder

## Selection precedence

Apply selection rules in this order:

1. Explicit model or reasoning-effort constraints stated by the user for the current request.
2. The capability and cost rules in this skill.
3. Configured, inherited, or runtime defaults only when the user explicitly requests their use in the current request.

Persistent user configuration is a fallback default, not an explicit current-request constraint. It does not take precedence over the router.

When this router is invoked as part of a delegation workflow, its selected model and reasoning effort are intended to be explicitly applied to the dispatch. No separate authorization to override configured defaults is required.

If an explicit current-request user constraint prevents the capability floor from being met, return `dispatchable: false` and explain the conflict. Do not silently ignore the constraint or lower the floor.

## Tier guide

- **Fast**: bounded, low-risk work with clear requirements and straightforward verification. Examples include codebase exploration, mechanical transformations, and simple or repetitive tasks.
- **Standard**: work requiring substantive judgment, cross-file behavioral reasoning, interactive or agentic coding, deep debugging, or ordinary substantive code review.
- **Premium**: security-sensitive or high-stakes work, difficult long-horizon reasoning, complex work over large codebases, prior important review misses, repeated reasoning failures, or user-requested best quality.

File count, language mix, platform scope, and test count do not determine the tier by themselves.

Tiers describe task capability requirements, not price, latency, provider labels, or model families.

The same model family may qualify for different tiers at different reasoning-effort settings. The selected model and effort together form the routed configuration.

## Required routing inputs

Before returning a dispatchable route, determine:

- task objective
- work class
- stakes
- security sensitivity
- ambiguity
- reasoning difficulty
- expected context size
- review history
- verification approach
- explicit current-request user constraints
- models accepted by the current dispatch interface
- reasoning-effort values accepted by the current dispatch interface

If the current runtime's accepted model or reasoning-effort values cannot be determined, return `dispatchable: false`.

Do not claim that a model or effort is selectable based only on a catalog entry, pricing entry, provider label, or configured default.

## Decision order

1. Apply explicit current-request user constraints.
2. If the task is code review, PR review, auditing, or security review, determine its capability floor using [`reference/review-routing.md`](reference/review-routing.md).
3. Otherwise, determine the floor from stakes, security sensitivity, ambiguity, reasoning difficulty, context requirements, and verification requirements.
4. Apply any escalation requirement from [`reference/escalation-policy.md`](reference/escalation-policy.md).
5. Use [`reference/model-catalog.md`](reference/model-catalog.md) to identify eligible model-and-effort configurations for the resulting tier.
6. Restrict candidates to exact models and reasoning-effort values accepted by the current dispatch interface.
7. If several exact configurations qualify, use [`reference/pricing.md`](reference/pricing.md) to minimize expected total cost of successful completion.
8. Resolve the selected configuration to one exact model and one exact reasoning-effort value.
9. Resolve a same-tier fallback to one exact model and one exact reasoning-effort value when one is available.
10. If either required selected value cannot be resolved, return `dispatchable: false`.

Capability floors override price, convenience, configured defaults, and runtime defaults.

Availability may require a fallback, but it does not lower the capability floor.

## Selection guidelines

- Reuse a route only when the work class, stakes, security sensitivity, ambiguity, affected behavior, review history, context requirements, verification requirements, current-request constraints, and runtime capabilities are materially unchanged.
- Use the named task defaults in [`reference/model-catalog.md#task-defaults`](reference/model-catalog.md#task-defaults) as provisional starting points.
- Resolve every catalog effort range to one exact dispatch value before returning the route.
- For bounded, low-risk work, choose Fast unless a concrete reasoning, interaction, security, or risk factor requires a higher tier.
- Mechanical changes may remain Fast even when they affect multiple files, provided their correctness is straightforward to verify.
- Changes requiring cross-file behavioral reasoning are normally at least Standard.
- For large context, first look for a same-tier configuration confirmed by the runtime to support the required context.
- Escalate only if context or reasoning requirements cannot be met within the current tier.
- Prefer a same-tier fallback when the first configuration is unavailable.
- Change tiers only when the task floor changes or no available same-tier configuration can satisfy it.
- If multiple supported versions of the same model fit the task, prefer the latest version unless an older version has lower expected cost or demonstrated better task fit.
- Do not infer capability from price, recency, provider, or model name.
- When task-specific evaluation evidence is unavailable, use the named default, identify the choice as provisional, and require appropriate verification.
- Optimize expected cost to complete the task successfully, including input, output, cache writes and reads, retries, tool use, and verification—not token rates alone.

## Configured defaults

Configured, inherited, and runtime defaults may be considered only when the user explicitly requests their use in the current request.

Otherwise:

- do not preserve them
- do not give them precedence
- do not return them instead of a concrete route
- do not omit the model or effort so the runtime can apply them
- do not describe overriding them as requiring separate permission

The router's purpose is to select the dispatch configuration. A route that leaves selection to defaults has not completed that purpose.

## Review routing

For code review, PR review, auditing, or security review, apply [`reference/review-routing.md`](reference/review-routing.md).

Review floors are:

- Fast only for mechanical or non-semantic changes with straightforward verification
- Standard for ordinary substantive review
- Premium for security-sensitive, high-stakes, prior-important-miss, or otherwise demanding review

Do not lower a review floor because the preferred configuration is unavailable or expensive.

## Availability and fallback

When a selected model or effort is unavailable:

1. Preserve the capability floor.
2. Select another available configuration in the same tier.
3. Resolve it to an exact model and exact reasoning-effort value.
4. Prefer the lowest expected-cost configuration with adequate task fit.
5. Report that availability caused the fallback.

If no exact same-tier configuration is available:

- return `dispatchable: false`, or
- raise the tier only when a higher-tier configuration is available and the user permits the additional cost

Never silently route below the capability floor.

A fallback containing an effort range or unresolved value is not a dispatchable fallback.

## Evidence expectations

Use the strongest available evidence in this order:

1. task-specific local evaluations
2. demonstrated success on materially similar work
3. platform or provider task guidance
4. provisional catalog defaults

When relying on provisional guidance:

- state the uncertainty
- do not describe the choice as proven
- require verification appropriate to the task's stakes

## Output format

Always return these fields:

- `dispatchable`: `true` or `false`
- `tier`: `Fast`, `Standard`, or `Premium`
- `model`: exact dispatch-interface model value, or `unresolved`
- `reasoning_effort`: exact dispatch-interface effort value, or `unresolved`
- `reason`: task fit, capability-floor rationale, cost assumptions, and evidence or uncertainty
- `escalation_trigger`: concrete trigger or `none`
- `fallback`: exact same-tier model and effort, or `none`

For a dispatchable route:

```yaml
dispatchable: true
tier: Standard
model: gpt-6.1-sol
reasoning_effort: high
reason: Substantive cross-file debugging requires behavioral reasoning. This configuration is available in the current runtime and is the provisional general-work choice.
escalation_trigger: Escalate if verification exposes an unresolved reasoning gap or the task becomes security-sensitive.
fallback:
  model: gpt-6-sol
  reasoning_effort: high
```

For a route that cannot be resolved:

```yaml
dispatchable: false
tier: Standard
model: unresolved
reasoning_effort: unresolved
reason: The task requires Standard capability, but the current dispatch interface's exact supported model or reasoning-effort values could not be confirmed.
escalation_trigger: none
fallback: none
```

When an explicit current-request constraint prevents the floor from being met:

```yaml
dispatchable: false
tier: Premium
model: unresolved
reasoning_effort: unresolved
reason: The user required a configuration that does not satisfy the Premium capability floor for this security-sensitive review.
escalation_trigger: none
fallback: none
```

A route with `dispatchable: false` must not be used to launch a subagent.

Do not return:

- `reasoning_effort: default`
- `reasoning_effort: runtime default`
- `reasoning_effort: auto`
- `reasoning_effort: high or greater`
- `reasoning_effort: runtime-supported`
- `model: runtime-selected`
- a family name when the dispatch interface requires a versioned ID

An exception applies only when one of those terms is an exact accepted dispatch value and the user explicitly requested it.

## Red flags

- Returning a route without an exact model and exact reasoning effort.
- Treating persistent configuration as an instruction that overrides routing.
- Claiming that separate authorization is needed to override configured defaults.
- Omitting dispatch fields to preserve runtime selection.
- Defaulting to Standard or Premium without a concrete capability requirement.
- Using Fast for substantive code review, security-sensitive work, or high-stakes judgment.
- Using Premium for bounded execution when neither stakes nor reasoning difficulty requires it.
- Lowering a review or safety floor because the preferred configuration is unavailable.
- Escalating solely because tests fail, a dependency is missing, or the environment is misconfigured.
- Treating file count or language count as sufficient evidence for escalation.
- Selecting an older model version when a newer version has equal or lower expected cost and no demonstrated disadvantage.
- Claiming precise per-model cost control when the platform selects models automatically.
- Describing provider guidance or a catalog default as measured task-specific evidence.
- Returning catalog range wording instead of an exact dispatch value.

## References

Load only when needed:

- [`reference/review-routing.md`](reference/review-routing.md): authoritative code-review and security-review floors.
- [`reference/escalation-policy.md`](reference/escalation-policy.md): authoritative escalation and failure-diagnosis rules.
- [`reference/model-catalog.md`](reference/model-catalog.md): eligible model-and-effort configurations and task defaults.
- [`reference/pricing.md`](reference/pricing.md): Copilot pricing and expected-cost calculations.
- [`reference/patterns.md`](reference/patterns.md): non-authoritative examples and edge cases.

## Sources

Catalog and pricing references were verified against:

- [Supported AI models in GitHub Copilot](https://docs.github.com/en/copilot/reference/ai-models/supported-models)
- [AI model comparison](https://docs.github.com/en/copilot/reference/ai-models/model-comparison)
- [GitHub Copilot models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)

The sources were verified on **2026-09-29**.

Recheck them when current availability or pricing is required because plans, runtimes, prices, and model availability can differ.

Use:

- supported-models for availability and retirement
- model-comparison for task guidance
- models-and-pricing for rates
- the current dispatch interface for exact selectable model IDs and effort values

A published price does not establish that a model is selectable.

For refreshes, fetch live sources directly. Reconcile supported models, pricing rows, context thresholds, cache charges, exclusions, and availability restrictions. If retrieval disagrees with a user's live page, bypass stale caches before claiming that an entry is absent.
