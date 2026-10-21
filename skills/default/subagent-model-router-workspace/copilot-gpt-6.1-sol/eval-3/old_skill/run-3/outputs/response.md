```yaml
dispatchable: true
tier: Standard
model: claude-sonnet-5.5
reasoning_effort: high
reason: >-
  Ordinary substantive review requires Standard. Supplied task evidence confirms
  both exact configurations are accepted and equally capable, overriding
  provisional catalog guidance. Sonnet 5.5 costs $0.02:
  (100000 / 1000000 × $0.10) + (1000 / 1000000 × $10).
  Sonnet 5 costs $0.03:
  (100000 / 1000000 × $0.20) + (1000 / 1000000 × $10).
  No new writes, uncached input, retries, or verification differences.
escalation_trigger: Verification exposes a reasoning gap or security-sensitive behavior.
fallback:
  model: claude-sonnet-5
  reasoning_effort: high
```

If the interface later lists only model names, **dispatchable: false**. Accepted effort values become unresolved; prior acceptance cannot establish current availability.
