# Quickstart: Billing Disputes Workflow

## Prerequisites

- Access to the target billing portal repository that contains the existing `backend/` FastAPI service and `frontend/` React application referenced in `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/with_skill/run-1/outputs/plan.md`.
- PostgreSQL available for local or staging migrations.
- Backend tooling available for migrations/tests (`python3`, project virtualenv, Alembic/pytest or the repository equivalents).
- Frontend dependencies installed for the React + TypeScript app.
- A way to run the existing scheduler/worker process that will emit SLA warning/breach events from the persisted deadlines described in `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/with_skill/run-1/outputs/research.md`.

## 1. Implement

1. Add the dispute tables, constraints, and indexes from `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/with_skill/run-1/outputs/data-model.md`, then apply the migration:

```bash
cd backend && alembic upgrade head
```

Expected outcome: the database contains `disputes` and `dispute_events` (or their repository-equivalent names), with the composite list index, event timeline index, and SLA deadline columns in place.

2. Implement the backend endpoints and OpenAPI contract from `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/with_skill/run-1/outputs/contracts/disputes.openapi.yaml`, then run the narrow backend suite for the new module:

```bash
cd backend && pytest tests/contract/test_disputes_api.py tests/integration/test_disputes_workflow.py -q
```

Expected outcome: contract and workflow tests pass for create/list/detail/transition/assignment/export behavior, including agent vs manager permissions and append-only activity recording.

3. Implement the React list/detail/timeline screens using the pure-component and shared-type decisions in `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/with_skill/run-1/outputs/research.md`, then compile the frontend:

```bash
cd frontend && npm run build
```

Expected outcome: the frontend build succeeds with the new disputes feature routes, typed API client usage, and no TypeScript errors around status/action handling.

## 2. Validate

1. Re-run the backend contract and performance-focused tests after seeding representative dispute data:

```bash
cd backend && pytest tests/contract/test_disputes_api.py tests/performance/test_disputes_list_p95.py -q
```

Expected outcome: the API contract stays aligned to the OpenAPI artifact and the list endpoint demonstrates the required p95 target under a 50k-dispute test profile.

2. Validate the frontend role controls and timeline rendering:

```bash
cd frontend && npm test -- disputes
```

Expected outcome: agent-only creation flows, manager reassignment/override controls, and ordered activity timeline rendering all pass in the existing frontend test runner.

3. Validate monthly CSV export formatting and audit coverage:

```bash
cd backend && pytest tests/integration/test_dispute_export_csv.py tests/integration/test_dispute_sla_events.py -q
```

Expected outcome: the CSV export uses the documented column order and `text/csv` behavior, and SLA warning/breach events are emitted into the immutable timeline.

## 3. Rollout/Operate

1. Deploy the backend/frontend changes together so the UI and contract stay in sync.
2. Enable the existing scheduler/worker job that scans `sla_warn_at` and `sla_breach_at` and appends due events.
3. Monitor dispute list latency, active queue depth, and SLA breach counts after rollout.
4. Run the first monthly export with operations/finance and confirm the column set matches the contract artifact.

Expected outcome: support agents can manage disputes end-to-end, managers can reassign/override within policy, SLA deadlines generate auditable events, and finance receives a repeatable monthly export.
