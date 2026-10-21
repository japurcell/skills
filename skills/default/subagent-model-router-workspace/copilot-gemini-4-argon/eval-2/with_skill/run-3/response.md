```yaml
dispatchable: true
tier: Fast
model: gpt-5.6-luna
reasoning_effort: medium
reason: Deterministic log summarization stays at the Fast capability floor; context size increase from 80000 to 150000 tokens triggers rerouting and crosses the >100K pricing threshold for claude-haiku-5.5 while staying in the <=200K tier for gpt-5.6-luna. Both runtime-accepted candidates have demonstrated equal task fit, no cache writes or retries, and matching verification costs. At 150000 uncached input tokens and 2000 output tokens, gpt-5.6-luna costs $0.0324 USD ($0.0300 input at $0.20/1M + $0.0024 output at $1.20/1M), beating claude-haiku-5.5 at $0.0800 USD ($0.0750 input at $0.50/1M + $0.0050 output at $2.50/1M).
escalation_trigger: Verification exposes a reasoning or correctness gap, required context exceeds Fast capacity, or task requirements shift from deterministic summarization to substantive analysis.
fallback:
  model: claude-haiku-5.5
  reasoning_effort: medium
```
