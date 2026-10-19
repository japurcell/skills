```yaml
dispatchable: true
tier: Standard
model: claude-sonnet-5.5
reasoning_effort: high
reason: >-
  Ordinary substantive review requires Standard. Both exact configurations
  are accepted and equally capable on this task.
  claude-sonnet-5: (100000 / 1000000 × $0.20) + (1000 / 1000000 × $10.00) = $0.03.
  claude-sonnet-5.5: (100000 / 1000000 × $0.10) + (1000 / 1000000 × $10.00) = $0.02.
  No new cache writes, uncached input, or retries; verification costs are identical.
escalation_trigger: Verification reveals a reasoning gap or security sensitivity emerges.
fallback:
  model: claude-sonnet-5
  reasoning_effort: high
```

**Model names alone:** route becomes `dispatchable: false`. Without confirmed accepted effort values, `reasoning_effort` is `unresolved`; neither selection nor fallback may dispatch.
