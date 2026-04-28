## Proposed vertical-slice breakdown (present first)

1. **Title**: Implement saved search CRUD (create, read, update, delete)
   **Type**: AFK
   **Execution wave**: W1
   **Blocked by**: None
   **User stories covered**: Saved search creation and management

2. **Title**: Enable alert delivery for saved searches
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Implement saved search CRUD
   **User stories covered**: Alert delivery for saved searches

3. **Title**: Add notification preference editing (non-blocking for initial CRUD)
   **Type**: AFK
   **Execution wave**: W3
   **Blocked by**: Slice 2: Enable alert delivery for saved searches
   **User stories covered**: Notification preference editing

4. **Title**: Implement alert pause/resume without deleting saved search
   **Type**: AFK
   **Execution wave**: W4
   **Blocked by**: Slice 3: Add notification preference editing
   **User stories covered**: Pausing alerts

---

### Draft child issues

#### Child Issue 1: Implement saved search CRUD

```
## Parent

#4100

## What to build

Implement the ability for users to create, read, update, and delete saved searches from the search page. This includes UI, backend, and persistence as needed.

## Type

AFK

## Acceptance criteria

- [ ] Users can create a saved search from the search page
- [ ] Users can view, edit, and delete their saved searches
- [ ] Saved searches persist across sessions

## Verification

- [ ] Tests pass: `<insert test command>`
- [ ] Build succeeds: `<insert build command>`
- [ ] Manual check: Create, edit, and delete a saved search as a user

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W1
- Ready to start when: this issue has no blockers

## User stories covered

Saved search creation and management

## Files likely touched

- `src/search/`
- `src/saved-searches/`
- `tests/search/`

## Estimated scope

Medium: 3-5 files
```

#### Child Issue 2: Enable alert delivery for saved searches

```
## Parent

#4100

## What to build

Enable email alerts for users when the results of their saved searches change. Integrate with notification and email systems as needed.

## Type

AFK

## Acceptance criteria

- [ ] Users receive email alerts when saved search results change
- [ ] Alerts are sent only for active saved searches

## Verification

- [ ] Tests pass: `<insert test command>`
- [ ] Build succeeds: `<insert build command>`
- [ ] Manual check: Receive alert for a changed saved search

## Blocked by

- Blocked by #<child-issue-1>

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W2
- Ready to start when: #<child-issue-1> is closed

## User stories covered

Alert delivery for saved searches

## Files likely touched

- `src/alerts/`
- `src/notifications/`
- `tests/alerts/`

## Estimated scope

Medium: 3-5 files
```

#### Child Issue 3: Add notification preference editing

```
## Parent

#4100

## What to build

Allow users to edit notification preferences for saved search alerts. This should not block initial CRUD implementation.

## Type

AFK

## Acceptance criteria

- [ ] Users can change notification settings for saved search alerts
- [ ] Changes take effect without requiring saved search deletion

## Verification

- [ ] Tests pass: `<insert test command>`
- [ ] Build succeeds: `<insert build command>`
- [ ] Manual check: Edit notification preferences for a saved search

## Blocked by

- Blocked by #<child-issue-2>

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W3
- Ready to start when: #<child-issue-2> is closed

## User stories covered

Notification preference editing

## Files likely touched

- `src/notifications/`
- `src/saved-searches/`
- `tests/notifications/`

## Estimated scope

Small: 1-2 files
```

#### Child Issue 4: Implement alert pause/resume without deleting saved search

```
## Parent

#4100

## What to build

Allow users to pause and resume alerts for a saved search without deleting the search itself.

## Type

AFK

## Acceptance criteria

- [ ] Users can pause alerts for a saved search
- [ ] Users can resume alerts for a saved search
- [ ] Pausing does not delete the saved search

## Verification

- [ ] Tests pass: `<insert test command>`
- [ ] Build succeeds: `<insert build command>`
- [ ] Manual check: Pause and resume alerts for a saved search

## Blocked by

- Blocked by #<child-issue-3>

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W4
- Ready to start when: #<child-issue-3> is closed

## User stories covered

Pausing alerts

## Files likely touched

- `src/alerts/`
- `src/saved-searches/`
- `tests/alerts/`

## Estimated scope

Small: 1-2 files
```

---

### Managed parent-body tracking guidance (for #4100)

```
<!-- prd-to-tasks:start -->
## Task graph

- [ ] W1 - #<child-issue-1> Implement saved search CRUD - AFK - blocked by none
- [ ] W2 - #<child-issue-2> Enable alert delivery for saved searches - AFK - blocked by #<child-issue-1>
- [ ] W3 - #<child-issue-3> Add notification preference editing - AFK - blocked by #<child-issue-2>
- [ ] W4 - #<child-issue-4> Implement alert pause/resume without deleting saved search - AFK - blocked by #<child-issue-3>

## How to grab work

1. Open this parent issue and inspect its direct subissues.
2. The executable work is in the sibling implementation issues listed above.
3. Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
4. If several AFK issues are ready in the same wave, they may be worked in parallel.
5. Do not start HITL issues until the named human decision or review has happened.
<!-- prd-to-tasks:end -->
```

---

### Summary

Created task graph for saved search CRUD and alerting feature.

Parent: #4100 (existing)

Child issues:

1. #<child-issue-1> Implement saved search CRUD - W1 - AFK - blocked by none
2. #<child-issue-2> Enable alert delivery for saved searches - W2 - AFK - blocked by #<child-issue-1>
3. #<child-issue-3> Add notification preference editing - W3 - AFK - blocked by #<child-issue-2>
4. #<child-issue-4> Implement alert pause/resume without deleting saved search - W4 - AFK - blocked by #<child-issue-3>

How to grab work:

- Open parent #4100 and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- Read the managed `Task graph` / `How to grab work` section in the parent body.

Notes:

- Notification preference editing is not a blocker for initial CRUD (per comments).
- Alert delivery is allowed to ship after CRUD (per comments).
- All slices are AFK; no HITL slices required.
- Issue numbers are placeholders for this dry run.
