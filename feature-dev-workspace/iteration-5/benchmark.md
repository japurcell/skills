# Skill Benchmark: feature-dev

**Model**: GPT-5.4
**Date**: 2026-03-26T20:20:52Z
**Evals**: 2 (1 run each per configuration)

## Summary

| Metric    | With Skill  | Old Skill   | Delta |
| --------- | ----------- | ----------- | ----- |
| Pass Rate | 100% ± 0%   | 100% ± 0%   | +0.00 |
| Time      | 0.0s ± 0.0s | 0.0s ± 0.0s | +0.0s |
| Tokens    | 13154 ± 0   | 13992 ± 0   | -838  |

## Notes

- Strict artifact-quality checks still tie at 100% for both configurations.
- This means the refinement improved rigor but is still not discriminating for this prompt.
- with_skill is cheaper on token usage in this sample, but uses slightly more tool calls.
- A true separator likely needs one negative control (for example, intentionally missing risk framing or missing file rationale) or multiple independent prompts.
