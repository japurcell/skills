# Handoff: Sync Retry Debugging

## Goal
Fix sync retry behavior without losing the failing integration signal.

## Current Status
- **Done**: Inspected `src/sync_retry.py` and identified the failing integration test.
- **Remaining**: Make retry stop swallowing vendor timeouts and rerun the focused integration test first.

## Next-Agent Focus
We were debugging sync retries. Next time start with the failing integration test.

## Exact Next Step
Run and investigate `tests/test_sync_retry.py`.

## Relevant Files and Artifacts
- `src/sync_retry.py`: Source file containing retry logic.
- `tests/test_sync_retry.py`: Failing integration test to start with next.
- `session_notes.md`: Contains notes on what was done and what remains.
- `logs/retry.log`: Log file showing vendor timeout. (Sensitive info redacted).
- `diffs/patch.diff`: Current work in progress for `sync_retry.py`.

## Briefing
We are working on fixing the sync retry mechanism to properly handle vendor timeouts instead of swallowing them. The initial investigation of `src/sync_retry.py` is complete, and we have a failing integration test and a patch in progress. Begin by running the failing integration test in `tests/test_sync_retry.py`. Note: A user requested this file be saved to `docs/handoff.md`, but it was placed here according to skill rules.