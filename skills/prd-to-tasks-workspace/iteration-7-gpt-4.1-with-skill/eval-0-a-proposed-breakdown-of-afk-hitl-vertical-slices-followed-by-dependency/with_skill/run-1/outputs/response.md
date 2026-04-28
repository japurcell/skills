# Proposed vertical-slice breakdown (present first)

1. **Title**: Saved search CRUD (Create, Read, Update, Delete)
   **Type**: AFK
   **Execution wave**: W1
   **Blocked by**: None
   **User stories covered**: Saved search management

2. **Title**: Alert delivery for saved searches
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Saved search CRUD
   **User stories covered**: Alert notifications

3. **Title**: Pause/resume alerts for saved searches
   **Type**: AFK
   **Execution wave**: W3
   **Blocked by**: Slice 2: Alert delivery
   **User stories covered**: Alert management

4. **Title**: Edit notification preferences for saved search alerts
   **Type**: AFK
   **Execution wave**: W4
   **Blocked by**: Slice 3: Pause/resume alerts
   **User stories covered**: Notification preferences

---

## Child issue draft 1

### Saved search CRUD (Create, Read, Update, Delete)

## Parent

#4100

## What to build

Implement the ability for users to create, view, update, and delete saved searches from the search page. This includes UI, backend, and persistence layers.

## Type

AFK

## Acceptance criteria

- [ ] Users can create a saved search from the search page
- [ ] Users can view a list of their saved searches
- [ ] Users can update and delete saved searches

## Verification

- [ ] Tests pass: `python3 -m unittest tests/saved_searches/`
- [ ] Build succeeds: `python3 -m build`
- [ ] Manual check: Create, update, and delete a saved search via the UI

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W1
- Ready to start when: this issue has no blockers, or every issue listed in `Blocked by` is closed

## User stories covered

Saved search management

## Files likely touched

- `search/views.py`
- `search/models.py`
- `search/templates/search/`
- `tests/saved_searches/`

## Estimated scope

Medium: 3-5 files

---

## Child issue draft 2

### Alert delivery for saved searches

## Parent

#4100

## What to build

Enable email alerts for users when results of their saved searches change. Integrate with the notification system and ensure delivery reliability.

## Type

AFK

## Acceptance criteria

- [ ] Users receive email alerts when saved search results change
- [ ] Alerts are sent only for active saved searches
- [ ] Delivery failures are logged

## Verification

- [ ] Tests pass: `python3 -m unittest tests/alerts/`
- [ ] Build succeeds: `python3 -m build`
- [ ] Manual check: Trigger a saved search change and verify email delivery

## Blocked by

- Blocked by #<child-1>

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W2
- Ready to start when: #<child-1> is closed

## User stories covered

Alert notifications

## Files likely touched

- `alerts/engine.py`
- `alerts/email.py`
- `tests/alerts/`

## Estimated scope

Medium: 3-5 files

---

## Child issue draft 3

### Pause/resume alerts for saved searches

## Parent

#4100

## What to build

Allow users to pause and resume alerts for their saved searches without deleting the search. Update UI and backend to support this toggle.

## Type

AFK

## Acceptance criteria

- [ ] Users can pause alerts for a saved search
- [ ] Users can resume alerts for a saved search
- [ ] Paused alerts do not trigger notifications

## Verification

- [ ] Tests pass: `python3 -m unittest tests/alerts/`
- [ ] Build succeeds: `python3 -m build`
- [ ] Manual check: Pause and resume alerts, verify no emails are sent while paused

## Blocked by

- Blocked by #<child-2>

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W3
- Ready to start when: #<child-2> is closed

## User stories covered

Alert management

## Files likely touched

- `alerts/models.py`
- `alerts/views.py`
- `search/templates/search/`
- `tests/alerts/`

## Estimated scope

Small: 1-2 files

---

## Child issue draft 4

### Edit notification preferences for saved search alerts

## Parent

#4100

## What to build

Allow users to edit notification preferences (e.g., frequency, channels) for saved search alerts. UI and backend changes required.

## Type

AFK

## Acceptance criteria

- [ ] Users can change alert frequency and channels
- [ ] Changes take effect without requiring search deletion
- [ ] Preferences are persisted

## Verification

- [ ] Tests pass: `python3 -m unittest tests/alerts/`
- [ ] Build succeeds: `python3 -m build`
- [ ] Manual check: Edit preferences and verify correct alert behavior

## Blocked by

- Blocked by #<child-3>

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W4
- Ready to start when: #<child-3> is closed

## User stories covered

Notification preferences

## Files likely touched

- `alerts/models.py`
- `alerts/views.py`
- `search/templates/search/`
- `tests/alerts/`

## Estimated scope

Small: 1-2 files

---

<!-- prd-to-tasks:start -->

## Task graph

- [ ] W1 - #<child-1> Saved search CRUD (Create, Read, Update, Delete) - AFK - blocked by none
- [ ] W2 - #<child-2> Alert delivery for saved searches - AFK - blocked by #<child-1>
- [ ] W3 - #<child-3> Pause/resume alerts for saved searches - AFK - blocked by #<child-2>
- [ ] W4 - #<child-4> Edit notification preferences for saved search alerts - AFK - blocked by #<child-3>

## How to grab work

1. Open this parent issue and inspect its direct subissues.
2. The executable work is in the sibling implementation issues listed above.
3. Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
4. If several AFK issues are ready in the same wave, they may be worked in parallel.
5. Do not start HITL issues until the named human decision or review has happened.
<!-- prd-to-tasks:end -->

---

## Subissue attachment commands

```bash
PARENT_ISSUE_ID=$(gh issue view 4100 --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view <child-1> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"
# Repeat for each child issue
```

---

Created task graph for saved searches, alerts, and notification preferences.

Parent: #4100 Saved searches, alerts, and notification preferences

Child issues:

1. #<child-1> Saved search CRUD (Create, Read, Update, Delete) - W1 - AFK - blocked by none
2. #<child-2> Alert delivery for saved searches - W2 - AFK - blocked by #<child-1>
3. #<child-3> Pause/resume alerts for saved searches - W3 - AFK - blocked by #<child-2>
4. #<child-4> Edit notification preferences for saved search alerts - W4 - AFK - blocked by #<child-3>

How to grab work:

- Open parent #4100 and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- If the parent issue already existed, read the managed `Task graph` / `How to grab work` section in its body.

Notes:

- Notification preference edits are not a blocker for initial saved search creation.
- Shipping saved-search CRUD before alert delivery is acceptable.
