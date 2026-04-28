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

### Child Issue Drafts

---

#### 1. Add threshold schema support

##### Parent

#4200

##### What to build

Extend the billing alert policy schema to support configurable threshold values for triggering alerts.

##### Type

AFK

##### Acceptance criteria

- [ ] Schema supports threshold values
- [ ] Thresholds are validated and persisted
- [ ] Documentation is updated

##### Verification

- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Thresholds can be set and retrieved

##### Blocked by

None - can start immediately

##### Queue position

- Parent queue: direct subissue of #4200
- Execution wave: W1
- Ready to start when: this issue has no blockers

##### User stories covered

Not explicit in source

##### Files likely touched

- `src/billing/alerts/schema/`
- `tests/billing/alerts/schema/`

##### Estimated scope

Medium: 3-5 files

---

#### 2. Implement email alert delivery

##### Parent

#4200

##### What to build

Implement email delivery for billing alerts when thresholds are crossed. Integrate with the existing notification system.

##### Type

AFK

##### Acceptance criteria

- [ ] Email is sent when threshold is crossed
- [ ] Email content includes alert details
- [ ] Delivery failures are logged

##### Verification

- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Email is received on threshold breach

##### Blocked by

- Blocked by #1

##### Queue position

- Parent queue: direct subissue of #4200
- Execution wave: W2
- Ready to start when: #1 is closed

##### User stories covered

Not explicit in source

##### Files likely touched

- `src/billing/alerts/email/`
- `src/notifications/`
- `tests/billing/alerts/email/`

##### Estimated scope

Medium: 3-5 files

---

#### 3. Implement Slack alert delivery

##### Parent

#4200

##### What to build

Implement Slack delivery for billing alerts when thresholds are crossed. Integrate with the existing notification system.

##### Type

AFK

##### Acceptance criteria

- [ ] Slack message is sent when threshold is crossed
- [ ] Message includes alert details
- [ ] Delivery failures are logged

##### Verification

- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Slack message is received on threshold breach

##### Blocked by

- Blocked by #1

##### Queue position

- Parent queue: direct subissue of #4200
- Execution wave: W2
- Ready to start when: #1 is closed

##### User stories covered

Not explicit in source

##### Files likely touched

- `src/billing/alerts/slack/`
- `src/notifications/`
- `tests/billing/alerts/slack/`

##### Estimated scope

Medium: 3-5 files

---

#### 4. Build alert history UI

##### Parent

#4200

##### What to build

Create a UI for admins to view the history of billing alerts, including delivery status for both email and Slack alerts.

##### Type

AFK

##### Acceptance criteria

- [ ] UI displays alert history
- [ ] Delivery status for each alert is shown
- [ ] Supports filtering by alert type and date

##### Verification

- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: UI displays correct alert history

##### Blocked by

- Blocked by #2
- Blocked by #3

##### Queue position

- Parent queue: direct subissue of #4200
- Execution wave: W3
- Ready to start when: #2 and #3 are closed

##### User stories covered

Not explicit in source

##### Files likely touched

- `src/billing/alerts/ui/`
- `tests/billing/alerts/ui/`

##### Estimated scope

Medium: 3-5 files

---

### Managed parent-body block for #4200

```
<!-- prd-to-tasks:start -->

## Task graph

- [ ] W1 - #1 Add threshold schema support - AFK - blocked by none
- [ ] W2 - #2 Implement email alert delivery - AFK - blocked by #1
- [ ] W2 - #3 Implement Slack alert delivery - AFK - blocked by #1
- [ ] W3 - #4 Build alert history UI - AFK - blocked by #2, #3

## How to grab work

1. Open this parent issue and inspect its direct subissues.
2. The executable work is in the sibling implementation issues listed above.
3. Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
4. If several AFK issues are ready in the same wave, they may be worked in parallel.
5. Do not start HITL issues until the named human decision or review has happened.
<!-- prd-to-tasks:end -->
```

---

### Subissue Attachment Commands (Draft)

```bash
# After creating issues, attach them to the parent:
# PARENT_ISSUE_ID and CHILD_ISSUE_ID are placeholders

gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"
```

---

### Summary

Created task graph for billing alert policies (draft).

Parent: #4200 (existing)

Child issues:

1. #1 Add threshold schema support - W1 - AFK - blocked by none
2. #2 Implement email alert delivery - W2 - AFK - blocked by #1
3. #3 Implement Slack alert delivery - W2 - AFK - blocked by #1
4. #4 Build alert history UI - W3 - AFK - blocked by #2, #3

How to grab work:

- Open parent #4200 and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- Read the managed `Task graph` / `How to grab work` section in its body.

Notes:

- All issue numbers are placeholders for this dry run.
- No HITL slices identified; all are AFK.
- No real GitHub mutations performed.
