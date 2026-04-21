# Quickstart: Billing Disputes Workflow

## Prerequisites

- Work in the actual billing portal repository that already contains the FastAPI + PostgreSQL backend and the React + TypeScript frontend described in `plan.md`.
- Before coding, map the assumed `backend/...` and `frontend/src/features/disputes/...` paths from `plan.md` onto the portal repo's real module names.
- Have local database credentials, an authenticated test account with both `agent` and `manager` roles, and the dispute OpenAPI contract at `contracts/disputes-openapi.yaml` available for reference.

## 1. Implement

1. Create the dispute schema objects and indexes from the data model.
   - Command: `python3 -m alembic revision -m "add billing disputes workflow"`
   - Expected outcome: a new migration file is created under the backend migration directory with `disputes` and `dispute_activity` tables plus the list/SLA indexes called out in `data-model.md`.

2. Apply the migration locally and wire the FastAPI router/service layer from Research decisions 1-4.
   - Command: `python3 -m alembic upgrade head`
   - Expected outcome: the local Postgres database contains the new tables/indexes and the backend can serve the dispute router without schema errors.

3. Run the application stack with the contract and UI paths from `plan.md` in place.
   - Command: `python3 -m uvicorn backend.app.main:app --reload`
   - Expected outcome: the backend starts successfully, exposes the dispute routes defined in `contracts/disputes-openapi.yaml`, and is ready for frontend integration.

## 2. Validate

1. Verify backend role gates, transitions, audit logging, and performance-sensitive list behavior.
   - Command: `python3 -m pytest backend/tests/integration/test_disputes_api.py backend/tests/performance/test_disputes_list_query.py`
   - Expected outcome: tests confirm agents can create disputes, managers can reassign/override outcomes, every mutation appends timeline activity, and the list-query harness remains within the p95 target.

2. Verify the React dispute pages and assignment/timeline UX from Research decision 6.
   - Command: `npm test -- --runInBand src/features/disputes/__tests__/DisputeListPage.test.tsx src/features/disputes/__tests__/DisputeDetailPage.test.tsx`
   - Expected outcome: list filters, detail rendering, SLA badges, assignment controls, and timeline state changes render from server-backed data without duplicated client-state bugs.

3. Smoke-test the OpenAPI contract and monthly CSV export.
   - Command: `curl -sS -H 'Accept: text/csv' 'http://127.0.0.1:8000/api/disputes/exports/monthly?month=2026-04' | head`
   - Expected outcome: the response starts with CSV headers for the monthly outcome export and matches the fields documented in `contracts/disputes-openapi.yaml`.

## 3. Rollout/Operate

- Deploy the database migration before enabling dispute traffic so the list/detail endpoints never run against a partial schema.
- Monitor list endpoint p95 latency and the count of breached disputes after launch; both should be visible in the portal's existing API and operations dashboards.
- Schedule or expose the monthly CSV export only for authorized internal users, and verify exported rows reconcile with terminal dispute counts for the same month.
- Document the mapping from the assumed plan paths to the portal repo's real module names so `/create-tasks` and implementation work stay aligned.
