# Quickstart: Billing Disputes Workflow

## Prerequisites

- Backend service dependencies installed and Postgres reachable.
- Frontend dependencies installed.
- DB migration tooling available (Alembic or project equivalent).
- Environment variables configured for DB and API base URL.

## 1. Implement

1. Create and apply dispute schema migrations (tables for disputes, comments, assignment history, audit events, indexes):

```bash
cd backend && alembic upgrade head
```

Expected outcome: Migration completes with new dispute-related tables and indexes present.

2. Add backend endpoints from contract (list, detail, transition, reassign, CSV export) and SLA job wiring:

```bash
cd backend && pytest tests/integration/disputes -q
```

Expected outcome: Integration suite for dispute workflow passes, confirming transition rules and role checks.

3. Add frontend dispute list/detail and transition UI bound to the API contract:

```bash
cd frontend && npm run build
```

Expected outcome: Frontend compiles successfully with disputes routes/components and no type errors.

## 2. Validate

1. Run backend contract and performance-oriented checks for list endpoint behavior:

```bash
cd backend && pytest tests/contract/test_disputes_api.py tests/integration/test_dispute_list_performance.py -q
```

Expected outcome: Contract tests pass and performance test confirms list endpoint p95 target (<250ms) under seeded data profile.

2. Run frontend tests for role-specific actions and timeline rendering:

```bash
cd frontend && npm test -- disputes
```

Expected outcome: Agent and manager permissions, status transitions, and timeline rendering are validated.

3. Validate monthly CSV export semantics:

```bash
cd backend && pytest tests/integration/test_dispute_export_csv.py -q
```

Expected outcome: Export includes expected monthly rows, stable headers, and outcome totals.

## 3. Rollout/Operate

1. Enable SLA job in production scheduler and monitor warning/breach event counts.
2. Add dashboard/alerts for breaches by assignee and queue backlog.
3. Run first monthly export in production and confirm accounting handoff.

Expected outcome: Dispute operations are observable, SLA events fire automatically, and reporting is reproducible.
