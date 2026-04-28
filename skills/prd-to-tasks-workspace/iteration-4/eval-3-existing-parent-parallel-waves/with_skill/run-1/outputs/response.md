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

<!-- prd-to-tasks:start -->
## Task graph

- [ ] W1 - #<child-issue-number-1> Add threshold schema support - AFK - blocked by none
- [ ] W2 - #<child-issue-number-2> Implement email alert delivery - AFK - blocked by #<child-issue-number-1>
- [ ] W2 - #<child-issue-number-3> Implement Slack alert delivery - AFK - blocked by #<child-issue-number-1>
- [ ] W3 - #<child-issue-number-4> Build alert history UI - AFK - blocked by #<child-issue-number-2>, #<child-issue-number-3>

## How to grab work

1. Open this parent issue (#4200) and inspect its direct subissues.
2. The executable work is in the sibling implementation issues listed above.
3. Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
4. If several AFK issues are ready in the same wave, they may be worked in parallel.
5. Do not start HITL issues until the named human decision or review has happened.
<!-- prd-to-tasks:end -->

---

## Draft Child Issues

### 1. Add threshold schema support
**Parent:** #4200
**Type:** AFK
**Execution wave:** W1
**Blocked by:** None
**User stories covered:** Not explicit in source

#### What to build
Add schema support for defining billing alert thresholds, including storage, validation, and migration as needed.

#### Acceptance criteria
- [ ] Schema supports threshold configuration for billing alerts
- [ ] Validation logic prevents invalid thresholds
- [ ] Migration covers existing data

#### Verification
- [ ] Tests pass: `<test command>`
- [ ] Build succeeds: `<build command>`
- [ ] Manual check: Thresholds can be configured and validated

#### Files likely touched
- `src/billing/schema/`
- `migrations/`
- `tests/billing/`

#### Estimated scope
Medium: 3-5 files

---

### 2. Implement email alert delivery
**Parent:** #4200
**Type:** AFK
**Execution wave:** W2
**Blocked by:** #<child-issue-number-1>
**User stories covered:** Not explicit in source

#### What to build
Send billing alerts via email when thresholds are crossed, using the new schema.

#### Acceptance criteria
- [ ] Email is sent to configured recipients when alert triggers
- [ ] Email content includes threshold and usage details
- [ ] Delivery failures are logged

#### Verification
- [ ] Tests pass: `<test command>`
- [ ] Build succeeds: `<build command>`
- [ ] Manual check: Email alerts are sent and received

#### Files likely touched
- `src/billing/alerts/email/`
- `src/billing/alerts/`
- `tests/billing/alerts/`

#### Estimated scope
Medium: 3-5 files

---

### 3. Implement Slack alert delivery
**Parent:** #4200
**Type:** AFK
**Execution wave:** W2
**Blocked by:** #<child-issue-number-1>
**User stories covered:** Not explicit in source

#### What to build
Send billing alerts via Slack when thresholds are crossed, using the new schema.

#### Acceptance criteria
- [ ] Slack message is sent to configured channel when alert triggers
- [ ] Message includes threshold and usage details
- [ ] Delivery failures are logged

#### Verification
- [ ] Tests pass: `<test command>`
- [ ] Build succeeds: `<build command>`
- [ ] Manual check: Slack alerts are sent and received

#### Files likely touched
- `src/billing/alerts/slack/`
- `src/billing/alerts/`
- `tests/billing/alerts/`

#### Estimated scope
Medium: 3-5 files

---

### 4. Build alert history UI
**Parent:** #4200
**Type:** AFK
**Execution wave:** W3
**Blocked by:** #<child-issue-number-2>, #<child-issue-number-3>
**User stories covered:** Not explicit in source

#### What to build
Create a UI for admins to view the history of billing alerts, including delivery status for both email and Slack.

#### Acceptance criteria
- [ ] UI lists all alert events with timestamps and delivery status
- [ ] Supports filtering by alert type and status
- [ ] Errors and delivery failures are visible

#### Verification
- [ ] Tests pass: `<test command>`
- [ ] Build succeeds: `<build command>`
- [ ] Manual check: Alert history UI works as described

#### Files likely touched
- `src/billing/ui/AlertHistory.tsx`
- `src/billing/alerts/`
- `tests/billing/ui/`

#### Estimated scope
Medium: 3-5 files

---

## Summary
Created draft task graph for billing alert policies in parent #4200. All issues are AFK and vertically sliced. Use placeholders for child issue numbers in this dry run.
