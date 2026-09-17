---
type: Known Issue
description: Hook observability and trace-store failures; load only for emitters, SQLite traces, transcript finalization, logging, rotation, or maintenance
---

# Hook Observability - Known Issues

## Direct helper execution breaks relative imports

Run maintenance as `python3 -m helpers.observability --maintenance` with `cwd` at the runtime scripts directory. Direct file execution has no package context.

## SQLite side files can leak permissions

WAL and SHM files can be recreated with permissive modes. Reapply `0o600` after connection and suppress transient permission errors so observability remains fail open.

## Cyclical payloads can recurse without bound

Track active container identities with `id()`. Replace cycles with a sentinel instead of recursing.

## File deletion inside transactions starves writers

Read paths and close the transaction, delete files outside SQLite, then open a separate write transaction for row deletion and incremental vacuum.

## POSIX locking imports crash Windows

Import `fcntl` inside locking helpers. On `ImportError`, use the supported unlocked fallback instead of failing module import.

## Finalization state transitions can discard transcripts

Transition `finalizing` to `sealing` inside `_finalize_session()` and require one successful guarded update before merge and cleanup.

## Stale finalization needs resumable maintenance

Maintenance and `_finalize_session()` must both accept stale `finalizing` and `sealing` sessions. If either status filter omits `sealing`, recovery returns before transcript merge.

## Concurrent finalizers need one owner

Acquire a per-session filesystem lock before state transition, merge, and cleanup. Keep the lock under the runtime log directory.

## Parent session IDs can escape registry paths

Sanitize `parent_session_id` with `[^A-Za-z0-9_-]` immediately after extraction and before database or path use.

## Atomic-write failures can leak temporary files

Wrap chunk and final transcript writes in `try...finally`; remove the `.tmp` path in `finally` when it still exists.

## Progress messages must not complete captures

Ignore payloads with `type: progress` in `complete_hook_capture`. Finalize capture only for the actual hook result.

## Empty Gemini probe logs can hide fallback writes

An empty file selected through `GEMINI_OBSERVABILITY_LOG_PATH` does not by itself prove that Gemini skipped a hook. If the CLI does not pass that variable to the hook process, the emitter falls back to `$HOME/.gemini/hooks/logs/observability.ndjson`. Check that default log, then invoke the installed emitter directly with the override before classifying the failure as event dispatch, environment propagation, or emitter failure.
