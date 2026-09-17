---
type: Agent Instruction
description: Hook observability and trace-store rules; load only when changing emitters, SQLite traces, transcript finalization, logging, or maintenance
---

# Hook Observability Rules

Load this file only for observability, trace-store, transcript, log-rotation, or maintenance work. General hook contracts remain in [hooks.md](hooks.md).

- Keep `send-event.py` registered for every supported Copilot and Gemini event, including Gemini lifecycle events with no other operational behavior.
- `send-event.py` and the Copilot/Gemini observability helpers are generated from canonical `hooks/families/` sources. Regenerate with `python3 scripts/generate-hooks.py --write` and require a clean `--check`; their installed copies remain runtime-local and self-contained.
- Create primary and shadow audit files with `0o600` at descriptor creation. Create shadow parents first and keep paired writes inside one lock section.
- Treat WAL-journaled `observability_v1.db` as trace source of truth. Apply write-heavy WAL and incremental-vacuum PRAGMAs only during schema initialization or recovery; keep connection setup lightweight.
- Secure SQLite, WAL, SHM, registry, and transcript files with `0o600`; secure `registries/subagents` with `0o700`.
- Guard POSIX-only locking imports. Reuse connections in polling and maintenance helpers; poll completed spans at 100 ms.
- Sanitize `parent_session_id` with `[^A-Za-z0-9_-]` before storing or using it in paths.
- Track visited containers while shrinking payloads. Check `max_bytes // 4` before UTF-8 encoding; preserve the 512 KiB payload and 10 KiB string limits while retaining smaller fields.
- Set session `start_time_ms` from the actual `session_start` event timestamp.
- Clean atomic `.tmp` writes in `finally`. Append late trace chunks to saved JSONL when active transcript directories are already finalized.
- Finalize through explicit `finalizing` and `sealing` states under a per-session filesystem lock. Maintenance finalization must abandon outstanding spans without polling and set `has_errors` only when it abandoned at least one span.
- Run detached maintenance at most once per 24 hours. Touch its sentinel only in the started child. Delete files outside SQLite transactions, then remove rows and compact in a separate write transaction.
- Scavenge active directories and registries only when older than 24 hours and terminal or absent from the database.
- Launch maintenance as `python3 -m helpers.observability --maintenance` with `cwd` at the runtime scripts directory.
- On Windows, bypass `os.kill(pid, 0)` for the current PID.
- Rotation must fail open without clearing active logs. Always prune stale backups, honor `GEMINI_` or `COPILOT_OBSERVABILITY_LOG_*` variables before generic `OBSERVABILITY_LOG_*` variables, default to 10 MB and 100 backups, allow zero-byte rotation disablement, and pre-scan backup directories. Do not clamp user maxima.

For architecture decisions, read [hooks ADRs](../memory/adrs/hooks.md). For failures and recovery, read [observability known issues](../memory/known-issues/hooks-observability.md). For tests, read [observability hook testing](../memory/testing/hooks-observability.md).
