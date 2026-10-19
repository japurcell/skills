```yaml
dispatchable: true
tier: Fast
model: gpt-5.6-luna
reasoning_effort: medium
reason: >-
  Deterministic summarization remains Fast. Both accepted configurations have
  demonstrated equal task fit. At 150000 uncached input and 2000 output tokens,
  gpt-5.6-luna costs $0.0300 + $0.0024 = $0.0324.
  claude-haiku-5.5 exceeds its 100K threshold and costs
  $0.0750 + $0.0050 = $0.0800.
  Select gpt-5.6-luna, saving $0.0476. No cache writes or retries;
  verification costs match. No user model constraint or task-fit uncertainty.
escalation_trigger: Verification reveals a reasoning gap or task stops being deterministic.
fallback:
  model: claude-haiku-5.5
  reasoning_effort: medium
```
