```yaml
dispatchable: true
tier: Fast
model: claude-haiku-5.5
reasoning_effort: medium
reason: Summarizing explicit test failures without diagnosing code is bounded, low-risk mechanical work with a Fast floor. Dispatch accepts only claude-haiku-4.5 and claude-haiku-5.5 at medium effort. At 80000 uncached input tokens (<=100K threshold) and 2000 output tokens with no cache writes, retries, or verification difference, claude-haiku-5.5 costs $0.0090 USD (0.90 AI Credits) vs $0.0900 USD (9.00 AI Credits) for claude-haiku-4.5. Provisional catalog guidance used without task-specific evidence; verify summary matches raw failure output.
escalation_trigger: Escalate to Standard if root-cause code diagnosis is required or verification exposes a reasoning gap.
fallback:
  model: claude-haiku-4.5
  reasoning_effort: medium
```

**Estimated token cost:**
- `claude-haiku-5.5` (≤100K row: $0.10/1M input, $0.50/1M output): `(80000 × $0.10 / 1,000,000) + (2000 × $0.50 / 1,000,000) = $0.0080 + $0.0010 = $0.0090 USD` (`0.90` GitHub AI Credits).
- `claude-haiku-4.5` fallback (default row: $1.00/1M input, $5.00/1M output): `(80000 × $1.00 / 1,000,000) + (2000 × $5.00 / 1,000,000) = $0.0800 + $0.0100 = $0.0900 USD` (`9.00` GitHub AI Credits).
