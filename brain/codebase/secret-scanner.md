# Secret scanner limits and evidence

- Pending candidate scanning retains an 8 MiB total-byte budget (`8388608`). Count each unique source/path candidate, including conflict index stages.
- Repository enumeration and content acquisition are separate; worktree content may change during capture. Do not claim one atomic repository snapshot.
- Pinned index object IDs and verified private spool replay protect the content they actually captured, not every mutable repository state.
- Incomplete scans must never be described as clean. Publication/repository capture contracts differ from ordinary pending-file scans.
- `hooks-diagnostics-v1` is a strict deny-only diagnostic route; it is not a scan-bypass mechanism.
- Historical incidents on 2026-10-15 measured 8,403,665 and 9,264,664 bytes against the 8,388,608-byte cap. Exact candidate inventories and installed versions were not retained, so these are not current reproductions.
- Investigate recovery and capacity before changing budgets; preserve failed observations and capture limits.

Evidence checked 2026-10-20: [limits](../../hooks/runtime/scan_types.py), [merge fixtures](../../scripts/test-scan-secrets-merge.py), [diagnostic recovery](../../scripts/test-hook-diagnostic-recovery.py). Recheck when enumeration, capture, locking, or limits change. Follow-up: [todos](../todos.md).
