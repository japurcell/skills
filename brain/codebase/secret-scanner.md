# Secret scanner limits and evidence

- The internal pending-candidate default retains an 8 MiB total-byte budget (`8388608`); current explicit checkpoint/publication commands select different profiles through [scan budgets](../../hooks/runtime/scan_budget.py) and [their public contract](../../README.md#explicit-secret-checks-and-git-gates). Do not apply the legacy default to every command. Count each unique source/path candidate, including distinct conflict index stages even when the visible worktree file is small. Smaller capture batches do not fix aggregate capacity; candidate accounting remains separate from framing and replay.
- Repository enumeration and content acquisition are separate; worktree content may change during capture. Do not claim one atomic repository snapshot.
- Pinned index object IDs and verified private spool replay protect the content they actually captured, not every mutable repository state.
- Incomplete scans must never be described as clean, including skipped or truncated supported content. Publication/repository capture contracts differ from ordinary pending-file scans. For binary handling, document actual coverage and limits and test textual credential material; byte inspection does not establish OCR or identical scanning of every binary format.
- Retain earlier credential findings when later capture, read, or budget work fails, alongside the incomplete result; a later failure does not erase findings already established.
- Keep finite byte, snapshot, time, capture, finding, and audit-output bounds. Explicit blocking checks must deny incomplete inspection; completed earlier batches do not certify unchecked versions.
- For legacy scanner registrations only, `hooks-diagnostics-v1` is a strict deny-only diagnostic route. Current installations use standalone diagnostics; neither route grants a scan bypass.
- Historical incidents on 2026-10-15 measured 8,403,665 and 9,264,664 bytes against the 8,388,608-byte cap. Exact candidate inventories and installed versions were not retained, so these are not current reproductions.
- Before authorized capacity work, define supported aggregate workload, capture disk/memory, timeout, and latency together. A first rejected reservation is not a full inventory or sufficient capacity target. Historical incidents authorize neither a budget increase nor a new setting.

For a scanner incident, installed/source mismatch, or blocked diagnostic path, read [scanner recovery](secret-scanner-recovery.md). For a future authorized limit change, read [security acceptance](security-testing.md#acceptance-evidence) before designing the fix.

Evidence checked 2026-10-20: [limits](../../hooks/runtime/scan_types.py), [merge fixtures](../../scripts/test-scan-secrets-merge.py), [diagnostic recovery](../../scripts/test-hook-diagnostic-recovery.py). Recheck when enumeration, capture, locking, or limits change. Follow-up: [todos](../todos.md).
