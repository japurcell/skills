## Parent tracker draft

### Title
Admin Audit Log Export: Filtering, CSV Export, and Failure Visibility

### Body

#### Source

Admins can filter audit logs by actor, date range, and event type, export filtered logs as CSV for compliance, and see export failures.

#### Task graph

- [ ] W1 - Filter audit logs by actor, date range, and event type - AFK - blocked by none
- [ ] W2 - Export filtered audit logs as CSV - AFK - blocked by #<child-1>
- [ ] W3 - Show admin-visible export failures - AFK - blocked by #<child-2>

#### How to grab work

Work is executed from this issue's direct subissues. Start with any open AFK issue in the lowest-numbered wave whose blockers are all closed. If multiple AFK issues share that wave and do not block one another, they may be worked in parallel. HITL issues require the named human decision or review before implementation.

---

## Child issue draft 1

### Title
Filter audit logs by actor, date range, and event type

```
## Parent

#<parent-issue-number>

## What to build

Implement filtering for the admin audit log by actor, date range, and event type, allowing admins to narrow results in the UI and backend.

## Type

AFK

## Acceptance criteria

- [ ] Admins can filter audit logs by actor
- [ ] Admins can filter audit logs by date range
- [ ] Admins can filter audit logs by event type

## Verification

- [ ] Tests pass: `<targeted backend/API test command>`
- [ ] Build succeeds: `<relevant build command, if known and applicable>`
- [ ] Manual check: Admin filters logs in UI and sees correct results

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers, or every issue listed in `Blocked by` is closed

## User stories covered

Not explicit in source

## Files likely touched

- `src/audit/logs/filtering.ts`
- `src/audit/logs/ui/FilterControls.tsx`
- `tests/audit/logs/filtering.test.ts`

## Estimated scope

Medium: 3-5 files
```

---

## Child issue draft 2

### Title
Export filtered audit logs as CSV

```
## Parent

#<parent-issue-number>

## What to build

Enable admins to export the currently filtered audit logs as a CSV file for compliance purposes.

## Type

AFK

## Acceptance criteria

- [ ] Admins can export filtered audit logs as CSV
- [ ] Exported CSV matches the filtered results
- [ ] Export is available for download after processing

## Verification

- [ ] Tests pass: `<targeted backend/API test command>`
- [ ] Build succeeds: `<relevant build command, if known and applicable>`
- [ ] Manual check: Admin downloads CSV and verifies contents match filters

## Blocked by

- Blocked by #<child-1>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: every issue listed in `Blocked by` is closed

## User stories covered

Not explicit in source

## Files likely touched

- `src/audit/logs/exporter.ts`
- `src/audit/logs/ui/ExportButton.tsx`
- `tests/audit/logs/exporter.test.ts`

## Estimated scope

Medium: 3-5 files
```

---

## Child issue draft 3

### Title
Show admin-visible export failures

```
## Parent

#<parent-issue-number>

## What to build

Display clear error messages to admins when audit log export fails, including reasons for failure and suggested next steps.

## Type

AFK

## Acceptance criteria

- [ ] Admins see a clear error message if export fails
- [ ] Error includes reason for failure
- [ ] Admin is guided on next steps or retry

## Verification

- [ ] Tests pass: `<targeted backend/API test command>`
- [ ] Build succeeds: `<relevant build command, if known and applicable>`
- [ ] Manual check: Admin triggers export failure and sees appropriate error in UI

## Blocked by

- Blocked by #<child-2>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W3
- Ready to start when: every issue listed in `Blocked by` is closed

## User stories covered

Not explicit in source

## Files likely touched

- `src/audit/logs/exporter.ts`
- `src/audit/logs/ui/ExportButton.tsx`
- `src/audit/logs/ui/ExportError.tsx`
- `tests/audit/logs/exporter.test.ts`

## Estimated scope

Medium: 3-5 files
```

---

## Subissue attachment commands

```
# After creating issues, attach them to the parent (replace placeholders with real IDs):
PARENT_ISSUE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_ISSUE_ID_1=$(gh issue view <child-1> --json id --jq .id)
CHILD_ISSUE_ID_2=$(gh issue view <child-2> --json id --jq .id)
CHILD_ISSUE_ID_3=$(gh issue view <child-3> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID_1\"}) { issue { number } }
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID_2\"}) { issue { number } }
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID_3\"}) { issue { number } }
}"
```

---

## Final summary

Created task graph for admin audit log export (filtering, CSV export, failure visibility).

Parent: #<parent-issue-number> Admin Audit Log Export: Filtering, CSV Export, and Failure Visibility

Child issues:

1. #<child-1> Filter audit logs by actor, date range, and event type - W1 - AFK - blocked by none
2. #<child-2> Export filtered audit logs as CSV - W2 - AFK - blocked by #<child-1>
3. #<child-3> Show admin-visible export failures - W3 - AFK - blocked by #<child-2>

How to grab work:

- Open parent #<parent-issue-number> and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- Read the managed Task graph / How to grab work section in the parent body.

Notes:

- All slices are AFK and can be implemented in order.
- Placeholders used for issue numbers in this draft.
