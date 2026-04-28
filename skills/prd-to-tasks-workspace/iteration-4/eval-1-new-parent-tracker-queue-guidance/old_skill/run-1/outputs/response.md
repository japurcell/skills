# Drafted Task Graph for Admin Audit Log Exports

**Note:** This is a dry-run draft. All issue numbers are placeholders (e.g., #<parent-issue-number>, #<child-issue-number>). No GitHub mutations have been performed.

## Parent Tracker Issue (Draft)

### Title
Admin Audit Log Export: Filtering, CSV Export, and Failure Handling

### Body

#### Source
Admins can filter audit logs by actor, date range, and event type, export CSV for compliance, and see export failures.

#### Task graph
- [ ] W1 - Implement audit log filtering by actor, date range, and event type - AFK - blocked by none
- [ ] W1 - Implement CSV export of filtered audit logs - AFK - blocked by none
- [ ] W2 - Handle and display export failures - AFK - blocked by #<child-issue-1>

#### How to grab work
Work is executed from this issue's direct subissues. Start with any open AFK issue in the lowest-numbered wave whose blockers are all closed. If multiple AFK issues share that wave and do not block one another, they may be worked in parallel. HITL issues require the named human decision or review before implementation.

---

## Child Issues (Draft)

### 1. Implement audit log filtering by actor, date range, and event type
**Parent:** #<parent-issue-number>
**Type:** AFK
**Execution wave:** W1
**Blocked by:** None
**User stories covered:** Filtering audit logs by actor, date range, and event type

#### What to build
Enable admins to filter audit logs by actor, date range, and event type in the admin UI and backend API.

#### Acceptance criteria
- [ ] Admins can select actor(s), date range, and event type(s) as filters
- [ ] Filtered results are reflected in the UI and API
- [ ] Filtering is performant for large datasets

#### Verification
- [ ] Tests pass: `npm test` (or project test command)
- [ ] Build succeeds: `npm run build` (or project build command)
- [ ] Manual check: Filtering works as expected in UI and API

#### Files likely touched
- `src/admin/audit-log/`
- `src/api/audit-log/`
- `tests/admin/audit-log/`

#### Estimated scope
Medium: 3-5 files

#### Queue position
- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers

---

### 2. Implement CSV export of filtered audit logs
**Parent:** #<parent-issue-number>
**Type:** AFK
**Execution wave:** W1
**Blocked by:** None
**User stories covered:** Exporting filtered audit logs as CSV for compliance

#### What to build
Allow admins to export the currently filtered audit logs as a CSV file for compliance purposes.

#### Acceptance criteria
- [ ] Export button is available when filters are applied
- [ ] Exported CSV matches the filtered results
- [ ] CSV format meets compliance requirements

#### Verification
- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Exported CSV is correct and downloadable

#### Files likely touched
- `src/admin/audit-log/export/`
- `src/api/audit-log/export/`
- `tests/admin/audit-log/export/`

#### Estimated scope
Medium: 3-5 files

#### Queue position
- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers

---

### 3. Handle and display export failures
**Parent:** #<parent-issue-number>
**Type:** AFK
**Execution wave:** W2
**Blocked by:** #<child-issue-1>
**User stories covered:** Displaying export failures to admins

#### What to build
Detect, log, and display export failures to admins, including error messages and retry options if appropriate.

#### Acceptance criteria
- [ ] Export failures are detected and logged
- [ ] Admins see clear error messages on export failure
- [ ] Retry option is available if appropriate

#### Verification
- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Export failures are handled and displayed correctly

#### Files likely touched
- `src/admin/audit-log/export/`
- `src/api/audit-log/export/`
- `tests/admin/audit-log/export/`

#### Estimated scope
Small: 1-2 files

#### Queue position
- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<child-issue-1> is closed

---

## Summary
Created task graph for admin audit log exports (draft, dry-run).

Parent: #<parent-issue-number> Admin Audit Log Export: Filtering, CSV Export, and Failure Handling

Child issues:
1. #<child-issue-1> Implement audit log filtering by actor, date range, and event type - W1 - AFK - blocked by none
2. #<child-issue-2> Implement CSV export of filtered audit logs - W1 - AFK - blocked by none
3. #<child-issue-3> Handle and display export failures - W2 - AFK - blocked by #<child-issue-1>

How to grab work:
- Open parent #<parent-issue-number> and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- Read the managed `Task graph` / `How to grab work` section in the parent body.

Notes:
- All issue numbers are placeholders.
- No GitHub mutations have been performed.
- All slices are AFK and can be implemented in parallel where not blocked.
- No HITL slices identified for this PRD.
