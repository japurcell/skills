# Data Model: Release Calendar Role Controls

## Entity: ProductArea

- Purpose: Organizational grouping used to scope release windows, permissions, and manager approval queues.
- Fields:
  - `id` (string or uuid, required)
  - `slug` (string, required, unique)
  - `display_name` (string, required)
  - `active` (boolean, required)
- Relationships:
  - One-to-many with `ReleaseWindow`
  - One-to-many with `ReleaseCalendarRoleAssignment` when permissions are scoped by area
- Invariants:
  - `slug` is stable enough to support grouping and filtering in the approvals endpoint.
  - Inactive product areas cannot receive new release-window proposals without an explicit override.

## Entity: ReleaseCalendarRoleAssignment

- Purpose: Resolves a user's effective release-calendar role globally or for a specific product area.
- Fields:
  - `id` (uuid, required)
  - `user_id` (string, required)
  - `role` (enum: `viewer`, `editor`, `release_manager`, required)
  - `scope_type` (enum: `global`, `product_area`, required)
  - `scope_id` (string or uuid, nullable when `scope_type = global`)
  - `granted_at` (timestamp, required)
  - `granted_by` (string, required)
  - `revoked_at` (timestamp, nullable)
- Invariants:
  - At most one active assignment exists per `(user_id, scope_type, scope_id)`.
  - `viewer` is read-only.
  - `editor` can draft, propose, and cancel within allowed workflow rules but cannot approve/reject proposals.
  - `release_manager` can perform manager-only transitions for all release windows inside scope.

## Entity: ReleaseWindow

- Purpose: Canonical planning record rendered in the shared release calendar.
- Fields:
  - `id` (uuid, required)
  - `product_area_id` (string or uuid, required, FK -> `ProductArea.id`)
  - `title` (string, required, 1..200)
  - `description` (string, optional)
  - `start_at` (timestamp, required)
  - `end_at` (timestamp, required)
  - `state` (enum: `draft`, `proposed`, `approved`, `blocked`, `cancelled`, required)
  - `created_by` (string, required)
  - `updated_by` (string, required)
  - `created_at` (timestamp, required)
  - `updated_at` (timestamp, required)
  - `version` (integer, required)
- Relationships:
  - Many-to-one with `ProductArea`
  - One-to-many with `ReleaseWindowTransition`
  - One-to-many with `NotificationOutboxEvent`
- Invariants:
  - `end_at > start_at`.
  - Only the transition service may change `state`.
  - Every successful transition increments `version`.
  - Existing read fields remain available during the one-quarter compatibility window.

## Entity: ReleaseWindowTransition

- Purpose: Immutable audit record for every successful workflow state transition.
- Fields:
  - `id` (uuid, required)
  - `release_window_id` (uuid, required, FK -> `ReleaseWindow.id`)
  - `from_state` (enum: `draft`, `proposed`, `approved`, `blocked`, `cancelled`, required)
  - `to_state` (same enum, required)
  - `reason` (string, required, 3..1000 chars)
  - `actor_id` (string, required)
  - `actor_role` (enum: `viewer`, `editor`, `release_manager`, required)
  - `actor_display_name` (string, optional)
  - `created_at` (timestamp, required)
  - `metadata` (json/jsonb, optional)
- Invariants:
  - Every change to `ReleaseWindow.state` writes exactly one corresponding transition row.
  - Transition history is append-only.
  - `reason`, `actor_id`, and `actor_role` are always persisted.
  - Actor metadata is derived from authenticated context, not trusted from arbitrary client input.

## Entity: NotificationOutboxEvent

- Purpose: Durable queue entry for approval/rejection notifications emitted after transaction commit.
- Fields:
  - `id` (uuid, required)
  - `aggregate_type` (string, required, value `release_window`)
  - `aggregate_id` (uuid, required)
  - `event_type` (enum: `release_window.approved`, `release_window.rejected`, `release_window.blocked`, required)
  - `payload` (json/jsonb, required)
  - `status` (enum: `pending`, `processing`, `sent`, `failed`, `dead_letter`, required)
  - `retry_count` (integer, required, default 0)
  - `available_at` (timestamp, required)
  - `created_at` (timestamp, required)
  - `last_error` (string, optional)
- Invariants:
  - Outbox events are created inside the same transaction as the successful workflow transition.
  - Dispatcher retries preserve the original payload and are idempotent.
  - Provider-specific delivery identifiers, if any, live in `payload` or related dispatch metadata rather than mutating the canonical release-window record.

## Read Model: PendingApprovalGroup

- Purpose: Manager-facing response group for pending approvals bucketed by product area.
- Fields:
  - `productAreaId` (string or uuid, required)
  - `productArea` (string, required)
  - `pendingCount` (integer, required)
  - `items` (array of `PendingApprovalItem`, required)
  - `nextCursor` (string, nullable)
- Query rules:
  - Only includes release windows where `state = proposed`.
  - Group ordering is stable by `productArea` ascending.
  - Item ordering within a group is `updated_at DESC`, then `id DESC` for tie-breaking.

## Read Model: PendingApprovalItem

- Purpose: Lightweight summary shown in the release-manager queue.
- Fields:
  - `id` (uuid, required)
  - `title` (string, required)
  - `productAreaId` (string or uuid, required)
  - `productArea` (string, required)
  - `startAt` (timestamp, required)
  - `endAt` (timestamp, required)
  - `requestedBy` (string, required)
  - `requestedAt` (timestamp, required)
  - `latestReason` (string, required)
  - `version` (integer, required)
- Invariants:
  - Each item reflects the latest proposed state for one release window.
  - `latestReason` is sourced from the latest transition into the current state.

## Command Model: TransitionRequest

- Purpose: Request payload for the additive workflow write endpoint.
- Fields:
  - `targetState` (enum: `proposed`, `approved`, `blocked`, `cancelled`, required)
  - `reason` (string, required, 3..1000 chars)
  - `expectedVersion` (integer, optional but strongly recommended)
- Invariants:
  - Client cannot supply `actor_id` or `actor_role`; those are derived from the authenticated request context.
  - Illegal role/state combinations fail validation without mutating data.

## Lifecycle / State transitions

Allowed transitions:

- `draft -> proposed` by `editor` or `release_manager`
- `draft -> cancelled` by owning `editor` or `release_manager`
- `proposed -> approved` by `release_manager`
- `proposed -> blocked` by `release_manager`
- `proposed -> cancelled` by owning `editor` or `release_manager`
- `blocked -> proposed` by `editor` or `release_manager`
- `blocked -> cancelled` by `release_manager`
- `approved -> blocked` by `release_manager` when downstream issues require reopening

Global validation rules:

- Every transition requires `reason` plus server-derived actor metadata.
- `viewer` can never submit a transition.
- Conflict responses are returned for illegal state changes or stale `expectedVersion` values.
- Approval queue entries are derived from current `ReleaseWindow` state, not from a separately maintained approval table.

## Indexing and performance notes

- Index `release_windows(state, product_area_id, updated_at DESC, id DESC)` for the grouped pending-approvals endpoint.
- Index `release_window_transitions(release_window_id, created_at DESC)` for transition history and latest-reason lookups.
- Index `notification_outbox_events(status, available_at)` for dispatcher polling.
- Keep permission resolution cacheable within a request, but never trust frontend-only role checks for authorization.
