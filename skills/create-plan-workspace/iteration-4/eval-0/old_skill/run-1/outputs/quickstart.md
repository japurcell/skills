# Quickstart: Billing Disputes Workflow

## Prerequisites

- Access to the target billing portal repository with the FastAPI backend, React + TypeScript frontend, and PostgreSQL migrations.
- Local database or review environment credentials that can run the new disputes migration.
- Existing auth stack capable of exposing `agent` and `manager` roles to backend dependencies.
- Ability to run backend tests with `python3 -m pytest` and frontend tests through the portal's existing Node-based test runner.

## 1. Implement

1. **Apply the schema and audit-log design from `plan.md` + `data-model.md`.**
   - Command: `alembic revision -m "billing disputes workflow" && alembic upgrade head`
   - Expected outcome: new `billing_disputes` and `dispute_activity` tables exist with status/SLA constraints and the unresolved-dispute indexes described in `research.md` Decision 2.

2. **Wire the FastAPI contract from `contracts/disputes.openapi.yaml`.**
   - Command: `python3 -m uvicorn backend.app.main:app --reload`
   - Expected outcome: the running service exposes list/detail/create/transition/assignment/export dispute endpoints, and `/openapi.json` includes the disputes tag plus a documented `text/csv` monthly export response (Decision 3).

3. **Add the React feature module using the backend state machine and RBAC rules.**
   - Command: `(cd frontend && npm run dev)`
   - Expected outcome: agents can create and progress disputes, managers can reassign/override outcomes, and the UI renders timeline + SLA state from the API model described in `data-model.md`.

## 2. Validate

1. **Verify backend lifecycle, RBAC, and contract behavior.**
   - Command: `python3 -m pytest backend/tests/integration/test_disputes_api.py backend/tests/contract/test_disputes_openapi.py -q`
   - Expected outcome: tests prove valid transitions, role restrictions, immutable activity creation, and OpenAPI alignment for JSON plus CSV endpoints.

2. **Verify frontend workflow coverage.**
   - Command: `(cd frontend && npm test -- disputes)`
   - Expected outcome: dispute list/detail/create flows, manager reassignment, and outcome override UI coverage pass against the API shapes and permissions from Decisions 3 and 4.

3. **Smoke-test export and SLA behavior end to end.**
   - Command: `curl -i "http://localhost:8000/api/disputes/exports/monthly?month=2026-03"`
   - Expected outcome: HTTP 200 with `Content-Type: text/csv`, CSV headers matching `data-model.md`, and terminal disputes only; unresolved disputes continue to surface `warning`/`breached` SLA states in the list endpoint.

## 3. Rollout/Operate

- Release backend migration before exposing the frontend route so the list/detail screens never hit missing tables.
- Seed or configure the allowed `reason_code` set before enabling create flow, otherwise agents will hit validation failures at the API layer.
- Add operational visibility for unresolved counts by `sla_state` and manager overrides so Decisions 1, 2, and 5 remain observable after rollout.
- Keep the first increment on synchronous documented CSV export; if monthly exports become operationally heavy, promote that endpoint behind a queued job as a follow-on task rather than expanding scope in the initial implementation.
