## Goal
- Fix sync retry behavior without losing the failing integration signal.

## Status
- **Done:** inspected `src/sync_retry.py`; identified retry logic bug and failing test target.
- **In progress:** preserving failure-first workflow for retry debugging.
- **Remaining:** change retry behavior so vendor timeout is not swallowed; rerun failing integration test first.

## Next focus
- Sync retry limit handling in `src/sync_retry.py`.

## Next step
- Run the failing integration test in `tests/test_sync_retry.py` first, then update `should_retry` to stop at `attempt >= max_attempts`.

## Decisions and constraints
- User asked for `docs/handoff.md`, but handoff path must remain under `.agents/scratchpad/`; wrote fallback root handoff.
- Keep artifact references by path; do not inline large logs/diffs.
- Sensitive auth/token and traceback details must stay redacted.

## Relevant files and artifacts
- `session_notes.md` - current status and requested next step.
- `src/sync_retry.py` - current buggy logic returns `True` unconditionally.
- `tests/test_sync_retry.py` - failing retry-limit behavior check.
- `logs/retry.log` - vendor-timeout failure context (reference only).
- `diffs/patch.diff` - candidate fix changing retry condition (reference only).

## Durable learnings
- Start retry debugging from the failing integration test to preserve signal before code edits.
