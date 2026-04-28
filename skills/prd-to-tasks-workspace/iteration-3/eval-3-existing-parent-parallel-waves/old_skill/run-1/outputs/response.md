Dry run for `prd-to-tasks` using the assigned `SKILL.md` only.

Because the source is an existing GitHub parent issue, the assigned skill treats that parent as immutable and does **not** draft a body update.

## Exact user-facing output the skill would send first

1. **Title**: Add billing alert threshold schema support  
   **Type**: AFK  
   **Blocked by**: None  
   **User stories covered**: Not explicit in source
2. **Title**: Deliver billing alerts by email  
   **Type**: AFK  
   **Blocked by**: Slice 1: Add billing alert threshold schema support  
   **User stories covered**: Not explicit in source
3. **Title**: Deliver billing alerts to Slack  
   **Type**: AFK  
   **Blocked by**: Slice 1: Add billing alert threshold schema support  
   **User stories covered**: Not explicit in source
4. **Title**: Show billing alert history in UI  
   **Type**: AFK  
   **Blocked by**: Slice 2: Deliver billing alerts by email; Slice 3: Deliver billing alerts to Slack  
   **User stories covered**: Not explicit in source

Does the granularity feel right: too coarse, too fine, or about right?
Are dependency relationships correct?
Should any slices be merged or split further?
Are the correct slices marked HITL and AFK?

## Issue graph draft for after approval

Parent: `#<parent-issue-number>` (existing PRD issue, unchanged)

Child issues:
1. `#<child-1>` Add billing alert threshold schema support - AFK - blocked by none
2. `#<child-2>` Deliver billing alerts by email - AFK - blocked by `#<child-1>`
3. `#<child-3>` Deliver billing alerts to Slack - AFK - blocked by `#<child-1>`
4. `#<child-4>` Show billing alert history in UI - AFK - blocked by `#<child-2>`, `#<child-3>`

Notes:
- The parent issue is treated as immutable and is not edited.
- Future implementation agents would discover the next task from the parent issue's direct subissues plus each child issue's `Blocked by` section.
- Dry run only; commands and issue bodies below are drafted and not executed.

## Parent body update commands

None. The assigned `SKILL.md` says to not close, rename, reword, relabel, or otherwise edit an existing parent issue, and separately says to not edit its body, title, labels, state, or other metadata.

## Draft child issue bodies

### `#<child-1>` Add billing alert threshold schema support

```markdown
## Parent

#<parent-issue-number>

## What to build

Add the threshold schema support required for billing alert policies so policy records can store the threshold configuration needed by downstream alert delivery paths.

## Type

AFK

## Acceptance criteria

- [ ] Billing alert policy data can persist the threshold fields required by the PRD-defined alert policy shape.
- [ ] Existing reads and writes for billing alert policies continue to work with the new threshold schema support in place.
- [ ] Automated coverage verifies the supported threshold schema shape and any compatibility behavior.

## Verification

- [ ] Tests pass: `<targeted test command for billing alert policy schema coverage>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: create or inspect a billing alert policy record and confirm the threshold fields are stored and returned as expected.

## Blocked by

None - can start immediately

## User stories covered

Not explicit in source

## Files likely touched

- `src/billing-alert-policies/schema/*`
- `src/billing-alert-policies/model/*`
- `tests/billing-alert-policies/schema/*`

## Estimated scope

Medium: 3-5 files
```

### `#<child-2>` Deliver billing alerts by email

```markdown
## Parent

#<parent-issue-number>

## What to build

Deliver billing alerts by email using the billing alert policy threshold configuration so a triggered policy sends the expected email notification through the existing delivery path.

## Type

AFK

## Acceptance criteria

- [ ] A billing alert policy that crosses its configured threshold triggers an email alert with the expected billing alert details.
- [ ] Email delivery uses the stored threshold policy configuration and handles delivery failure without breaking policy evaluation.
- [ ] Automated coverage verifies the threshold-triggered email alert path.

## Verification

- [ ] Tests pass: `<targeted test command for billing alert email coverage>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: trigger a threshold breach and confirm the expected billing alert email is sent or queued.

