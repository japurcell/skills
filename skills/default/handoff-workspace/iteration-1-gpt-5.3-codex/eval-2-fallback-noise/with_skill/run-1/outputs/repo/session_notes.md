Goal: fix sync retry behavior without losing the failing integration signal.

Done:
- inspected src/sync_retry.py
- identified failing integration test

Remaining:
- make retry stop swallowing vendor timeouts
- rerun the focused integration test first

Requested next step:
- start with tests/test_sync_retry.py
