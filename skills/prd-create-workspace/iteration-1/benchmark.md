# Skill Benchmark: prd-create

**Model**: gpt-5.5
**Date**: 2026-04-27T22:36:01Z
**Evals**: 1, 2, 3 (1 runs each per configuration)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 100% ± 0% | 0% ± 0% | +1.00 |
| Time | 653.7s ± 102.5s | 76.3s ± 15.2s | +577.3s |
| Tokens | 51026 ± 3773 | 12871 ± 2267 | +38155 |

## Notes

- Offline benchmark mode intentionally blocked real GitHub issue creation; runs were graded on saved issue title/body plus intended gh issue create command.
- The with-skill runs consistently produced codebase exploration summaries, targeted official-source research, sequential interview logs with recommendations, PRD issue bodies, and filing commands.
- The without-skill baselines generally produced PRD bodies but skipped parallel code exploration, official-source research, and dependency-aware interview logging, causing all benchmark assertions to fail.
- Timing and token-like counts favor the baseline because it did substantially less work; the added cost is expected for the evidence-gathering and interview workflow required by prd-create.
- Only one run per eval/configuration was captured, so variance and flakiness are not measured in this iteration.
