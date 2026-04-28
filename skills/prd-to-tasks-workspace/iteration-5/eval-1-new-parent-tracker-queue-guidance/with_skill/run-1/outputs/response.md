# Parent Tracker Issue (Draft)

## Source

Admins can filter audit logs by actor, date range, and event type, export CSV for compliance, and see export failures.

## Task graph

- [ ] W1 - [Draft: Implement audit log filtering] - AFK - blocked by none
- [ ] W1 - [Draft: Implement CSV export functionality] - AFK - blocked by none
- [ ] W2 - [Draft: Handle export failures and reporting] - AFK - blocked by #2

## How to grab work

Work is executed from this issue's direct subissues. Start with any open AFK issue in the lowest-numbered wave whose blockers are all closed. If multiple AFK issues share that wave and do not block one another, they may be worked in parallel. HITL issues require the named human decision or review before implementation.

---

## Child Issue Drafts

---

### 1. Implement audit log filtering

#### Parent

#<parent-issue-number>

#### What to build

Add filtering to the admin audit log by actor, date range, and event type. Ensure the UI and backend support these filters.

#### Type

AFK

#### Acceptance criteria

- [ ] Admins can filter logs by actor
- [ ] Admins can filter logs by date range
- [ ] Admins can filter logs by event type

#### Verification

- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Filtering works as expected in the UI

#### Blocked by

None - can start immediately

#### Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers

#### User stories covered

Not explicit in source

#### Files likely touched

- `src/audit-log/`
- `src/backend/audit-log/`
- `tests/audit-log/`

#### Estimated scope

Medium: 3-5 files

---

### 2. Implement CSV export functionality

#### Parent

#<parent-issue-number>

#### What to build

Allow admins to export filtered audit logs as CSV for compliance purposes. Ensure the export respects all applied filters.

#### Type

AFK

#### Acceptance criteria

- [ ] Admins can export filtered logs as CSV
- [ ] Exported CSV matches applied filters
- [ ] Export is accessible from the UI

#### Verification

- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Exported CSV is correct

#### Blocked by

None - can start immediately

#### Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers

#### User stories covered

Not explicit in source

#### Files likely touched

- `src/audit-log/export/`
- `src/backend/audit-log/export/`
- `tests/audit-log/export/`

#### Estimated scope

Medium: 3-5 files

---

### 3. Handle export failures and reporting

#### Parent

#<parent-issue-number>

#### What to build

Detect and report export failures to the admin. Display clear error messages and log failures for troubleshooting.

#### Type

AFK

#### Acceptance criteria

- [ ] Export failures are detected
- [ ] Admins see clear error messages on failure
- [ ] Failures are logged for troubleshooting

#### Verification

- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Failure scenarios are handled and reported

#### Blocked by

- Blocked by #2

#### Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #2 is closed

#### User stories covered

Not explicit in source

#### Files likely touched

- `src/audit-log/export/`
- `src/backend/audit-log/export/`
- `tests/audit-log/export/`

#### Estimated scope

Small: 1-2 files

---

## Subissue Attachment Commands (Draft)

```bash
# After creating issues, attach them to the parent:
# PARENT_ISSUE_ID and CHILD_ISSUE_ID are placeholders

gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"
```

---

## Summary

Created task graph for admin audit log exports (draft).

Parent: #<parent-issue-number> Admin audit log exports

Child issues:

1. #1 Implement audit log filtering - W1 - AFK - blocked by none
2. #2 Implement CSV export functionality - W1 - AFK - blocked by none
3. #3 Handle export failures and reporting - W2 - AFK - blocked by #2

How to grab work:

- Open parent #<parent-issue-number> and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- Read the managed `Task graph` / `How to grab work` section in its body.

Notes:

- All issue numbers are placeholders for this dry run.
- No HITL slices identified; all are AFK.
- No real GitHub mutations performed.
