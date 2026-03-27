# Skill Benchmark: issue-to-spec

**Date**: 2026-03-26T23:52:58Z

## Summary

| Metric | With Skill | Old Skill | Delta |
|--------|------------|-----------|-------|
| Pass Rate | 75% ± 0% | 58% ± 29% | +0.17 |
| Time | 0.0s ± 0.0s | 0.0s ± 0.0s | +0.0s |
| Tokens | 0 ± 0 | 0 ± 0 | +0 |

## Notes

- Assertion discrimination is weak overall: issue-id check passes in 100% of runs for both configurations.
- The planning-ready guardrail fails in 100% of runs for both configurations, capping max pass rate at 75%.
- The command+error transparency assertions are the only differentiators, and only on eval 0.
- old_skill shows high variance (stddev 0.2887), while with_skill is stable at 0.75 (stddev 0.0).
- Time/tokens/tool-calls are effectively unavailable in current telemetry, so efficiency tradeoffs are inconclusive.
