Drafted task graph for admin audit log exports.

Parent: `#<parent-issue-number> Task graph: admin audit log exports`

Child issues:
1. `#<child-1> Filter audit log by actor` - W1 - AFK - blocked by none
2. `#<child-2> Filter audit log by date range` - W1 - AFK - blocked by none
3. `#<child-3> Filter audit log by event type` - W1 - AFK - blocked by none
4. `#<child-4> Export filtered audit logs as CSV` - W2 - AFK - blocked by `#<child-1>`, `#<child-2>`, `#<child-3>`
5. `#<child-5> Show admin-visible audit export failures` - W3 - AFK - blocked by `#<child-4>`

How to grab work:
- Open parent `#<parent-issue-number>` and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- No queue-guide issue is needed in this draft because the source was raw PRD text, so the parent tracker body carries the queue guidance.

Notes:
- Dry run only; commands and issue bodies are drafted below and were not executed.
- File paths, test commands, and build commands remain placeholders because no repository context was provided.

## Parent tracker draft

**Title**: `Task graph: admin audit log exports`

**Body**:

```markdown
## Source

Admins need audit log exports that support filtering by actor, date range, and event type; allow CSV export for compliance; and make export failures visible to admins.

## Task graph

- [ ] W1 - Filter audit log by actor - AFK - blocked by none
- [ ] W1 - Filter audit log by date range - AFK - blocked by none
- [ ] W1 - Filter audit log by event type - AFK - blocked by none
- [ ] W2 - Export filtered audit logs as CSV - AFK - blocked by Filter audit log by actor, Filter audit log by date range, Filter audit log by event type
- [ ] W3 - Show admin-visible audit export failures - AFK - blocked by Export filtered audit logs as CSV

## How to grab work

Work is executed from this issue's direct subissues. Start with any open AFK issue in the lowest-numbered wave whose blockers are all closed. If multiple AFK issues share that wave and do not block one another, they may be worked in parallel. HITL issues require the named human decision or review before implementation.
```

## Child issue drafts

### 1. `Filter audit log by actor`

```markdown
## Parent

#<parent-issue-number>

## What to build

Add an admin audit log filter that narrows results to events performed by a selected actor, and apply that filter consistently through the query path and admin view.

## Type

AFK

## Acceptance criteria

- [ ] Admins can choose an actor filter and see only matching audit log rows.
- [ ] The actor filter persists in the request/query path used to load audit log data.
- [ ] Filtered and unfiltered states are both covered by automated tests.

## Verification

- [ ] Tests pass: `<targeted test command for actor-filter audit log coverage>`
- [ ] Build succeeds: `<repo build command, if applicable>`
- [ ] Manual check: load the audit log, apply an actor filter, and confirm only that actor's events remain visible.

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers, or every issue listed in `Blocked by` is closed
- Parallel rule: if multiple AFK issues are ready in W1, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

- Admin can filter audit logs by actor.

## Files likely touched

- `<admin-audit-log-listing-view>`
- `<admin-audit-log-filter-controls>`
- `<audit-log-query-handler-or-endpoint>`
- `<audit-log-filter-tests>`

## Estimated scope

Medium: 3-5 files
```

### 2. `Filter audit log by date range`

```markdown
## Parent

#<parent-issue-number>

## What to build

Add an admin audit log date-range filter so admins can limit results to a chosen time window and get matching rows from the underlying query path.

## Type

AFK

## Acceptance criteria

- [ ] Admins can enter a start and end date and see only audit log rows inside that range.
- [ ] Invalid or empty date-range input is handled without breaking the audit log view.
- [ ] Automated tests cover the date-range filter behavior.

## Verification

- [ ] Tests pass: `<targeted test command for date-range audit log coverage>`
- [ ] Build succeeds: `<repo build command, if applicable>`
- [ ] Manual check: apply a date range and confirm rows outside the range are excluded.

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers, or every issue listed in `Blocked by` is closed
- Parallel rule: if multiple AFK issues are ready in W1, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

- Admin can filter audit logs by date range.

## Files likely touched

- `<admin-audit-log-listing-view>`
- `<admin-audit-log-filter-controls>`
- `<audit-log-query-handler-or-endpoint>`
- `<audit-log-filter-tests>`

## Estimated scope

Medium: 3-5 files
```

### 3. `Filter audit log by event type`

