## Goal
- Finish auth refresh retry backoff and stabilize the refresh retry test.

## Status
- **Done:** traced retry flow in `src/auth_refresh.py`; ran focused test (`python3 -m pytest tests/test_auth_refresh.py -q`); confirmed failure details in `logs/test-failure.txt`.
- **In progress:** choosing final retry schedule behavior in `build_retry_schedule`.
- **Remaining:** implement schedule update and re-run focused test.

## Next focus
- Retry backoff behavior in auth refresh.

## Next step
- Update `src/auth_refresh.py` so `build_retry_schedule()` produces the expected backoff progression for `tests/test_auth_refresh.py::test_refresh_retries_backoff`, then run `python3 -m pytest tests/test_auth_refresh.py -q`.

## Decisions / constraints
- Keep first retry at `0.5s`.
- Current plan in `plans/refresh-plan.md` says to add bounded jitter only after first failure.
- Do not record the flaky live token value in notes or handoff content.

## Relevant files / artifacts
- `src/auth_refresh.py` — current implementation returns constant retry delays.
- `tests/test_auth_refresh.py` — expected retry schedule assertion.
- `logs/test-failure.txt` — exact expected vs actual failure output.
- `plans/refresh-plan.md` — intended backoff/jitter direction.
- `session_notes.md` — prior progress notes (contains sensitive token that must stay redacted in future notes).

## Errors / blockers
- `FAILED tests/test_auth_refresh.py::test_refresh_retries_backoff`
- Expected `[0.5, 1.0, 2.0]`, actual `[0.5, 0.5, 0.5]`.
