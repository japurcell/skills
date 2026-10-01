---
name: subagent-model-router
description: Route subagent work to the cheapest capable model. Use before dispatching subagents, task tools, background agents, code reviewers, security reviewers, or parallel workers when a model must be selected.
---

# Subagent Model Router

Choose the lowest-cost dispatchable model-and-effort configuration that satisfies the task's capability floor.

## Dispatchable routes

A dispatchable route contains:

- one capability tier
- one exact model ID accepted by the dispatch interface
- one exact reasoning-effort value accepted by the dispatch interface

Do not return an implicit, inherited, conditional, ranged, or unresolved value as dispatchable.

The following are not dispatchable routing values:

- `default`
- `auto`
- `runtime-selected`
- `runtime default`
- “runtime-supported”
- “high or greater”
- “strongest available”
- “if applicable”
- an unexpanded placeholder

If configured defaults are explicitly requested, resolve them to their concrete model and effort values. If exact accepted values cannot be confirmed, return `dispatchable: false`.

## Selection precedence

Apply selection rules in this order:

1. Explicit constraints in the current user request, including an explicit request to use configured defaults.
2. The capability and cost rules in this skill.
3. No implicit, inherited, configured, or runtime default.

Persistent configuration is a fallback default, not a current-request constraint. It does not override this router.

When used for delegation, the selected model and effort must be explicitly applied to the dispatch. No separate permission to override configured defaults is required.

If a current-request constraint prevents the capability floor from being met, return `dispatchable: false` and explain the conflict.

## Capability tiers

- **Fast**: bounded, low-risk work with clear requirements and straightforward verification, including exploration and mechanical or repetitive tasks.
- **Standard**: substantive judgment, cross-file behavioral reasoning, interactive or agentic coding, deep debugging, or ordinary substantive review.
- **Premium**: security-sensitive or high-stakes work, difficult long-horizon reasoning, complex large-codebase work, prior important review misses, repeated reasoning failures, or user-requested best quality.

Tiers classify task requirements and model-and-effort configurations—not price, latency, provider, or model family.

File count, language mix, platform scope, and test count do not determine a tier by themselves.

The capability floor is the lowest permitted tier. If availability requires a higher-tier configuration, report the tier of the selected configuration and explain the availability-driven increase.

## Routing procedure

1. Gather:
   - objective and work class
   - stakes and security sensitivity
   - ambiguity and reasoning difficulty
   - expected context size
   - review history
   - verification approach
   - current-request constraints
   - exact models and effort values accepted by the dispatch interface
2. For code review, PR review, auditing, or security review, determine the floor using [`reference/review-routing.md`](reference/review-routing.md).
3. Otherwise, determine the floor from risk, ambiguity, reasoning, context, and verification needs.
4. Apply [`reference/escalation-policy.md`](reference/escalation-policy.md).
5. Identify eligible configurations using [`reference/model-catalog.md`](reference/model-catalog.md).
6. Restrict candidates to exact model and effort values accepted by the dispatch interface.
7. Among capable candidates, use [`reference/pricing.md`](reference/pricing.md) to minimize expected total cost of successful completion.
8. Select one exact configuration and, when available, one exact same-tier fallback.
9. Return `dispatchable: false` if the selected model or effort cannot be resolved exactly.

Capability floors override price, convenience, and defaults. Availability never permits routing below the floor.

## Selection rules

- Reuse a route only when work class, stakes, security sensitivity, ambiguity, affected behavior, review history, context, verification, current-request constraints, and runtime capabilities are materially unchanged.
- Use the catalog's task defaults as provisional starting points.
- Resolve every catalog entry to one exact model and effort accepted by the dispatch interface.
- Prefer Fast for bounded, low-risk work unless a concrete requirement establishes a higher floor.
- Mechanical multi-file work may remain Fast when verification is straightforward.
- Cross-file behavioral reasoning is normally at least Standard.
- For large context, first seek a same-tier configuration confirmed to support it.
- Prefer a same-tier fallback when the first configuration is unavailable.
- If no same-tier configuration is available, use the lowest-cost capable higher-tier configuration unless a current-request constraint prohibits it.
- Prefer the latest model version unless an older version has lower expected cost or demonstrated better task fit.
- Do not infer capability from price, recency, provider, or model name.
- Optimize expected completion cost, including tokens, cache behavior, retries, tool use, and verification.
- Do not select a model scheduled to retire before the subtask is expected to run.

Use evidence in this order:

1. task-specific local evaluation
2. demonstrated success on materially similar work
3. platform or provider guidance
4. provisional catalog defaults

When relying on provisional guidance, state the uncertainty and require verification appropriate to the stakes.

## Output

Always return:

```yaml
dispatchable: <true|false>
tier: <Fast|Standard|Premium>
model: <exact dispatch value or unresolved>
reasoning_effort: <exact dispatch value or unresolved>
reason: <task fit, capability floor, cost assumptions, and uncertainty>
escalation_trigger: <concrete trigger or none>
fallback:
  model: <exact same-tier dispatch value>
  reasoning_effort: <exact dispatch value>
```

Use `fallback: none` when no exact same-tier fallback exists.

For an availability-driven higher-tier selection, `tier` is the selected configuration's tier. Explain the lower capability floor and the availability-driven increase in `reason`.

Example:

```yaml
dispatchable: true
tier: Standard
model: gpt-6-luna
reasoning_effort: max
reason: A bounded substantive review requires Standard capability. This provisional budget-review configuration is accepted by the current dispatch interface.
escalation_trigger: Escalate if verification exposes an unresolved reasoning gap or the task becomes security-sensitive.
fallback:
  model: gpt-5.6-luna
  reasoning_effort: max
```

If exact values cannot be confirmed:

```yaml
dispatchable: false
tier: Standard
model: unresolved
reasoning_effort: unresolved
reason: The task requires Standard capability, but an exact accepted model-and-effort configuration could not be confirmed.
escalation_trigger: none
fallback: none
```

A route with `dispatchable: false` must not be used for dispatch.

## References

Load only when needed:

- [`reference/review-routing.md`](reference/review-routing.md): review floors.
- [`reference/escalation-policy.md`](reference/escalation-policy.md): escalation and failure diagnosis.
- [`reference/model-catalog.md`](reference/model-catalog.md): configurations and task defaults.
- [`reference/pricing.md`](reference/pricing.md): Copilot rates and expected-cost comparison.
- [`reference/patterns.md`](reference/patterns.md): non-authoritative examples.
