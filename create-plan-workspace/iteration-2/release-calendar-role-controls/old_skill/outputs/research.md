# Phase 0 Research: Release Calendar Role Controls

## Decision 1: Authorization model and permission enforcement

- Decision: Use role-based access control with endpoint-level guards plus domain-level transition authorization checks.
- Rationale: Endpoint guards stop unauthorized access early; domain checks prevent bypass when services are reused internally and ensure state transitions remain safe.
- Alternatives considered:
  - Frontend-only role checks: rejected because it is not a security boundary.
  - Endpoint guards only: rejected because direct service calls could bypass route protections.

## Decision 2: Workflow state machine design

- Decision: Implement an explicit backend state machine for `draft`, `proposed`, `approved`, `blocked`, `cancelled` with transition validation and mandatory transition metadata (`reason`, `actor_id`, `actor_role`, timestamp).
- Rationale: A centralized state machine guarantees legal transitions and consistent auditability.
- Alternatives considered:
  - Free-form status updates with ad hoc checks: rejected due to drift and weak audit guarantees.
  - Database triggers as sole validator: rejected due to lower application-level clarity and harder testability.

## Decision 3: API compatibility strategy

- Decision: Keep existing read endpoints stable; introduce additive response fields and new mutation/pending-approval endpoints for one-quarter compatibility window.
- Rationale: Meets backward-compatibility constraint while enabling progressive adoption.
- Alternatives considered:
  - Immediate breaking API replacement: rejected due to compatibility requirement.
  - Forked v2-only API: rejected due to migration overhead in one-quarter coexistence period.

## Decision 4: Notification integration pattern

- Decision: Emit approval decision events (`release_window.approved`, `release_window.rejected`) asynchronously after transaction commit using an outbox-style publish step.
- Rationale: Prevents notification loss on partial failures and decouples user-facing latency from notification delivery.
- Alternatives considered:
  - Inline synchronous notification call in request path: rejected due to latency and reliability risks.
  - Fire-and-forget in-process callback: rejected due to crash-loss risk.

## Decision 5: Pending approvals endpoint query approach

- Decision: Add `GET /release-windows/approvals/pending?productArea=` that groups by product area in query results, backed by index on `(state, product_area, updated_at)`.
- Rationale: Satisfies grouped listing requirement and keeps query performant at planning-week concurrency.
- Alternatives considered:
  - Client-side grouping after full fetch: rejected for excess payload and latency.
  - Materialized view only: deferred as unnecessary complexity for initial scope.

## Decision 6: Performance strategy for <150ms perceived UI latency

- Decision: Use optimistic UI update for editor proposal submit, server-side pagination/filtering for pending approvals, and selective cache invalidation for calendar slices.
- Rationale: Keeps interactions responsive while preserving backend correctness.
- Alternatives considered:
  - Fully real-time websocket sync for all users: rejected as out-of-scope complexity for this feature.
  - No optimistic interactions: rejected due to perceived latency risk.

## Unknown resolution summary

All previously implied unknowns are resolved:

- Tech stack and test stack confirmed from spec constraints.
- Role and state model concretized.
- API shape and compatibility approach defined.
- Notification and performance strategies selected.

No unresolved blocking questions remain for Phase 1.
