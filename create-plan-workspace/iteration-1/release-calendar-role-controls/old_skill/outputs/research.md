# Research: Release Calendar Role Controls

## Decision 1: Role-Based Access Control Implementation

**Decision**: Implement role-based access control using a middleware pattern in Express.js with role-specific permissions stored in the database.

**Rationale**:
- The existing monorepo already uses Express.js middleware for authentication and authorization.
- Role-based access control (RBAC) is a well-established pattern for web applications.
- Storing roles and permissions in PostgreSQL allows runtime changes without code deployment.
- Middleware pattern integrates seamlessly with existing request/response cycle.

**Alternatives considered**:
- **ABAC (Attribute-Based Access Control)**: More flexible but adds complexity for a simple three-role system. Postpone if future requirements demand attribute-level control.
- **JWT claims**: Could embed roles in tokens but would require token refresh on permission changes. Database-driven approach is more flexible.
- **Policy engine (e.g., OPA)**: Overkill for three-role system; would complicate deployment and testing.

**Resolution**: Middleware-enforced RBAC with database-backed role-permission mappings.

---

## Decision 2: State Machine for Release Windows

**Decision**: Implement release window state transitions using a finite state machine with enforced rules: only specific roles can trigger specific state transitions.

**Rationale**:
- Spec requires explicit multi-state workflow (draft → proposed → approved/blocked → cancelled).
- State machines prevent invalid transitions (e.g., cannot go from `approved` directly to `draft`).
- Role-based guards on transitions enforce approval requirements (only `release_manager` can move to `approved`).
- Clear state semantics reduce bugs and improve testability.

**Alternatives considered**:
- **Direct state update**: Simple but allows invalid transitions and loses workflow semantics.
- **Event sourcing**: Provides full audit trail but adds complexity to querying current state. Defer unless audit requirements intensify.
- **Database constraints alone**: Insufficient; business logic for approval rules needs role context.

**Resolution**: In-memory state machine in `ApprovalWorkflow` service with database-persisted state and audit log. Transitions include reason and actor metadata (Spec #4).

---

## Decision 3: Notification Service Integration

**Decision**: Integrate via async queuing pattern: state transitions publish events to a notification queue; notification service subscribes asynchronously.

**Rationale**:
- Decouples calendar service from notification service; calendar operations don't block on notifications.
- Handles notification delivery failures gracefully (retry queue).
- Follows existing monorepo patterns (assumed queue/event bus exists).
- Supports future integrations (Slack, email, webhooks) without calendar service changes.

**Alternatives considered**:
- **Synchronous call**: Simplest but creates tight coupling and risk that calendar operation fails if notification service is down.
- **Webhook direct call**: Works but notification service outage blocks approvals. Queue pattern is safer.

**Resolution**: Publish `ReleaseWindowStateChanged` event to notification queue on every successful state transition with transition details (old state, new state, reason, actor).

---

## Decision 4: API Design for Approvals Endpoint

**Decision**: Create a new endpoint `GET /api/approvals?groupBy=productArea` that returns pending approvals for the current user's release_manager role.

**Rationale**:
- Spec requirement #6: "endpoint to list pending approvals grouped by product area".
- Query parameter allows flexible grouping without creating separate endpoints.
- Current user context (from auth middleware) ensures users see only relevant approvals.
- Supports pagination for scales up to 300 concurrent users.

**Alternatives considered**:
- **Separate endpoints**: `/api/approvals/by-product-area` versus `/api/approvals/by-date`, etc. Too many endpoints; query params are more flexible.
- **WebSocket for real-time updates**: Not in scope; batch polling via `GET` is simpler and sufficient for now.

**Resolution**: Implement `GET /api/approvals` with query parameters for grouping and filtering. Return approval records with state, reason, product area, and timestamps.

---

## Decision 5: Backward Compatibility Strategy

**Decision**: Use API versioning and database migration pattern to ensure one-quarter backward compatibility.

**Rationale**:
- Spec constraint: existing API clients must work during transition period.
- Database migrations are additive: new tables for roles/permissions; existing calendar table unchanged.
- New endpoints (`/api/approvals`, role-check middleware) do not affect existing endpoints.
- Deprecation warnings guide clients to migrate to role-aware endpoints.

**Alternatives considered**:
- **Parallel APIs**: Maintain old and new API versions separately (too much code duplication).
- **Feature flags**: Can be used for gradual rollout; combine with versioning for cleanest transition.

**Resolution**: Existing calendar endpoints continue to work as-is (backward compatible). New role-aware features in new endpoints and UI paths. Deprecate old behavior over one quarter with clear warnings.

---

## Decision 6: UI Latency Performance

**Decision**: Implement optimistic updates on the frontend with role-based permission checks to achieve <150ms perceived latency.

**Rationale**:
- Spec requirement: <150ms latency for calendar UI interactions.
- Optimistic updates (update UI immediately, confirm with backend) eliminate perceived network delay.
- Role-based permission checks in UI (via React hooks) prevent invalid state before server call.
- Fallback to server validation ensures security.

**Alternatives considered**:
- **Backend optimization alone**: Backend <50ms latency is hard; network round-trip adds latency regardless.
- **GraphQL subscriptions**: Powerful but adds complexity; optimistic updates are simpler for this scope.

**Resolution**: Optimistic updates with local state management (React Context or Zustand); role-based UI permission checks; fallback server validation for security.

---

## Summary of Technical Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| **Role-based access** | Middleware-enforced RBAC with database-backed roles | Existing pattern, database-driven flexibility |
| **State management** | Finite state machine with role-based guards | Prevents invalid transitions, clear workflow |
| **Notifications** | Async event-based queue integration | Decoupling, resilience, future extensibility |
| **Approvals endpoint** | `GET /api/approvals?groupBy=productArea` | Flexible, spec-compliant, scalable |
| **Backward compatibility** | Additive migrations, new endpoints, deprecation warnings | Meet one-quarter constraint without duplication |
| **UI latency** | Optimistic updates + role-based checks | Achieve <150ms perceived latency |

All unknowns from Technical Context are now resolved. Proceed to Phase 1 design.
