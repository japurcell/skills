dispatchable: true
tier: Standard
model: claude-sonnet-5.5
reasoning_effort: high
reason: "Ordinary substantive review has a Standard floor. The prompt confirms both exact high-effort configurations are accepted and equally capable. For 100,000 confirmed cached-input tokens and 1,000 output tokens, claude-sonnet-5.5 costs $0.0200: $0.0100 cached input plus $0.0100 output. claude-sonnet-5 costs $0.0300: $0.0200 cached input plus $0.0100 output. Cache writes, uncached input, and retries are zero, and verification costs are identical."
escalation_trigger: none
fallback:
  model: claude-sonnet-5
  reasoning_effort: high
estimated_token_costs_usd:
  claude-sonnet-5: 0.03
  claude-sonnet-5.5: 0.02
later_interface_without_effort_values:
  dispatchable: false
  reason: "The dispatch contract requires the exact effort to be confirmed. An interface that advertises only model names does not confirm high."
