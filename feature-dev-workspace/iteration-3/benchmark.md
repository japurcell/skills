# Skill Benchmark: feature-dev

**Model**: GPT-5.4
**Date**: 2026-03-26T19:58:05Z
**Evals**: 2 (1 run each per configuration)

## Summary

| Metric    | With Skill  | Old Skill   | Delta |
| --------- | ----------- | ----------- | ----- |
| Pass Rate | 100% ± 0%   | 100% ± 0%   | +0.00 |
| Time      | 0.0s ± 0.0s | 0.0s ± 0.0s | +0.0s |
| Tokens    | 6900 ± 0    | 6050 ± 0    | +850  |

## Notes

- This focused handoff benchmark is non-discriminating: both configurations pass all 5 assertions.
- The new file-backed artifact assertion is still too easy to satisfy in a design-only prompt because the baseline can also describe the path and template correctly.
- In this sample the revised skill is costlier, not cheaper: higher token usage, more tool calls, and one recoverable error.
- This suggests the next useful eval should require actually producing or updating a handoff artifact, not just proposing one.
