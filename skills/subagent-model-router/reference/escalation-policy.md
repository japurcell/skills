# Escalation Policy

This file owns general escalation policy. For code review, PR review, auditing, or security review, first establish the review floor using [`review-routing.md`](review-routing.md).

Use the named defaults in [`model-catalog.md#task-defaults`](model-catalog.md#task-defaults) after determining the required tier.

## Escalate when

Escalate when a concrete capability or risk trigger applies, including:

- verification exposes a reasoning or correctness gap after instructions, inputs, dependencies, and environment have been checked
- the worker repeatedly misses material constraints
- the reasoning is too shallow for the demonstrated task complexity
- the required context cannot fit in any suitable same-tier configuration
- no available same-tier configuration can satisfy the task floor
- the user explicitly requests a stronger tier or best-quality routing
- stakes, ambiguity, or security sensitivity materially increase
- repeated failures show that the current configuration is not capable of completing the task reliably

For non-review work, a prior important miss on materially similar work normally justifies escalation by one tier. Escalate directly to Premium when the miss also establishes high stakes, security sensitivity, or unusually difficult reasoning.

For review work, prior-miss rules are owned by [`review-routing.md`](review-routing.md).

## Diagnose before escalating

Do not treat every failure as evidence that a stronger model is needed.

Before escalating, check whether the problem is caused by:

- unclear or conflicting instructions
- missing files or context
- unavailable dependencies
- insufficient permissions
- an unsupported or unavailable model
- environment or tool failures
- an ordinary test failure caused by the code under test
- a task that should be split into smaller units
- missing or inadequate verification

An unsupported or unavailable model normally calls for an available same-tier fallback.

A failing test is evidence about the code or environment, not automatically evidence that the worker needs more reasoning capability. Escalate only when diagnosis reveals a reasoning gap, an unmet capability requirement, or greater task risk.

## Do not escalate merely because

- the work mechanically executes tests, lint, builds, scripts, formatting, search, or file enumeration
- the work is a deterministic transformation with clear verification
- multiple files or languages are involved
- a more expensive or newer model exists
- the preferred model is unavailable but a capable same-tier fallback exists
- the initial output requires an ordinary correction that does not reveal a capability gap

Authoring, reviewing, or diagnosing tests, scripts, or build logic may still require Standard or Premium when substantial judgment, subtle correctness, or security risk is involved.

## Escalation path

| Current tier | Normal next step |
| --- | --- |
| Fast | Standard |
| Standard | Premium |
| Premium | Better-fitting Premium configuration, more context, task decomposition, independent verification, or human review |

A task may move directly to Premium when its capability floor becomes Premium. Do not force stepwise escalation when security sensitivity, high stakes, or another Premium requirement is already established.

## Before escalating

Confirm that:

- instructions are clear and internally consistent
- required files and context are available
- dependencies, permissions, tools, and environment have been checked
- task decomposition has been considered
- appropriate verification exists
- the current model-and-effort configuration satisfies the current floor
- the proposed higher tier addresses a specific observed gap

## Availability fallback

When a model or effort setting is unavailable:

1. Preserve the task's capability floor.
2. Choose another available configuration in the same tier when possible.
3. Prefer the lowest expected-cost configuration with adequate task fit.
4. Change the route only if no available same-tier configuration can satisfy the floor.
5. Report that the fallback was caused by availability.

Availability never justifies routing below the established floor.
