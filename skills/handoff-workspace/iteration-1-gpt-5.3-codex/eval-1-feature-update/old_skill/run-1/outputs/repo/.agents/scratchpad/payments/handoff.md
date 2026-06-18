## Goal
- Finish payment retry rollout.

## Status
- **Done:** retry cap landed in `src/payment_retry.py`; cap behavior covered in `tests/test_payment_retry.py`.
- **In progress:** no retry metrics instrumentation yet.
- **Remaining:** add retry metrics and update rollout docs.

## Next focus
- Retry metrics and docs.

## Next step
- Add retry metrics emission in `src/payment_retry.py`, then document the metric names and rollout notes in docs based on `session_notes.md` and `reports/benchmark.txt`.

## Relevant artifacts
- `session_notes.md` — confirms remaining work is retry metrics + rollout docs.
- `reports/benchmark.txt` — benchmark context for docs (`p95 fell 480ms -> 310ms`, no new retry unit test failures).
- `src/payment_retry.py` — current retry cap implementation (`next_delay`).
- `tests/test_payment_retry.py` — existing cap test to extend after metrics wiring.
