# Quickstart: Release Calendar Role Controls

## Prerequisites

- Monorepo with `backend/` and `frontend/` projects available.
- Node.js 20+ and package manager used by repo (`pnpm` commands shown below).
- PostgreSQL reachable for local integration tests.
- Notification service sandbox credentials configured.

## 1. Implement

1. Generate and apply schema changes for state transitions, role assignments, and notification outbox.

```bash
pnpm --filter backend run db:migrate
```

Expected outcome: migration completes successfully; new tables/indexes for `release_window_transitions`, `user_role_assignments`, and notification outbox are present.

2. Implement role policy and transition guard in backend, then wire new versioned endpoints from the API contract.

```bash
pnpm --filter backend run test -- release-approval
```

Expected outcome: unit tests for role matrix and state-machine guards pass, confirming `viewer` cannot mutate and `release_manager` controls approvals.

3. Implement frontend role-aware calendar actions and pending approvals panel grouped by product area.

```bash
pnpm --filter frontend run test -- release-calendar
```

Expected outcome: component/service tests pass; editors can propose, managers can approve/reject, viewers are read-only.

## 2. Validate

1. Run backend integration tests for API contracts and transition audit invariants.

```bash
pnpm --filter backend run test:integration -- release-windows
```

Expected outcome: integration suite verifies transition reason/actor metadata is required and persisted for all transitions.

2. Run end-to-end validation for role behavior and approval workflow latency-sensitive paths.

```bash
pnpm --filter frontend run playwright test e2e/release-calendar
```

Expected outcome: E2E tests pass for viewer/editor/release_manager journeys and pending approvals visibility.

3. Run full checks used by CI before merge.

```bash
pnpm run lint && pnpm run test
```

Expected outcome: lint/test pipeline is green with no regressions.

## 3. Rollout/Operate

1. Deploy backend endpoints with compatibility mode enabled (keep legacy read contracts for one quarter).

```bash
pnpm --filter backend run deploy -- --env=staging
```

Expected outcome: versioned write endpoints are live in staging; legacy consumers continue functioning.

2. Verify operational metrics and notification delivery.

```bash
pnpm --filter backend run ops:check -- release-windows
```

Expected outcome: pending approval endpoint p95 remains within target, notification event queue drains without sustained failures.

3. Promote to production and monitor planning-week concurrency.

```bash
pnpm --filter backend run deploy -- --env=production
```

Expected outcome: feature is available to all roles; system supports 300 concurrent users with no permission or transition integrity incidents.
