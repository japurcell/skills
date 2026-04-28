## Proposed vertical-slice breakdown (present first)

1. **Title**: Add threshold schema support
   **Type**: AFK
   **Execution wave**: W1
   **Blocked by**: None
   **User stories covered**: Not explicit in source

2. **Title**: Implement email alert delivery
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Add threshold schema support
   **User stories covered**: Not explicit in source

3. **Title**: Implement Slack alert delivery
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Add threshold schema support
   **User stories covered**: Not explicit in source

4. **Title**: Build alert history UI
   **Type**: AFK
   **Execution wave**: W3
   **Blocked by**: Slice 2: Implement email alert delivery, Slice 3: Implement Slack alert delivery
   **User stories covered**: Not explicit in source

---

## Child issue drafts

### Add threshold schema support

## Parent

#4200

## What to build

Define and implement schema for alert thresholds, including validation and migration support for billing alert policies.

## Type

AFK

## Acceptance criteria

- [ ] New schema supports configurable alert thresholds per billing policy.
- [ ] Validation logic enforces correct threshold formats and values.
- [ ] Migration applies cleanly to existing data.

## Verification

- [ ] Tests pass: targeted unit tests for schema and validation logic
- [ ] Migration tested on sample data

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #4200
- Execution wave: W1
- Ready to start when: this issue has no blockers, or every issue listed in `Blocked by` is closed

## User stories covered

Not explicit in source

## Files likely touched

- billing/alerts/schema.py
- billing/alerts/models.py
- migrations/

## Estimated scope

Medium: 3-5 files

---

### Implement email alert delivery

## Parent

#4200

## What to build

Add email delivery for billing alerts using the new threshold schema.

## Type

AFK

## Acceptance criteria

- [ ] Alerts are sent via email when thresholds are crossed.
- [ ] Email content includes relevant billing and threshold details.
- [ ] Delivery failures are logged.

## Verification

- [ ] Tests pass: integration tests for email delivery
- [ ] Manual test with test thresholds

## Blocked by

- Blocked by #<threshold-schema-issue-number>

## Queue position

- Parent queue: direct subissue of #4200
- Execution wave: W2
- Ready to start when: this issue has no blockers, or every issue listed in `Blocked by` is closed

## User stories covered

Not explicit in source

## Files likely touched

- billing/alerts/email.py
- billing/alerts/tests/

## Estimated scope

Medium: 3-5 files

---

### Implement Slack alert delivery

## Parent

#4200

## What to build

Add Slack delivery for billing alerts using the new threshold schema.

## Type

AFK

## Acceptance criteria

- [ ] Alerts are sent to Slack channels when thresholds are crossed.
- [ ] Slack messages include relevant billing and threshold details.
- [ ] Delivery failures are logged.

## Verification

- [ ] Tests pass: integration tests for Slack delivery
- [ ] Manual test with test thresholds

## Blocked by

- Blocked by #<threshold-schema-issue-number>

## Queue position

- Parent queue: direct subissue of #4200
- Execution wave: W2
- Ready to start when: this issue has no blockers, or every issue listed in `Blocked by` is closed

## User stories covered

Not explicit in source

## Files likely touched

- billing/alerts/slack.py
- billing/alerts/tests/

## Estimated scope

Medium: 3-5 files

---

### Build alert history UI

## Parent

#4200

## What to build

Implement UI to display alert history, showing all delivered alerts and their statuses.

## Type

AFK

## Acceptance criteria

- [ ] UI lists all alerts with timestamps, delivery method, and status.
- [ ] Supports filtering by alert type and delivery method.
- [ ] Handles empty and error states gracefully.

## Verification

- [ ] Tests pass: UI tests for alert history display and filtering
- [ ] Manual verification in browser

## Blocked by

- Blocked by #<email-alert-issue-number>
- Blocked by #<slack-alert-issue-number>

## Queue position

- Parent queue: direct subissue of #4200
- Execution wave: W3
- Ready to start when: this issue has no blockers, or every issue listed in `Blocked by` is closed

## User stories covered

Not explicit in source

## Files likely touched

- billing/alerts/ui/
- billing/alerts/api.py

## Estimated scope

Medium: 3-5 files

---

<!-- prd-to-tasks:start -->
## Task graph

- [ ] W1 - #<threshold-schema-issue-number> Add threshold schema support - AFK - blocked by none
- [ ] W2 - #<email-alert-issue-number> Implement email alert delivery - AFK - blocked by #<threshold-schema-issue-number>
- [ ] W2 - #<slack-alert-issue-number> Implement Slack alert delivery - AFK - blocked by #<threshold-schema-issue-number>
- [ ] W3 - #<alert-history-ui-issue-number> Build alert history UI - AFK - blocked by #<email-alert-issue-number>, #<slack-alert-issue-number>

## How to grab work

1. Open this parent issue and inspect its direct subissues.
2. The executable work is in the sibling implementation issues listed above.
3. Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
4. If several AFK issues are ready in the same wave, they may be worked in parallel.
5. Do not start HITL issues until the named human decision or review has happened.
<!-- prd-to-tasks:end -->

---

## Subissue attachment commands

```bash
# Attach child issues to parent #4200 (replace placeholders with real issue numbers)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"
```

---

## Final summary

Created task graph for billing alert policies (parent: #4200).

Child issues:
1. #<threshold-schema-issue-number> Add threshold schema support - W1 - AFK - blocked by none
2. #<email-alert-issue-number> Implement email alert delivery - W2 - AFK - blocked by #<threshold-schema-issue-number>
3. #<slack-alert-issue-number> Implement Slack alert delivery - W2 - AFK - blocked by #<threshold-schema-issue-number>
4. #<alert-history-ui-issue-number> Build alert history UI - W3 - AFK - blocked by #<email-alert-issue-number>, #<slack-alert-issue-number>

How to grab work:
- Open parent #4200 and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- Read the managed Task graph / How to grab work section in its body.


```bash
gh api graphql -f query='mutation { addSubIssue(input: {issueId: "<parent-issue-node-id>", subIssueId: "<threshold-schema-issue-node-id>"}) { clientMutationId } }'
gh api graphql -f query='mutation { addSubIssue(input: {issueId: "<parent-issue-node-id>", subIssueId: "<email-alert-issue-node-id>"}) { clientMutationId } }'
gh api graphql -f query='mutation { addSubIssue(input: {issueId: "<parent-issue-node-id>", subIssueId: "<slack-alert-issue-node-id>"}) { clientMutationId } }'
gh api graphql -f query='mutation { addSubIssue(input: {issueId: "<parent-issue-node-id>", subIssueId: "<alert-history-ui-issue-node-id>"}) { clientMutationId } }'
```
