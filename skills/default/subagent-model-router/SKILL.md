---
name: subagent-model-router
description: Route subagent work to the cheapest capable model. Use before dispatching subagents, task tools, background agents, code reviewers, security reviewers, or parallel workers when a model must be selected.
---

# Subagent Model Router

Choose the lowest-cost dispatchable configuration at the task's capability floor. Use a higher tier when no capable configuration at the floor is available.

## Dispatch contract

A dispatchable route specifies one tier and an exact model-and-effort pair accepted by the dispatch interface. Defaults, inheritance, placeholders, ranges, and conditional values are not exact values. If either value cannot be confirmed, return `dispatchable: false`; this includes interfaces that expose no effort value.

Apply both returned values explicitly when delegating. Never dispatch a `dispatchable: false` route.

## Constraints and independence

Honor explicit user model or effort constraints already in scope, then apply this skill's capability and cost rules. Missing constraints mean `none`, not ambiguity. Persistent configuration does not override routing. Use configured defaults only when explicitly requested by the user; resolve them to exact values that satisfy the floor.

Select independently without asking the user to choose, approve, confirm, or restate a model, effort, or default. Request only essential missing task facts. If constraints prevent meeting the floor, return `dispatchable: false`.

A routing attempt uses the task facts, runtime capabilities, and constraints in scope when it begins. Solicited preferences cannot retroactively justify it; changed constraints require a fresh attempt.

## Capability tiers

- **Fast**: bounded, low-risk work with clear requirements and straightforward verification, including exploration and mechanical or repetitive tasks.
- **Standard**: substantive judgment, cross-file behavioral reasoning, interactive or agentic coding, deep debugging, or ordinary substantive review.
- **Premium**: security-sensitive or high-stakes work, difficult long-horizon reasoning, complex large-codebase work, prior important review misses, repeated reasoning failures, or user-requested best quality.

Tiers classify task requirements and model-and-effort configurations. Price, latency, provider, model family, and recency do not establish capability. File count, language mix, platform scope, and test count alone do not raise the floor. Prefer Fast for bounded low-risk work unless a concrete requirement establishes a higher floor.

## Routing procedure

1. Gather objective, work class, stakes, security sensitivity, ambiguity, reasoning difficulty, affected behavior, context size, review history, verification approach, existing constraints (or `none`), and exact runtime model/effort capabilities.
2. Determine the lowest permitted tier. For code/PR review and audits, load [review-routing.md](reference/review-routing.md). Otherwise use the tier definitions above.
3. For failures, changed risk, or context-fit problems, load [escalation-policy.md](reference/escalation-policy.md).
4. Load [model-catalog.md](reference/model-catalog.md) for candidate configurations. Confirm runtime acceptance, context capacity, and applicable restrictions. Exclude models scheduled to retire before the subtask runs.
5. Apply the availability rule below. Load [pricing.md](reference/pricing.md) and compare all eligible candidates at applicable context and cache rates. Task defaults are provisional starting points, not preference orders.
6. Return one exact route and the lowest-cost eligible alternative at its selected tier, if any.

Reuse a route only when the facts gathered in step 1 are materially unchanged.

### Availability

Preserve the capability floor. First seek a capable configuration at that tier, including for large context. If none is available, select the lowest-cost capable higher-tier configuration permitted by user constraints. If none qualifies, return `dispatchable: false`.

When a selected configuration becomes unavailable, apply the same rule starting at its selected tier. A higher-tier selection caused only by availability does not raise the task's capability floor. Report the selected tier and explain the original floor and availability-driven increase.

### Evidence

Use evidence in this order: task-specific local evaluation, demonstrated success on materially similar work, platform/provider guidance, then provisional catalog defaults.

Prefer the latest version unless an older version has lower expected completion cost or demonstrated better task fit.

## Output

Return the complete structured decision; the caller controls storage and presentation. If capability is based on provisional guidance, explicitly label it provisional and state the required verification in `reason`.

```yaml
dispatchable: <true|false>
tier: <Fast|Standard|Premium>
model: <exact dispatch value or unresolved>
reasoning_effort: <exact dispatch value or unresolved>
reason: <task fit, capability floor, cost assumptions, uncertainty, and any availability-driven increase>
escalation_trigger: <concrete trigger or none>
fallback:
  model: <exact same-tier dispatch value>
  reasoning_effort: <exact dispatch value>
```

Use `fallback: none` only when no other exact same-tier configuration meets task requirements, runtime capabilities, and user constraints. Explain what excludes alternatives. For a failed selection, report the required floor and unresolved values with the reason dispatch is blocked.

A dispatchable result is a decision, not a request for approval or pending confirmation.

## Additional references

- [patterns.md](reference/patterns.md): optional boundary cases and output examples; non-authoritative.
- [maintenance.md](reference/maintenance.md): load only when refreshing catalog/pricing snapshots or investigating historical exclusions.
