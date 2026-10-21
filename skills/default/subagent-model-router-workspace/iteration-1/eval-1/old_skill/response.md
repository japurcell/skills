dispatchable: true
tier: Fast
model: claude-haiku-5.5
reasoning_effort: medium
estimated_token_cost_usd: 0.009
reason: Summarizing explicit test failures without diagnosing code is bounded Fast work. At 80,000 uncached input tokens and 2,000 output tokens, Haiku 5.5 costs $0.009 versus $0.090 for Haiku 4.5; cache, retry, and verification costs are excluded as specified.
escalation_trigger: Escalate if the task expands into code diagnosis or verification reveals a reasoning gap.
fallback:
  model: claude-haiku-4.5
  reasoning_effort: medium
