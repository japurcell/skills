# Draft: Admin Audit Log Export Task Graph

## Parent Tracker Issue (Draft)

**Title:** Admin Audit Log Export: Filtering, CSV Export, and Failure Handling

**Body:**

## Source

Admins can filter audit logs by actor, date range, and event type, export CSV for compliance, and see export failures.

## Task graph

- [ ] W1 - Implement audit log filtering by actor, date range, and event type - AFK - blocked by none
- [ ] W1 - Implement CSV export of filtered audit logs - AFK - blocked by: Implement audit log filtering
- [ ] W2 - Implement export failure handling and user-visible error reporting - AFK - blocked by: Implement CSV export

## How to grab work

Work is executed from this issue's direct subissues. Start with any open AFK issue in the lowest-numbered wave whose blockers are all closed. If multiple AFK issues share that wave and do not block one another, they may be worked in parallel. HITL issues require the named human decision or review before implementation.

---

## Child Issues (Drafts)

### 1. Implement audit log filtering by actor, date range, and event type

**Parent:** #<parent-issue-number>

**What to build:**
Enable filtering of admin audit logs by actor, date range, and event type in the UI and backend.

**Type:** AFK

**Acceptance criteria:**
- [ ] Admins can select actor(s), date range, and event type(s) to filter logs
- [ ] Filtered results are accurate and performant
- [ ] Filtering works in both UI and API (if applicable)

**Verification:**
- [ ] Tests pass: `<test command>`
- [ ] Build succeeds: `<build command>`
- [ ] Manual check: Filtering returns correct results for various inputs

**Blocked by:** None - can start immediately

**Queue position:**
- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers

**User stories covered:** Not explicit in source

**Files likely touched:**
- `src/audit-log/`
- `src/api/`
- `src/ui/`
- `tests/audit-log/`

**Estimated scope:** Medium: 3-5 files

---

### 2. Implement CSV export of filtered audit logs

**Parent:** #<parent-issue-number>

**What to build:**
Allow admins to export the currently filtered audit logs as a CSV file for compliance purposes.

**Type:** AFK

**Acceptance criteria:**
- [ ] Exported CSV matches filtered results
- [ ] CSV includes all relevant fields
- [ ] Export is accessible from the UI

**Verification:**
- [ ] Tests pass: `<test command>`
- [ ] Build succeeds: `<build command>`
- [ ] Manual check: Exported CSV matches UI/API results

**Blocked by:** Implement audit log filtering by actor, date range, and event type

**Queue position:**
- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: Implement audit log filtering is closed

**User stories covered:** Not explicit in source

**Files likely touched:**
- `src/audit-log/export/`
- `src/ui/`
- `tests/audit-log/`

**Estimated scope:** Medium: 3-5 files

---

### 3. Implement export failure handling and user-visible error reporting

**Parent:** #<parent-issue-number>

**What to build:**
Detect and handle export failures, surfacing clear error messages to admins when export fails.

**Type:** AFK

**Acceptance criteria:**
- [ ] Export failures are detected and logged
- [ ] Admins see clear error messages on export failure
- [ ] Failure cases are covered by tests

**Verification:**
- [ ] Tests pass: `<test command>`
- [ ] Build succeeds: `<build command>`
- [ ] Manual check: Simulated export failures show correct error messages

**Blocked by:** Implement CSV export of filtered audit logs

**Queue position:**
- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: Implement CSV export of filtered audit logs is closed

**User stories covered:** Not explicit in source

**Files likely touched:**
- `src/audit-log/export/`
- `src/ui/`
- `tests/audit-log/`

**Estimated scope:** Small: 1-2 files

---

## Summary

Created task graph for admin audit log export features.

Parent: #<parent-issue-number> Admin Audit Log Export: Filtering, CSV Export, and Failure Handling

Child issues:
1. #<child-issue-number-1> Implement audit log filtering by actor, date range, and event type - W1 - AFK - blocked by none
2. #<child-issue-number-2> Implement CSV export of filtered audit logs - W1 - AFK - blocked by #<child-issue-number-1>
3. #<child-issue-number-3> Implement export failure handling and user-visible error reporting - W2 - AFK - blocked by #<child-issue-number-2>

How to grab work:
- Open parent #<parent-issue-number> and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- If the parent issue already existed, read the managed `Task graph` / `How to grab work` section in its body.

Notes:
- All issue numbers and references are placeholders for this dry-run benchmark.
- No GitHub mutation or implementation was performed.
