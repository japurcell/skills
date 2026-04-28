## Proposed vertical-slice breakdown (present first)

1. **Title**: Create saved search CRUD interface
   **Type**: AFK
   **Execution wave**: W1
   **Blocked by**: None
   **User stories covered**: Save search criteria and retrieve saved searches

2. **Title**: Add email alert delivery for saved searches
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Create saved search CRUD interface
   **User stories covered**: Email users when search results change

3. **Title**: Implement alert pause capability
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Create saved search CRUD interface
   **User stories covered**: Users can pause alerts without deleting saved search

4. **Title**: Notification preference editing (decoupled from saved search)
   **Type**: AFK
   **Execution wave**: W3
   **Blocked by**: None
   **User stories covered**: Users can configure notification preferences independently

## Child issue drafts

### Child 1: Create saved search CRUD interface

## Parent

#4100

## What to build

Users can create, read, update, and delete saved searches from the search page. A saved search stores search criteria (filters, query, date range) and can be retrieved later.

## Type

AFK

## Acceptance criteria

- [ ] Users can save current search state with a name
- [ ] Users can view their saved searches
- [ ] Users can load a saved search to re-run it
- [ ] Users can delete a saved search

## Verification

- [ ] Tests pass: `npm run test -- saved-search.test.ts`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Create, retrieve, and delete a saved search via the UI

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W1
- Ready to start when: this issue has no blockers

## User stories covered

Save search criteria and retrieve saved searches

## Files likely touched

- `src/features/search/SavedSearch.tsx`
- `src/api/savedSearches.ts`
- `src/db/migrations/saved_searches_table.sql`
- `tests/features/search/SavedSearch.test.ts`

## Estimated scope

Medium: 3-5 files

### Child 2: Add email alert delivery for saved searches

## Parent

#4100

## What to build

When a saved search's results change (based on polling or webhook), the system emails the users who have alerts enabled for that saved search with a digest of new results.

## Type

AFK

## Acceptance criteria

- [ ] Changes to saved search results trigger alert generation
- [ ] Email delivery includes new/changed results since last alert
- [ ] Users receive emails at configurable frequency

## Verification

- [ ] Tests pass: `npm run test -- emailAlert.test.ts`
- [ ] Manual check: Trigger a result change and verify email receipt

## Blocked by

- Blocked by #<child-1-issue-number>

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W2
- Ready to start when: #4100's direct child issue for saved search CRUD is closed

## User stories covered

Email users when search results change

## Files likely touched

- `src/workers/alertWorker.ts`
- `src/services/emailService.ts`
- `src/db/models/SavedAlert.ts`
- `tests/workers/alertWorker.test.ts`

## Estimated scope

Medium: 3-5 files

### Child 3: Implement alert pause capability

## Parent

#4100

## What to build

Users can pause an alert without deleting the saved search. A paused alert will not generate or send email notifications, but the saved search remains available for later use.

## Type

AFK

## Acceptance criteria

- [ ] Users can pause/unpause an alert from saved search detail
- [ ] Paused alerts do not generate notifications
- [ ] Paused alerts can be resumed later

## Verification

- [ ] Tests pass: `npm run test -- alertPause.test.ts`
- [ ] Manual check: Pause an alert and verify no emails are sent

## Blocked by

- Blocked by #<child-1-issue-number>

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W2
- Ready to start when: #4100's direct child issue for saved search CRUD is closed

## User stories covered

Users can pause alerts without deleting the saved search

## Files likely touched

- `src/features/search/AlertControls.tsx`
- `src/db/models/SavedAlert.ts`
- `tests/features/search/AlertControls.test.ts`

## Estimated scope

Small: 1-2 files

### Child 4: Notification preference editing (decoupled from saved search)

## Parent

#4100

## What to build

Users can edit global notification preferences (frequency, channels, quiet hours) without affecting saved search creation. These preferences apply across all alerts.

## Type

AFK

## Acceptance criteria

- [ ] Users can access notification preferences settings
- [ ] Preferences include email frequency and quiet hours
- [ ] Changes take effect immediately

## Verification

- [ ] Tests pass: `npm run test -- notificationPreferences.test.ts`
- [ ] Manual check: Update preferences and verify they apply to new alerts

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W3
- Ready to start when: this issue has no blockers

## User stories covered

Users can configure notification preferences independently

## Files likely touched

- `src/features/settings/NotificationPreferences.tsx`
- `src/api/userPreferences.ts`
- `tests/features/settings/NotificationPreferences.test.ts`

## Estimated scope

Small: 1-2 files

## Managed parent-body tracking guidance

<!-- prd-to-tasks:start -->

## Task graph

- [ ] W1 - #<child-1> Create saved search CRUD interface - AFK - blocked by none
- [ ] W2 - #<child-2> Add email alert delivery for saved searches - AFK - blocked by #<child-1>
- [ ] W2 - #<child-3> Implement alert pause capability - AFK - blocked by #<child-1>
- [ ] W3 - #<child-4> Notification preference editing - AFK - blocked by none

## How to grab work

1. Open this parent issue and inspect its direct subissues.
2. The executable work is in the sibling implementation issues listed above.
3. Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
4. If several AFK issues are ready in the same wave, they may be worked in parallel.
5. Do not start HITL issues until the named human decision or review has happened.

<!-- prd-to-tasks:end -->

## Subissue attachment commands

```bash
PARENT_ISSUE_ID=$(gh issue view 4100 --json id --jq .id)
CHILD_1_ID=$(gh issue view <child-1-issue-number> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_1_ID\"}) {
    issue { number }
  }
}"
# Repeat for each child issue
```

---

## Summary

Created task graph for saved searches and alerts feature.

Parent: #4100 (existing)

Child issues:
1. #<child-1> Create saved search CRUD interface - W1 - AFK - blocked by none
2. #<child-2> Add email alert delivery for saved searches - W2 - AFK - blocked by #<child-1>
3. #<child-3> Implement alert pause capability - W2 - AFK - blocked by #<child-1>
4. #<child-4> Notification preference editing - W3 - AFK - blocked by none

How to grab work:

- Open parent #4100 and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- The managed `Task graph` / `How to grab work` section in the parent body makes the queue explicit.

Notes:

- Saved search CRUD (W1) comes before alert delivery (W2) per existing issue requirements
- Notification preference editing (W4) is decoupled and can happen independently per comment constraint
- All child issues are vertical slices: saved search → alert delivery → pause capability → preferences
- No wrapper or queue-guide issue was created; guidance is managed in the parent's body only
