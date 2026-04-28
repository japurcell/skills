# Draft: Task Graph for Admin Audit Log Exports

**Source:** Raw PRD (no existing GitHub issue)

---

## Parent Tracker Issue (DRAFT)

**Title:** Admin Audit Log Export: Filtering, CSV Export, and Failure Visibility

**Body:**

### Source
Admins can filter audit logs by actor, date range, and event type, export results as CSV for compliance, and see export failures.

### Task graph
- [ ] W1 - Implement audit log filtering by actor, date range, and event type - AFK - blocked by none
- [ ] W2 - Implement CSV export of filtered audit logs - AFK - blocked by W1
- [ ] W3 - Display export failures to admins - AFK - blocked by W2

### How to grab work
Work is executed from this issue's direct subissues. Start with any open AFK issue in the lowest-numbered wave whose blockers are all closed. If multiple AFK issues share that wave and do not block one another, they may be worked in parallel. HITL issues require the named human decision or review before implementation.

---

## Draft Child Issues

### 1. Implement audit log filtering by actor, date range, and event type
**Parent:** #<parent-issue-number>
**Type:** AFK
**Execution wave:** W1
**Blocked by:** None
**User stories covered:** Not explicit in source

#### What to build
Enable admins to filter audit logs by actor, date range, and event type in the UI and backend.

#### Acceptance criteria
- [ ] Admins can select actor(s), date range, and event type(s) as filters
- [ ] Filtered results are reflected in the UI
- [ ] Filtering is performant for large datasets

#### Verification
- [ ] Tests pass: `<test command>`
- [ ] Build succeeds: `<build command>`
- [ ] Manual check: Filtering works as described

#### Files likely touched
- `src/audit-log/`
- `src/components/AdminAuditLogFilter.tsx`
- `tests/audit-log/`

#### Estimated scope
Medium: 3-5 files

---

### 2. Implement CSV export of filtered audit logs
**Parent:** #<parent-issue-number>
**Type:** AFK
**Execution wave:** W2
**Blocked by:** #<child-issue-number-1>
**User stories covered:** Not explicit in source

#### What to build
Allow admins to export the currently filtered audit log results as a CSV file.

#### Acceptance criteria
- [ ] Export button is available when filters are applied
- [ ] Exported CSV matches filtered results
- [ ] Large exports are handled efficiently (streamed or paginated if needed)

#### Verification
- [ ] Tests pass: `<test command>`
- [ ] Build succeeds: `<build command>`
- [ ] Manual check: CSV export works as described

#### Files likely touched
- `src/audit-log/export/`
- `src/components/AdminAuditLogExportButton.tsx`
- `tests/audit-log/export/`

#### Estimated scope
Medium: 3-5 files

---

### 3. Display export failures to admins
**Parent:** #<parent-issue-number>
**Type:** AFK
**Execution wave:** W3
**Blocked by:** #<child-issue-number-2>
**User stories covered:** Not explicit in source

#### What to build
Show clear error messages to admins when a CSV export fails, including reason and suggested next steps.

#### Acceptance criteria
- [ ] Export failures are surfaced in the UI
- [ ] Error messages are actionable and logged
- [ ] Failure cases are covered by tests

#### Verification
- [ ] Tests pass: `<test command>`
- [ ] Build succeeds: `<build command>`
- [ ] Manual check: Export failures are visible and informative

#### Files likely touched
- `src/audit-log/export/`
- `src/components/AdminAuditLogExportButton.tsx`
- `src/components/AdminAuditLogExportError.tsx`
- `tests/audit-log/export/`

#### Estimated scope
Small: 1-2 files

---

## Summary
Created draft task graph for admin audit log exports. All issues are AFK and vertically sliced. Use placeholders for issue numbers in this dry run.
