**Prompt:**
I have a backend-only PRD for webhook retry operations: when a delivery fails, the service should persist retry attempts, expose an internal admin API to replay a failed delivery, and emit retry outcome metrics to logs. There is no end-user or admin UI in this phase; the likely work is in API handlers, background workers, and persistence. Please break this into grabbable GitHub issues.

**Transcript Bullets:**
- User provided a backend-only PRD for webhook retry operations
- No UI work; focus is on API handlers, background workers, and persistence
- Parent tracker issue is needed since PRD is not in an existing issue
- Three vertical slices identified: persistence, replay API, and metrics
- Each child issue is AFK and in a separate execution wave
- Each child issue includes acceptance criteria, verification, and likely files
- Draft-only response; no GitHub mutations performed
- Output includes parent tracker, child issues, attachment commands, and summary
