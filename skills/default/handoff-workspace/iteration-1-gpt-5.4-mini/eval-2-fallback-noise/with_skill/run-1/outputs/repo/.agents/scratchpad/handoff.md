Goal: finish sync-retry debugging without losing the failing integration signal.

Status:
- Repo copied to outputs/repo.
- Evidence lives in `session_notes.md`, `logs/retry.log`, `diffs/patch.diff`, `src/sync_retry.py`, and `tests/test_sync_retry.py`.
- Current patch is tiny: `should_retry(attempt, max_attempts)` now returns `attempt < max_attempts`.

Next focus:
- Start with `tests/test_sync_retry.py` and reproduce the failure before changing code.

Next step:
- Run the focused integration test first, then inspect `src/sync_retry.py` only if it still fails.

Constraints:
- Write future handoff notes under `.agents/scratchpad/` only.
- Reference `logs/retry.log` and `diffs/patch.diff` by path, not by pasting their contents.
- Keep secret values and raw stack frames out of the handoff.
