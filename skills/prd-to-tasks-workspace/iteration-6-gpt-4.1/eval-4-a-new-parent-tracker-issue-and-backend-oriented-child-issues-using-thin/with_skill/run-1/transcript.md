**Prompt:**
I have a backend-only PRD for webhook retry operations: when a delivery fails, the service should persist retry attempts, expose an internal admin API to replay a failed delivery, and emit retry outcome metrics to logs. There is no end-user or admin UI in this phase; the likely work is in API handlers, background workers, and persistence. Please break this into grabbable GitHub issues.

**Skill Used:** prd-to-tasks

**Dry-run Transcript:**
- Read PRD and extracted requirements: persist retry attempts, internal admin API for replay, emit retry metrics to logs, backend only.
- Identified no UI or external-facing work; focus is on API, background jobs, and persistence.
- Broke work into thin, grabbable issues:
  1. Persist webhook retry attempts
  2. Implement background worker for retries
  3. Expose internal admin API to replay failed deliveries
  4. Emit retry outcome metrics to logs
  5. Document retry operations and API
- Used skill template for tracker and child issues, with placeholders for issue numbers.
- Output written to response.md as a tracker issue with checklists and descriptions.
