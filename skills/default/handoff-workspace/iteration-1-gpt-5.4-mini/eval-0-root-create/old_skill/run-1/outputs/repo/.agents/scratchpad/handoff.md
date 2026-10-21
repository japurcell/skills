# Handoff

**Goal:** finish auth refresh retry backoff without carrying forward any sensitive token text.

**Current status**
- `src/auth_refresh.py` still returns a flat retry schedule: `build_retry_schedule()` -> `[0.5, 0.5, 0.5]`.
- `tests/test_auth_refresh.py::test_refresh_retries_backoff` expects `[0.5, 1.0, 2.0]`.
- `logs/test-failure.txt` captures the exact mismatch.
- `session_notes.md` already notes the work-in-progress and explicitly says to keep the live token out of notes.

**Relevant files**
- `src/auth_refresh.py` — code to update.
- `tests/test_auth_refresh.py` — failing expectation to satisfy.
- `logs/test-failure.txt` — baseline failure output.
- `plans/refresh-plan.md` — intended retry plan.

**Next step**
- Update `build_retry_schedule()` so the retry backoff matches the test, then rerun `python3 -m pytest tests/test_auth_refresh.py -q`.

**Constraints**
- Do not copy any live token text into notes or summaries.
- Keep the fix narrow to auth refresh retry behavior.

**Suggested skills**
- `tdd` — make the retry test pass with the smallest behavior change.
