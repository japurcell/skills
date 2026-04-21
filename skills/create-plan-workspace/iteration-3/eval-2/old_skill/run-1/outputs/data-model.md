# Data Model: Release Calendar Role Controls

## Entity: ReleaseCalendarRoleAssignment

- Purpose: Resolves the actor's effective permissions for release-calendar actions, optionally scoped by product area.
- Fields:
  - `user_id` (string, required)
  - `role` (enum: `viewer`, `editor`, `release_manager`, required)
  - `scope_type` (enum: `global`, `product_area`, required)
  - `scope_id` (string, nullable when `scope_type = global`)
  - `granted_at` (timestamp, required)
  - `granted_by` (string, required)
- Invariants:
  - At most one active assignment exists per `(user_id, scope_type, scope_id)`.
  - `viewer` is read-only.
  - `editor` can create and re-submit proposals but cannot approve or reject another user's proposal.
  - `release_manager` can perform all editor actions plus approval, rejection, and blocking transitions.

## Entity: ReleaseWindow

- Purpose: Canonical release-calendar record shown in the shared planning calendar.
- Fields:
  - `id` (uuid, required)
  - `product_area` (string, required)
  - `title` (string, required, 1..200)
  - `description` (string, optional)
  - `start_at` (timestamp, required)
  - `end_at` (timestamp, required, must be greater than `start_at`)
  - `state` (enum: `draft`, `proposed`, `approved`, `blocked`, `cancelled`, required)
  - `created_by` (string, required)
  - `updated_by` (string, required)
  - `created_at` (timestamp, required)
  - `updated_at` (timestamp, required)
  - `version` (integer, required, optimistic concurrency token)
- Relationships:
  - One-to-many with `ReleaseWindowTransition`.
  - One-to-many with `NotificationOutboxEvent` for approval/rejection side effects.
- Invariants:
  - `end_at > start_at`.
  - Existing overlap business rules remain unchanged unless separately configured by the current application.
  - Only the transition service mutates `state`.
  - Additive API fields must not remove or rename existing read properties during the compatibility window.

## Entity: ReleaseWindowTransition

- Purpose: Immutable audit history for every state transition.
- Fields:
  - `id` (uuid, required)
  - `release_window_id` (uuid, required, FK -> `ReleaseWindow.id`)
  - `from_state` (enum: `draft`, `proposed`, `approved`, `blocked`, `cancelled`, required)
  - `to_state` (same enum, required)
  - `reason` (string, required, min length 3, max length 1000)
  - `actor_id` (string, required)
  - `actor_role` (enum: `viewer`, `editor`, `release_manager`, required)
  - `actor_display_name` (string, optional)
  - `created_at` (timestamp, required)
  - `metadata` (json/jsonb, optional)
- Invariants:
  - Every change to `ReleaseWindow.state` writes exactly one transition record.
  - `reason`, `actor_id`, and `actor_role` are always present.
  - Transition history is append-only.

## Entity: NotificationOutboxEvent

- Purpose: Durable queue entry for approval/rejection notifications sent after commit.
- Fields:
  - `id` (uuid, required)
  - `aggregate_type` (string, required; value `release_window`)
  - `aggregate_id` (uuid, required; matches `ReleaseWindow.id`)
  - `event_type` (enum: `release_window.approved`, `release_window.rejected`, required)
  - `payload` (json/jsonb, required)
  - `status` (enum: `pending`, `processing`, `sent`, `failed`, required)
  - `retry_count` (integer, required, default 0)
  - `available_at` (timestamp, required)
  - `created_at` (timestamp, required)
  - `last_error` (string, optional)
- Invariants:
  - Events are created only for committed approval/rejection transitions.
  - Dispatcher retries failed sends with backoff and preserves the original payload.
  - Reprocessing is idempotent by `(aggregate_id, event_type, created_at)`.

## Read Model: PendingApprovalGroup

- Purpose: Response shape for the manager approvals queue grouped by product area.
- Fields:
  - `product_area` (string, required)
  - `pending_count` (integer, required)
  - `items` (array of `PendingApprovalItem`, required)
- Query rules:
  - Derived from `ReleaseWindow` rows where `state = proposed`.
  - Supports optional `productArea` filtering.
  - Orders groups alphabetically and items by `updated_at DESC`.

## Read Model: PendingApprovalItem

- Purpose: Lightweight summary used by the approval dashboard.
- Fields:
  - `id` (uuid, required)
  - `title` (string, required)
  - `product_area` (string, required)
  - `start_at` (timestamp, required)
  - `end_at` (timestamp, required)
  - `requested_by` (string, required)
  - `requested_at` (timestamp, required)
  - `latest_reason` (string, required)
  - `version` (integer, required)
- Invariants:
  - Each item represents the latest proposed state for a release window.
  - Values are sourced from the current release-window row plus the latest matching transition.

## State transitions

Allowed transitions and role requirements:

- `draft -> proposed` by `editor` or `release_manager`
- `draft -> cancelled` by owning `editor` or `release_manager`
- `proposed -> approved` by `release_manager`
- `proposed -> blocked` by `release_manager`
- `proposed -> cancelled` by owning `editor` or `release_manager`
- `blocked -> proposed` by `editor` or `release_manager`
- `blocked -> cancelled` by `release_manager`
- `approved -> blocked` by `release_manager`

Global validation rules:

- Every transition request must include `reason` and actor metadata.
- `viewer` can never invoke a transition.
- Illegal transitions return a conflict/validation error and must not change persisted state.
- Transition writes must enforce optimistic locking with `expectedVersion` when provided.

## Indexing and performance notes

- Index `release_windows(state, product_area, updated_at DESC)` for the pending approvals endpoint.
- Index `release_window_transitions(release_window_id, created_at DESC)` for transition history and latest-reason lookups.
- Index `notification_outbox_events(status, available_at)` for the dispatcher.
- Use optimistic locking via `ReleaseWindow.version` to prevent lost updates under concurrent planning edits.
