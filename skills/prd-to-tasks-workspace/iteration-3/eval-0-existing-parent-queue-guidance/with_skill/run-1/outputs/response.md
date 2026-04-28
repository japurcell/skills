## Proposed vertical-slice breakdown (present first)

1. **Title**: Create a saved search from the search page  
   **Type**: AFK  
   **Execution wave**: W1  
   **Blocked by**: None  
   **User stories covered**: Saved searches can be created from the search page; notification preference edits should not block initial saved-search creation.

2. **Title**: Manage saved searches after creation  
   **Type**: AFK  
   **Execution wave**: W2  
   **Blocked by**: Slice 1: Create a saved search from the search page  
   **User stories covered**: Shipping saved-search CRUD before alert delivery is acceptable.

3. **Title**: Pause or resume a saved-search alert  
   **Type**: AFK  
   **Execution wave**: W3  
   **Blocked by**: Slice 2: Manage saved searches after creation  
   **User stories covered**: Users need a way to pause alerts without deleting the saved search; notification preference edits remain separate from initial creation.

4. **Title**: Email users when saved-search results change  
   **Type**: AFK  
   **Execution wave**: W4  
   **Blocked by**: Slice 3: Pause or resume a saved-search alert  
   **User stories covered**: Alerts can email users when results change.

Please confirm before issue creation:
- Does the granularity feel right: too coarse, too fine, or about right?
- Are the execution waves and dependency relationships correct?
- Should any slices be merged or split further?
- Are the correct slices marked HITL and AFK?

## Draft issue graph (post-approval)

Parent: `#<parent-issue-number>` existing saved-search PRD issue

1. `#<child-1-number>` Create a saved search from the search page - W1 - AFK - blocked by none
2. `#<child-2-number>` Manage saved searches after creation - W2 - AFK - blocked by `#<child-1-number>`
3. `#<child-3-number>` Pause or resume a saved-search alert - W3 - AFK - blocked by `#<child-2-number>`
4. `#<child-4-number>` Email users when saved-search results change - W4 - AFK - blocked by `#<child-3-number>`

## Draft child issues

### Child 1 — Create a saved search from the search page

**Title**: `Create a saved search from the search page`

```markdown
## Parent

#<parent-issue-number>

## What to build

Let a user save the current query directly from the search page so the saved search persists for later reuse without requiring the user to configure alert delivery or edit notification preferences first.

## Type

AFK

## Acceptance criteria

- [ ] A user can create a saved search from the current search page state.
- [ ] The new saved search is persisted and appears in the user's saved-search collection.
- [ ] Initial saved-search creation succeeds without requiring notification preference edits.

## Verification

- [ ] Tests pass: `<targeted test command>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: create a saved search from the search page and confirm it appears in the saved-search collection.

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers
- Parallel rule: if multiple AFK issues are ready in W1, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Saved searches can be created from the search page; notification preference edits should not block initial saved-search creation.

## Files likely touched

- `app/search/page.*`
- `app/saved-searches/create.*`
- `tests/saved-searches/create.*`

## Estimated scope

Medium: 3-5 files
```

### Child 2 — Manage saved searches after creation

**Title**: `Manage saved searches after creation`

```markdown
## Parent

#<parent-issue-number>

## What to build

Provide a saved-search management surface where a user can review saved searches created earlier, update core saved-search details, and delete a saved search without touching alert-delivery behavior.

## Type

AFK

## Acceptance criteria

- [ ] A user can view their existing saved searches in one management surface.
- [ ] A user can update core saved-search details without recreating the saved search.
- [ ] A user can delete a saved search cleanly.

## Verification

