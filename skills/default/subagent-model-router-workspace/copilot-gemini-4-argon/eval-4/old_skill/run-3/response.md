No. The recorded `fallback: none` is inconsistent.

Why:
- `fallback: none` is allowed only when no other exact same-tier configuration meets runtime capabilities and user constraints.
- `model-b` at `high` is an exact, runtime-accepted, capable `Standard` configuration with no user constraints excluding it, so it must be recorded as the fallback.
- `model-c` at `medium` is `Fast`, below the `Standard` capability floor, and remains ineligible regardless of cost.

Corrected route:

```yaml
dispatchable: true
tier: Standard
model: model-a
reasoning_effort: high
reason: Selected configuration meets the Standard capability floor and is accepted by the dispatch interface. model-b at high is an eligible same-tier fallback; model-c at medium is excluded because Fast is below the Standard floor.
escalation_trigger: Escalate to Premium if verification exposes a reasoning gap or stakes/security sensitivity increase.
fallback:
  model: model-b
  reasoning_effort: high
```
