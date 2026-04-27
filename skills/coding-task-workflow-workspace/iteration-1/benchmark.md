# Skill Benchmark: coding-task-workflow

**Model**: <model-name>
**Date**: 2026-04-27T15:25:04Z
**Evals**: 0, 1, 2, 3 (1 runs each per configuration)

## Summary

| Metric | With Skill | Z Old Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 100% ± 0% | 100% ± 0% | +0.00 |
| Time | 146.5s ± 28.3s | 146.5s ± 28.3s | +0.0s |
| Tokens | 1054 ± 1016 | 774 ± 549 | +281 |

## Notes

- All four evals passed 100% in both configurations, so the current eval set does not distinguish the leaner SKILL.md from the baseline version.
- The existing evals are rule-adherence checks for Gate E resume, ISSUE authority, sub-issue linking, and commit trailer formatting; they verify that the rewrite preserved behavior but do not measure context-efficiency gains directly.
- Timing was captured at batch granularity because per-run duration_ms was not exposed in the task notifications, so time metrics are approximate and most useful for rough comparison only.
