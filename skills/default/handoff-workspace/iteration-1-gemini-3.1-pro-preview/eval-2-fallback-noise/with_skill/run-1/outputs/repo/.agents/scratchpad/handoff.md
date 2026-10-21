# Handoff: Sync Retry Debugging

*Note: User requested writing to `docs/handoff.md`, but handoff rules require placing it under `.agents/scratchpad/`.*

## Goal
Fix sync retry behavior without losing the failing integration signal.

## Status
- Inspected `src/sync_retry.py`
- Identified failing integration test

## Next Focus
Failing integration test

## Next Step
Start with `tests/test_sync_retry.py` to make retry stop swallowing vendor timeouts, then rerun the focused integration test.

## Relevant files/artifacts
- `src/sync_retry.py` - Target implementation
- `tests/test_sync_retry.py` - Integration test to start with
- `logs/retry.log` - Shows vendor timeout while retrying sync request
- `diffs/patch.diff` - Recent retry limit patch
