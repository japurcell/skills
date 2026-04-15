# Skill Benchmark: issue-to-spec

**Date**: 2026-03-26T23:59:36Z

## Summary

| Metric | With Skill | Old Skill | Delta |
|--------|------------|-----------|-------|
| Pass Rate | 100% ± 0% | 92% ± 14% | +0.08 |
| Time | 0.0s ± 0.0s | 0.0s ± 0.0s | +0.0s |
| Tokens | 456 ± 20 | 551 ± 195 | -95 |

## Notes

- Only 1 of 4 assertions is discriminative here: the planning-ready guardrail in eval 2.
- Issue id, gh command presence, and gh error text assertions pass in all runs and provide low separation.
- with_skill is quality-stable (pass rate stddev 0.0) while old_skill has variance (stddev 0.1443).
- with_skill is also cheaper on token proxy (456.0 vs 550.7 mean, about 17.2% lower).
- Reported runs_per_configuration is 3, but each config has one run per eval; variance reflects cross-eval spread.
