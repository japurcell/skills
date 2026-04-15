# Quickstart: Billing Disputes Workflow Implementation

## 1. Backend foundation

1. Add dispute domain models/migrations for `Dispute` and `DisputeActivity` (and optional `DisputeAssignment`).
2. Implement service-layer transition policy and role authorization checks.
3. Persist SLA timestamps at create time and expose computed SLA state in list/detail responses.
4. Enforce append-only audit event writes for every mutation.

## 2. API implementation

1. Implement endpoints defined in `contracts/openapi-disputes.yaml`.
2. Add list filtering, pagination, and indexed query paths to satisfy p95 target.
3. Add monthly CSV export endpoint for dispute outcomes.
4. Add request/response validation aligned with contract schemas.

## 3. Frontend implementation

1. Build disputes list view with status, SLA indicators, assignee, and filters.
2. Build dispute detail view with timeline and comments.
3. Add actions for transition and reassignment with role-aware controls.
4. Add manager override flow for final outcome adjustments.

## 4. Validation and test flow

1. Run backend unit and integration tests for transition rules, role enforcement, SLA behavior, and export output.
2. Run contract tests verifying endpoint and schema conformance.
3. Run frontend tests for list/detail/action flows and role-gated UI.
4. Execute performance check for list endpoint at 50k-dispute scale; verify p95 <250ms.
5. Verify audit immutability by confirming no update/delete paths exist for timeline events.

## 5. Suggested command sequence (target implementation repo)

```bash
# Backend
pytest -q

# Contract checks (example)
pytest tests/contract -q

# Frontend (replace with repo-specific scripts)
npm test

# Optional performance benchmark script
# ./scripts/bench_disputes_list.sh
```

## Done criteria

- Role-based workflow complete for `agent` and `manager` actions.
- Required statuses and transitions enforced.
- SLA warning/breach behavior visible and test-covered.
- Immutable activity timeline in place for all key actions.
- OpenAPI contract and implementation aligned.
- Monthly CSV export available and validated.
