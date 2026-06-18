## Goal
Finish payment retry rollout.

## Status
- **Done:**
  - Landed retry cap logic in `src/payment_retry.py`.
  - Confirmed test coverage for the cap logic in `tests/test_payment_retry.py`.
  - Benchmarked retry latency: p95 fell from 480ms to 310ms.
- **Remaining:**
  - Wire retry metrics.
  - Update rollout docs.

## Next-agent focus
Retry metrics and docs.

## Exact next step
Wire retry metrics.

## Relevant files
- `src/payment_retry.py`: Contains `next_delay` with retry cap logic.
- `tests/test_payment_retry.py`: Tests for the retry cap logic.
- `session_notes.md`: Contains session rollout status.
- `reports/benchmark.txt`: Performance benchmark results showing improved p95.
