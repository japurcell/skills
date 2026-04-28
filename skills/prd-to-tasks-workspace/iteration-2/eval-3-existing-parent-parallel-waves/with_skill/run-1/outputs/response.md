Because the source context comes from an existing GitHub issue, I would first ask you to review this proposed breakdown before creating child issues:

1. **Title**: Add billing alert threshold policy schema
   **Type**: AFK
   **Execution wave**: W1
   **Blocked by**: None
   **User stories covered**: Not explicit in source
2. **Title**: Add email delivery for billing alert policies
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Add billing alert threshold policy schema
   **User stories covered**: Not explicit in source
3. **Title**: Add Slack delivery for billing alert policies
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Add billing alert threshold policy schema
   **User stories covered**: Not explicit in source
4. **Title**: Add billing alert history UI
   **Type**: AFK
   **Execution wave**: W3
   **Blocked by**: Slice 2: Add email delivery for billing alert policies; Slice 3: Add Slack delivery for billing alert policies
   **User stories covered**: Not explicit in source

Before I create the child issues, can you confirm:
- Does the granularity feel right: too coarse, too fine, or about right?
- Are the execution waves and dependency relationships correct?
- Should any slices be merged or split further?
- Are the correct slices marked HITL and AFK?

If approved, I would keep the existing parent issue untouched and create these direct child issues under it, plus one documentation-only queue-guide child issue so future agents can determine the next ready task from GitHub alone.

## Dry-run draft issue graph

Parent: `#<parent-issue-number>` existing immutable PRD issue

Direct subissues of the parent:
1. `#<schema-issue-number>` Add billing alert threshold policy schema - W1 - AFK - blocked by none
2. `#<email-issue-number>` Add email delivery for billing alert policies - W2 - AFK - blocked by `#<schema-issue-number>`
3. `#<slack-issue-number>` Add Slack delivery for billing alert policies - W2 - AFK - blocked by `#<schema-issue-number>`
4. `#<history-ui-issue-number>` Add billing alert history UI - W3 - AFK - blocked by `#<email-issue-number>`, `#<slack-issue-number>`
5. `#<queue-guide-issue-number>` Task graph: billing alert policies - documentation only; read first, do not implement

How to grab work:
- Open parent `#<parent-issue-number>` and inspect its direct subissues.
- The executable work is in the four sibling implementation issues; the queue-guide issue is documentation only.
- Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
- If several AFK issues are ready in the same wave, they may be worked in parallel.

## Draft child issue bodies

### 1) Add billing alert threshold policy schema

```markdown
## Parent

#<parent-issue-number>

## What to build

Add the threshold policy schema needed to store and validate billing alert policy thresholds so downstream delivery channels can rely on a stable definition.

## Type

AFK

## Acceptance criteria

- [ ] Billing alert policies can persist threshold configuration in the canonical schema used by the application.
- [ ] Threshold configuration is validated consistently wherever billing alert policies are created or updated.
- [ ] Existing policy flows continue to work when threshold configuration is absent or unchanged.

## Verification

- [ ] Tests pass: `<targeted billing alert schema test command>`
- [ ] Build succeeds: `<repo build command, if known>`
- [ ] Manual check: create or inspect a billing alert policy and verify threshold data is stored in the expected shape.

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers
- Parallel rule: if multiple AFK issues are ready in W1, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Not explicit in source

## Files likely touched

- `db/schema/billing_alert_policies.*`
- `app/billing_alerts/policy_validation.*`
- `tests/billing_alerts/schema_*`

## Estimated scope

Medium: 3-5 files
```

### 2) Add email delivery for billing alert policies

```markdown
## Parent

#<parent-issue-number>

## What to build

Deliver billing alerts by email using the threshold policy schema so a triggered policy can send the expected email notification end to end.

## Type

AFK

## Acceptance criteria

- [ ] A billing alert policy with email delivery enabled produces an email notification when its threshold condition is met.
- [ ] Email delivery uses the shared threshold schema rather than a channel-specific configuration shape.
- [ ] Failures in the email path are surfaced in the existing alerting flow without breaking unrelated policies.

## Verification

- [ ] Tests pass: `<targeted billing alert email test command>`
- [ ] Build succeeds: `<repo build command, if known>`
- [ ] Manual check: trigger a qualifying billing event and verify the expected email notification is produced.

## Blocked by

- Blocked by #<schema-issue-number>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<schema-issue-number> is closed
- Parallel rule: if multiple AFK issues are ready in W2, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Not explicit in source

## Files likely touched

- `app/billing_alerts/email_delivery.*`
- `app/billing_alerts/policy_evaluator.*`
- `tests/billing_alerts/email_*`

## Estimated scope

Medium: 3-5 files
```

### 3) Add Slack delivery for billing alert policies

