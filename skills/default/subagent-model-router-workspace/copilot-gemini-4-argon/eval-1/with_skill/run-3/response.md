```yaml
dispatchable: true
tier: Fast
model: claude-haiku-5.5
reasoning_effort: medium
reason: Summarizing explicit test failures without code diagnosis is bounded, low-risk mechanical work requiring the Fast floor. Capability is based on provisional catalog guidance; verify the summary includes every explicit failure verbatim without hallucinated root-cause claims. At 80,000 uncached input tokens (≤100K tier) and 2,000 output tokens with no cache writes or retries, claude-haiku-5.5 costs $0.0090 USD ($0.0080 input + $0.0010 output; 0.9 AI credits) versus $0.0900 USD ($0.0800 input + $0.0100 output; 9.0 AI credits) for claude-haiku-4.5, and is the latest version.
escalation_trigger: Task expands to diagnosing root causes in code, input exceeds 100K tokens and changes cost comparison, or verification reveals missed/misstated failures.
fallback:
  model: claude-haiku-4.5
  reasoning_effort: medium
```

Estimated token cost:
- `claude-haiku-5.5` (`medium`, ≤100K input): `$0.0090` USD (`0.08M * $0.10 = $0.0080` input + `0.002M * $0.50 = $0.0010` output; `0.9` AI credits).
- `claude-haiku-4.5` (`medium`, fallback): `$0.0900` USD (`0.08M * $1.00 = $0.0800` input + `0.002M * $5.00 = $0.0100` output; `9.0` AI credits).
