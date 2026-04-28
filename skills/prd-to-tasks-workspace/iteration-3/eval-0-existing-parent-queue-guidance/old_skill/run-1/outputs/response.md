Dry run only; no GitHub issues were created or edited. The assigned skill treats the existing parent issue as immutable, so placeholder issue numbers are used below.

## Proposed vertical-slice breakdown

1. **Title**: Create saved searches from the search page  
   **Type**: AFK  
   **Blocked by**: None  
   **User stories covered**: Users can create a saved search from the search page.
2. **Title**: View saved searches in a management page  
   **Type**: AFK  
   **Blocked by**: Slice 1: Create saved searches from the search page  
   **User stories covered**: Saved-search CRUD - read/list existing saved searches.
3. **Title**: Edit a saved search  
   **Type**: AFK  
   **Blocked by**: Slice 2: View saved searches in a management page  
   **User stories covered**: Saved-search CRUD - update an existing saved search.
4. **Title**: Delete a saved search  
   **Type**: AFK  
   **Blocked by**: Slice 2: View saved searches in a management page  
   **User stories covered**: Saved-search CRUD - delete an existing saved search.
5. **Title**: Send default email alerts when saved-search results change  
   **Type**: AFK  
   **Blocked by**: Slice 1: Create saved searches from the search page  
   **User stories covered**: Alerts can email users when results change.
6. **Title**: Pause alert delivery on a saved search  
   **Type**: AFK  
   **Blocked by**: Slice 2: View saved searches in a management page; Slice 5: Send default email alerts when saved-search results change  
   **User stories covered**: Users can pause alerts without deleting the saved search.
7. **Title**: Edit saved-search notification preferences  
   **Type**: AFK  
   **Blocked by**: Slice 2: View saved searches in a management page; Slice 5: Send default email alerts when saved-search results change  
   **User stories covered**: Notification preference edits should not block initial saved-search creation.

Review questions the skill would ask before real issue creation:
- Does the granularity feel right: too coarse, too fine, or about right?
- Are dependency relationships correct?
- Should any slices be merged or split further?
- Are the correct slices marked HITL and AFK?

Assuming that breakdown is approved for this dry run, here are the drafted child issues and commands.

## Issue graph

Parent: `#<existing-parent-issue-number>` (existing, immutable)

Child issues:
1. `#<child-1> Create saved searches from the search page` - AFK - blocked by none
2. `#<child-2> View saved searches in a management page` - AFK - blocked by `#<child-1>`
3. `#<child-3> Edit a saved search` - AFK - blocked by `#<child-2>`
4. `#<child-4> Delete a saved search` - AFK - blocked by `#<child-2>`
5. `#<child-5> Send default email alerts when saved-search results change` - AFK - blocked by `#<child-1>`
6. `#<child-6> Pause alert delivery on a saved search` - AFK - blocked by `#<child-2>`, `#<child-5>`
7. `#<child-7> Edit saved-search notification preferences` - AFK - blocked by `#<child-2>`, `#<child-5>`

## Draft child issues

### `#<child-1> Create saved searches from the search page`

```markdown
## Parent

#<existing-parent-issue-number>

## What to build

Add an end-to-end saved-search creation flow on the search page so a user can save the current query without leaving the search experience.

## Type

AFK

## Acceptance criteria

- [ ] A user can create a saved search from the search page using the current search query/context.
- [ ] The saved search persists and is available for later management and alerting flows.
- [ ] Automated coverage verifies successful creation and at least one invalid-input or duplicate-path case.

## Verification

- [ ] Tests pass: `<targeted test command>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: From the search page, save a query and confirm it appears as a persisted saved search.

## Blocked by

None - can start immediately

## User stories covered

Users can create a saved search from the search page.

## Files likely touched

- `search-page/*`
- `saved-searches/*`
- `api/*`
- `tests/*`

## Estimated scope

Medium: 3-5 files
```

### `#<child-2> View saved searches in a management page`

```markdown
## Parent

#<existing-parent-issue-number>

## What to build

Add a saved-search management view so users can see the saved searches they already created and open the entry point for later edit, delete, pause, and preference actions.

## Type

AFK

## Acceptance criteria

- [ ] A user can open a saved-search management view and see their existing saved searches.
- [ ] The view shows enough saved-search state for downstream actions, including whether alerts are active or paused when that data exists.
- [ ] Automated coverage verifies the list/read path and the empty-state behavior.

## Verification

- [ ] Tests pass: `<targeted test command>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: Create at least one saved search, open the management view, and confirm it is listed.

