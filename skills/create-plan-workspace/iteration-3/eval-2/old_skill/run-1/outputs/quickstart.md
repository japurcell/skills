# Quickstart: Release Calendar Role Controls

## Prerequisites

- Node.js 20+ and the monorepo package manager (`pnpm` assumed below).
- PostgreSQL available for local backend development.
- Seeded users or fixtures covering `viewer`, `editor`, and `release_manager`.
- Notification service sandbox or a local mock endpoint for approval/rejection events.
- Environment variables for backend DB connectivity and notification credentials configured.

## 1. Implement

1. Apply the workflow persistence changes from plan slices 2 and 4.

```bash
pnpm --filter backend db:migrate
pnpm --filter backend dev
```

Expected outcome:

- Database schema includes `release_window_transitions` and `notification_outbox_events`.
- The backend starts with an additive `POST /api/release-windows/:id/transitions` endpoint and grouped pending-approvals read support.

2. Wire the role-aware Next.js UI from plan slice 5.

```bash
pnpm --filter frontend dev
```

Expected outcome:

- The calendar page renders read-only, proposal, or approval controls based on the authenticated role.
- Transition attempts require a reason dialog before submit.

## 2. Validate

1. Run focused automated coverage for the workflow and UI.

```bash
pnpm --filter backend test -- release-windows
pnpm --filter frontend test:e2e -- release-calendar
```

Expected outcome:

- Jest verifies authorization, legal/illegal transitions, optimistic locking, audit writes, and notification outbox creation.
- Playwright verifies viewer/editor/manager flows without regressing existing read-only calendar behavior.

2. Verify the grouped approvals contract against a running local stack.

```bash
curl -s http://localhost:3000/api/release-windows/approvals/pending | jq '.groups'
```

Expected outcome:

- The response contains groups keyed by `productArea`, each item remains in `proposed` state, and missing roles receive a 403 on manager-only views.

## 3. Rollout/Operate

- Deploy backend schema/API support before enabling the new frontend controls.
- Preserve additive read compatibility for one quarter; remove deprecated assumptions only after dependent teams migrate.
- Monitor API p95 latency for calendar and pending-approval routes, notification outbox retry rates, and authorization-denial counts by role.
- If notification failures spike, keep workflow state authoritative and replay from `notification_outbox_events` rather than asking users to resubmit transitions.
