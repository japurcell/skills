# Skill Benchmark: skillify

**Model**: <model-name>
**Date**: 2026-04-07T19:10:58Z
**Evals**: 0, 1, 2 (3 runs each per configuration)

## Summary

| Metric    | With Skill  | Without Skill | Delta |
| --------- | ----------- | ------------- | ----- |
| Pass Rate | 100% ± 0%   | 13% ± 10%     | +0.87 |
| Time      | 0.0s ± 0.0s | 0.0s ± 0.0s   | +0.0s |
| Tokens    | 5660 ± 789  | 4440 ± 1251   | +1220 |

## Notes

- with_skill passed all 45 structural assertions across three runs for each eval, while without_skill passed 6 of 45 and averages 13% ± 10% pass rate.
- The previously weak companion-note checks have been replaced with frontmatter and workflow assertions, and those new checks cleanly separate with_skill from baseline across evals 0, 1, and 2.
- The tightened eval-2 task-agent assertion remains discriminative across all three runs: every with_skill run uses an explicit **Execution**: Task agent annotation and every baseline run fails it.
- The eval-2 allowed-tools check is more stable when graded against the benchmark-analysis core tool mix instead of an exact tool list; one successful with_skill variant used `Task` instead of `Edit` while preserving the intended workflow.
- Per-step Success criteria remains the strongest suite-wide signal: every with_skill run satisfied it and every baseline run failed it.
- Timing is still non-informative in this environment because subagent duration and token notifications were unavailable; time remains zeroed and token values are directional proxies from output size.