## Blocked by

- Blocked by #<child-1>

## User stories covered

Saved-search CRUD - read/list existing saved searches.

## Files likely touched

- `saved-searches/*`
- `account-or-settings/*`
- `api/*`
- `tests/*`

## Estimated scope

Medium: 3-5 files
```

### `#<child-3> Edit a saved search`

```markdown
## Parent

#<existing-parent-issue-number>

## What to build

Allow a user to update an existing saved search so the saved query remains useful without forcing deletion and recreation.

## Type

AFK

## Acceptance criteria

- [ ] A user can edit an existing saved search from the saved-search management flow.
- [ ] The updated saved search persists and is reflected in subsequent views and alert evaluation.
- [ ] Automated coverage verifies successful update behavior and invalid-edit handling.

## Verification

- [ ] Tests pass: `<targeted test command>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: Update a saved search and confirm the new definition is retained on reload.

## Blocked by

- Blocked by #<child-2>

## User stories covered

Saved-search CRUD - update an existing saved search.

## Files likely touched

- `saved-searches/*`
- `api/*`
- `tests/*`

## Estimated scope

Small: 1-2 files
```

### `#<child-4> Delete a saved search`

```markdown
## Parent

#<existing-parent-issue-number>

## What to build

Allow a user to delete an existing saved search from the management flow so obsolete searches can be removed cleanly.

## Type

AFK

## Acceptance criteria

- [ ] A user can delete a saved search from the saved-search management flow.
- [ ] Deleted saved searches no longer appear in the management view or participate in alert delivery.
- [ ] Automated coverage verifies the delete path and the post-delete state.

## Verification

- [ ] Tests pass: `<targeted test command>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: Delete a saved search and confirm it no longer appears or generates alert activity.

## Blocked by

- Blocked by #<child-2>

## User stories covered

Saved-search CRUD - delete an existing saved search.

## Files likely touched

- `saved-searches/*`
- `api/*`
- `tests/*`

## Estimated scope

Small: 1-2 files
```

### `#<child-5> Send default email alerts when saved-search results change`

```markdown
## Parent

#<existing-parent-issue-number>

## What to build

Add the default alert-delivery path so a saved search can email the user when the underlying results change, without requiring notification preference editing before the first saved search can be created.

## Type

AFK

## Acceptance criteria

- [ ] A saved search can trigger an email alert when its results change.
- [ ] The initial delivery flow works with a sensible default alert configuration and does not depend on a separate notification-preferences editor.
- [ ] Automated coverage verifies at least one changed-results alert path and one no-change path.

## Verification

- [ ] Tests pass: `<targeted test command>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: Create a saved search, cause its result set to change, and confirm an alert email is produced.

## Blocked by

- Blocked by #<child-1>

## User stories covered

Alerts can email users when results change.

## Files likely touched

- `saved-searches/*`
- `alerts-or-notifications/*`
- `jobs-or-workers/*`
- `mailers/*`
- `tests/*`

## Estimated scope

Medium: 3-5 files
```

### `#<child-6> Pause alert delivery on a saved search`

```markdown
## Parent

#<existing-parent-issue-number>

## What to build

Allow a user to pause alert delivery for an existing saved search without deleting the saved search itself, so the saved query remains available while emails stop.

## Type

AFK

## Acceptance criteria

- [ ] A user can pause alert delivery on an existing saved search from the saved-search management flow.
- [ ] A paused saved search remains visible and editable, but no alert emails are sent while it is paused.
- [ ] Automated coverage verifies the paused state and that resuming restores delivery behavior.

## Verification

- [ ] Tests pass: `<targeted test command>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: Pause a saved search with alerting enabled, confirm no emails are sent on change, then resume and confirm delivery returns.

## Blocked by

- Blocked by #<child-2>
- Blocked by #<child-5>

## User stories covered

Users can pause alerts without deleting the saved search.

## Files likely touched

- `saved-searches/*`
- `alerts-or-notifications/*`
- `jobs-or-workers/*`
- `tests/*`

