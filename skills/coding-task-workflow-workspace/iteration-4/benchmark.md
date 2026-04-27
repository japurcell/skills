# Skill Benchmark: coding-task-workflow

**Model**: claude-haiku-4.5
**Evals**: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 (1 run each per configuration)

## Summary

| Metric | With Skill | Old Skill | Delta |
|--------|------------|-----------|-------|
| Pass Rate | 100% ± 0% | 100% ± 0% | +0.00 |
| Time | 72.4s ± 13.9s | 71.8s ± 20.9s | +0.6s |
| Output chars proxy | 5735 ± 3982 | 6451 ± 4159 | -715 |

## Notes

- The task runtime exposed elapsed duration but not total token counts in read_agent output; benchmark token values fall back to output character counts, not actual model tokens.
- Current skill SKILL.md size changed from 888 to 791 words and from 6,353 to 5,636 bytes versus HEAD baseline.
