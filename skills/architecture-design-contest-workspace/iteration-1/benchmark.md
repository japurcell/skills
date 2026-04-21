# Skill Benchmark: architecture-design-contest

**Model**: <model-name>
**Date**: 2026-04-21T16:13:55Z
**Evals**: 0, 1, 2, 3, 4, 5 (1 runs each per configuration)

## Summary

| Metric | With Skill | Old Skill | Delta |
|--------|------------|-----------|-------|
| Pass Rate | 89% ± 12% | 82% ± 15% | +0.07 |
| Time | 815.8s ± 381.9s | 843.7s ± 406.7s | -27.8s |
| Tokens | 11256 ± 1459 | 10727 ± 2625 | +530 |

## Notes

- with_skill improves mean pass rate from 82.5% to 89.2% (+6.7 percentage points).
- with_skill wins outright on eval 3 and eval 5, and ties the baseline on evals 0, 1, 2, and 4.
- with_skill is slightly faster on average (815.8s vs 843.7s, 27.8s faster) but uses modestly more output tokens/chars on average (+530).
- No measured eval regressed versus the baseline.
