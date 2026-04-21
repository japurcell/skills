# Quickstart: Release Calendar Role Controls

## Prerequisites

- Node.js 20+ installed for the target monorepo runtime.
- PostgreSQL available locally or in a shared dev environment.
- Seed data or fixtures for three authenticated personas: `viewer`, `editor`, and `release_manager`.
- Notification service sandbox credentials or a mock endpoint so outbox dispatch can be exercised safely.
- The implementation repository checked out with package names equivalent to the backend/frontend paths described in `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-2/with_skill/run-1/outputs/plan.md`.

## 1. Implement

1. Land plan slices 1-4 on the backend: role policy, audited transition persistence, additive HTTP endpoints, and outbox dispatch.

```bash
pnpm --filter backend db:migrate
pnpm --filter backend dev
```

Expected outcome:

- The database now contains release-window transition and notification-outbox tables (or equivalent schema changes).
- The backend exposes `POST /api/release-windows/:releaseWindowId/transitions` and `GET /api/release-windows/approvals/pending` without removing legacy read behavior.
- Manager approvals and editor proposals record `reason`, actor metadata, and optimistic-lock version changes.

2. Land plan slice 5 on the frontend: role-aware calendar controls, grouped approval queue, and reason capture UX.

```bash
pnpm --filter frontend dev
```

Expected outcome:

- The calendar loads with read-only behavior for `viewer`, proposal actions for `editor`, and approval/rejection controls for `release_manager`.
- Interactive controls are isolated to client-side components while initial data load stays server-rendered.
- Every workflow action requires a reason dialog before the mutation request is sent.

## 2. Validate

1. Prove backend workflow rules and async side effects from plan slices 1-4.

```bash
pnpm --filter backend test -- release-windows
```

Expected outcome:

- Jest covers role authorization, legal/illegal transitions, optimistic-lock conflicts, grouped pending-approval queries, and notification outbox creation.
- Async assertions confirm approval/rejection transitions enqueue outbox work without blocking the request path.

2. Prove role-aware user flows from plan slice 5 with isolated identities.

```bash
pnpm --filter frontend test:e2e -- release-calendar
```

Expected outcome:

- Playwright passes separate viewer/editor/release-manager scenarios using distinct authenticated states.
- Viewer attempts to mutate are denied, editor can propose changes, and release managers can approve/block while seeing grouped pending items by product area.

3. Smoke-test the additive approval queue contract against a running local stack.

```bash
curl -s "http://localhost:3000/api/release-windows/approvals/pending?productArea=payments" | jq '.groups[0].productArea'
```

Expected outcome:

- The response returns grouped pending approvals keyed by product area.
- Only `proposed` release windows appear in the queue, and unauthorized users receive a 403 for manager-only access.

## 3. Rollout/Operate

- Deploy backend schema and additive APIs before exposing the new frontend controls.
- Keep old read consumers supported for one quarter; remove temporary compatibility shims only after dependent teams migrate.
- Monitor API p95 latency for calendar and approvals routes, notification retry/dead-letter rates, and authorization-denial counts by role/product area.
- If notification delivery fails, replay from `notification_outbox_events` rather than asking users to repeat approval or rejection actions.
