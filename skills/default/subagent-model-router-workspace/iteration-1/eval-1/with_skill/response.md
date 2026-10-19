dispatchable: true
tier: Fast
model: claude-haiku-5.5
reasoning_effort: medium
reason: "Summarizing explicit test failures is bounded, low-risk work with a straightforward result, so Fast is the capability floor. At 80,000 uncached input tokens and 2,000 output tokens, claude-haiku-5.5 uses the <=100K row: (80,000 * $0.10 + 2,000 * $0.50) / 1,000,000 = $0.009. claude-haiku-4.5 costs $0.09 for the same token shape. Cache writes and retries are zero and verification costs are equal."
escalation_trigger: none
fallback:
  model: claude-haiku-4.5
  reasoning_effort: medium
estimated_token_cost_usd: 0.009
