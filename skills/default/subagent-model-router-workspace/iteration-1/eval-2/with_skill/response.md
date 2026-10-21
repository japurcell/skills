dispatchable: true
tier: Fast
model: gpt-5.6-luna
reasoning_effort: medium
reason: "Deterministic log summarization is bounded, low-risk work, so Fast is the capability floor. With 150,000 uncached input tokens and 2,000 output tokens, gpt-5.6-luna uses its <=200K row and costs $0.0324: $0.0300 input plus $0.0024 output. claude-haiku-5.5 uses its >100K row and costs $0.0800: $0.0750 input plus $0.0050 output. Task fit and verification are equal; there are no cache writes or retries."
escalation_trigger: none
fallback:
  model: claude-haiku-5.5
  reasoning_effort: medium
estimated_token_costs_usd:
  gpt-5.6-luna: 0.0324
  claude-haiku-5.5: 0.08
