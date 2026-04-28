Drafted task graph for billing alert policies.

Parent: `#<parent-issue-number> <existing parent title>`

Child issues:
1. `#<child-1> Add billing alert threshold policy schema support` - W1 - AFK - blocked by none
2. `#<child-2> Deliver billing alert emails from threshold policies` - W2 - AFK - blocked by `#<child-1>`
3. `#<child-3> Deliver billing alert Slack notifications from threshold policies` - W2 - AFK - blocked by `#<child-1>`
4. `#<child-4> Show billing alert history across email and Slack deliveries` - W3 - AFK - blocked by `#<child-2>`, `#<child-3>`

How to grab work:
- Open parent `#<parent-issue-number>` and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- Read the managed `Task graph` / `How to grab work` section in the parent body.

Notes:
- Dry run only; commands and issue bodies are drafted below and were not executed.
- Because the source came from an existing GitHub issue, the skill would first present the proposed breakdown below for review before creating child issues.
- Parent issue number, title, and current body text were not provided in the workspace, so placeholders are preserved.

## Proposed breakdown for review

1. **Title**: Add billing alert threshold policy schema support
   **Type**: AFK
   **Execution wave**: W1
   **Blocked by**: None
   **User stories covered**: Billing alert policies need threshold schema support before delivery paths can be implemented.
2. **Title**: Deliver billing alert emails from threshold policies
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Add billing alert threshold policy schema support
   **User stories covered**: Billing alert policies send email alerts after threshold schema support exists.
3. **Title**: Deliver billing alert Slack notifications from threshold policies
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Add billing alert threshold policy schema support
   **User stories covered**: Billing alert policies send Slack alerts after threshold schema support exists.
4. **Title**: Show billing alert history across email and Slack deliveries
   **Type**: AFK
   **Execution wave**: W3
   **Blocked by**: Slice 2: Deliver billing alert emails from threshold policies; Slice 3: Deliver billing alert Slack notifications from threshold policies
   **User stories covered**: Alert history UI depends on both delivery paths.

The skill would ask:
- Does the granularity feel right: too coarse, too fine, or about right?
- Are the execution waves and dependency relationships correct?
- Should any slices be merged or split further?
- Are the correct slices marked HITL and AFK?

## Parent issue body managed-block update draft

```markdown
<!-- prd-to-tasks:start -->
## Task graph

- [ ] W1 - #<child-1> Add billing alert threshold policy schema support - AFK - blocked by none
- [ ] W2 - #<child-2> Deliver billing alert emails from threshold policies - AFK - blocked by #<child-1>
- [ ] W2 - #<child-3> Deliver billing alert Slack notifications from threshold policies - AFK - blocked by #<child-1>
- [ ] W3 - #<child-4> Show billing alert history across email and Slack deliveries - AFK - blocked by #<child-2>, #<child-3>

## How to grab work

1. Open this parent issue and inspect its direct subissues.
2. The executable work is in the sibling implementation issues listed above.
3. Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
4. If several AFK issues are ready in the same wave, they may be worked in parallel.
5. Do not start HITL issues until the named human decision or review has happened.
<!-- prd-to-tasks:end -->
```

## Child issue drafts

### 1. `Add billing alert threshold policy schema support`

```markdown
## Parent

#<parent-issue-number>

## What to build

Add threshold policy schema support for billing alerts so downstream delivery slices can create, validate, store, and read threshold-based alert definitions through the existing billing alert path.

## Type

AFK

## Acceptance criteria

- [ ] Threshold fields required for billing alert policies can be created, stored, and read through the existing billing alert configuration path.
- [ ] Invalid or incomplete threshold policy data is rejected with covered validation behavior.
- [ ] Automated tests cover the supported threshold schema shape used by downstream delivery paths.

## Verification

- [ ] Tests pass: `<targeted test command for billing alert threshold schema coverage>`
- [ ] Build succeeds: `<repo build command, if known>`
- [ ] Manual check: create or inspect a billing alert policy with threshold settings and confirm the saved payload round-trips correctly.

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers, or every issue listed in `Blocked by` is closed
- Parallel rule: if multiple AFK issues are ready in W1, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

- Billing alert policies need threshold schema support before delivery features can use them.

## Files likely touched

- `<billing-alert-policy-schema>`
- `<billing-alert-policy-validation>`
- `<billing-alert-policy-read-write-path>`
- `<billing-alert-threshold-schema-tests>`

## Estimated scope

Medium: 3-5 files
```

### 2. `Deliver billing alert emails from threshold policies`

