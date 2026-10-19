`fallback: none` is valid and required.

```yaml
dispatchable: true
tier: Standard
model: model-a
reasoning_effort: high
reason: Standard capability floor met by model-a at high. User constraint restricts selection to model-a's family, excluding model-b at high. No other configuration in model-a's family is available in the runtime, leaving no eligible same-tier fallback.
escalation_trigger: Verification exposes a reasoning gap or risk increases.
fallback: none
```

Per SKILL.md, `fallback: none` applies when no other exact same-tier configuration satisfies task requirements, runtime capabilities, and user constraints. `model-b` (`high`) fails the explicit user family constraint, and no other runtime candidate exists.
