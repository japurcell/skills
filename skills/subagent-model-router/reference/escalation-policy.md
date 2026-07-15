# Escalation Policy

Use when the first route may not be sufficient.

## Rule

Start with the cheapest capable tier. Escalate only for a concrete reason.

## Escalate when the model

- fails tests or verification
- misses important constraints
- gives shallow reasoning on a complex task
- cannot maintain needed context
- is unavailable and no same-tier model fits

Do not escalate only because a stronger model exists.

## Escalation path

| From | To |
|---|---|
| Fast | Standard |
| Standard | Premium |
| Premium | Faster premium only if speed is the issue |

## Before escalating, check for

- ambiguous instructions
- missing files or context
- lack of tests or verification
- overly broad scope
- work that should be split into smaller tasks
