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

Implicit, inherited, conditional, ranged, or unresolved values are not dispatchable. This includes:

- `default`
- `auto`
- `runtime-selected`
- `runtime default`
- “runtime-supported”
- “high or greater”
- “strongest available”
- “if applicable”
- an unexpanded placeholder

If exact accepted values cannot be confirmed, return `dispatchable: false`.

## Selection precedence and independence

Apply selection rules in this order:

1. Explicit model or effort constraints already stated by the user before the current routing attempt.
2. The capability and cost rules in this skill.
3. No implicit, inherited, configured, or runtime default.

Absent model or effort instructions mean `none`; they are not ambiguity. Independently select the route without asking the user to choose, approve, confirm, or restate a model, effort, or configured default.

Persistent configuration does not override the router. If the user explicitly requested configured defaults before the attempt, resolve them to exact values and verify that they satisfy the capability floor.

A routing attempt uses the task facts, runtime capabilities, and user constraints already in scope when it begins. A solicited model preference cannot retroactively justify that attempt. If constraints change, begin a fresh attempt.

If essential task facts are missing, request only those facts. If exact runtime values cannot be determined or an explicit constraint prevents the floor from being met, return `dispatchable: false`.

For delegation, the returned model and effort must be explicitly applied. No separate model-selection permission or confirmation is required.

## Capability tiers

- **Fast**: bounded, low-risk work with clear requirements and straightforward verification, including exploration and mechanical or repetitive tasks.
- **Standard**: substantive judgment, cross-file behavioral reasoning, interactive or agentic coding, deep debugging, or ordinary substantive review.
- **Premium**: security-sensitive or high-stakes work, difficult long-horizon reasoning, complex large-codebase work, prior important review misses, repeated reasoning failures, or user-requested best quality.

Tiers classify task requirements and model-and-effort configurations—not price, latency, provider, or model family.

File count, language mix, platform scope, and test count do not determine a tier by themselves.

The capability floor is the lowest permitted tier. If availability requires a higher-tier configuration, report the selected configuration's tier and explain the availability-driven increase.

## Routing procedure

1. Gather:
   - objective and work class
   - stakes and security sensitivity
   - ambiguity and reasoning difficulty
   - expected context size
   - review history
   - verification approach
   - model or effort constraints already in scope, or `none`
   - exact models and effort values accepted by the dispatch interface
2. For code review, PR review, auditing, or security review, determine the floor using [`reference/review-routing.md`](reference/review-routing.md).
3. Otherwise, determine the floor from risk, ambiguity, reasoning, context, and verification needs.
4. Apply [`reference/escalation-policy.md`](reference/escalation-policy.md).
5. Identify eligible configurations using [`reference/model-catalog.md`](reference/model-catalog.md).
6. Restrict candidates to exact configurations accepted by the dispatch interface.
7. Among capable candidates, use [`reference/pricing.md`](reference/pricing.md) to minimize expected completion cost.
8. Select one exact configuration and, when available, one exact same-tier fallback.
9. Return `dispatchable: false` if the selected model or effort cannot be resolved exactly.

Capability floors override price, convenience, and defaults. Availability never permits routing below the floor.

## Selection rules

- Return the route as a decision, not an approval request.
- Reuse a route only when work class, stakes, security sensitivity, ambiguity, affected behavior, review history, context, verification, constraints, and runtime capabilities are materially unchanged.
- Use the catalog's task defaults as provisional starting points.
- Resolve every catalog entry to one exact model and effort accepted by the dispatch interface.
- Prefer Fast for bounded, low-risk work unless a concrete requirement establishes a higher floor.
- Mechanical multi-file work may remain Fast when verification is straightforward.
- Cross-file behavioral reasoning is normally at least Standard.
- For large context, first seek a same-tier configuration confirmed to support it.
- Prefer a same-tier fallback when the first configuration is unavailable.
- If none is available, use the lowest-cost capable higher-tier configuration unless a user constraint prohibits it.
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

For an availability-driven higher-tier selection, report the selected tier and explain the lower capability floor and availability-driven increase in `reason`.

A dispatchable result is a routing decision, not an approval request. Do not mark it tentative or pending confirmation.

Example:

```yaml
dispatchable: true
tier: Standard
model: gpt-6-luna
reasoning_effort: max
reason: A bounded substantive review requires Standard capability. This provisional budget-review configuration is accepted by the current dispatch interface.
escalation_trigger: Escalate if verification exposes a reasoning gap or the task becomes security-sensitive.
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
