## Goal
- Finish payment retry rollout.

## Status
- Retry cap landed in `src/payment_retry.py`.
- Cap logic is covered by `tests/test_payment_retry.py`.
- Benchmark notes show p95 dropped from 480ms to 310ms.
- Remaining work: retry metrics and rollout docs.

## Next focus
- Wire retry metrics and update docs for the rollout.

## Next step
- Add retry metrics in `src/payment_retry.py`, extend tests if needed, then update rollout docs to match.

## Relevant artifacts
- `session_notes.md` — current rollout state.
- `reports/benchmark.txt` — benchmark result and test signal.
- `src/payment_retry.py` — retry implementation.
- `tests/test_payment_retry.py` — cap coverage.
