## New parent tracker issue

### Parent tracker draft

**Title**: Admin audit log exports

**Body**:

## Source

Admin audit log exports: admins can filter by actor, date range, and event type, export CSV for compliance, and see export failures.

## Task graph

- [ ] W1 - Add audit log persistence - AFK - blocked by none
- [ ] W2 - Filter audit logs by actor/date/event type - AFK - blocked by W1
- [ ] W3 - Export filtered audit logs as CSV - AFK - blocked by W2
- [ ] W4 - Show admin-visible export failures - AFK - blocked by W3

## How to grab work

Work is executed from this issue's direct subissues. Start with any open AFK issue in the lowest-numbered wave whose blockers are all closed. If multiple AFK issues share that wave and do not block one another, they may be worked in parallel. HITL issues require the named human decision or review before implementation.

---

## Child issue drafts

### Child 1: Add audit log persistence

## Parent

#<parent-issue-number>

## What to build

Audit events (actor, action, resource, timestamp) are persisted to a queryable store. This forms the foundation for filtering and exporting.

## Type

AFK

## Acceptance criteria

- [ ] Schema exists for storing audit events
- [ ] Audit events are captured and logged on key actions
- [ ] Events include actor, action, resource, timestamp, and metadata

## Verification

- [ ] Tests pass: `npm run test -- audit.test.ts`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Perform an auditable action and verify it appears in the database

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers

## User stories covered

Foundation for audit log filtering and export

## Files likely touched

- `src/db/migrations/audit_events_table.sql`
- `src/db/models/AuditEvent.ts`
- `src/services/auditService.ts`
- `tests/services/auditService.test.ts`

## Estimated scope

Medium: 3-5 files

### Child 2: Filter audit logs by actor/date/event type

## Parent

#<parent-issue-number>

## What to build

Admins can filter the audit log view by actor (who performed the action), date range (when it happened), and event type (what action occurred).

## Type

AFK

## Acceptance criteria

- [ ] Filter UI renders with actor, date, and event type controls
- [ ] Filters reduce returned audit events correctly
- [ ] Filter combinations work together

## Verification

- [ ] Tests pass: `npm run test -- auditFilter.test.ts`
- [ ] Manual check: Apply multiple filters and verify results

## Blocked by

- Blocked by #<child-1-issue-number>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<parent-issue-number>'s direct child issue for audit log persistence is closed

## User stories covered

Admins can filter by actor, date range, and event type

## Files likely touched

- `src/features/admin/AuditLogFilters.tsx`
- `src/api/auditLogs.ts`
- `tests/features/admin/AuditLogFilters.test.ts`

## Estimated scope

Small: 1-2 files

### Child 3: Export filtered audit logs as CSV

## Parent

#<parent-issue-number>

## What to build

Admins can export the currently filtered audit log view as a CSV file for compliance purposes. The export includes all audit event fields and respects current filters.

## Type

AFK

## Acceptance criteria

- [ ] Export button appears in audit log UI
- [ ] CSV contains all relevant audit fields
- [ ] CSV respects current filter state

## Verification

- [ ] Tests pass: `npm run test -- auditExport.test.ts`
- [ ] Manual check: Apply filters and export CSV, verify content

## Blocked by

- Blocked by #<child-2-issue-number>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W3
- Ready to start when: #<parent-issue-number>'s direct child issue for audit log filtering is closed

## User stories covered

Export filtered audit logs for compliance

## Files likely touched

- `src/features/admin/AuditLogExport.tsx`
- `src/services/csvExport.ts`
- `tests/features/admin/AuditLogExport.test.ts`

## Estimated scope

Small: 1-2 files

### Child 4: Show admin-visible export failures

## Parent

#<parent-issue-number>

## What to build

If an export fails (e.g., database unavailable, CSV generation error), admins see a user-friendly error message explaining what went wrong and can retry.

## Type

AFK

## Acceptance criteria

- [ ] Export errors are caught and displayed
- [ ] Error messages are specific and actionable
- [ ] Retry functionality works

## Verification

- [ ] Tests pass: `npm run test -- exportErrors.test.ts`
- [ ] Manual check: Force an export failure and verify error display

## Blocked by

- Blocked by #<child-3-issue-number>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W4
- Ready to start when: #<parent-issue-number>'s direct child issue for audit log export is closed

## User stories covered

Admins can see export failures

## Files likely touched

- `src/features/admin/ExportErrorHandler.tsx`
- `tests/features/admin/ExportErrorHandler.test.ts`

## Estimated scope

Small: 1-2 files

---

## Summary

Created task graph for admin audit log exports.

Parent: #<parent-issue-number> (placeholder) (new)

Child issues:

1. #<child-1> Add audit log persistence - W1 - AFK - blocked by none
2. #<child-1> Filter audit logs by actor/date/event type - W2 - AFK - blocked by #<child-2>
3. #<child-1> Export filtered audit logs as CSV - W3 - AFK - blocked by #<child-2>
4. #<child-1> Show admin-visible export failures - W4 - AFK - blocked by #<child-2>

How to grab work:

- Open parent #<parent-issue-number> and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- If the parent issue already existed, read the managed `Task graph` / `How to grab work` section in its body.

Notes:

- All child issues are vertical slices, each delivering one complete feature through the layers it touches
- Dependencies are minimal and necessary: persistence → filtering → export → error handling
- Execution waves make the next ready AFK issue obvious from GitHub alone
