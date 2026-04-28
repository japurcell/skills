## Proposed vertical-slice breakdown (present first)

1. **Title**: Saved search CRUD (create, read, update, delete)
   **Type**: AFK
   **Execution wave**: W1
   **Blocked by**: None
   **User stories covered**: Not explicit in source
2. **Title**: Alert delivery for saved searches
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Saved search CRUD
   **User stories covered**: Not explicit in source
3. **Title**: Pause/resume alerts for saved searches
   **Type**: AFK
   **Execution wave**: W3
   **Blocked by**: Slice 2: Alert delivery for saved searches
   **User stories covered**: Not explicit in source
4. **Title**: Edit notification preferences for saved searches
   **Type**: AFK
   **Execution wave**: W4
   **Blocked by**: Slice 3: Pause/resume alerts for saved searches
   **User stories covered**: Not explicit in source

---

### Child Issue Drafts

---
#### Saved search CRUD (create, read, update, delete)

```
## Parent

#4100

## What to build

Implement the ability for users to create, read, update, and delete saved searches from the search page.

## Type

AFK

## Acceptance criteria

- [ ] Users can create a saved search from the search page
- [ ] Users can view their saved searches
- [ ] Users can update an existing saved search
- [ ] Users can delete a saved search

## Verification

- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Create, update, and delete a saved search via the UI

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W1
- Ready to start when: this issue has no blockers

## User stories covered

Not explicit in source

## Files likely touched

- `src/search/savedSearches.ts`
- `src/search/SearchPage.tsx`
- `tests/search/savedSearches.test.ts`

## Estimated scope

Medium: 3-5 files
```

---
#### Alert delivery for saved searches

```
## Parent

#4100

## What to build

Enable alert delivery for saved searches, so users can receive email notifications when search results change.

## Type

AFK

## Acceptance criteria

- [ ] Users can opt in to receive alerts for a saved search
- [ ] Users receive email notifications when results change
- [ ] Alerts are only available for existing saved searches

## Verification

- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Receive an alert for a changed search result

## Blocked by

- Blocked by #<issue-number-for-saved-search-CRUD>

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W2
- Ready to start when: #<issue-number-for-saved-search-CRUD> is closed

## User stories covered

Not explicit in source

## Files likely touched

- `src/alerts/alertDelivery.ts`
- `src/search/savedSearches.ts`
- `tests/alerts/alertDelivery.test.ts`

## Estimated scope

Medium: 3-5 files
```

---
#### Pause/resume alerts for saved searches

```
## Parent

#4100

## What to build

Allow users to pause and resume alerts for their saved searches without deleting the saved search.

## Type

AFK

## Acceptance criteria

- [ ] Users can pause alerts for a saved search
- [ ] Users can resume alerts for a saved search
- [ ] Pausing alerts does not delete the saved search

## Verification

- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Pause and resume alerts for a saved search

## Blocked by

- Blocked by #<issue-number-for-alert-delivery>

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W3
- Ready to start when: #<issue-number-for-alert-delivery> is closed

## User stories covered

Not explicit in source

## Files likely touched

- `src/alerts/alertDelivery.ts`
- `src/search/savedSearches.ts`
- `tests/alerts/alertDelivery.test.ts`

## Estimated scope

Small: 1-2 files
```

---
#### Edit notification preferences for saved searches

```
## Parent

#4100

## What to build

Allow users to edit notification preferences for their saved searches (e.g., frequency, channels).

## Type

AFK

## Acceptance criteria

- [ ] Users can change notification frequency for a saved search
- [ ] Users can change notification channels (e.g., email, SMS) for a saved search
- [ ] Editing preferences does not block initial saved-search creation

## Verification

- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Edit notification preferences for a saved search

## Blocked by

- Blocked by #<issue-number-for-pause-resume-alerts>

## Queue position

- Parent queue: direct subissue of #4100
- Execution wave: W4
- Ready to start when: #<issue-number-for-pause-resume-alerts> is closed

## User stories covered

Not explicit in source

## Files likely touched

- `src/alerts/alertPreferences.ts`
- `src/search/savedSearches.ts`
- `tests/alerts/alertPreferences.test.ts`

## Estimated scope

Small: 1-2 files
```

---

### Managed parent-body block

```
<!-- prd-to-tasks:start -->
## Task graph

- [ ] W1 - #<issue-number-for-saved-search-CRUD> Saved search CRUD (create, read, update, delete) - AFK - blocked by none
- [ ] W2 - #<issue-number-for-alert-delivery> Alert delivery for saved searches - AFK - blocked by #<issue-number-for-saved-search-CRUD>
- [ ] W3 - #<issue-number-for-pause-resume-alerts> Pause/resume alerts for saved searches - AFK - blocked by #<issue-number-for-alert-delivery>
- [ ] W4 - #<issue-number-for-edit-notification-prefs> Edit notification preferences for saved searches - AFK - blocked by #<issue-number-for-pause-resume-alerts>

## How to grab work

1. Open this parent issue and inspect its direct subissues.
2. The executable work is in the sibling implementation issues listed above.
3. Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
4. If several AFK issues are ready in the same wave, they may be worked in parallel.
5. Do not start HITL issues until the named human decision or review has happened.
<!-- prd-to-tasks:end -->
```

---

### Subissue attachment commands (draft)

```
# For each child issue, after creation:
PARENT_ISSUE_ID=$(gh issue view 4100 --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view <child-issue-number> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"
```

---

### Summary

Created task graph for saved searches, alerts, and notification preferences.

Parent: #4100 (existing)

Child issues:

1. #<issue-number-for-saved-search-CRUD> Saved search CRUD (create, read, update, delete) - W1 - AFK - blocked by none
2. #<issue-number-for-alert-delivery> Alert delivery for saved searches - W2 - AFK - blocked by #<issue-number-for-saved-search-CRUD>
3. #<issue-number-for-pause-resume-alerts> Pause/resume alerts for saved searches - W3 - AFK - blocked by #<issue-number-for-alert-delivery>
4. #<issue-number-for-edit-notification-prefs> Edit notification preferences for saved searches - W4 - AFK - blocked by #<issue-number-for-pause-resume-alerts>

How to grab work:
- Open parent #4100 and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- Read the managed `Task graph` / `How to grab work` section in the parent issue body.

Notes:
- All issue numbers except #4100 are placeholders.
- No GitHub mutations or code implementations were performed (dry run).