```markdown
## Parent

#<parent-issue-number>

## What to build

Deliver billing alerts to Slack using the threshold policy schema so a triggered policy can send the expected Slack notification end to end.

## Type

AFK

## Acceptance criteria

- [ ] A billing alert policy with Slack delivery enabled produces a Slack notification when its threshold condition is met.
- [ ] Slack delivery uses the shared threshold schema rather than a channel-specific configuration shape.
- [ ] Failures in the Slack path are surfaced in the existing alerting flow without breaking unrelated policies.

## Verification

- [ ] Tests pass: `<targeted billing alert Slack test command>`
- [ ] Build succeeds: `<repo build command, if known>`
- [ ] Manual check: trigger a qualifying billing event and verify the expected Slack notification is produced.

## Blocked by

- Blocked by #<schema-issue-number>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<schema-issue-number> is closed
- Parallel rule: if multiple AFK issues are ready in W2, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Not explicit in source

## Files likely touched

- `app/billing_alerts/slack_delivery.*`
- `app/billing_alerts/policy_evaluator.*`
- `tests/billing_alerts/slack_*`

## Estimated scope

Medium: 3-5 files
```

### 4) Add billing alert history UI

```markdown
## Parent

#<parent-issue-number>

## What to build

Expose the billing alert history UI so users can review the alert events generated by the email and Slack delivery paths from one consistent interface.

## Type

AFK

## Acceptance criteria

- [ ] The alert history UI shows billing alert events produced by both email and Slack delivery paths.
- [ ] Users can distinguish the delivery channel and key alert details from the UI.
- [ ] The UI handles missing or failed delivery records without breaking the history view.

## Verification

- [ ] Tests pass: `<targeted billing alert history UI test command>`
- [ ] Build succeeds: `<repo build command, if known>`
- [ ] Manual check: generate one email alert and one Slack alert, then verify both appear correctly in the history UI.

## Blocked by

- Blocked by #<email-issue-number>
- Blocked by #<slack-issue-number>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W3
- Ready to start when: #<email-issue-number> and #<slack-issue-number> are both closed
- Parallel rule: if multiple AFK issues are ready in W3, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Not explicit in source

## Files likely touched

- `ui/billing_alerts/history.*`
- `app/billing_alerts/history_query.*`
- `tests/ui/billing_alerts/history_*`

## Estimated scope

Medium: 3-5 files
```

### 5) Task graph: billing alert policies

```markdown
## Parent

#<parent-issue-number>

## Purpose

This issue documents how to grab implementation work from parent #<parent-issue-number>. Do not implement this issue itself.

## Executable subissues

1. W1 - #<schema-issue-number> Add billing alert threshold policy schema - AFK - blocked by none
2. W2 - #<email-issue-number> Add email delivery for billing alert policies - AFK - blocked by #<schema-issue-number>
3. W2 - #<slack-issue-number> Add Slack delivery for billing alert policies - AFK - blocked by #<schema-issue-number>
4. W3 - #<history-ui-issue-number> Add billing alert history UI - AFK - blocked by #<email-issue-number>, #<slack-issue-number>

## How to grab work

1. Open parent #<parent-issue-number> and inspect its subissues.
2. The executable work is in the sibling implementation issues listed above; this queue-guide issue is documentation only.
3. Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
4. If several AFK issues are ready in the same wave, they may be worked in parallel.
5. Do not start HITL issues until the named human decision or review has happened.
```

## Draft commands the skill would produce after approval

Create blocker first, then parallelizable W2 issues, then W3 UI, then queue guide:

```bash
gh issue create --repo <owner/repo> --title "Add billing alert threshold policy schema" --body-file /home/adam/dev/personal/skills/skills/prd-to-tasks-workspace/iteration-2/eval-3-existing-parent-parallel-waves/with_skill/run-1/schema-issue.md
gh issue create --repo <owner/repo> --title "Add email delivery for billing alert policies" --body-file /home/adam/dev/personal/skills/skills/prd-to-tasks-workspace/iteration-2/eval-3-existing-parent-parallel-waves/with_skill/run-1/email-issue.md
gh issue create --repo <owner/repo> --title "Add Slack delivery for billing alert policies" --body-file /home/adam/dev/personal/skills/skills/prd-to-tasks-workspace/iteration-2/eval-3-existing-parent-parallel-waves/with_skill/run-1/slack-issue.md
gh issue create --repo <owner/repo> --title "Add billing alert history UI" --body-file /home/adam/dev/personal/skills/skills/prd-to-tasks-workspace/iteration-2/eval-3-existing-parent-parallel-waves/with_skill/run-1/history-ui-issue.md
gh issue create --repo <owner/repo> --title "Task graph: billing alert policies" --body-file /home/adam/dev/personal/skills/skills/prd-to-tasks-workspace/iteration-2/eval-3-existing-parent-parallel-waves/with_skill/run-1/queue-guide-issue.md
```

Attach each created child issue directly to the immutable parent; do not nest implementation issues under the queue-guide issue:

```bash
PARENT_ISSUE_ID=$(gh issue view <parent-issue-number> --repo <owner/repo> --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view <schema-issue-number> --repo <owner/repo> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"

CHILD_ISSUE_ID=$(gh issue view <email-issue-number> --repo <owner/repo> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"

CHILD_ISSUE_ID=$(gh issue view <slack-issue-number> --repo <owner/repo> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"

CHILD_ISSUE_ID=$(gh issue view <history-ui-issue-number> --repo <owner/repo> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"

CHILD_ISSUE_ID=$(gh issue view <queue-guide-issue-number> --repo <owner/repo> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"
```
