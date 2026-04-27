# Skill Benchmark: coding-task-workflow

**Model**: <model-name>
**Date**: 2026-04-27T17:22:39Z
**Evals**: 0, 1, 2, 3, 4, 5, 6, 7 (1 runs each per configuration)

## Summary

| Metric | With Skill | Z Old Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 100% ± 0% | 72% ± 36% | +0.28 |
| Time | 83.8s ± 22.1s | 81.1s ± 35.1s | +2.6s |
| Tokens | 752 ± 462 | 610 ± 234 | +142 |

## Notes

- Legacy rule-preservation evals 0-3 stayed green for both versions, so the rewrite preserved the existing hard-stop, issue-authority, sub-issue-linking, and commit-shape behavior.
- The revised skill cleanly passes all new GitHub-native evals 4-7, while the old snapshot still answers in terms of local workflow artifacts such as 00-intake.md, 02-exploration/*, 05-plan.md, 06-task-graph.yaml, 07-implementation-log.md, and .coding-workflow/work/<slug>/.
- Performance overhead is modest: the revised skill uses slightly more tokens and time because it now explains the GitHub-native artifact hierarchy explicitly, but the pass-rate gain is much larger than the cost.
