# Data Model: Release Calendar Role Controls

## Entity: UserRoleAssignment

- Purpose: Determines user permissions in release calendar context.
- Fields:
  - `user_id` (string, required)
  - `role` (enum: `viewer`, `editor`, `release_manager`, required)
  - `scope_type` (enum: `global`, `product_area`, required)
  - `scope_id` (string, nullable when global)
  - `granted_at` (timestamp, required)
  - `granted_by` (string, required)
- Invariants:
  - One active assignment per `(user_id, scope_type, scope_id)`.
  - `viewer` has read-only access.
  - `editor` can create proposal transitions but cannot approve/reject.
  - `release_manager` can approve/reject and perform all editor actions.

## Entity: ReleaseWindow

- Purpose: Represents a planned release window on the calendar.
- Fields:
  - `id` (uuid, required)
  - `product_area` (string, required)
  - `title` (string, required, 1..200)
  - `description` (string, optional)
  - `start_at` (timestamp, required)
  - `end_at` (timestamp, required, must be > `start_at`)
  - `state` (enum: `draft`, `proposed`, `approved`, `blocked`, `cancelled`, required)
  - `created_by` (string, required)
  - `updated_by` (string, required)
  - `created_at` (timestamp, required)
  - `updated_at` (timestamp, required)
  - `version` (integer, required, optimistic concurrency)
- Relationships:
  - One-to-many with `ReleaseWindowTransition`.
- Invariants:
  - Overlap policy follows existing business rules (unchanged by this feature).
  - State transitions only via validated transition service.

## Entity: ReleaseWindowTransition

- Purpose: Immutable audit record for every state change.
- Fields:
  - `id` (uuid, required)
  - `release_window_id` (uuid, required, FK -> `ReleaseWindow.id`)
  - `from_state` (enum, required)
  - `to_state` (enum, required)
  - `reason` (string, required, min length 3)
  - `actor_id` (string, required)
  - `actor_role` (enum: `viewer`, `editor`, `release_manager`, required)
  - `actor_display_name` (string, optional)
  - `created_at` (timestamp, required)
  - `metadata` (jsonb, optional)
- Invariants:
  - Every `ReleaseWindow.state` change creates exactly one transition record.
  - `reason`, `actor_id`, and `actor_role` are non-null on every transition.

## Entity: PendingApprovalView (read model)

- Purpose: Supports grouped listing of release windows awaiting manager action.
- Source: Derived from `ReleaseWindow` where `state = proposed`.
- Fields:
  - `product_area` (string)
  - `pending_count` (integer)
  - `items` (array of lightweight release window summaries)
- Query constraints:
  - Supports optional `product_area` filter.
  - Stable ordering by `updated_at DESC`.

## State Transitions

Allowed transitions and role requirements:

- `draft -> proposed` by `editor` or `release_manager` (reason required)
- `proposed -> approved` by `release_manager` (reason required; emits approval notification)
- `proposed -> blocked` by `release_manager` (reason required)
- `proposed -> cancelled` by `editor` owner or `release_manager` (reason required)
- `approved -> blocked` by `release_manager` (reason required)
- `blocked -> proposed` by `editor` or `release_manager` (reason required)
- `blocked -> cancelled` by `release_manager` (reason required)
- `draft -> cancelled` by `editor` owner or `release_manager` (reason required)

Disallowed examples:

- Any transition by `viewer`
- `approved -> draft`
- Any transition without reason/actor metadata

## Indexing and performance notes

- `release_windows(state, product_area, updated_at DESC)` for pending approvals.
- `release_window_transitions(release_window_id, created_at DESC)` for audit timeline retrieval.
- Use optimistic locking via `version` to prevent lost updates under concurrency.
