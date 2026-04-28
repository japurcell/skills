# Dry run output for `prd-to-tasks`

Using placeholder draft issue numbers because this benchmark run does not create real GitHub issues.

Created task graph for admin audit log exports.

Parent: #5000 Admin audit log exports tracker

## Parent tracker draft

**Title**: `Admin audit log exports tracker`

**Body**:

```markdown
## Source

Admins need audit log exports that support filtering by actor, date range, and event type, allow CSV export for compliance, and surface export failures.

## Task graph

- [ ] Filter admin audit logs by actor, date range, and event type - AFK - blocked by none
- [ ] Export filtered admin audit logs as CSV - AFK - blocked by none
- [ ] Show admin audit log export failures - AFK - blocked by Export filtered admin audit logs as CSV

## How to grab work

Start with any unchecked AFK issue marked "None - can start immediately" in its Blocked by section. HITL issues require the named human decision or review before implementation.
```

## Draft commands

```bash
gh issue create --title "Admin audit log exports tracker" --body-file parent-body.md
gh issue create --title "Filter admin audit logs by actor, date range, and event type" --body-file child-1-body.md
gh issue create --title "Export filtered admin audit logs as CSV" --body-file child-2-body.md
gh issue create --title "Show admin audit log export failures" --body-file child-3-body.md
```

## Child issue drafts

### #5001 Filter admin audit logs by actor, date range, and event type

```markdown
## Parent

#5000

## What to build

Add an end-to-end audit log filtering flow so admins can narrow the audit log by actor, date range, and event type and see matching results in the admin experience.

## Type

AFK

## Acceptance criteria

- [ ] Admins can apply actor, date range, and event type filters together and only matching audit log entries are shown.
- [ ] The filtering flow handles empty-result and invalid-filter cases without breaking the audit log experience.
- [ ] Automated coverage verifies the filtered query path and admin-facing results.

## Verification

- [ ] Tests pass: `<targeted test command>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: Apply each filter and a combined filter in the admin UI and confirm the visible entries match expected audit data.

## Blocked by

None - can start immediately

## User stories covered

Admins can filter by actor, date range, and event type.

## Files likely touched

- `src/admin/audit-log/*`
- `src/api/audit-log/*`
- `tests/audit-log/*`

## Estimated scope

Medium: 3-5 files
```

### #5002 Export filtered admin audit logs as CSV

```markdown
## Parent

#5000

## What to build

Add a compliance-oriented CSV export flow that lets admins export the currently requested audit log data set, including applied filters, into a downloadable CSV.

## Type

AFK

## Acceptance criteria

- [ ] Admins can trigger a CSV export from the audit log experience and receive a downloadable file.
- [ ] The CSV export respects actor, date range, and event type filters and includes the expected audit data columns for compliance use.
- [ ] Automated coverage verifies the export path and manual verification confirms the downloaded CSV matches the filtered audit data.

## Verification

- [ ] Tests pass: `<targeted test command>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: Export a filtered audit log result set and confirm the CSV contents and row count match the filtered view.

## Blocked by

None - can start immediately

## User stories covered

Admins can export CSV for compliance.

## Files likely touched

- `src/admin/audit-log/*`
- `src/api/audit-export/*`
- `tests/audit-export/*`

## Estimated scope

Medium: 3-5 files
```

### #5003 Show admin audit log export failures

```markdown
## Parent

#5000

## What to build

Add a visible export failure path so admins see when an audit log CSV export fails, understand that the export did not complete, and can retry without losing context.

## Type

AFK

## Acceptance criteria

- [ ] When an audit log export fails, the admin experience surfaces a clear failure message tied to the export action.
- [ ] The failure state preserves the admin's current audit log context so a retry can be attempted without re-entering filters.
- [ ] Automated coverage verifies at least one export failure path and manual verification confirms the failure feedback is visible to admins.

## Verification

- [ ] Tests pass: `<targeted test command>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: Force an export failure and confirm the admin sees the failure state and can retry from the same filtered context.

## Blocked by

- Blocked by #5002

## User stories covered

Admins can see export failures.

## Files likely touched

- `src/admin/audit-log/*`
- `src/api/audit-export/*`
- `tests/audit-export/*`

## Estimated scope

Small: 1-2 files
```

## Draft subissue attachment commands

```bash
PARENT_ISSUE_ID=$(gh issue view 5000 --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view 5001 --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: "$PARENT_ISSUE_ID", subIssueId: "$CHILD_ISSUE_ID"}) {
    issue { number }
  }
}"

PARENT_ISSUE_ID=$(gh issue view 5000 --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view 5002 --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: "$PARENT_ISSUE_ID", subIssueId: "$CHILD_ISSUE_ID"}) {
    issue { number }
  }
}"

PARENT_ISSUE_ID=$(gh issue view 5000 --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view 5003 --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: "$PARENT_ISSUE_ID", subIssueId: "$CHILD_ISSUE_ID"}) {
    issue { number }
  }
}"
```

## Final summary

Created task graph for admin audit log exports.

Parent: #5000 Admin audit log exports tracker

Child issues:
1. #5001 Filter admin audit logs by actor, date range, and event type - AFK - blocked by none
2. #5002 Export filtered admin audit logs as CSV - AFK - blocked by none
3. #5003 Show admin audit log export failures - AFK - blocked by #5002

Notes:
- Placeholder issue numbers are used for this dry run only.
- No HITL slice was needed because the source did not name a decision, review, or signoff gate.
