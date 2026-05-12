# Quickstart: Release Calendar Role Controls

## Prerequisites

- Work in the actual product monorepo that contains the Node backend, Next.js frontend, existing auth layer, and notification service integration; this benchmark workspace only contains planning artifacts.
- Have access to three test users representing `viewer`, `editor`, and `release_manager` roles.
- Use these artifacts while implementing:
  - `plan.md` for scope and compatibility constraints
  - `research.md` for the authorization, caching, and testing decisions
  - `data-model.md` for the state machine and invariants
  - `contracts/release-calendar-role-controls.openapi.yaml` for the API contract

## 1. Implement

1. Locate the current release-calendar UI, release-window API handlers, auth policy layer, and notification integration in the product monorepo.
   ```bash
   git grep -nE "release.?calendar|release.?window|approval|notification|authorize|role" .
   ```
   Expected outcome: you identify the packages/modules that currently own calendar rendering, release-window persistence, authorization checks, and outbound notifications so the feature can be added without inventing parallel paths.

2. Add the workflow state machine and immutable transition log from `data-model.md`, then wire the additive endpoints defined in `contracts/release-calendar-role-controls.openapi.yaml`.
   ```bash
   git grep -nE "draft|proposed|approved|blocked|cancelled|transition" .
   ```
   Expected outcome: you confirm whether an existing workflow model can be extended; if not, you add durable transition records, role-derived capabilities, and grouped pending-approval queries without breaking existing read APIs.

3. Update the Next.js calendar UI to honor server-derived capabilities, render role-appropriate controls, and revalidate the calendar plus pending-approval summary after mutations.
   - Keep read-heavy calendar views cache-friendly and use targeted refresh/revalidation after proposing or deciding.
   - Make rejection send the window back to `draft` with a required reason field.
   - Emit notification work only after the transition persists successfully.

## 2. Validate

1. Verify the grouped pending-approvals endpoint as a release manager.
   ```bash
   curl -sS "$BASE_URL/api/release-approvals/pending?groupBy=productArea"      -H "Authorization: Bearer $RELEASE_MANAGER_TOKEN"
   ```
   Expected outcome: the response returns product-area groups containing only `proposed` release windows and includes no unauthorized areas.

2. Verify that an editor can propose but cannot approve.
   ```bash
   curl -i -X POST "$BASE_URL/api/release-windows/$WINDOW_ID/transitions"      -H "Authorization: Bearer $EDITOR_TOKEN"      -H "Content-Type: application/json"      -d '{"targetState":"approved","reason":"ship it"}'
   ```
   Expected outcome: the API rejects the request with `403 Forbidden`, proving that approval remains exclusive to `release_manager`.

3. Run focused backend and UI tests on the actual monorepo implementation.
   ```bash
   npx jest --runInBand release-calendar
   npx playwright test --grep "release calendar approvals"
   ```
   Expected outcome: Jest covers permission and transition rules, and Playwright verifies that each role sees the right calendar controls and approval flow behavior end to end.

## 3. Rollout/Operate

- Ship the new endpoints and response fields additively so existing clients remain functional for the one-quarter compatibility window.
- Monitor transition-log volume, approval latency, and notification failures during planning week.
- Track perceived calendar latency for the approval summary and main calendar view; re-tune caching/revalidation if interactions exceed the 150ms target.
- Exercise one full decision round trip before rollout completion.
  ```bash
  curl -sS -X POST "$BASE_URL/api/release-windows/$WINDOW_ID/transitions"     -H "Authorization: Bearer $RELEASE_MANAGER_TOKEN"     -H "Content-Type: application/json"     -d '{"targetState":"draft","decisionType":"reject","reason":"conflicts with freeze window"}'
  ```
  Expected outcome: the window returns to `draft`, the transition log records the rejection reason plus actor metadata, and the rejection notification is queued after commit.
