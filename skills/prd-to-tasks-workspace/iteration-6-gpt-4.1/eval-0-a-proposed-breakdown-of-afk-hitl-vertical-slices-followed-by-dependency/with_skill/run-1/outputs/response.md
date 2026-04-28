# Draft: PRD to Tasks Breakdown for Issue #4100

## Proposed vertical-slice breakdown (present first)

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
   **Blocked by**: Slice 2: Alert delivery for saved searches
   **User stories covered**: Alert management

4. **Title**: Edit notification preferences for alerts
   **Type**: AFK
   **Execution wave**: W4
   **Blocked by**: Slice 3: Pause/resume alerts for saved searches
   **User stories covered**: Notification preferences

---

## Child issue drafts

### 1. Saved search CRUD (Create, Read, Update, Delete)

```markdown
## Parent

#4100

## What to build

Implement the ability for users to create, view, update, and delete saved searches from the search page.

## Type

AFK

## Acceptance criteria

- [ ] Users can create a saved search from the search page
- [ ] Users can view a list of their saved searches
- [ ] Users can update an existing saved search
- [ ] Users can delete a saved search

## Verification

- [ ] Tests pass: `<targeted backend and UI test command>`
- [ ] Build succeeds: `<relevant build command, if known and applicable>`
- [ ] Manual check: Create, view, update, and delete a saved search via the UI

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W1
- Ready to start when: this issue has no blockers, or every issue listed in `Blocked by` is closed

## User stories covered

Saved search management

## Files likely touched

- `src/search/savedSearches.ts`
- `src/ui/SearchPage.tsx`
- `tests/search/savedSearches.test.ts`

## Estimated scope

Medium: 3-5 files
```

### 2. Alert delivery for saved searches

```markdown
## Parent

#4100

## What to build

Enable email alerts to be sent to users when results of their saved searches change.

## Type

AFK

## Acceptance criteria

- [ ] Users receive email alerts when saved search results change
- [ ] Alerts are only sent for active saved searches

## Verification

- [ ] Tests pass: `<targeted backend and notification test command>`
- [ ] Build succeeds: `<relevant build command, if known and applicable>`
- [ ] Manual check: Trigger a saved search result change and verify email delivery

## Blocked by

- Blocked by #<child-1>

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W2
- Ready to start when: every issue listed in `Blocked by` is closed

## User stories covered

Alert notifications

## Files likely touched

- `src/alerts/alertDelivery.ts`
- `src/notifications/email.ts`
- `tests/alerts/alertDelivery.test.ts`

## Estimated scope

Medium: 3-5 files
```

### 3. Pause/resume alerts for saved searches

```markdown
## Parent

#4100

## What to build

Allow users to pause and resume alerts for their saved searches without deleting the saved search.

## Type

AFK

## Acceptance criteria

- [ ] Users can pause alerts for a saved search
- [ ] Users can resume alerts for a saved search
- [ ] Paused alerts do not trigger notifications

## Verification

- [ ] Tests pass: `<targeted backend and UI test command>`
- [ ] Build succeeds: `<relevant build command, if known and applicable>`
- [ ] Manual check: Pause and resume alerts, verify no emails are sent while paused

## Blocked by

- Blocked by #<child-2>

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W3
- Ready to start when: every issue listed in `Blocked by` is closed

## User stories covered

Alert management

## Files likely touched

- `src/alerts/alertSettings.ts`
- `src/ui/AlertControls.tsx`
- `tests/alerts/alertSettings.test.ts`

## Estimated scope

Small: 1-2 files
```

### 4. Edit notification preferences for alerts

```markdown
## Parent

#4100

## What to build

Allow users to edit notification preferences (e.g., frequency, channels) for their saved search alerts.

## Type

AFK

## Acceptance criteria

- [ ] Users can change the frequency of alert notifications
- [ ] Users can select notification channels (e.g., email, SMS)
- [ ] Changes apply without requiring saved search recreation

## Verification

- [ ] Tests pass: `<targeted backend and UI test command>`
- [ ] Build succeeds: `<relevant build command, if known and applicable>`
- [ ] Manual check: Edit preferences and verify correct alert delivery

## Blocked by

- Blocked by #<child-3>

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W4
- Ready to start when: every issue listed in `Blocked by` is closed

## User stories covered

Notification preferences

## Files likely touched

- `src/alerts/notificationPreferences.ts`
- `src/ui/NotificationSettings.tsx`
- `tests/alerts/notificationPreferences.test.ts`

## Estimated scope

Small: 1-2 files
```

---

## Managed parent-body block

```markdown
<!-- prd-to-tasks:start -->

## Task graph

- [ ] W1 - #<child-1> Saved search CRUD (Create, Read, Update, Delete) - AFK - blocked by none
- [ ] W2 - #<child-2> Alert delivery for saved searches - AFK - blocked by #<child-1>
- [ ] W3 - #<child-3> Pause/resume alerts for saved searches - AFK - blocked by #<child-2>
- [ ] W4 - #<child-4> Edit notification preferences for alerts - AFK - blocked by #<child-3>

## How to grab work

1. Open this parent issue and inspect its direct subissues.
2. The executable work is in the sibling implementation issues listed above.
3. Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
4. If several AFK issues are ready in the same wave, they may be worked in parallel.
5. Do not start HITL issues until the named human decision or review has happened.
<!-- prd-to-tasks:end -->
```

---

## Subissue attachment commands (draft)

```bash
PARENT_ISSUE_ID=$(gh issue view 4100 --json id --jq .id)
CHILD_ISSUE_ID_1=$(gh issue view <child-1> --json id --jq .id)
CHILD_ISSUE_ID_2=$(gh issue view <child-2> --json id --jq .id)
CHILD_ISSUE_ID_3=$(gh issue view <child-3> --json id --jq .id)
CHILD_ISSUE_ID_4=$(gh issue view <child-4> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID_1\"}) { issue { number } }
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID_2\"}) { issue { number } }
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID_3\"}) { issue { number } }
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID_4\"}) { issue { number } }
}"
```

---

## Final summary

```markdown
Created task graph for saved search CRUD, alert delivery, alert pause/resume, and notification preferences.

Parent: #4100 Saved searches and alerts

Child issues:

1. #<child-1> Saved search CRUD (Create, Read, Update, Delete) - W1 - AFK - blocked by none
2. #<child-2> Alert delivery for saved searches - W2 - AFK - blocked by #<child-1>
3. #<child-3> Pause/resume alerts for saved searches - W3 - AFK - blocked by #<child-2>
4. #<child-4> Edit notification preferences for alerts - W4 - AFK - blocked by #<child-3>

How to grab work:

- Open parent #4100 and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- If the parent issue already existed, read the managed `Task graph` / `How to grab work` section in its body.

Notes:

- Notification preference edits are not a blocker for initial saved search creation.
- Alert delivery is allowed to ship after saved-search CRUD.
- All slices are AFK; no HITL slices required.
```
