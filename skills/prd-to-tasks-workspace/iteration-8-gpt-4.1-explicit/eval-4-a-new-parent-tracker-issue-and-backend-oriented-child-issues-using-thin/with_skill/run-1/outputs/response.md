## Parent tracker draft

### Title
Webhook retry operations: persistence, replay API, and metrics (backend-only)

### Body

## Source

Backend-only PRD for webhook retry operations: when a delivery fails, the service should persist retry attempts, expose an internal admin API to replay a failed delivery, and emit retry outcome metrics to logs. No end-user or admin UI in this phase; work is in API handlers, background workers, and persistence.

## Task graph

- [ ] W1 - Persist webhook retry attempts - AFK - blocked by none
- [ ] W2 - Internal admin API to replay failed delivery - AFK - blocked by #<child-1>
- [ ] W3 - Emit retry outcome metrics to logs - AFK - blocked by #<child-2>

## How to grab work

Work is executed from this issue's direct subissues. Start with any open AFK issue in the lowest-numbered wave whose blockers are all closed. If multiple AFK issues share that wave and do not block one another, they may be worked in parallel. HITL issues require the named human decision or review before implementation.

---

## Child issue draft 1

## Parent

#<parent-issue-number> (placeholder)

## What to build

Implement persistence for webhook retry attempts. When a webhook delivery fails, record the attempt, including relevant metadata (timestamp, payload, error, etc.), in persistent storage for later replay and analysis.

## Type

AFK

## Acceptance criteria

- [ ] Failed webhook deliveries are recorded with all relevant metadata
- [ ] Data is queryable for replay and analysis
- [ ] Persistence is robust to service restarts

## Verification

- [ ] Tests pass: `targeted backend test command`
- [ ] Build succeeds: `relevant build command, if known and applicable`
- [ ] Manual check: verify persisted retry attempts in storage after simulated failures

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers, or every issue listed in `Blocked by` is closed

## User stories covered

Not explicit in source

## Files likely touched

- `src/webhooks/persistence.py`
- `tests/webhooks/test_persistence.py`

## Estimated scope

Medium: 3-5 files

---

## Child issue draft 2

## Parent

#<parent-issue-number> (placeholder)

## What to build

Expose an internal admin API endpoint to replay a failed webhook delivery by ID. The endpoint should trigger a retry using the persisted data, updating the retry record with the outcome.

## Type

AFK

## Acceptance criteria

- [ ] Internal API endpoint exists to trigger replay by retry ID
- [ ] Replay uses persisted data and updates the record with the new outcome
- [ ] Only accessible to authorized internal users/services

## Verification

- [ ] Tests pass: `targeted API/worker test command`
- [ ] Build succeeds: `relevant build command, if known and applicable`
- [ ] Manual check: replay a failed delivery via API and verify outcome in persistence

## Blocked by

- Blocked by #<child-1>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: every issue listed in `Blocked by` is closed

## User stories covered

Not explicit in source

## Files likely touched

- `src/webhooks/admin_api.py`
- `src/webhooks/persistence.py`
- `tests/webhooks/test_admin_api.py`

## Estimated scope

Medium: 3-5 files

---

## Child issue draft 3

## Parent

#<parent-issue-number> (placeholder)

## What to build

Emit retry outcome metrics to logs for each webhook retry attempt, including success/failure, number of attempts, and relevant metadata. Metrics should be structured for easy aggregation and monitoring.

## Type

AFK

## Acceptance criteria

- [ ] Each retry attempt emits a structured log entry with outcome and metadata
- [ ] Metrics are suitable for aggregation and monitoring
- [ ] Logging does not impact retry performance

## Verification

- [ ] Tests pass: `targeted backend test command`
- [ ] Build succeeds: `relevant build command, if known and applicable`
- [ ] Manual check: verify log entries for retry attempts and outcomes

## Blocked by

- Blocked by #<child-2>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W3
- Ready to start when: every issue listed in `Blocked by` is closed

## User stories covered

Not explicit in source

## Files likely touched

- `src/webhooks/metrics.py`
- `src/webhooks/persistence.py`
- `tests/webhooks/test_metrics.py`

## Estimated scope

Medium: 3-5 files

---

## Subissue attachment commands

```bash
# Attach child issues to parent (placeholders)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID_1\"}) { issue { number } }
}"
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID_2\"}) { issue { number } }
}"
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID_3\"}) { issue { number } }
}"
```

---

## Final summary

Created task graph for backend-only webhook retry operations (persistence, replay API, metrics).

Parent: #<parent-issue-number> Webhook retry operations: persistence, replay API, and metrics (placeholder)

Child issues:

1. #<child-1> Persist webhook retry attempts - W1 - AFK - blocked by none
2. #<child-2> Internal admin API to replay failed delivery - W2 - AFK - blocked by #<child-1>
3. #<child-3> Emit retry outcome metrics to logs - W3 - AFK - blocked by #<child-2>

How to grab work:

- Open parent #<parent-issue-number> and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- If the parent issue already existed, read the managed `Task graph` / `How to grab work` section in its body.

Notes:

- All issue numbers and IDs are placeholders; this is a dry-run draft.
- No GitHub mutations have been performed.
