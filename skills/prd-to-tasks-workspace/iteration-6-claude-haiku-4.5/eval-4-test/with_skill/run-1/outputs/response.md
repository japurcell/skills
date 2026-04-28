## New parent tracker issue planned

When creating this for real, use a placeholder such as #7001.

## Proposed vertical-slice breakdown

1. **Title**: Persist webhook retry attempts to database
   **Type**: AFK
   **Execution wave**: W1
   **Blocked by**: None
   **User stories covered**: Store retry history for failed deliveries

2. **Title**: Expose internal admin API to replay failed deliveries
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Persist webhook retry attempts to database
   **User stories covered**: Admins can manually replay failed webhook deliveries

3. **Title**: Emit retry outcome metrics to logs
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Persist webhook retry attempts to database
   **User stories covered**: Retry success/failure metrics are logged and queryable

## Child issue drafts

### Child 1: Persist webhook retry attempts to database

## Parent

#<parent-issue-number>

## What to build

When a webhook delivery fails, persist the attempt (timestamp, failure reason, retry count) to the database. This enables replay, history, and outcome tracking.

## Type

AFK

## Acceptance criteria

- [ ] Failed webhook attempts are persisted with metadata
- [ ] Retry count is incremented on each attempt
- [ ] Failure reason is captured and stored
- [ ] Retry history can be queried by webhook ID

## Verification

- [ ] Tests pass: `npm run test -- webhookRetry.persistence.test.ts`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Database contains retry records for failed webhook deliveries
- [ ] Manual check: Trigger a failed webhook and verify retry row in database

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers

## User stories covered

Store retry history for failed deliveries

## Files likely touched

- `src/db/migrations/webhook_retries_table.sql`
- `src/db/models/WebhookRetry.ts`
- `src/workers/webhookWorker.ts`
- `tests/db/models/WebhookRetry.test.ts`

## Estimated scope

Medium: 3-5 files

### Child 2: Expose internal admin API to replay failed deliveries

## Parent

#<parent-issue-number>

## What to build

Internal admin API endpoint that allows replay of a specific failed webhook delivery. Endpoint should accept delivery ID and trigger an immediate retry.

## Type

AFK

## Acceptance criteria

- [ ] POST /admin/webhooks/retry/:id endpoint exists
- [ ] Endpoint triggers immediate replay
- [ ] Response includes retry status
- [ ] Only accessible internally (no external auth checks needed)

## Verification

- [ ] Tests pass: `npm run test -- webhookRetry.api.test.ts`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Call replay API and verify webhook is retried immediately

## Blocked by

- Blocked by #<child-1-issue-number>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<parent-issue-number>'s direct child issue for webhook retry persistence is closed

## User stories covered

Admins can manually replay failed webhook deliveries

## Files likely touched

- `src/api/admin/webhookRetry.ts`
- `src/handlers/webhookRetry.ts`
- `tests/api/admin/webhookRetry.test.ts`

## Estimated scope

Small: 1-2 files

### Child 3: Emit retry outcome metrics to logs

## Parent

#<parent-issue-number>

## What to build

Log structured metrics when webhook retries complete (success/failure, attempt count, latency). These logs should be queryable for monitoring and alerting.

## Type

AFK

## Acceptance criteria

- [ ] Retry outcome logged on each attempt (success/failure)
- [ ] Logs include attempt count and latency
- [ ] Log format is structured (JSON) for querying
- [ ] Metrics include delivery ID and webhook type

## Verification

- [ ] Tests pass: `npm run test -- webhookRetry.metrics.test.ts`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Query logs and verify retry metrics appear

## Blocked by

- Blocked by #<child-1-issue-number>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<parent-issue-number>'s direct child issue for webhook retry persistence is closed

## User stories covered

Retry success/failure metrics are logged and queryable

## Files likely touched

- `src/workers/webhookWorker.ts`
- `src/services/loggingService.ts`
- `tests/workers/webhookWorker.test.ts`

## Estimated scope

Small: 1-2 files

---

## Summary

Created task graph for webhook retry operations feature.

Parent: #<parent-issue-number> (placeholder - new)

Child issues:

1. #<child-1> Persist webhook retry attempts to database - W1 - AFK - blocked by none
2. #<child-1> Expose internal admin API to replay failed deliveries - W2 - AFK - blocked by #<child-2>
3. #<child-1> Emit retry outcome metrics to logs - W2 - AFK - blocked by #<child-2>

How to grab work:

- Open parent #<parent-issue-number> and inspect its direct subissues.
- Start with W1 (persistence) which has no blockers.
- After W1 is closed, pick any W2 issue (replay API or metrics logging) to work in parallel.

Notes:

- Focuses on backend-only work: API handlers, worker processes, persistence layer, and logging
- No frontend or UI work is included in this phase
- Retry persistence (W1) is the foundation for both admin replay and metrics logging (W2)
- Replay API and metrics logging can proceed in parallel once persistence is complete
- All verification uses backend-appropriate checks: targeted tests, API calls, database queries, and log inspection
