# Escalation Policy

This file owns escalation policy. For review work, first establish the floor using [`review-routing.md`](review-routing.md).

## Escalation triggers

Escalate when:

- verification reveals a reasoning or correctness gap after instructions, inputs, and environment are checked
- material constraints are repeatedly missed
- reasoning is inadequate for the demonstrated complexity
- required context cannot fit in a suitable same-tier configuration
- new task evidence raises the capability floor
- the user requests a stronger tier or best quality
- stakes, ambiguity, or security sensitivity materially increase
- repeated failures demonstrate inadequate capability

For non-review work, a prior important miss on materially similar work normally raises the route one tier. Move directly to Premium when the miss establishes high stakes, security sensitivity, or unusually difficult reasoning.

For review work, follow the prior-miss rule in [`review-routing.md`](review-routing.md).

## Diagnose first

Before escalating, check:

- instructions and inputs
- files and context
- dependencies and permissions
- tools and environment
- model and effort availability
- whether the task should be split
- whether verification is adequate

A failing test ordinarily indicates a code or environment issue, not a model-capability issue.

Do not escalate merely because:

- tests, lint, builds, formatting, scripts, search, or file enumeration are being executed mechanically
- the work is deterministic and directly verifiable
- several files or languages are involved
- a newer or more expensive model exists
- an ordinary correction is required
- the preferred model is unavailable but a capable same-tier alternative exists

Authoring, reviewing, or diagnosing tests, scripts, or build logic may still require a higher tier when substantial judgment or risk is involved.

## Escalation path

| Current tier | Next action |
| --- | --- |
| Fast | Standard |
| Standard | Premium |
| Premium | Better-fitting Premium configuration, more context, task decomposition, stronger verification, or human review |

Move directly to the tier required by a changed capability floor; stepwise escalation is not mandatory.

Before escalating the capability floor, confirm that the change addresses a specific capability, context, or risk gap.

## Availability

When a configuration is unavailable:

1. preserve the capability floor
2. choose the lowest-cost capable same-tier configuration
3. resolve it to an exact model and effort
4. report the availability-driven fallback

If no same-tier configuration is available, choose the lowest-cost available higher-tier configuration that satisfies the floor and current-request constraints. Report the availability-driven tier increase.

If no qualifying configuration is available, return `dispatchable: false`.

Never select a configuration below the capability floor.

Selecting a higher-tier configuration solely because no same-tier configuration is available is an availability-driven promotion, not evidence that the task's capability floor increased.
