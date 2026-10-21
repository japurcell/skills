# Routing Patterns

Non-authoritative examples. Follow [SKILL.md](../SKILL.md), [review-routing.md](review-routing.md), and [escalation-policy.md](escalation-policy.md) if an example conflicts.

## Boundary cases

| Situation | Decision |
| --- | --- |
| Mechanical rename across many files, straightforward verification | Fast |
| Substantive one-file review | At least Standard |
| Bounded feature review | Standard; budget-review starting candidate |
| Cross-component behavioral review | Standard; general-work starting candidate |
| Review authentication or subtle concurrency/cache-consistency risk | Premium |
| Similar review previously missed an important issue | Premium floor |
| Non-review task previously missed an important constraint | Apply general escalation, normally one tier |
| Tests fail or a dependency is missing | Diagnose code/environment before capability escalation |
| Preferred configuration unavailable | Apply the availability rule; never go below the floor |
| Scope, risk, context, constraints, or runtime capabilities change | Route again |
| Premium work still fails | Better-fitting Premium configuration, decomposition, stronger verification, or human review |

## Output examples

Synthetic IDs below assume confirmed runtime acceptance and task fit; they are not catalog entries or preferred models.

```yaml
dispatchable: true
tier: Standard
model: model-a
reasoning_effort: high
reason: Substantive bounded review requires Standard. Both candidates have demonstrated task fit; model-a has the lower expected cost at the supplied token volumes and rates.
escalation_trigger: Verification exposes a reasoning gap or security sensitivity emerges.
fallback:
  model: model-b
  reasoning_effort: high
```

When accepted values cannot be confirmed:

```yaml
dispatchable: false
tier: Standard
model: unresolved
reasoning_effort: unresolved
reason: Standard capability is required, but the runtime exposes no accepted effort values, so neither a selection nor a fallback can be confirmed.
escalation_trigger: none
fallback: none
```
