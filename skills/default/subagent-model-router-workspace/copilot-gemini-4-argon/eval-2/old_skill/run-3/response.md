```yaml
dispatchable: true
tier: Fast
model: gpt-5.6-luna
reasoning_effort: medium
reason: Deterministic log summarization keeps a Fast floor. Context grew from 80,000 to 150,000 uncached input tokens (crossing claude-haiku-5.5's >100K threshold while staying under gpt-5.6-luna's ≤200K threshold), requiring a reroute. With equal demonstrated task fit, 0 cache writes, 0 retries, and matching verification costs: gpt-5.6-luna costs $0.0324 USD (150,000 × $0.20/1M = $0.0300 input + 2,000 × $1.20/1M = $0.0024 output), whereas claude-haiku-5.5 costs $0.0800 USD (150,000 × $0.50/1M = $0.0750 input + 2,000 × $2.50/1M = $0.0050 output).
escalation_trigger: Escalate to Standard if verification reveals reasoning or correctness gaps, input exceeds suitable Fast context limits, or requirements shift from deterministic summarization to behavioral analysis.
fallback:
  model: claude-haiku-5.5
  reasoning_effort: medium
```

**Cost breakdown (150,000 uncached input + 2,000 output tokens):**
- `gpt-5.6-luna` (`medium`, `≤200K` row): `0.15M × $0.20 + 0.002M × $1.20 = $0.0300 + $0.0024 = $0.0324` (3.24 AI Credits)
- `claude-haiku-5.5` (`medium`, `>100K` row): `0.15M × $0.50 + 0.002M × $2.50 = $0.0750 + $0.0050 = $0.0800` (8.00 AI Credits)
