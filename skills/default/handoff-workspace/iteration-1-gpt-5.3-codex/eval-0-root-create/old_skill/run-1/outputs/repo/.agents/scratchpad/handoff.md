## Goal
- Finish auth refresh retry backoff behavior and stabilize the flaky auth refresh test.

## Status
- **Done**
  - Traced retry flow in `src/auth_refresh.py`.
  - Ran focused test for auth refresh retries.
- **In progress**
  - Aligning retry schedule behavior with expectations.
- **Remaining**
  - Implement correct retry backoff in `src/auth_refresh.py`.
  - Re-run `tests/test_auth_refresh.py` and confirm retry test passes.

## Next focus
- Complete auth refresh retry backoff while keeping sensitive token values out of all notes and handoff artifacts.

## Next step
- Update `build_retry_schedule` in `src/auth_refresh.py` so it produces the expected backoff `[0.5, 1.0, 2.0]`, then run `python3 -m pytest tests/test_auth_refresh.py -q`.

## Decisions and constraints
- Do not include live token strings in any notes or handoff text.
- Keep this handoff concise and artifact-referenced (no raw log dumps).

## Relevant files and artifacts
- `src/auth_refresh.py` — current retry schedule implementation.
- `tests/test_auth_refresh.py` — expected backoff assertion.
- `logs/test-failure.txt` — failing output showing expected vs actual schedule.
- `plans/refresh-plan.md` — retry plan notes to reconcile with test expectation.
- `session_notes.md` — current progress summary and redaction requirement.

## Errors/blockers
- `test_refresh_retries_backoff` currently fails because schedule is constant (`[0.5, 0.5, 0.5]`) instead of expected backoff.
- Plan note mentions jitter, but test expects deterministic values; resolve by matching current test contract first.
