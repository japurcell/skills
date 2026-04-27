# Skill Benchmark: coding-task-workflow

**Model**: claude-haiku-4.5
**Date**: 2026-04-27T19:33:44Z
**Evals**: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 (1 run each per configuration)

## Summary

| Metric | With Skill | Old Skill | Delta |
|--------|------------|-----------|-------|
| Pass Rate | 100% ± 0% | 92% ± 19% | +0.08 |
| Time | 112.3s ± 27.3s | 112.3s ± 24.0s | +0.0s |
| Output chars proxy | 15374 ± 5605 | 15902 ± 5299 | -528 |

## Notes

- New evals 10 and 11 discriminate the requested behavior: the updated skill passes mandatory Phase 8/10 subagent delegation, while the old snapshot preserves direct primary-agent execution for sequential implementation and verification work.
- Timing uses wall-clock elapsed seconds captured from background-agent runs; token values use output character counts as a proxy because total token counts were not exposed by read_agent output.
- Existing evals 0-9 remained passing for both configurations, so the change did not regress the GitHub-native workflow rules already covered by the suite.
