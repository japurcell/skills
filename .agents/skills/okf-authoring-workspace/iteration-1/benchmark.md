# okf-authoring benchmark

- Executor model: `gpt-5.6-luna`
- Analyzer: `deterministic grade_benchmark.py`
- Runs: one per evaluation and configuration (16 total)
- Validation: grader-owned fixture copy, scoped diff, and real `scripts/lint-okf.py` evidence

| Configuration | Mean eval pass rate | Expectations |
| --- | ---: | ---: |
| `with_skill` | 100.0% | 72/72 (100.0%) |
| `without_skill` | 71.5% | 52/72 (72.2%) |

Duration telemetry was observed for 5/16 runs and token telemetry for 3/16 runs. Time and token comparisons are omitted because coverage is incomplete.

See `execution-manifest.json` for per-run model routing evidence and `review.html` for human output review.
