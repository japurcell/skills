# Quickstart: Billing Disputes Workflow

## Prerequisites

- Review `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/old_skill/run-1/outputs/plan.md`, `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/old_skill/run-1/outputs/research.md`, `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/old_skill/run-1/outputs/data-model.md`, and `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/old_skill/run-1/outputs/contracts/openapi-disputes.yaml` before implementation so the domain model, decisions, and interface contract stay aligned.
- Work inside the billing portal implementation repository that owns the FastAPI backend and React frontend described in the spec.
- Ensure database migration tooling and role-based auth fixtures for `agent` and `manager` are available in that repository.

## 1. Implement

1. Scaffold the feature slices that match the planned backend/frontend structure.

   ```bash
   cd <billing-portal-repo> && mkdir -p backend/src/api/disputes backend/src/services/disputes backend/src/models backend/src/exports backend/tests/unit/disputes backend/tests/integration/disputes backend/tests/contract frontend/src/pages/disputes frontend/src/components/disputes frontend/src/services/disputesApi frontend/tests/disputes
   ```

   Expected outcome: the repository contains dedicated backend, contract-test, and frontend folders that match the structure defined in `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/old_skill/run-1/outputs/plan.md`.

2. Implement the backend domain model and migration using the entities and invariants from `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/old_skill/run-1/outputs/data-model.md`.

   Expected outcome: `Dispute` and `DisputeActivity` persistence supports required fields, SLA deadlines, immutable timeline events, and role-aware transitions.

3. Implement the FastAPI endpoints described in `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/old_skill/run-1/outputs/contracts/openapi-disputes.yaml` and wire them to service-layer authorization, transition, assignment, and CSV-export logic.

   Expected outcome: create/list/detail/transition/assignment/export flows all share the same contract and audit behavior.

4. Build the React list and detail experiences with status/SLA indicators, timeline rendering, assignment controls, and manager-only override actions.

   Expected outcome: agents can create and progress disputes, and managers can reassign or override outcomes without bypassing the audit trail.

## 2. Validate

1. Run backend unit, integration, and contract suites for disputes.

   ```bash
   cd <billing-portal-repo> && python3 -m pytest backend/tests/unit/disputes backend/tests/integration/disputes backend/tests/contract -q
   ```

   Expected outcome: transition rules, role permissions, SLA timestamps, audit immutability, and contract conformance all pass.

2. Run the frontend disputes workflow tests in the repository's existing React test runner.

   ```bash
   cd <billing-portal-repo>/frontend && npm test -- disputes
   ```

   Expected outcome: list/detail rendering, comments, transitions, reassignment, and manager-only override controls behave as specified in `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/old_skill/run-1/outputs/contracts/openapi-disputes.yaml` and `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/old_skill/run-1/outputs/research.md`.

3. Verify the live API behaviors needed for operations reporting.

   ```bash
   curl -sS -H 'Accept: text/csv' 'http://localhost:8000/api/disputes/exports/monthly?month=2026-04' | head
   ```

   Expected outcome: the response is CSV output for finalized April disputes with columns that match the export model in `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/old_skill/run-1/outputs/data-model.md`.

## 3. Rollout/Operate

- Enable queue monitoring for disputes nearing `sla_warn_at` or `sla_breach_at`, and add dashboards/alerts for breached open disputes.
- Train support managers on reassignment and outcome override flows so supervisory actions stay explicit and auditable.
- Schedule or document the monthly export operating procedure, including who runs exports, where CSVs are delivered, and how reruns are handled after data corrections.
- After rollout, monitor list endpoint p95 latency and timeline query performance to confirm the 50k-dispute target still holds under production traffic.
