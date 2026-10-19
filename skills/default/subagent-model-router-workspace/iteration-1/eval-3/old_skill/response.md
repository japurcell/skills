dispatchable: true
tier: Standard
model: claude-sonnet-5.5
reasoning_effort: high
estimated_token_cost_usd: 0.02
reason: Ordinary substantive review has a Standard floor. Given the stated accepted, equally capable configurations and 100,000 confirmed cached input tokens plus 1,000 output tokens, Sonnet 5.5 costs $0.02 versus $0.03 for Sonnet 5. Previously paid cache writes, retries, and verification add no cost here.
escalation_trigger: Escalate if verification reveals a reasoning gap or the review becomes higher-stakes or security-sensitive.
fallback:
  model: claude-sonnet-5
  reasoning_effort: high
later_interface_dispatchable: false
later_interface_reason: Model names without accepted effort values do not confirm the exact high effort, so the route cannot be returned as dispatchable.
