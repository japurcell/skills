# Phase 0 Research: Release Calendar Role Controls

## Decision 1: Permission enforcement model

- Decision: Enforce permissions twice: route-level guards for immediate rejection and domain-level policy checks inside the release-window service.
- Rationale: The route layer protects HTTP entry points, while domain checks keep internal service reuse from bypassing security rules. This gives a single source of truth for role capabilities by product area.
- Alternatives considered:
  - Frontend-only permission checks: rejected because the browser is not a security boundary.
  - Route guards only: rejected because background jobs or internal service calls could bypass authorization.

## Decision 2: Transition API shape and compatibility window

- Decision: Introduce an additive `POST /release-windows/{id}/transitions` endpoint that accepts `targetState`, `reason`, and `expectedVersion`, while preserving existing read endpoints and layering optional workflow metadata into responses.
- Rationale: One generic mutation endpoint keeps approval/proposal/cancellation logic in one place, simplifies frontend integration, and satisfies the one-quarter backward-compatibility requirement.
- Alternatives considered:
  - Separate `/approve`, `/reject`, `/propose`, and `/cancel` endpoints: rejected because it duplicates transition validation and expands surface area.
  - Immediate versioned v2 API: rejected because the spec requires compatibility rather than a breaking migration.

## Decision 3: Workflow state machine and audit schema

- Decision: Model release-window workflow as an explicit state machine with immutable `release_window_transitions` records for every state change.
- Rationale: A state machine makes legal transitions testable and reviewable, while immutable audit records satisfy the requirement for reason plus actor metadata on every change.
- Alternatives considered:
  - Free-form status writes with handler-specific validation: rejected because it invites drift and inconsistent audit behavior.
  - Database triggers as the sole validation mechanism: rejected because application-level tests and error reporting would become harder to reason about.

## Decision 4: Notification delivery strategy

- Decision: Write approval/rejection notifications to an outbox table inside the same transaction as the state change, then dispatch asynchronously.
- Rationale: This guarantees that notifications are emitted only for committed changes and keeps approval actions within the latency budget by removing external network calls from the request path.
- Alternatives considered:
  - Inline synchronous calls to the notification service: rejected because failures would either slow or incorrectly fail user actions.
  - Fire-and-forget in-process callbacks: rejected because process crashes could drop events without traceability.

## Decision 5: Pending approvals query pattern

- Decision: Back `GET /release-windows/approvals/pending` with a grouped query over proposed release windows, indexed by `(state, product_area, updated_at DESC)`, and paginate within each response.
- Rationale: Grouping at the database/API layer avoids large client-side payloads, gives predictable ordering for release managers, and supports 300 concurrent users during planning week.
- Alternatives considered:
  - Client-side grouping after fetching every proposed window: rejected for latency and payload growth.
  - Materialized view refreshed on a schedule: rejected because the workflow requires near-real-time manager queues.

## Decision 6: Frontend interaction strategy for sub-150ms perceived latency

- Decision: Keep reads cacheable, use optimistic UI for editor proposal submission, and do immediate cache invalidation/refetch after manager approval or rejection.
- Rationale: Proposal actions feel instantaneous to editors, while manager actions still resolve against backend truth before the UI settles, which reduces state drift in multi-user planning sessions.
- Alternatives considered:
  - Full real-time socket synchronization: rejected as unnecessary scope for the requested feature.
  - No optimistic behavior at all: rejected because the UI would feel sluggish under network variance.

## Decision 7: Rollout and regression boundary

- Decision: Deploy backend schema/API support first, ship frontend controls behind existing role-aware rendering, and keep legacy read consumers operational for one quarter.
- Rationale: This sequencing reduces cross-team coordination risk and honors the compatibility constraint without blocking backend validation work.
- Alternatives considered:
  - Frontend-first rollout: rejected because required APIs and audit persistence would not exist yet.
  - Immediate removal of legacy fields or clients: rejected because the spec explicitly forbids breaking changes during the compatibility window.

## Unknown resolution summary

All actionable uncertainties from the spec are resolved for implementation planning:

- The workflow is implemented as a single audited transition API instead of separate action endpoints.
- Notification integration uses an outbox dispatcher to protect latency and durability.
- The grouped pending approvals read model and indexing strategy are defined.
- Frontend and backend responsibilities are split clearly enough for task decomposition.

No blocking research questions remain before `/create-tasks`.
