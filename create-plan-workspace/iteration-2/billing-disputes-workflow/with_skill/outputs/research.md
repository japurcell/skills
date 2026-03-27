# Research: Billing Disputes Workflow

## Decision 1: Represent lifecycle with strict server-side transition rules

- Decision: Enforce allowed transitions on the backend using a transition map (`open -> investigating|rejected`, `investigating -> waiting_on_customer|resolved|rejected`, `waiting_on_customer -> investigating|resolved|rejected`, terminal states no outgoing transitions except manager override).
- Rationale: Guarantees consistent workflow state and prevents UI-only validation bypass.
- Alternatives considered:
  - Client-side validation only: rejected due to integrity risk.
  - Fully dynamic status graph in DB config: rejected for initial scope complexity.

## Decision 2: Store immutable activity timeline in append-only audit table

- Decision: Use an append-only `dispute_events` table with event type, actor, timestamp, metadata JSON, and previous/new status where applicable.
- Rationale: Satisfies immutable audit requirement and supports timeline rendering without mutating historical records.
- Alternatives considered:
  - Mutable `updated_at` snapshots on dispute row: rejected because history can be lost.
  - Event sourcing for entire dispute aggregate: rejected as too heavy for current scope.

## Decision 3: Drive SLA warning/breach via scheduled job with computed deadlines

- Decision: Persist `sla_warn_at` and `sla_breach_at` at creation; run a periodic backend job (every 5 minutes) to emit warning/breach events and mark SLA state.
- Rationale: Keeps SLA logic deterministic and queryable while avoiding per-request computation overhead.
- Alternatives considered:
  - Compute SLA state at read time only: rejected due to inconsistent alerting behavior.
  - External queue-only timer per dispute: rejected for higher operational complexity.

## Decision 4: API contract format is OpenAPI with explicit transition and assignment endpoints

- Decision: Define contracts in OpenAPI 3.1, including list/detail/transition/reassign/export endpoints and role constraints.
- Rationale: Aligns with team preference and supports backend/frontend integration and contract testing.
- Alternatives considered:
  - Ad hoc markdown endpoint docs: rejected as non-enforceable.
  - GraphQL migration: rejected as out of scope.

## Decision 5: Meet list p95 target with indexed filtering + keyset pagination

- Decision: Implement indexed query paths on `(status, assignee_id, created_at)` plus keyset pagination by `(created_at, id)` for stable performance at 50k disputes.
- Rationale: Improves latency predictability compared with large offset scans.
- Alternatives considered:
  - Offset pagination only: rejected for degraded deep-page performance.
  - Materialized view for all list variants: deferred unless performance tests fail.

## Decision 6: Monthly CSV export generated server-side and streamed

- Decision: Build server endpoint returning streamed CSV for a month filter; include totals and standardized outcome columns.
- Rationale: Supports operational reporting without requiring direct DB access by agents.
- Alternatives considered:
  - Manual DB export scripts: rejected for repeatability/compliance concerns.
  - Async offline file generation only: deferred unless export runtime becomes large.
