```yaml
dispatchable: true
tier: Standard
model: claude-sonnet-5.5
reasoning_effort: high
reason: Ordinary substantive review sets a Standard floor. Both configurations are accepted by the Copilot dispatch interface and have equal task capability here. With 100,000 confirmed cached-input tokens, 1,000 output tokens, zero uncached input or new cache writes, no retries, and identical verification: claude-sonnet-5.5 costs $0.02 (0.1M * $0.10 = $0.01 cached input + 0.001M * $10.00 = $0.01 output; 2 AI Credits), while claude-sonnet-5 costs $0.03 (0.1M * $0.20 = $0.02 cached input + 0.001M * $10.00 = $0.01 output; 3 AI Credits). claude-sonnet-5.5 is both cheaper and the latest version.
escalation_trigger: Verification reveals a reasoning gap, a prior important review miss applies, or security/concurrency/trust-boundary risk emerges (escalate to Premium).
fallback:
  model: claude-sonnet-5
  reasoning_effort: high
```

If the interface later advertises only model names without accepted effort values, the route does **not** remain dispatchable (`dispatchable: false`, `reasoning_effort: unresolved`, `fallback: none`). The dispatch contract requires confirming both an exact model ID and an exact reasoning-effort value accepted by the interface; never dispatch when effort support cannot be confirmed.
