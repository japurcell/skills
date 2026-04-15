# Quickstart: Release Calendar Role Controls

## 1. Prerequisites

- Node.js 20+ and package manager used by the monorepo (`npm`, `pnpm`, or `yarn`)
- Running PostgreSQL instance used by backend local environment
- Existing auth seed users for roles: `viewer`, `editor`, `release_manager`
- Notification service sandbox or local mock endpoint enabled

## 2. Implement

1. Add role guards and transition service:
   - Implement role checks in backend `auth/role-guards`.
   - Implement explicit transition validator/state machine in backend domain service.
2. Persist transition metadata:
   - Ensure every state mutation path writes immutable `ReleaseWindowTransition` entries.
3. Add/extend endpoints:
   - Proposal and state transition mutation endpoints.
   - Pending approvals grouped endpoint.
4. Integrate notifications:
   - Emit approve/reject events after successful commit.
5. Update frontend:
   - Role-aware action visibility and disabled states.
   - Pending approvals UI grouped by product area.

Suggested commands:

```bash
# install dependencies (workspace root)
pnpm install

# run backend and frontend in dev mode
pnpm --filter backend dev
pnpm --filter frontend dev
```

Expected result:

- Backend and frontend start successfully.
- Calendar UI renders role-specific controls based on authenticated user role.

## 3. Validate

Run test suite for impacted layers:

```bash
# backend unit/integration
pnpm --filter backend test -- release-windows

# frontend e2e focused on release calendar role flows
pnpm --filter frontend test:e2e -- release-calendar
```

Expected result:

- Tests verify role permissions, legal/illegal transitions, required reason and actor metadata, notification emission behavior, and pending approvals grouping.
- No regressions in existing read flows.

## 4. API verification checklist

- `viewer` receives 403 on all release-window write endpoints.
- `editor` can propose and cancel own draft/proposed windows where allowed.
- `release_manager` can approve/reject transitions and receives success responses.
- Transition payloads without `reason` are rejected with validation errors.
- Pending approvals endpoint returns grouped data by `product_area` and honors filter.
- Legacy consumers continue to read existing release window endpoints without breaking schema changes.

## 5. Rollout notes

- Deploy backend additive changes first; frontend can safely roll out after.
- Keep compatibility window active for one quarter.
- Monitor endpoint p95 latency and notification failure rates.
- Add temporary logging/metrics on transition denials to detect misconfigured role assignments.
