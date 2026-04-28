## Proposed vertical-slice breakdown

1. **Title**: Add billing alert threshold schema support
   **Type**: AFK
   **Execution wave**: W1
   **Blocked by**: None
   **User stories covered**: Store and manage billing alert thresholds

2. **Title**: Email alert delivery for billing thresholds
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Add billing alert threshold schema support
   **User stories covered**: Send email when billing threshold is exceeded

3. **Title**: Slack alert delivery for billing thresholds
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Add billing alert threshold schema support
   **User stories covered**: Send Slack notification when billing threshold is exceeded

4. **Title**: Billing alert history UI
   **Type**: AFK
   **Execution wave**: W3
   **Blocked by**: Slices 2-3: Email and Slack alert delivery
   **User stories covered**: Admins can view alert delivery history

## Child issue drafts

### Child 1: Add billing alert threshold schema support

## Parent

#4200

## What to build

Store billing alert policy configurations (thresholds, recurrence, recipients) in the database. This forms the foundation for all subsequent alert delivery.

## Type

AFK

## Acceptance criteria

- [ ] Schema exists for billing alert thresholds
- [ ] Thresholds can be created, read, updated, and deleted
- [ ] Thresholds include amount, currency, and recurrence settings

## Verification

- [ ] Tests pass: `npm run test -- billingAlerts.schema.test.ts`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Create a threshold via API and verify it's persisted

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #4200
- Execution wave: W1
- Ready to start when: this issue has no blockers

## User stories covered

Store and manage billing alert thresholds

## Files likely touched

- `src/db/migrations/billing_alerts_table.sql`
- `src/db/models/BillingAlert.ts`
- `src/api/billingAlerts.ts`
- `tests/db/models/BillingAlert.test.ts`

## Estimated scope

Medium: 3-5 files

### Child 2: Email alert delivery for billing thresholds

## Parent

#4200

## What to build

When a billing threshold is exceeded, send email notifications to configured recipients. The email should include threshold details and actual spend.

## Type

AFK

## Acceptance criteria

- [ ] Email is sent when threshold is exceeded
- [ ] Email includes spend amount and threshold
- [ ] Recipients receive emails based on policy

## Verification

- [ ] Tests pass: `npm run test -- billingAlerts.email.test.ts`
- [ ] Manual check: Trigger a threshold and verify email receipt

## Blocked by

- Blocked by #<child-1-issue-number>

## Queue position

- Parent queue: direct subissue of #4200
- Execution wave: W2
- Ready to start when: #4200's direct child issue for billing alert schema is closed

## User stories covered

Send email when billing threshold is exceeded

## Files likely touched

- `src/workers/billingAlertWorker.ts`
- `src/services/emailService.ts`
- `tests/workers/billingAlertWorker.test.ts`

## Estimated scope

Small: 1-2 files

### Child 3: Slack alert delivery for billing thresholds

## Parent

#4200

## What to build

When a billing threshold is exceeded, send Slack notifications to configured channels. The message should include threshold and spend details.

## Type

AFK

## Acceptance criteria

- [ ] Slack message is sent when threshold is exceeded
- [ ] Message includes spend amount and threshold
- [ ] Channel routing works based on policy

## Verification

- [ ] Tests pass: `npm run test -- billingAlerts.slack.test.ts`
- [ ] Manual check: Trigger a threshold and verify Slack message

## Blocked by

- Blocked by #<child-1-issue-number>

## Queue position

- Parent queue: direct subissue of #4200
- Execution wave: W2
- Ready to start when: #4200's direct child issue for billing alert schema is closed

## User stories covered

Send Slack notification when billing threshold is exceeded

## Files likely touched

- `src/workers/billingAlertWorker.ts`
- `src/integrations/slackIntegration.ts`
- `tests/integrations/slackIntegration.test.ts`

## Estimated scope

Small: 1-2 files

### Child 4: Billing alert history UI

## Parent

#4200

## What to build

Admins can view a history of sent billing alerts. The UI shows which thresholds were triggered, when, and delivery status (sent/failed).

## Type

AFK

## Acceptance criteria

- [ ] Alert history page displays past alerts
- [ ] Admins can filter by threshold or date range
- [ ] Delivery status is visible

## Verification

- [ ] Tests pass: `npm run test -- billingAlerts.history.test.ts`
- [ ] Manual check: View alert history page and verify past alerts display

## Blocked by

- Blocked by #<child-2-issue-number>, #<child-3-issue-number>

## Queue position

- Parent queue: direct subissue of #4200
- Execution wave: W3
- Ready to start when: both email and Slack alert delivery issues are closed

## User stories covered

Admins can view alert delivery history

## Files likely touched

- `src/features/billing/AlertHistory.tsx`
- `src/api/billingAlerts.ts`
- `tests/features/billing/AlertHistory.test.ts`

## Estimated scope

Small: 1-2 files

## Managed parent-body tracking guidance

<!-- prd-to-tasks:start -->

## Task graph

- [ ] W1 - #<child-1> Add billing alert threshold schema support - AFK - blocked by none
- [ ] W2 - #<child-2> Email alert delivery for billing thresholds - AFK - blocked by #<child-1>
- [ ] W2 - #<child-3> Slack alert delivery for billing thresholds - AFK - blocked by #<child-1>
- [ ] W3 - #<child-4> Billing alert history UI - AFK - blocked by #<child-2>, #<child-3>

## How to grab work

1. Open this parent issue and inspect its direct subissues.
2. The executable work is in the sibling implementation issues listed above.
3. Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
4. If several AFK issues are ready in the same wave, they may be worked in parallel.
5. Do not start HITL issues until the named human decision or review has happened.

<!-- prd-to-tasks:end -->

---

## Summary

Created task graph for billing alert policies feature.

Parent: #4200 (existing)

Child issues:

1. #<child-1> Add billing alert threshold schema support - W1 - AFK - blocked by none
2. #<child-2> Email alert delivery for billing thresholds - W2 - AFK - blocked by #<child-1>
3. #<child-3> Slack alert delivery for billing thresholds - W2 - AFK - blocked by #<child-1>
4. #<child-4> Billing alert history UI - W3 - AFK - blocked by #<child-2>, #<child-3>

How to grab work:

- Open parent #4200 and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- The managed `Task graph` / `How to grab work` section on the parent body makes the queue explicit.

Notes:

- Schema support (W1) must come first before both email and Slack delivery
- Email and Slack delivery (W2) can be implemented in parallel
- History UI (W3) depends on both delivery implementations being complete
- All work is AFK and can proceed once assigned
