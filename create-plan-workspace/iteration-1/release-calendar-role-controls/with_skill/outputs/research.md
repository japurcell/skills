# Phase 0 Research: Release Calendar Role Controls

## Decisions & Rationale

### 1. Storage Model for Role Permissions

**Decision**: Role permissions stored as database records (role_permissions table) linked to users and calendar entities.

**Rationale**:
- Scalable for adding/revoking permissions without code changes
- Audit trail support via created_at, actor_id fields
- Supports dynamic product area grouping for pending approvals endpoint

**Alternatives Considered**:
- Hard-coded role matrix: rejected (not flexible for future team changes)
- JWT claims only: rejected (no audit trail, difficult to revoke)

### 2. State Machine Implementation

**Decision**: Use explicit state transition table with validation rules. Allowed transitions:
- draft → proposed (by editor/release_manager)
- proposed → approved (by release_manager only)
- proposed → blocked (by release_manager only)
- approved, blocked → cancelled (by release_manager)

**Rationale**:
- Prevents invalid state transitions
- Clear audit trail for each change
- Requirement explicitly states "every state transition requires a reason and actor metadata"

**Alternatives Considered**:
- Simple enum field: rejected (no runtime validation enforcement)
- Unstructured workflow service: rejected (hard to audit and maintain)

### 3. Notification Service Integration

**Decision**: Use event-based notification triggers on state transitions. Backend emits events for approval/rejection:
1. Proposed event → notify release_manager
2. Approved event → notify relevant teams
3. Rejected event → notify proposer

**Rationale**:
- Decouples calendar service from notification implementation
- Supports requirement: "Integrate with notification service for approvals and rejections"
- Aligns with existing notification service patterns in monorepo

**Alternatives Considered**:
- Synchronous notifications: rejected (potential latency spikes at 300 concurrent users)
- Polling: rejected (inefficient, delayed notifications)

### 4. Pending Approvals Endpoint Implementation

**Decision**: Query-based endpoint returning approval records grouped by product_area:
