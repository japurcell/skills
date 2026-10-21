## Goal
- Finish payment retry rollout.

## Status
- Retry cap landed in `src/payment_retry.py`.
- Unit test coverage exists in `tests/test_payment_retry.py`.
- Benchmark notes in `reports/benchmark.txt` show p95 fell from 480ms to 310ms.

## Remaining
- Wire retry metrics.
- Update rollout docs.

## Next focus
- Retry metrics and docs.

## Exact next step
- Add retry metric emission in the payment retry flow, then update rollout docs to describe the cap and metrics.

## Relevant files
- `src/payment_retry.py` — current retry logic.
- `tests/test_payment_retry.py` — cap coverage.
- `reports/benchmark.txt` — latest performance note.
- `session_notes.md` — concise state summary.
