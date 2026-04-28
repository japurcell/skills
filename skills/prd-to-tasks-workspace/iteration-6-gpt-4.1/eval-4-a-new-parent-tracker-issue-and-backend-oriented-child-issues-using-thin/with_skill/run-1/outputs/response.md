# Epic: Webhook Retry Operations (Backend)

## Overview
Implement backend support for webhook retry operations. When a delivery fails, the system should:
- Persist retry attempts
- Expose an internal admin API to replay failed deliveries
- Emit retry outcome metrics to logs

No end-user or admin UI is included in this phase. Work is limited to API handlers, background workers, and persistence.

## Child Issues

- [ ] **Persist webhook retry attempts**
  - Design and implement a persistence layer to record each webhook delivery attempt, including metadata (timestamp, status, error, etc.).
  - Ensure failed attempts are stored for later replay and analysis.

- [ ] **Implement background worker for retries**
  - Create a background worker that processes failed webhook deliveries and schedules retries according to a defined policy (e.g., exponential backoff).
  - Integrate with the persistence layer to fetch and update retry attempts.

- [ ] **Expose internal admin API to replay failed deliveries**
  - Design and implement an internal-only API endpoint to trigger a replay of a specific failed webhook delivery by ID.
  - Ensure proper authentication/authorization for internal use.

- [ ] **Emit retry outcome metrics to logs**
  - Add structured logging for each retry attempt, including outcome (success/failure), number of attempts, and error details.
  - Ensure logs are suitable for downstream metrics/monitoring systems.

- [ ] **Document retry operations and API**
  - Write internal documentation covering the retry mechanism, API usage, and logging/metrics format.

---

*This issue is a tracker. Child issues should be created for each task above. Use placeholders for issue numbers if not yet created.*
