## Proposed vertical-slice breakdown (present first)

1. **Title**: Add billing alert threshold schema support
   **Type**: AFK
   **Execution wave**: W1
   **Blocked by**: None
   **User stories covered**: Threshold schema for billing alerts

2. **Title**: Implement email alert delivery for billing alerts
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Add billing alert threshold schema support
   **User stories covered**: Email alert delivery

3. **Title**: Implement Slack alert delivery for billing alerts
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Add billing alert threshold schema support
   **User stories covered**: Slack alert delivery

4. **Title**: Add alert history UI (depends on both delivery paths)
   **Type**: AFK
   **Execution wave**: W3
   **Blocked by**: Slice 2: Implement email alert delivery for billing alerts, Slice 3: Implement Slack alert delivery for billing alerts
   **User stories covered**: Alert history UI

---

### Draft child issues

#### Child Issue 1: Add billing alert threshold schema support

```
## Parent

#4200

## What to build

Add schema support for billing alert thresholds. Define and persist threshold values that trigger billing alerts.

## Type

AFK

## Acceptance criteria

- [ ] Threshold schema is defined and persisted
- [ ] Thresholds can be set and updated
- [ ] Thresholds are used to trigger alerts

## Verification

- [ ] Tests pass: `<insert test command>`
- [ ] Build succeeds: `<insert build command>`
- [ ] Manual check: Set and update thresholds, verify alerts trigger

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #4200
- Execution wave: W1
- Ready to start when: this issue has no blockers

## User stories covered

Threshold schema for billing alerts

## Files likely touched

- `src/billing/`
- `src/alerts/`
- `tests/billing/`

## Estimated scope

Medium: 3-5 files
```

#### Child Issue 2: Implement email alert delivery for billing alerts

```
## Parent

#4200

## What to build

Implement email delivery for billing alerts triggered by threshold crossings.

## Type

AFK

## Acceptance criteria

- [ ] Email alerts are sent when thresholds are crossed
- [ ] Email content includes relevant billing info

## Verification

- [ ] Tests pass: `<insert test command>`
- [ ] Build succeeds: `<insert build command>`
- [ ] Manual check: Receive email alert for threshold crossing

## Blocked by

- Blocked by #<child-issue-1>

## Queue position

- Parent queue: direct subissue of #4200
- Execution wave: W2
- Ready to start when: #<child-issue-1> is closed

## User stories covered

Email alert delivery

## Files likely touched

- `src/alerts/`
- `src/email/`
- `tests/alerts/`

## Estimated scope

Medium: 3-5 files
```

#### Child Issue 3: Implement Slack alert delivery for billing alerts

```
## Parent

#4200

## What to build

Implement Slack delivery for billing alerts triggered by threshold crossings.

## Type

AFK

## Acceptance criteria

- [ ] Slack alerts are sent when thresholds are crossed
- [ ] Slack messages include relevant billing info

## Verification

- [ ] Tests pass: `<insert test command>`
- [ ] Build succeeds: `<insert build command>`
- [ ] Manual check: Receive Slack alert for threshold crossing

## Blocked by

- Blocked by #<child-issue-1>

## Queue position

- Parent queue: direct subissue of #4200
- Execution wave: W2
- Ready to start when: #<child-issue-1> is closed

## User stories covered

Slack alert delivery

## Files likely touched

- `src/alerts/`
- `src/slack/`
- `tests/alerts/`

## Estimated scope

Medium: 3-5 files
```

#### Child Issue 4: Add alert history UI

```
## Parent

#4200

## What to build

Add a UI to display the history of billing alerts. This depends on both email and Slack alert delivery being implemented.

## Type

AFK

## Acceptance criteria

- [ ] Users can view a list of past billing alerts
- [ ] Alert history includes delivery channel and timestamp

## Verification

- [ ] Tests pass: `<insert test command>`
- [ ] Build succeeds: `<insert build command>`
- [ ] Manual check: View alert history in UI

## Blocked by

- Blocked by #<child-issue-2>
- Blocked by #<child-issue-3>

## Queue position

- Parent queue: direct subissue of #4200
- Execution wave: W3
- Ready to start when: #<child-issue-2> and #<child-issue-3> are closed

## User stories covered

Alert history UI

## Files likely touched

- `src/ui/alerts/`
- `src/alerts/`
- `tests/ui/alerts/`

## Estimated scope

Medium: 3-5 files
```

---

### Managed parent-body tracking guidance (for #4200)

```
<!-- prd-to-tasks:start -->
## Task graph

- [ ] W1 - #<child-issue-1> Add billing alert threshold schema support - AFK - blocked by none
- [ ] W2 - #<child-issue-2> Implement email alert delivery for billing alerts - AFK - blocked by #<child-issue-1>
- [ ] W2 - #<child-issue-3> Implement Slack alert delivery for billing alerts - AFK - blocked by #<child-issue-1>
- [ ] W3 - #<child-issue-4> Add alert history UI - AFK - blocked by #<child-issue-2>, #<child-issue-3>

## How to grab work

1. Open this parent issue and inspect its direct subissues.
2. The executable work is in the sibling implementation issues listed above.
3. Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
4. If several AFK issues are ready in the same wave, they may be worked in parallel.
5. Do not start HITL issues until the named human decision or review has happened.
<!-- prd-to-tasks:end -->
```

---

### Summary

Created task graph for billing alert policies feature.

Parent: #4200 (existing)

Child issues:

1. #<child-issue-1> Add billing alert threshold schema support - W1 - AFK - blocked by none
2. #<child-issue-2> Implement email alert delivery for billing alerts - W2 - AFK - blocked by #<child-issue-1>
3. #<child-issue-3> Implement Slack alert delivery for billing alerts - W2 - AFK - blocked by #<child-issue-1>
4. #<child-issue-4> Add alert history UI - W3 - AFK - blocked by #<child-issue-2>, #<child-issue-3>

How to grab work:

- Open parent #4200 and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- Read the managed `Task graph` / `How to grab work` section in the parent body.

Notes:

- Email and Slack alert delivery can proceed in parallel after threshold schema support.
- Alert history UI depends on both delivery paths.
- All slices are AFK; no HITL slices required.
- Issue numbers are placeholders for this dry run.
