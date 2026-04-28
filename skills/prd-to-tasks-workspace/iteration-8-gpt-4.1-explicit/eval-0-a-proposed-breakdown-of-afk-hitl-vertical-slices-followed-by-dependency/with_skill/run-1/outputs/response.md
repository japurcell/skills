## Proposed vertical-slice breakdown (present first)

1. **Title**: Saved search CRUD (create, read, update, delete)
   **Type**: AFK
   **Execution wave**: W1
   **Blocked by**: None
   **User stories covered**: Saved search management
2. **Title**: Alert delivery for saved searches
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Saved search CRUD
   **User stories covered**: Email alerts for saved search changes
3. **Title**: Pause/resume alerts for saved searches
   **Type**: AFK
   **Execution wave**: W3
   **Blocked by**: Slice 2: Alert delivery for saved searches
   **User stories covered**: Pausing alerts without deleting saved search
4. **Title**: Edit notification preferences for saved searches
   **Type**: AFK
   **Execution wave**: W4
   **Blocked by**: Slice 3: Pause/resume alerts for saved searches
   **User stories covered**: Notification preference edits

---

## Child issue draft 1

## Parent

#4100

## What to build

Implement CRUD (create, read, update, delete) operations for saved searches from the search page, allowing users to manage their saved searches.

## Type

AFK

## Acceptance criteria

- [ ] Users can create a saved search from the search page
- [ ] Users can view a list of their saved searches
- [ ] Users can update the name or parameters of a saved search
- [ ] Users can delete a saved search

## Verification

- [ ] Tests pass: `targeted backend and UI test command`
- [ ] Build succeeds: `relevant build command, if known`
- [ ] Manual check: User can perform CRUD actions from the search page UI

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

---

## Child issue draft 2

## Parent

#4100

## What to build

Implement alert delivery for saved searches: when results change, send email alerts to users based on their saved search criteria.

## Type

AFK

## Acceptance criteria

- [ ] System detects changes in saved search results
- [ ] Email alerts are sent to users when results change
- [ ] Alerts are only sent for active saved searches

## Verification

- [ ] Tests pass: `targeted backend and email delivery test command`
- [ ] Build succeeds: `relevant build command, if known`
- [ ] Manual check: User receives email when saved search results change

## Blocked by

- Blocked by #<child-1>

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W2
- Ready to start when: every issue listed in `Blocked by` is closed

## User stories covered

Email alerts for saved search changes

## Files likely touched

- `src/alerts/alertDelivery.ts`
- `src/search/savedSearches.ts`
- `tests/alerts/alertDelivery.test.ts`

## Estimated scope

Medium: 3-5 files

---

## Child issue draft 3

## Parent

#4100

## What to build

Allow users to pause and resume alerts for a saved search without deleting the saved search itself.

## Type

AFK

## Acceptance criteria

- [ ] Users can pause alerts for a saved search
- [ ] Users can resume alerts for a saved search
- [ ] Paused searches do not trigger email alerts

## Verification

- [ ] Tests pass: `targeted backend and UI test command`
- [ ] Build succeeds: `relevant build command, if known`
- [ ] Manual check: User can pause/resume alerts and verify no emails are sent when paused

## Blocked by

- Blocked by #<child-2>

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W3
- Ready to start when: every issue listed in `Blocked by` is closed

## User stories covered

Pausing alerts without deleting saved search

## Files likely touched

- `src/alerts/alertDelivery.ts`
- `src/ui/SavedSearches.tsx`
- `tests/alerts/alertDelivery.test.ts`

## Estimated scope

Small: 1-2 files

---

## Child issue draft 4

## Parent

#4100

## What to build

Enable users to edit notification preferences for saved searches (e.g., frequency, channels), without blocking initial saved-search creation.

## Type

AFK

## Acceptance criteria

- [ ] Users can edit notification frequency for a saved search
- [ ] Users can change notification channels (e.g., email, in-app)
- [ ] Changes apply without affecting saved search existence

## Verification

- [ ] Tests pass: `targeted backend and UI test command`
- [ ] Build succeeds: `relevant build command, if known`
- [ ] Manual check: User can edit preferences and see changes reflected in alert delivery

## Blocked by

- Blocked by #<child-3>

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W4
- Ready to start when: every issue listed in `Blocked by` is closed

## User stories covered

Notification preference edits

## Files likely touched

- `src/alerts/alertPreferences.ts`
- `src/ui/SavedSearches.tsx`
- `tests/alerts/alertPreferences.test.ts`

## Estimated scope

Small: 1-2 files

---

<!-- prd-to-tasks:start -->

## Task graph

- [ ] W1 - #<child-1> Saved search CRUD (create, read, update, delete) - AFK - blocked by none
- [ ] W2 - #<child-2> Alert delivery for saved searches - AFK - blocked by #<child-1>
- [ ] W3 - #<child-3> Pause/resume alerts for saved searches - AFK - blocked by #<child-2>
- [ ] W4 - #<child-4> Edit notification preferences for saved searches - AFK - blocked by #<child-3>

## How to grab work

1. Open this parent issue and inspect its direct subissues.
2. The executable work is in the sibling implementation issues listed above.
3. Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
4. If several AFK issues are ready in the same wave, they may be worked in parallel.
5. Do not start HITL issues until the named human decision or review has happened.
<!-- prd-to-tasks:end -->

---

```bash
# Attach child issues to parent (draft placeholders)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"
```

---

Created task graph for saved search CRUD, alert delivery, alert pause/resume, and notification preference edits.

Parent: #4100 Saved searches, alerts, and alert pause

Child issues:

1. #<child-1> Saved search CRUD (create, read, update, delete) - W1 - AFK - blocked by none
2. #<child-2> Alert delivery for saved searches - W2 - AFK - blocked by #<child-1>
3. #<child-3> Pause/resume alerts for saved searches - W3 - AFK - blocked by #<child-2>
4. #<child-4> Edit notification preferences for saved searches - W4 - AFK - blocked by #<child-3>

How to grab work:

- Open parent #4100 and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- Read the managed `Task graph` / `How to grab work` section in its body.

Notes:

- No HITL slices required; all are AFK.
- No new tracker issue created; all work is direct subissues of #4100.
- Notification preference edits do not block initial saved-search creation.
- Shipping saved-search CRUD before alert delivery is acceptable.