## Blocked by

- Blocked by #<child-1>

## User stories covered

Not explicit in source

## Files likely touched

- `src/billing-alert-policies/*`
- `src/alerts/email/*`
- `tests/billing-alerts/email/*`

## Estimated scope

Medium: 3-5 files
```

### `#<child-3>` Deliver billing alerts to Slack

```markdown
## Parent

#<parent-issue-number>

## What to build

Deliver billing alerts to Slack using the billing alert policy threshold configuration so a triggered policy posts the expected Slack alert through the existing integration path.

## Type

AFK

## Acceptance criteria

- [ ] A billing alert policy that crosses its configured threshold triggers a Slack alert with the expected billing alert details.
- [ ] Slack delivery uses the stored threshold policy configuration and handles delivery failure without breaking policy evaluation.
- [ ] Automated coverage verifies the threshold-triggered Slack alert path.

## Verification

- [ ] Tests pass: `<targeted test command for billing alert Slack coverage>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: trigger a threshold breach and confirm the expected billing alert is posted or queued for Slack delivery.

## Blocked by

- Blocked by #<child-1>

## User stories covered

Not explicit in source

## Files likely touched

- `src/billing-alert-policies/*`
- `src/alerts/slack/*`
- `tests/billing-alerts/slack/*`

## Estimated scope

Medium: 3-5 files
```

### `#<child-4>` Show billing alert history in UI

```markdown
## Parent

#<parent-issue-number>

## What to build

Show billing alert history in the UI so users can review sent billing alerts after both delivery paths exist, including entries generated from email and Slack alert deliveries.

## Type

AFK

## Acceptance criteria

- [ ] The billing alert history UI shows alert records produced by both email and Slack billing alert deliveries.
- [ ] History entries display the key billing alert details needed to understand what fired and where it was delivered.
- [ ] Automated coverage verifies the alert history UI with records from both delivery paths.

## Verification

- [ ] Tests pass: `<targeted test command for billing alert history UI coverage>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: trigger one email alert and one Slack alert, then confirm both appear in the billing alert history UI.

## Blocked by

- Blocked by #<child-2>
- Blocked by #<child-3>

## User stories covered

Not explicit in source

## Files likely touched

- `src/billing-alert-history/*`
- `src/ui/billing-alerts/*`
- `tests/billing-alert-history/*`

## Estimated scope

Medium: 3-5 files
```

## Draft commands the skill would produce after approval

```bash
gh issue create --title "Add billing alert threshold schema support" --body-file child-1-body.md
gh issue create --title "Deliver billing alerts by email" --body-file child-2-body.md
gh issue create --title "Deliver billing alerts to Slack" --body-file child-3-body.md
gh issue create --title "Show billing alert history in UI" --body-file child-4-body.md
```

```bash
PARENT_ISSUE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view <child-1> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"

PARENT_ISSUE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view <child-2> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"

PARENT_ISSUE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view <child-3> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"

PARENT_ISSUE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view <child-4> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"
```

## Draft final summary after creation

Created task graph for billing alert policies.

Parent: `#<parent-issue-number>` existing immutable PRD issue

Child issues:
1. `#<child-1>` Add billing alert threshold schema support - AFK - blocked by none
2. `#<child-2>` Deliver billing alerts by email - AFK - blocked by `#<child-1>`
3. `#<child-3>` Deliver billing alerts to Slack - AFK - blocked by `#<child-1>`
4. `#<child-4>` Show billing alert history in UI - AFK - blocked by `#<child-2>`, `#<child-3>`

Notes:
- The existing parent issue remains untouched.
- No parent body update was drafted because the assigned skill forbids editing existing parent issues.
- Dry run only; no GitHub issues were created.
