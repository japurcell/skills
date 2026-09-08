# Escalation Policy

Escalate only when the current route is not capable enough.

Use named defaults from [the catalog](model-catalog.md#task-defaults).

## Escalate when

- verification reveals a reasoning or correctness gap after instructions, inputs, and environment are checked
- constraints are missed
- reasoning is shallow for task complexity
- needed context does not fit
- no same-tier available model fits
- the route violates an agent-type floor
- the user requests a stronger tier
- prior same-class work missed an important issue
- stakes, ambiguity, or security sensitivity increase

For code/security review, also load `reference/review-routing.md`.

## Diagnose before escalating

Missing dependencies, permissions, unavailable models, and ordinary failing tests first require environment or failure diagnosis. An unsupported model calls for a same-tier available fallback. A test failure is evidence about the code, not automatically evidence that the worker needs more reasoning capability. Escalate when diagnosis exposes a reasoning gap or greater task risk.

## Do not escalate when

- work is deterministic and bounded
- work is only tests, lint, builds, scripts, formatting, search, or file enumeration
- a stronger model exists but no concrete need exists
- the output is a mechanical transformation with clear verification

Exception: keep execution cheap, but route judgment-heavy review to the proper review tier.

## Escalation path

| From | To |
|---|---|
| Fast | Standard |
| Standard | Premium |
| Premium | Same tier with better fit, more context, task split, or stronger verification |

## Before escalating, check

- instructions are clear
- needed files/context are available
- task should be split
- verification exists
- correct `agent_type` was selected
- selected model satisfies the floor

## Missed-issue feedback loop

If a prior review found no issue but a bug was later found, escalate the next review of the same task class by one tier.

Examples of task classes:

- auth flow
- redirects
- permissions
- test guards
- false-pass tests
- backend/frontend contracts
- API contracts
- migrations/deletion
- cache/concurrency behavior
- security-sensitive validation

Escalation:

| Prior route | Next same-class route |
|---|---|
| Fast review | Standard review, usually the budget-review default |
| Standard review | Premium review, usually the demanding-review default |
| Premium review | Premium again, with task split or stronger suited model |

Do not downshift until clean review history makes the prior miss no longer relevant.
