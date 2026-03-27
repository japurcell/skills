# Phase 0 Research: Release Calendar Role Controls

## Decision 1: Persist role permissions and release-window state in PostgreSQL with explicit transition history table

- Decision: Store release windows in a primary table and write every state transition to a `release_window_transitions` table containing `from_state`, `to_state`, `reason`, `actor_id`, `actor_role`, and `occurred_at`.
- Rationale: This satisfies the hard requirement that every transition has reason + actor metadata while enabling auditability and deterministic state reconstruction.
- Alternatives considered:
  - Event sourcing only: Strong history but adds higher operational complexity than needed for this feature scope.
  - JSON history column on release window: Simpler schema but weak queryability and indexing for audits.

## Decision 2: Enforce role checks server-side with a policy matrix and transition guard

- Decision: Implement centralized authorization policy (`viewer`, `editor`, `release_manager`) and transition guard that validates both role permission and legal state movement.
- Rationale: Prevents accidental edits and ensures UI behavior cannot bypass critical workflow rules.
- Alternatives considered:
  - Frontend-only role enforcement: Rejected due to security risk.
  - Scattered endpoint-level checks: Rejected due to drift risk and harder maintenance.

## Decision 3: Use explicit transition command endpoints for backward compatibility

- Decision: Add versioned command endpoints for propose/approve/reject/block/cancel, while keeping existing read endpoints behavior-compatible for one quarter.
- Rationale: Introduces workflow controls without breaking current clients during compatibility window.
- Alternatives considered:
  - Mutating existing endpoint semantics in place: Rejected; high compatibility risk.
  - Feature flag per endpoint with no versioning: Rejected; harder external contract clarity.

## Decision 4: Pending approvals endpoint grouped in SQL by product area

- Decision: Provide dedicated endpoint returning pending (`proposed`) windows grouped by `product_area`, including counts and item summaries.
- Rationale: Meets requirement directly and keeps frontend simple with a single API call.
- Alternatives considered:
  - Frontend grouping from flat list: Rejected due to larger payload handling and duplicated logic.
  - Materialized view only: Rejected for now; unnecessary complexity at current scale.

## Decision 5: Notification integration via asynchronous domain events

- Decision: Emit domain events on approval/rejection transitions and hand off to existing notification service client asynchronously.
- Rationale: Keeps transition latency low for UI while guaranteeing side effects are tracked and retriable.
- Alternatives considered:
  - Synchronous notification call in request path: Rejected due to latency and availability coupling.
  - Cron-based polling for changes: Rejected due to delayed user feedback.

## Decision 6: Meet performance/concurrency goals via index strategy + optimistic concurrency

- Decision: Add indexes on (`state`, `product_area`, `window_start`) and use optimistic concurrency (`version` column) on release window updates.
- Rationale: Supports pending approvals query and avoids conflicting writes during planning week at 300 concurrent users.
- Alternatives considered:
  - Serializable transactions globally: Rejected due to throughput cost.
  - In-memory locking only: Rejected due to multi-instance deployment risk.

## Decision 7: Testing approach anchored to existing stack (Jest + Playwright)

- Decision: Add unit tests for policy/transition guards, integration tests for API contracts and transition persistence, and Playwright tests for role-restricted UI flows.
- Rationale: Aligns with current tooling and validates both correctness and user-visible behavior.
- Alternatives considered:
  - New testing framework adoption: Rejected; unnecessary migration cost.
  - E2E-only coverage: Rejected; insufficient isolation for state-machine correctness.

## Decision 8: Unknowns closure summary

All material unknowns from technical context are resolved:

- Language/runtime versions selected.
- Storage and schema strategy selected.
- API compatibility strategy selected.
- Notification pattern selected.
- Performance and concurrency strategy selected.
- Test strategy selected.

No blocking clarifications remain for implementation planning.
