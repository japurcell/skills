## Proposed vertical-slice breakdown (present first)

1. **Title**: Implement saved search CRUD (create, read, update, delete)
   **Type**: AFK
   **Execution wave**: W1
   **Blocked by**: None
   **User stories covered**: Saved search creation, editing, deletion

2. **Title**: Enable alert delivery for saved searches
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Implement saved search CRUD
   **User stories covered**: Alert delivery for saved searches

3. **Title**: Add notification preference editing for alerts
   **Type**: AFK
   **Execution wave**: W3
   **Blocked by**: Slice 2: Enable alert delivery for saved searches
   **User stories covered**: Notification preference editing

4. **Title**: Implement alert pause/resume without deleting saved search
   **Type**: AFK
   **Execution wave**: W4
   **Blocked by**: Slice 2: Enable alert delivery for saved searches
   **User stories covered**: Pausing alerts without deleting saved search

---

### Draft child issues

#### Child Issue 1: Implement saved search CRUD (W1, AFK)

**Parent**: #4100

**What to build**: Implement backend and UI for creating, reading, updating, and deleting saved searches from the search page. Ensure users can manage their saved searches independently.

**Type**: AFK

**Acceptance criteria**:
- [ ] Users can create a saved search from the search page
- [ ] Users can view, edit, and delete their saved searches
- [ ] Changes are reflected immediately in the UI

**Verification**:
- [ ] Tests pass: `npm test` (or project equivalent)
- [ ] Build succeeds: `npm run build` (or project equivalent)
- [ ] Manual check: Create, edit, and delete saved searches as a user

**Blocked by**: None - can start immediately

**Queue position**:
- Parent queue: direct subissue of #4100
- Execution wave: W1
- Ready to start when: this issue has no blockers

**User stories covered**: Saved search CRUD

**Files likely touched**:
- `src/search/`
- `src/saved-searches/`
- `tests/saved-searches/`

**Estimated scope**: Medium: 3-5 files

---

#### Child Issue 2: Enable alert delivery for saved searches (W2, AFK)

**Parent**: #4100

**What to build**: Implement backend and UI to allow users to receive email alerts when saved search results change. Integrate with notification system.

**Type**: AFK

**Acceptance criteria**:
- [ ] Users can opt in to email alerts for saved searches
- [ ] Alerts are sent when results change
- [ ] Alert delivery can be toggled per saved search

**Verification**:
- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Subscribe to alerts and verify email delivery

**Blocked by**: Blocked by #<Child Issue 1>

**Queue position**:
- Parent queue: direct subissue of #4100
- Execution wave: W2
- Ready to start when: #<Child Issue 1> is closed

**User stories covered**: Alert delivery

**Files likely touched**:
- `src/alerts/`
- `src/saved-searches/`
- `tests/alerts/`

**Estimated scope**: Medium: 3-5 files

---

#### Child Issue 3: Add notification preference editing for alerts (W3, AFK)

**Parent**: #4100

**What to build**: Allow users to edit notification preferences for saved search alerts without blocking initial saved search creation. Preferences include email frequency, types of notifications, and opt-out.

**Type**: AFK

**Acceptance criteria**:
- [ ] Users can edit notification preferences for each saved search
- [ ] Changes take effect immediately
- [ ] Editing preferences does not block saved search creation

**Verification**:
- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Edit preferences and verify behavior

**Blocked by**: Blocked by #<Child Issue 2>

**Queue position**:
- Parent queue: direct subissue of #4100
- Execution wave: W3
- Ready to start when: #<Child Issue 2> is closed

**User stories covered**: Notification preference editing

**Files likely touched**:
- `src/alerts/`
- `src/preferences/`
- `tests/preferences/`

**Estimated scope**: Small: 1-2 files

---

#### Child Issue 4: Implement alert pause/resume without deleting saved search (W4, AFK)

**Parent**: #4100

**What to build**: Allow users to pause and resume alerts for a saved search without deleting the search itself. Ensure UI clearly distinguishes between paused and active alerts.

**Type**: AFK

**Acceptance criteria**:
- [ ] Users can pause alerts for a saved search
- [ ] Users can resume alerts for a saved search
- [ ] Pausing does not delete the saved search

**Verification**:
- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Pause/resume alerts and verify behavior

**Blocked by**: Blocked by #<Child Issue 2>

**Queue position**:
- Parent queue: direct subissue of #4100
- Execution wave: W4
- Ready to start when: #<Child Issue 2> is closed

**User stories covered**: Pausing alerts

**Files likely touched**:
- `src/alerts/`
- `src/saved-searches/`
- `tests/alerts/`

**Estimated scope**: Small: 1-2 files

---

### Managed parent-body tracking guidance (for #4100)

<!-- prd-to-tasks:start -->

## Task graph

- [ ] W1 - #<Child Issue 1> Implement saved search CRUD - AFK - blocked by none
- [ ] W2 - #<Child Issue 2> Enable alert delivery for saved searches - AFK - blocked by #<Child Issue 1>
- [ ] W3 - #<Child Issue 3> Add notification preference editing for alerts - AFK - blocked by #<Child Issue 2>
- [ ] W4 - #<Child Issue 4> Implement alert pause/resume without deleting saved search - AFK - blocked by #<Child Issue 2>

## How to grab work

1. Open this parent issue and inspect its direct subissues.
2. The executable work is in the sibling implementation issues listed above.
3. Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
4. If several AFK issues are ready in the same wave, they may be worked in parallel.
5. Do not start HITL issues until the named human decision or review has happened.
<!-- prd-to-tasks:end -->

---

Created task graph for saved searches and alerting feature.

Parent: #4100 Saved searches and alerting

Child issues:
1. #<Child Issue 1> Implement saved search CRUD - W1 - AFK - blocked by none
2. #<Child Issue 2> Enable alert delivery for saved searches - W2 - AFK - blocked by #<Child Issue 1>
3. #<Child Issue 3> Add notification preference editing for alerts - W3 - AFK - blocked by #<Child Issue 2>
4. #<Child Issue 4> Implement alert pause/resume without deleting saved search - W4 - AFK - blocked by #<Child Issue 2>

How to grab work:
- Open parent #4100 and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- If the parent issue already existed, read the managed `Task graph` / `How to grab work` section in its body.

Notes:
- Child issue numbers are placeholders for this dry run.
- No HITL slices identified; all are AFK.
- No code or GitHub mutations performed (dry run).