- [ ] Tests pass: `<targeted test command>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: open the saved-search management surface, edit one saved search, and delete another.

## Blocked by

- Blocked by #<child-1-number>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<child-1-number> is closed
- Parallel rule: if multiple AFK issues are ready in W2, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Shipping saved-search CRUD before alert delivery is acceptable.

## Files likely touched

- `app/settings/saved-searches/**`
- `app/saved-searches/update.*`
- `tests/saved-searches/manage.*`

## Estimated scope

Medium: 3-5 files
```

### Child 3 — Pause or resume a saved-search alert

**Title**: `Pause or resume a saved-search alert`

```markdown
## Parent

#<parent-issue-number>

## What to build

Add an explicit alert state control to each saved search so a user can pause delivery without deleting the saved search and later resume alerting from the same saved-search record.

## Type

AFK

## Acceptance criteria

- [ ] A user can pause alert delivery on an existing saved search while keeping the saved search intact.
- [ ] A user can resume a paused saved-search alert.
- [ ] The saved-search management surface clearly shows whether each alert is active or paused.

## Verification

- [ ] Tests pass: `<targeted test command>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: pause a saved-search alert, confirm the saved search remains, then resume it.

## Blocked by

- Blocked by #<child-2-number>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W3
- Ready to start when: #<child-2-number> is closed
- Parallel rule: if multiple AFK issues are ready in W3, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Users need a way to pause alerts without deleting the saved search; notification preference edits remain separate from initial creation.

## Files likely touched

- `app/settings/saved-searches/**`
- `app/saved-searches/alert-preferences.*`
- `tests/saved-searches/pause-alerts.*`

## Estimated scope

Medium: 3-5 files
```

### Child 4 — Email users when saved-search results change

**Title**: `Email users when saved-search results change`

```markdown
## Parent

#<parent-issue-number>

## What to build

Deliver email notifications for saved searches when matching results change, but only for saved searches whose alert state is active.

## Type

AFK

## Acceptance criteria

- [ ] A change in saved-search results schedules or sends an email to the saved-search owner.
- [ ] Paused saved searches do not send alert emails.
- [ ] Delivery behavior is covered by automated tests and is manually verifiable end to end.

## Verification

- [ ] Tests pass: `<targeted test command>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: trigger a result change for an active saved search and verify one email is delivered, then confirm a paused saved search does not send.

## Blocked by

- Blocked by #<child-3-number>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W4
- Ready to start when: #<child-3-number> is closed
- Parallel rule: if multiple AFK issues are ready in W4, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Alerts can email users when saved-search results change.

## Files likely touched

- `jobs/saved-search-alerts/**`
- `app/mailers/saved-search-alerts.*`
- `tests/saved-search-alerts/delivery.*`

## Estimated scope

Medium: 3-5 files
```

## Managed parent-body tracking guidance

```markdown
<!-- prd-to-tasks:start -->
## Task graph

- [ ] W1 - #<child-1-number> Create a saved search from the search page - AFK - blocked by none
- [ ] W2 - #<child-2-number> Manage saved searches after creation - AFK - blocked by #<child-1-number>
- [ ] W3 - #<child-3-number> Pause or resume a saved-search alert - AFK - blocked by #<child-2-number>
- [ ] W4 - #<child-4-number> Email users when saved-search results change - AFK - blocked by #<child-3-number>

## Next AFK task

- #<child-1-number> Create a saved search from the search page

## How to grab work

1. Open this parent issue and inspect its direct subissues.
2. The executable work is in the sibling implementation issues listed above.
3. Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
4. If several AFK issues are ready in the same wave, they may be worked in parallel.
5. Do not start HITL issues until the named human decision or review has happened.
<!-- prd-to-tasks:end -->
```

## Draft commands the skill would produce

### 1. Create child issue body files and draft `gh issue create` calls

```bash
cat > child-1-body.md <<'EOF'
## Parent

#<parent-issue-number>

## What to build

Let a user save the current query directly from the search page so the saved search persists for later reuse without requiring the user to configure alert delivery or edit notification preferences first.

## Type

AFK

## Acceptance criteria

- [ ] A user can create a saved search from the current search page state.
- [ ] The new saved search is persisted and appears in the user's saved-search collection.
- [ ] Initial saved-search creation succeeds without requiring notification preference edits.

## Verification

- [ ] Tests pass: <targeted test command>
- [ ] Build succeeds: <build command, if known>
- [ ] Manual check: create a saved search from the search page and confirm it appears in the saved-search collection.

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers
- Parallel rule: if multiple AFK issues are ready in W1, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Saved searches can be created from the search page; notification preference edits should not block initial saved-search creation.

## Files likely touched

- app/search/page.*
- app/saved-searches/create.*
- tests/saved-searches/create.*

## Estimated scope

Medium: 3-5 files
EOF
gh issue create --title "Create a saved search from the search page" --body-file child-1-body.md

cat > child-2-body.md <<'EOF'
## Parent

#<parent-issue-number>

## What to build

Provide a saved-search management surface where a user can review saved searches created earlier, update core saved-search details, and delete a saved search without touching alert-delivery behavior.

## Type

AFK

## Acceptance criteria

- [ ] A user can view their existing saved searches in one management surface.
- [ ] A user can update core saved-search details without recreating the saved search.
- [ ] A user can delete a saved search cleanly.

## Verification

- [ ] Tests pass: <targeted test command>
- [ ] Build succeeds: <build command, if known>
- [ ] Manual check: open the saved-search management surface, edit one saved search, and delete another.

## Blocked by

- Blocked by #<child-1-number>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<child-1-number> is closed
- Parallel rule: if multiple AFK issues are ready in W2, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Shipping saved-search CRUD before alert delivery is acceptable.

## Files likely touched

- app/settings/saved-searches/**
- app/saved-searches/update.*
- tests/saved-searches/manage.*

## Estimated scope

Medium: 3-5 files
EOF
gh issue create --title "Manage saved searches after creation" --body-file child-2-body.md

cat > child-3-body.md <<'EOF'
## Parent

#<parent-issue-number>

## What to build

Add an explicit alert state control to each saved search so a user can pause delivery without deleting the saved search and later resume alerting from the same saved-search record.

## Type

AFK

## Acceptance criteria

- [ ] A user can pause alert delivery on an existing saved search while keeping the saved search intact.
- [ ] A user can resume a paused saved-search alert.
- [ ] The saved-search management surface clearly shows whether each alert is active or paused.

## Verification

- [ ] Tests pass: <targeted test command>
- [ ] Build succeeds: <build command, if known>
- [ ] Manual check: pause a saved-search alert, confirm the saved search remains, then resume it.

## Blocked by

- Blocked by #<child-2-number>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W3
- Ready to start when: #<child-2-number> is closed
- Parallel rule: if multiple AFK issues are ready in W3, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Users need a way to pause alerts without deleting the saved search; notification preference edits remain separate from initial creation.

## Files likely touched

- app/settings/saved-searches/**
- app/saved-searches/alert-preferences.*
- tests/saved-searches/pause-alerts.*

## Estimated scope

Medium: 3-5 files
EOF
gh issue create --title "Pause or resume a saved-search alert" --body-file child-3-body.md

cat > child-4-body.md <<'EOF'
## Parent

#<parent-issue-number>

## What to build

Deliver email notifications for saved searches when matching results change, but only for saved searches whose alert state is active.

## Type

AFK

## Acceptance criteria

- [ ] A change in saved-search results schedules or sends an email to the saved-search owner.
- [ ] Paused saved searches do not send alert emails.
- [ ] Delivery behavior is covered by automated tests and is manually verifiable end to end.

## Verification

- [ ] Tests pass: <targeted test command>
- [ ] Build succeeds: <build command, if known>
- [ ] Manual check: trigger a result change for an active saved search and verify one email is delivered, then confirm a paused saved search does not send.

## Blocked by

- Blocked by #<child-3-number>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W4
- Ready to start when: #<child-3-number> is closed
- Parallel rule: if multiple AFK issues are ready in W4, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Alerts can email users when saved-search results change.

## Files likely touched

- jobs/saved-search-alerts/**
- app/mailers/saved-search-alerts.*
- tests/saved-search-alerts/delivery.*

## Estimated scope

Medium: 3-5 files
EOF
gh issue create --title "Email users when saved-search results change" --body-file child-4-body.md
```

### 2. Update the existing parent issue body with the managed block

```bash
CURRENT_BODY_FILE=$(mktemp)
UPDATED_BODY_FILE=$(mktemp)

gh issue view <parent-issue-number> --json body --jq .body > "$CURRENT_BODY_FILE"

python3 - "$CURRENT_BODY_FILE" "$UPDATED_BODY_FILE" <<'PY'
from pathlib import Path
import re
import sys

current_path = Path(sys.argv[1])
updated_path = Path(sys.argv[2])
current_body = current_path.read_text(encoding="utf-8")
managed_block = """<!-- prd-to-tasks:start -->
## Task graph

- [ ] W1 - #<child-1-number> Create a saved search from the search page - AFK - blocked by none
- [ ] W2 - #<child-2-number> Manage saved searches after creation - AFK - blocked by #<child-1-number>
- [ ] W3 - #<child-3-number> Pause or resume a saved-search alert - AFK - blocked by #<child-2-number>
- [ ] W4 - #<child-4-number> Email users when saved-search results change - AFK - blocked by #<child-3-number>

## Next AFK task

- #<child-1-number> Create a saved search from the search page

## How to grab work

1. Open this parent issue and inspect its direct subissues.
2. The executable work is in the sibling implementation issues listed above.
3. Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
4. If several AFK issues are ready in the same wave, they may be worked in parallel.
5. Do not start HITL issues until the named human decision or review has happened.
<!-- prd-to-tasks:end -->"""

pattern = re.compile(r"<!-- prd-to-tasks:start -->.*?<!-- prd-to-tasks:end -->", re.S)
if pattern.search(current_body):
    updated_body = pattern.sub(managed_block, current_body)
else:
    separator = "\n\n" if current_body.strip() else ""
    updated_body = f"{current_body.rstrip()}{separator}{managed_block}\n"

updated_path.write_text(updated_body, encoding="utf-8")
PY

gh issue edit <parent-issue-number> --body-file "$UPDATED_BODY_FILE"
```

### 3. Attach each child issue as a direct subissue of the existing parent

```bash
PARENT_ISSUE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_1_ISSUE_ID=$(gh issue view <child-1-number> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_1_ISSUE_ID\"}) {
    issue { number }
  }
}"

CHILD_2_ISSUE_ID=$(gh issue view <child-2-number> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_2_ISSUE_ID\"}) {
    issue { number }
  }
}"

CHILD_3_ISSUE_ID=$(gh issue view <child-3-number> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_3_ISSUE_ID\"}) {
    issue { number }
  }
}"

CHILD_4_ISSUE_ID=$(gh issue view <child-4-number> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_4_ISSUE_ID\"}) {
    issue { number }
  }
}"
```

## Draft final summary

Drafted task graph for the existing saved-search parent issue.

Parent: `#<parent-issue-number>` existing saved-search PRD issue

Child issues:
1. `#<child-1-number>` Create a saved search from the search page - W1 - AFK - blocked by none
2. `#<child-2-number>` Manage saved searches after creation - W2 - AFK - blocked by `#<child-1-number>`
3. `#<child-3-number>` Pause or resume a saved-search alert - W3 - AFK - blocked by `#<child-2-number>`
4. `#<child-4-number>` Email users when saved-search results change - W4 - AFK - blocked by `#<child-3-number>`

How to grab work:
- Open parent `#<parent-issue-number>` and inspect its direct subissues.
- The executable work is in the parent issue's sibling direct subissues, not in the parent issue body itself.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- Next AFK task: `#<child-1-number>` Create a saved search from the search page.

Notes:
- Draft only; no real GitHub issues or parent-body edits were performed.
- Placeholder issue numbers are used because the parent issue number and created child numbers were not provided in the prompt.