## Estimated scope

Medium: 3-5 files
```

### `#<child-7> Edit saved-search notification preferences`

```markdown
## Parent

#<existing-parent-issue-number>

## What to build

Add a notification-preferences editing flow for saved-search alerts so users can change supported delivery settings after initial saved-search creation, without making that editor a prerequisite for the first saved-search flow.

## Type

AFK

## Acceptance criteria

- [ ] A user can edit the supported notification preferences for an existing saved-search alert.
- [ ] Initial saved-search creation remains available even if notification preference editing has not shipped yet.
- [ ] Automated coverage verifies preference updates persist and affect later alert delivery behavior.

## Verification

- [ ] Tests pass: `<targeted test command>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: Change a saved search's notification preferences and confirm the new settings are reflected on subsequent alert delivery.

## Blocked by

- Blocked by #<child-2>
- Blocked by #<child-5>

## User stories covered

Notification preference edits should not block initial saved-search creation.

## Files likely touched

- `saved-searches/*`
- `alerts-or-notifications/*`
- `account-or-settings/*`
- `tests/*`

## Estimated scope

Medium: 3-5 files
```

## Parent body update commands

None. The assigned skill says that when the source was a GitHub issue, that issue should be treated as the parent tracker and its body, title, labels, state, and other metadata should not be edited.

## Dry-run command draft

```bash
# create child issues in dependency order under the existing parent tracker
gh issue create --title "Create saved searches from the search page" --body-file child-1.md
gh issue create --title "View saved searches in a management page" --body-file child-2.md
gh issue create --title "Edit a saved search" --body-file child-3.md
gh issue create --title "Delete a saved search" --body-file child-4.md
gh issue create --title "Send default email alerts when saved-search results change" --body-file child-5.md
gh issue create --title "Pause alert delivery on a saved search" --body-file child-6.md
gh issue create --title "Edit saved-search notification preferences" --body-file child-7.md

# attach each child to the existing parent
PARENT_ISSUE_ID=$(gh issue view <existing-parent-issue-number> --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view <child-1> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"

CHILD_ISSUE_ID=$(gh issue view <child-2> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"

CHILD_ISSUE_ID=$(gh issue view <child-3> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"

CHILD_ISSUE_ID=$(gh issue view <child-4> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"

CHILD_ISSUE_ID=$(gh issue view <child-5> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"

CHILD_ISSUE_ID=$(gh issue view <child-6> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"

CHILD_ISSUE_ID=$(gh issue view <child-7> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"
```

## Durable queue guidance

- The existing parent issue stays immutable; do not edit its title, body, labels, or state.
- Executable work lives in that parent issue's direct child sub-issues listed above.
- The next AFK task is `#<child-1> Create saved searches from the search page`.
- After `#<child-1>` closes, `#<child-2> View saved searches in a management page` and `#<child-5> Send default email alerts when saved-search results change` are the next AFK tasks and can be worked independently.
- `#<child-7> Edit saved-search notification preferences` is intentionally downstream so notification-preference editing does not block initial saved-search creation.

## Final summary

Created task graph for saved searches plus alert delivery from an existing parent issue.

Parent: `#<existing-parent-issue-number>` (immutable existing parent)

Child issues:
1. `#<child-1> Create saved searches from the search page` - AFK - blocked by none
2. `#<child-2> View saved searches in a management page` - AFK - blocked by `#<child-1>`
3. `#<child-3> Edit a saved search` - AFK - blocked by `#<child-2>`
4. `#<child-4> Delete a saved search` - AFK - blocked by `#<child-2>`
5. `#<child-5> Send default email alerts when saved-search results change` - AFK - blocked by `#<child-1>`
6. `#<child-6> Pause alert delivery on a saved search` - AFK - blocked by `#<child-2>`, `#<child-5>`
7. `#<child-7> Edit saved-search notification preferences` - AFK - blocked by `#<child-2>`, `#<child-5>`

Notes:
- Placeholder issue numbers are used because this benchmark run does not create real GitHub issues.
- The breakdown keeps saved-search CRUD ahead of alert delivery where useful, and keeps notification preference edits off the critical path for initial saved-search creation.
- No parent-body update was drafted because the assigned skill forbids editing an existing parent issue.
