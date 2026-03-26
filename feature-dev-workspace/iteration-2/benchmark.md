# Skill Benchmark: feature-dev

**Model**: GPT-5.4
**Date**: 2026-03-26T19:42:05Z
**Evals**: 0, 1, 2 (1 run each per configuration)

## Summary

| Metric    | With Skill  | Old Skill   | Delta |
| --------- | ----------- | ----------- | ----- |
| Pass Rate | 100% ± 0%   | 94% ± 10%   | +0.06 |
| Time      | 0.0s ± 0.0s | 0.0s ± 0.0s | +0.0s |
| Tokens    | 5359 ± 2058 | 6060 ± 2074 | -701  |

## Notes

- The only discriminating expectation in this iteration is eval 1's calibration check; the other 13 expectations pass in both configurations.
- Evals 0 and 2 are saturated at 100% for both sides, so they mostly confirm baseline competence rather than differentiating the revised skill.
- Token usage is lower with the revised skill on every eval in this iteration, with a mean reduction of about 701 tokens.
- Error counts also improve materially: the revised skill records 1 total executor error across the three evals, versus 6 for the old skill.
- The benchmark still cannot support latency conclusions because every run records 0.0 seconds.