```markdown
## Parent

#<parent-issue-number>

## What to build

Implement the end-to-end email delivery path for threshold-based billing alerts so supported policies can trigger and send email notifications using the stored threshold schema.

## Type

AFK

## Acceptance criteria

- [ ] Threshold-based billing alert policies can trigger an email notification through the existing alert execution path.
- [ ] Email delivery uses the stored threshold policy data and records the result needed by later history views.
- [ ] Automated tests cover a successful billing alert email delivery flow.

## Verification

- [ ] Tests pass: `<targeted test command for billing alert email delivery coverage>`
- [ ] Build succeeds: `<repo build command, if known>`
- [ ] Manual check: trigger a threshold billing alert and confirm the expected email notification is sent or queued.

## Blocked by

- Blocked by #<child-1>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<child-1> is closed
- Parallel rule: if multiple AFK issues are ready in W2, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

- Billing alert policies send email alerts once threshold schema support exists.

## Files likely touched

- `<billing-alert-execution-path>`
- `<billing-alert-email-delivery-service>`
- `<billing-alert-email-template-or-payload-builder>`
- `<billing-alert-email-delivery-tests>`

## Estimated scope

Medium: 3-5 files
```

### 3. `Deliver billing alert Slack notifications from threshold policies`

```markdown
## Parent

#<parent-issue-number>

## What to build

Implement the end-to-end Slack delivery path for threshold-based billing alerts so supported policies can trigger and send Slack notifications using the stored threshold schema.

## Type

AFK

## Acceptance criteria

- [ ] Threshold-based billing alert policies can trigger a Slack notification through the existing alert execution path.
- [ ] Slack delivery uses the stored threshold policy data and records the result needed by later history views.
- [ ] Automated tests cover a successful billing alert Slack delivery flow.

## Verification

- [ ] Tests pass: `<targeted test command for billing alert Slack delivery coverage>`
- [ ] Build succeeds: `<repo build command, if known>`
- [ ] Manual check: trigger a threshold billing alert and confirm the expected Slack notification is posted or queued.

## Blocked by

- Blocked by #<child-1>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<child-1> is closed
- Parallel rule: if multiple AFK issues are ready in W2, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

- Billing alert policies send Slack alerts once threshold schema support exists.

## Files likely touched

- `<billing-alert-execution-path>`
- `<billing-alert-slack-delivery-service>`
- `<billing-alert-slack-message-builder>`
- `<billing-alert-slack-delivery-tests>`

## Estimated scope

Medium: 3-5 files
```

### 4. `Show billing alert history across email and Slack deliveries`

```markdown
## Parent

#<parent-issue-number>

## What to build

Add the billing alert history UI so users can review alert deliveries across both email and Slack channels with the delivery records produced by the existing notification paths.

## Type

AFK

## Acceptance criteria

- [ ] The alert history UI shows billing alert delivery records for both email and Slack notifications.
- [ ] The UI distinguishes relevant delivery details needed to review threshold-based alert activity across both channels.
- [ ] Automated tests cover the alert history UI with both email and Slack delivery data.

## Verification

- [ ] Tests pass: `<targeted test command for billing alert history UI coverage>`
- [ ] Build succeeds: `<repo build command, if known>`
- [ ] Manual check: view alert history after email and Slack alerts have fired and confirm both delivery paths appear correctly.

## Blocked by

- Blocked by #<child-2>
- Blocked by #<child-3>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W3
- Ready to start when: #<child-2> and #<child-3> are both closed
- Parallel rule: if multiple AFK issues are ready in W3, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

- Users can review billing alert history only after both email and Slack delivery paths exist.

## Files likely touched

- `<billing-alert-history-ui>`
- `<billing-alert-history-data-loader>`
- `<billing-alert-history-row-or-detail-component>`
- `<billing-alert-history-ui-tests>`

## Estimated scope

Medium: 3-5 files
```

## Dry-run command draft

```bash
# create child issues in dependency order against the existing parent tracker
 gh issue create --title "Add billing alert threshold policy schema support" --body-file child-1.md
 gh issue create --title "Deliver billing alert emails from threshold policies" --body-file child-2.md
 gh issue create --title "Deliver billing alert Slack notifications from threshold policies" --body-file child-3.md
 gh issue create --title "Show billing alert history across email and Slack deliveries" --body-file child-4.md

# update the existing parent issue body with the managed task-graph block
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

- [ ] W1 - #<child-1> Add billing alert threshold policy schema support - AFK - blocked by none
- [ ] W2 - #<child-2> Deliver billing alert emails from threshold policies - AFK - blocked by #<child-1>
- [ ] W2 - #<child-3> Deliver billing alert Slack notifications from threshold policies - AFK - blocked by #<child-1>
- [ ] W3 - #<child-4> Show billing alert history across email and Slack deliveries - AFK - blocked by #<child-2>, #<child-3>

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

# attach each child to the existing parent tracker
PARENT_ISSUE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
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
```
