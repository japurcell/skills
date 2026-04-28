1. **Title**: Save current search from the search page
   **Type**: AFK
   **Execution wave**: W1
   **Blocked by**: None
   **User stories covered**: Saved searches can be created from the search page
2. **Title**: Manage saved searches from My Searches
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Save current search from the search page
   **User stories covered**: Saved-search CRUD
3. **Title**: Send email alerts for saved searches
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Save current search from the search page
   **User stories covered**: Alerts can email users when results change
4. **Title**: Pause saved-search alerts without deleting the search
   **Type**: AFK
   **Execution wave**: W3
   **Blocked by**: Slice 3: Send email alerts for saved searches
   **User stories covered**: Users need a way to pause alerts without deleting the saved search
5. **Title**: Edit saved-search notification preferences
   **Type**: AFK
   **Execution wave**: W3
   **Blocked by**: Slice 3: Send email alerts for saved searches
   **User stories covered**: Notification preference edits should not block initial saved-search creation

Assuming this breakdown is approved, here is the drafted child-issue set for the existing immutable parent #<parent-issue-number>.

## Draft child issues

### Child issue 1
**Title**: Save current search from the search page

```markdown
## Parent

#<parent-issue-number>

## What to build

Add an end-to-end save flow on the search page so a signed-in user can persist the current search criteria as a saved search without leaving the page.

## Type

AFK

## Acceptance criteria

- [ ] A user can save the currently configured search from the search page and get a success state tied to the persisted saved search.
- [ ] The saved search is associated with the current user and stores the search inputs needed to rerun it later.
- [ ] Duplicate-save handling is defined in-product so the user either updates the existing saved search or gets a clear validation error.

## Verification

- [ ] Tests pass: `<targeted saved-search creation test command>`
- [ ] Build succeeds: `<project build command>`
- [ ] Manual check: create a saved search from the search page and confirm it appears in the user’s saved-search collection.

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers
- Parallel rule: if multiple AFK issues are ready in W1, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Saved searches can be created from the search page

## Files likely touched

- `frontend/search/*`
- `backend/saved-searches/*`
- `tests/saved-searches/*`

## Estimated scope

Medium: 3-5 files
```

### Child issue 2
**Title**: Manage saved searches from My Searches

```markdown
## Parent

#<parent-issue-number>

## What to build

Add a saved-search management surface where a user can view existing saved searches, update saved-search metadata or query details, and delete a saved search they no longer want.

## Type

AFK

## Acceptance criteria

- [ ] A user can open a saved-search management surface and see their saved searches with enough detail to identify each one.
- [ ] A user can edit supported saved-search details and the updated state is reflected the next time the saved search is loaded.
- [ ] A user can delete a saved search and it no longer appears in the management surface.

## Verification

- [ ] Tests pass: `<targeted saved-search CRUD test command>`
- [ ] Build succeeds: `<project build command>`
- [ ] Manual check: list, edit, and delete a saved search from the management surface.

## Blocked by

- Blocked by #<child-1-number>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<child-1-number> is closed
- Parallel rule: if multiple AFK issues are ready in W2, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Saved-search CRUD

## Files likely touched

- `frontend/saved-searches/*`
- `backend/saved-searches/*`
- `tests/saved-searches/*`

## Estimated scope

Medium: 3-5 files
```

### Child issue 3
**Title**: Send email alerts for saved searches

```markdown
## Parent

#<parent-issue-number>

## What to build

Add the alerting path that detects when a saved search’s results change and sends an email notification to the owning user.

## Type

AFK

## Acceptance criteria

- [ ] The system evaluates saved searches for result changes and identifies when an email alert should be sent.
- [ ] A user receives an email for a saved search only when qualifying result changes occur.
- [ ] Alert delivery is recorded so repeat evaluations do not send duplicate emails for the same unchanged result set.

## Verification

- [ ] Tests pass: `<targeted saved-search alert delivery test command>`
- [ ] Build succeeds: `<project build command>`
- [ ] Manual check: trigger a result change for a saved search and confirm one email is sent.

## Blocked by

- Blocked by #<child-1-number>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<child-1-number> is closed
- Parallel rule: if multiple AFK issues are ready in W2, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Alerts can email users when results change

## Files likely touched

- `backend/saved-search-alerts/*`
- `backend/notifications/*`
- `tests/saved-search-alerts/*`

## Estimated scope

Medium: 3-5 files
```

### Child issue 4
**Title**: Pause saved-search alerts without deleting the search

```markdown
## Parent

#<parent-issue-number>

## What to build

Add a pause/resume control for saved-search alerts so a user can stop email delivery temporarily while keeping the saved search itself intact.

## Type

AFK

## Acceptance criteria

- [ ] A user can pause alert delivery for a saved search without deleting or changing the saved search definition.
- [ ] A paused saved search does not send alert emails while paused.
- [ ] A user can resume alert delivery and future qualifying result changes send alerts again.

## Verification

- [ ] Tests pass: `<targeted saved-search pause alert test command>`
- [ ] Build succeeds: `<project build command>`
- [ ] Manual check: pause a saved-search alert, verify no email is sent while paused, then resume and verify alerts resume.

## Blocked by

- Blocked by #<child-3-number>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W3
- Ready to start when: #<child-3-number> is closed
- Parallel rule: if multiple AFK issues are ready in W3, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Users need a way to pause alerts without deleting the saved search

## Files likely touched

- `frontend/saved-searches/*`
- `backend/saved-search-alerts/*`
- `tests/saved-search-alerts/*`

## Estimated scope

Small: 1-2 files
```

### Child issue 5
**Title**: Edit saved-search notification preferences

```markdown
## Parent

#<parent-issue-number>

## What to build

Add a notification-preferences edit path for saved-search alerts so users can adjust alert-related preferences after saved-search creation instead of blocking the initial save flow.

## Type

AFK

## Acceptance criteria

- [ ] A user can edit saved-search alert preferences after the saved search exists.
- [ ] Preference changes are respected by subsequent saved-search alert evaluations and deliveries.
- [ ] Initial saved-search creation still succeeds without requiring the user to visit or complete the preference-edit flow.

## Verification

- [ ] Tests pass: `<targeted saved-search notification preference test command>`
- [ ] Build succeeds: `<project build command>`
- [ ] Manual check: create a saved search without editing preferences, then change preferences and confirm later alerts follow the new settings.

## Blocked by

- Blocked by #<child-3-number>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W3
- Ready to start when: #<child-3-number> is closed
- Parallel rule: if multiple AFK issues are ready in W3, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Notification preference edits should not block initial saved-search creation

## Files likely touched

- `frontend/notification-preferences/*`
- `backend/notifications/*`
- `tests/notification-preferences/*`

## Estimated scope

Small: 1-2 files
```

## Draft queue-guide child issue

**Title**: How to grab work: saved search alerts

```markdown
## Parent

#<parent-issue-number>

## Purpose

This issue documents how to grab implementation work from parent #<parent-issue-number>. Do not implement this issue itself.

## Executable subissues

1. W1 - #<child-1-number> Save current search from the search page - AFK - blocked by none
2. W2 - #<child-2-number> Manage saved searches from My Searches - AFK - blocked by #<child-1-number>
3. W2 - #<child-3-number> Send email alerts for saved searches - AFK - blocked by #<child-1-number>
4. W3 - #<child-4-number> Pause saved-search alerts without deleting the search - AFK - blocked by #<child-3-number>
5. W3 - #<child-5-number> Edit saved-search notification preferences - AFK - blocked by #<child-3-number>

## How to grab work

1. Open parent #<parent-issue-number> and inspect its subissues.
2. The executable work is in the sibling implementation issues listed above; this queue-guide issue is documentation only.
3. Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
4. The current next AFK task is #<child-1-number> Save current search from the search page.
5. After #<child-1-number> closes, #<child-2-number> and #<child-3-number> may be worked in parallel.
6. Do not start HITL issues until the named human decision or review has happened.
```

## Draft commands (dry run only; do not execute)

Create the child issues in dependency order, then create the queue-guide issue:

```bash
gh issue create --title "Save current search from the search page" --body-file issue-1.md
gh issue create --title "Manage saved searches from My Searches" --body-file issue-2.md
gh issue create --title "Send email alerts for saved searches" --body-file issue-3.md
gh issue create --title "Pause saved-search alerts without deleting the search" --body-file issue-4.md
gh issue create --title "Edit saved-search notification preferences" --body-file issue-5.md
gh issue create --title "How to grab work: saved search alerts" --body-file queue-guide.md
```

Attach each created issue directly to the existing parent issue (do not nest implementation issues under the queue-guide issue):

```bash
PARENT_ISSUE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view <child-1-number> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: "$PARENT_ISSUE_ID", subIssueId: "$CHILD_ISSUE_ID"}) {
    issue { number }
  }
}"

CHILD_ISSUE_ID=$(gh issue view <child-2-number> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: "$PARENT_ISSUE_ID", subIssueId: "$CHILD_ISSUE_ID"}) {
    issue { number }
  }
}"

CHILD_ISSUE_ID=$(gh issue view <child-3-number> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: "$PARENT_ISSUE_ID", subIssueId: "$CHILD_ISSUE_ID"}) {
    issue { number }
  }
}"

CHILD_ISSUE_ID=$(gh issue view <child-4-number> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: "$PARENT_ISSUE_ID", subIssueId: "$CHILD_ISSUE_ID"}) {
    issue { number }
  }
}"

CHILD_ISSUE_ID=$(gh issue view <child-5-number> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: "$PARENT_ISSUE_ID", subIssueId: "$CHILD_ISSUE_ID"}) {
    issue { number }
  }
}"

CHILD_ISSUE_ID=$(gh issue view <queue-guide-number> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: "$PARENT_ISSUE_ID", subIssueId: "$CHILD_ISSUE_ID"}) {
    issue { number }
  }
}"
```

Created task graph for the existing saved-search parent issue.

Parent: #<parent-issue-number> <existing immutable parent title>

Child issues:
1. #<child-1-number> Save current search from the search page - W1 - AFK - blocked by none
2. #<child-2-number> Manage saved searches from My Searches - W2 - AFK - blocked by #<child-1-number>
3. #<child-3-number> Send email alerts for saved searches - W2 - AFK - blocked by #<child-1-number>
4. #<child-4-number> Pause saved-search alerts without deleting the search - W3 - AFK - blocked by #<child-3-number>
5. #<child-5-number> Edit saved-search notification preferences - W3 - AFK - blocked by #<child-3-number>
6. #<queue-guide-number> How to grab work: saved search alerts - documentation only - blocked by none

How to grab work:
- Open parent #<parent-issue-number> and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- If a queue-guide issue was created, read it first and do not implement it.

Notes:
- The parent issue was treated as immutable.
- The executable work remains in the parent issue’s sibling direct subissues; the queue-guide issue is documentation only.
- The current next AFK task is #<child-1-number> Save current search from the search page.
