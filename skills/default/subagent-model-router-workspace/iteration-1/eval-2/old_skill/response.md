dispatchable: true
tier: Fast
model: gpt-5.6-luna
reasoning_effort: medium
estimated_token_cost_usd: 0.0324
reason: Deterministic log summarization is bounded Fast work. With 150,000 uncached input tokens and 2,000 output tokens, GPT-5.6 Luna costs $0.0324 and Haiku 5.5 costs $0.0800; the supplied equal task fit and equal verification costs favor Luna. No cache writes or retries are included.
escalation_trigger: Escalate if the task expands beyond deterministic summarization or verification reveals a reasoning gap.
fallback:
  model: claude-haiku-5.5
  reasoning_effort: medium
