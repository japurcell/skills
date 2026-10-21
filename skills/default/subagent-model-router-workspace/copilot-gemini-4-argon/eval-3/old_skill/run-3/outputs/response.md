```yaml
dispatchable: true
tier: Standard
model: claude-sonnet-5.5
reasoning_effort: high
reason: Ordinary substantive review requires Standard capability. User constrains evaluation to claude-sonnet-5 at high and claude-sonnet-5.5 at high, both accepted and equally capable here (note: catalog provisionally lists medium for Standard Sonnet 5/5.5; high is provisional for this route, verify review output). For 100,000 confirmed cached-input tokens and 1,000 output tokens (0 uncached input, 0 cache write, 0 retries, identical verification), claude-sonnet-5.5 costs $0.020 ($0.010 cached input at $0.10/1M + $0.010 output at $10.00/1M) versus $0.030 for claude-sonnet-5 ($0.020 cached input at $0.20/1M + $0.010 output at $10.00/1M).
escalation_trigger: Escalate to Premium if verification exposes a reasoning gap, a prior important review miss applies, or the review becomes security-sensitive.
fallback:
  model: claude-sonnet-5
  reasoning_effort: high
```

### Cost comparison

- **`claude-sonnet-5.5` (`high`)**: `(100,000 / 1,000,000) * $0.10 + (1,000 / 1,000,000) * $10.00 = $0.010 + $0.010 = $0.020` (2.0 AI Credits)
- **`claude-sonnet-5` (`high`)**: `(100,000 / 1,000,000) * $0.20 + (1,000 / 1,000,000) * $10.00 = $0.020 + $0.010 = $0.030` (3.0 AI Credits)

### If effort values are omitted by the interface

Not dispatchable (`dispatchable: false`, `reasoning_effort: unresolved`, `fallback: none`). Every dispatchable route requires both an exact accepted model ID and an exact accepted reasoning-effort value; implicit, runtime-default, or unconfirmed efforts are not permitted.
