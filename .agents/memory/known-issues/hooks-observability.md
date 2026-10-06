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

## Domain log overrides do not isolate observability storage

`AUDIT_LOG` and scanner or guard paths select their own logs; they do not change provider observability NDJSON or its adjacent SQLite database. Keep logging active and run children under a disposable `HOME`.

## Empty Gemini probe logs can hide fallback writes

An empty file selected through `GEMINI_OBSERVABILITY_LOG_PATH` does not by itself prove that Gemini skipped a hook. If the CLI does not pass that variable to the hook process, the emitter falls back to `$HOME/.gemini/hooks/logs/observability.ndjson`. Check that default log, then invoke the installed emitter directly with the override before classifying the failure as event dispatch, environment propagation, or emitter failure.

## Detached maintenance can race test cleanup

A `SessionStart` or terminal hook can launch detached maintenance when a disposable home's maintenance sentinel is absent. The child touches the sentinel at startup, so its creation does not prove that cleanup work has finished; removing the home while maintenance is active can fail with `Directory not empty`. `install_into_temp_home` seeds fresh sentinels for both providers to isolate unrelated fixtures. An intentional launch test removes the relevant sentinel before its event and waits with a bound for a stale active-directory progress marker to be removed by final scavenging before fixture teardown. Scope mocked locking subprocesses to the disposable `HOME`; otherwise they can write a trace database in the real user home.

## Strict warnings expose unowned runtime resources

Structural-corruption recovery formerly leaked the connection when `_connect_db` setup PRAGMAs failed before return. Detached maintenance also discarded a still-running `Popen` handle. Public installed-hook cases now require no `ResourceWarning` while retaining corruption recovery and a nonblocking emitter. Close each failed initialization/recovery connection; create the daemon waiter before spawning, retain its handle and signal the owner after success or failure. The waiter never joins the foreground and may stop at interpreter shutdown; this establishes tested resource ownership, not graceful shutdown or power-loss durability. Close fixture pipe and manifest streams explicitly too.
