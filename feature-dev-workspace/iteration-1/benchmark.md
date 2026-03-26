# Skill Benchmark: feature-dev

**Model**: GPT-5.4
**Date**: 2026-03-26T19:06:55Z
**Evals**: 0, 1, 2 (1 run each per configuration)

## Summary

| Metric    | With Skill  | Old Skill   | Delta |
| --------- | ----------- | ----------- | ----- |
| Pass Rate | 100% ± 0%   | 93% ± 12%   | +0.07 |
| Time      | 0.0s ± 0.0s | 0.0s ± 0.0s | +0.0s |
| Tokens    | 7123 ± 2803 | 7270 ± 1732 | -147  |

## Notes

- Benchmark coverage is narrow: only 1 of the 13 graded expectations differentiates the skill, so most of the current benchmark measures baseline competence rather than skill-specific value.
- The only clear quality win is eval 1's question-discipline check; with_skill passes it and old_skill fails it.
- No expectation passes in old_skill while failing in with_skill, so this benchmark shows a modest improvement without evidence of regression.
- The benchmark cannot support latency conclusions because every run records 0.0 seconds.
- Token usage is mixed by eval: the revised skill is much leaner on eval 1, slightly larger on eval 0, and materially larger on eval 2.
- old_skill logged one executor error on eval 2 while with_skill logged none, which slightly understates the operational difference if you look only at pass rate.
