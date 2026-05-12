# Skill Benchmark: security-review

**Model**: GPT-5.4
**Date**: 2026-04-07T20:14:46Z
**Evals**: 0, 1, 2 (3 runs each per configuration)

## Summary

| Metric    | With Skill  | Without Skill | Delta |
| --------- | ----------- | ------------- | ----- |
| Pass Rate | 100% ± 0%   | 100% ± 0%     | +0.00 |
| Time      | 0.0s ± 0.0s | 0.0s ± 0.0s   | +0.0s |
| Tokens    | 1234 ± 420  | 1564 ± 588    | -330  |

## Notes

- In iteration-2, `without_skill` is the snapshotted pre-edit skill, not a no-skill baseline.
- The revised skill preserved a 100% pass rate across all three runs and all evals, but the old skill was already at 100% on this regression set, so pass rate did not move.
- The prompt edit did reduce the output-size proxy by about 330 characters on average (1234 vs 1564), which matches the intended shift toward shorter, more triage-friendly findings.
- Timing data is unavailable in this environment because subagent duration notifications were not surfaced; all time metrics are 0.0 and token values are proxied from output size.
