# Handoff: Auth Refresh Retry Backoff

## Goal
Make auth refresh retries deterministic and stop the flaky retry failure.

## Current Status
- **Done**: Traced retry flow in `src/auth_refresh.py`. Ran `python3 -m pytest tests/test_auth_refresh.py -q`.
- **In Progress**: Comparing fixed backoff vs jittered backoff for `build_retry_schedule`.
- **Remaining**: Update retry schedule and rerun the auth refresh test.

## Relevant Artifacts
- `src/auth_refresh.py`: Target file for fix (`build_retry_schedule()`).
- `tests/test_auth_refresh.py`: Test file (`test_refresh_retries_backoff`).
- `logs/test-failure.txt`: Contains error output. Actual is `[0.5, 0.5, 0.5]`, expected `[0.5, 1.0, 2.0]`.
- `plans/refresh-plan.md`: Retry plan (keep first at 0.5s, add bounded jitter, rerun test).

## Next Step
Update `build_retry_schedule` in `src/auth_refresh.py` to implement the backoff logic and rerun `tests/test_auth_refresh.py::test_refresh_retries_backoff`.

## Notes
- Token redacted for security.