```markdown
## Parent

#<parent-issue-number>

## What to build

Add an admin audit log event-type filter so admins can narrow results to one or more event categories and get matching data end to end.

## Type

AFK

## Acceptance criteria

- [ ] Admins can select an event type filter and see only matching audit log rows.
- [ ] The selected event type is included in the data-fetch path for audit logs.
- [ ] Automated tests cover event-type filtering behavior.

## Verification

- [ ] Tests pass: `<targeted test command for event-type audit log coverage>`
- [ ] Build succeeds: `<repo build command, if applicable>`
- [ ] Manual check: choose an event type and confirm only matching rows remain visible.

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers, or every issue listed in `Blocked by` is closed
- Parallel rule: if multiple AFK issues are ready in W1, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

- Admin can filter audit logs by event type.

## Files likely touched

- `<admin-audit-log-listing-view>`
- `<admin-audit-log-filter-controls>`
- `<audit-log-query-handler-or-endpoint>`
- `<audit-log-filter-tests>`

## Estimated scope

Medium: 3-5 files
```

### 4. `Export filtered audit logs as CSV`

```markdown
## Parent

#<parent-issue-number>

## What to build

Allow admins to export the currently filtered audit log results as CSV so compliance users can download the exact subset they are reviewing.

## Type

AFK

## Acceptance criteria

- [ ] Admins can trigger a CSV export from the audit log view and the export respects actor, date-range, and event-type filters.
- [ ] The downloaded file is a valid CSV containing the filtered audit log records needed for compliance review.
- [ ] Automated tests cover successful export generation for filtered results.

## Verification

- [ ] Tests pass: `<targeted test command for audit-log CSV export coverage>`
- [ ] Build succeeds: `<repo build command, if applicable>`
- [ ] Manual check: apply filters, export CSV, and confirm the downloaded rows match the filtered audit log view.

## Blocked by

- Blocked by #<child-1>
- Blocked by #<child-2>
- Blocked by #<child-3>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<child-1>, #<child-2>, and #<child-3> are all closed
- Parallel rule: if multiple AFK issues are ready in W2, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

- Admin can export filtered audit logs as CSV for compliance.

## Files likely touched

- `<admin-audit-log-listing-view>`
- `<audit-log-export-endpoint-or-service>`
- `<csv-export-formatter>`
- `<audit-log-export-tests>`

## Estimated scope

Medium: 3-5 files
```

### 5. `Show admin-visible audit export failures`

```markdown
## Parent

#<parent-issue-number>

## What to build

Surface audit export failures in the admin experience so an admin can tell when a CSV export did not complete and what next action to take.

## Type

AFK

## Acceptance criteria

- [ ] Failed audit export attempts produce an admin-visible error state or message.
- [ ] The failure state does not present a successful download when export generation fails.
- [ ] Automated tests cover at least one export-failure path visible to admins.

## Verification

- [ ] Tests pass: `<targeted test command for audit-log export failure coverage>`
- [ ] Build succeeds: `<repo build command, if applicable>`
- [ ] Manual check: trigger an export failure scenario and confirm the admin sees the failure state instead of a successful download.

## Blocked by

- Blocked by #<child-4>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W3
- Ready to start when: #<child-4> is closed
- Parallel rule: if multiple AFK issues are ready in W3, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

- Admin can see export failures.

## Files likely touched

- `<admin-audit-log-export-trigger>`
- `<audit-log-export-endpoint-or-service>`
- `<admin-notification-or-error-state-component>`
- `<audit-log-export-failure-tests>`

## Estimated scope

Medium: 3-5 files
```

## Dry-run command draft

```bash
# create parent tracker
 gh issue create --title "Task graph: admin audit log exports" --body-file parent-issue.md

# create child issues in dependency order
 gh issue create --title "Filter audit log by actor" --body-file child-1.md
 gh issue create --title "Filter audit log by date range" --body-file child-2.md
 gh issue create --title "Filter audit log by event type" --body-file child-3.md
 gh issue create --title "Export filtered audit logs as CSV" --body-file child-4.md
 gh issue create --title "Show admin-visible audit export failures" --body-file child-5.md

# attach each child to the parent tracker
 PARENT_ISSUE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
 CHILD_ISSUE_ID=$(gh issue view <child-1> --json id --jq .id)
 gh api graphql -f query="
 mutation {
   addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
     issue { number }
   }
 }"

 CHILD_ISSUE_ID=$(gh issue view <child-2> --json id --jq .id)
 gh api graphql -f query="
 mutation {
   addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
     issue { number }
   }
 }"

 CHILD_ISSUE_ID=$(gh issue view <child-3> --json id --jq .id)
 gh api graphql -f query="
 mutation {
   addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
     issue { number }
   }
 }"

 CHILD_ISSUE_ID=$(gh issue view <child-4> --json id --jq .id)
 gh api graphql -f query="
 mutation {
   addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
     issue { number }
   }
 }"

 CHILD_ISSUE_ID=$(gh issue view <child-5> --json id --jq .id)
 gh api graphql -f query="
 mutation {
   addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
     issue { number }
   }
 }"
```
