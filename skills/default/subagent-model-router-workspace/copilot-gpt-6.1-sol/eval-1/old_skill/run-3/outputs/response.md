```yaml
dispatchable: true
tier: Fast
model: claude-haiku-5.5
reasoning_effort: medium
reason: >-
  Summarizing explicit test failures without diagnosis is bounded, low-risk work.
  Both accepted configurations meet the provisional Fast floor.
  With no quality evidence and equal verification costs, Haiku 5.5 is cheapest
  at 80000 input tokens, below its 100K pricing threshold.
  Verify the summary against the test output.
estimated_token_cost_usd: 0.009
cost_breakdown_usd:
  uncached_input: 0.008
  output: 0.001
escalation_trigger: Reroute if code diagnosis is required or verification exposes a reasoning gap.
fallback:
  model: claude-haiku-4.5
  reasoning_effort: medium
  estimated_token_cost_usd: 0.09
```
