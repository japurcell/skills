Goal: fix sync retry behavior without losing the failing integration signal.

Done:
- inspected src/sync_retry.py
- identified failing integration test

Remaining:
- make retry stop swallowing vendor timeouts
- rerun the focused integration test first

Requested next step:
- start with `tests/test_sync_retry.py:5`

Important details:
- likely bug is `src/sync_retry.py:2`, which returns `True` even when `attempt` hits `max_attempts`
- keep noisy artifacts referenced as `logs/retry.log` and `diffs/patch.diff`, not pasted
- verification state: focused integration test still needs rerun after the retry-limit fix
