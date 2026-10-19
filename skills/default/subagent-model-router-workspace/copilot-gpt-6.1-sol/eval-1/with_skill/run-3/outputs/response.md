```yaml
dispatchable: true
tier: Fast
model: claude-haiku-5.5
reasoning_effort: medium
reason: >-
  Summarizing explicit failures without diagnosis is bounded, low-risk work.
  Capability is provisional from the bundled catalog; verify faithful coverage
  without added diagnosis. Both accepted configurations qualify. At 80K input,
  Haiku 5.5 costs $0.009 versus Haiku 4.5 at $0.090.
  No cache writes or retries; verification costs are equal.
estimated_token_cost_usd: 0.009
escalation_trigger: Verification reveals material omissions or a reasoning gap.
fallback:
  model: claude-haiku-4.5
  reasoning_effort: medium
```
