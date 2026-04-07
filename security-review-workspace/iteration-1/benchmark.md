# Skill Benchmark: security-review

**Model**: GPT-5.4
**Date**: 2026-04-07T20:09:33Z
**Evals**: 0, 1, 2 (3 runs each per configuration)

## Summary

| Metric    | With Skill  | Without Skill | Delta |
| --------- | ----------- | ------------- | ----- |
| Pass Rate | 100% ± 0%   | 78% ± 16%     | +0.22 |
| Time      | 0.0s ± 0.0s | 0.0s ± 0.0s   | +0.0s |
| Tokens    | 1581 ± 609  | 1247 ± 402    | +334  |

## Notes

- Across three runs per configuration, the skill remains perfectly stable on this eval set while the no-skill baseline consistently misses the explicit severity-format assertions on the two positive cases.
- The exclusion-only eval passes in both configurations, so it validates false-positive filtering but does not differentiate skill value.
- The measurable lift in iteration-1 is structural rather than analytical: both configurations found the real vulnerabilities, but only the skill-guided runs reliably produced the expected markdown format and uppercase severity markers.
- Timing data is unavailable in this environment because subagent duration notifications were not surfaced; all time metrics are 0.0 and token values are proxied from output size.
