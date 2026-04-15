# Data Model: Release Calendar Role Controls

## Overview

The model introduces explicit role permissions, release-window lifecycle governance, and auditable state transitions.

## Entities

## 1. ReleaseWindow

- Purpose: Planned release interval tied to product area and workflow state.
- Fields:
  - `id` (UUID, PK)
  - `product_area` (text, indexed)
  - `title` (text)
  - `description` (text, nullable)
  - `window_start` (timestamp with time zone)
  - `window_end` (timestamp with time zone)
  - `state` (enum: `draft`, `proposed`, `approved`, `blocked`, `cancelled`, indexed)
  - `created_by` (UUID)
  - `updated_by` (UUID)
  - `version` (int, default 1) for optimistic concurrency
  - `created_at` (timestamp with time zone)
  - `updated_at` (timestamp with time zone)
- Validation rules:
  - `window_start < window_end`
  - `title` non-empty
  - `state` must be valid enum value

## 2. ReleaseWindowTransition

- Purpose: Immutable audit record of all state transitions with required reason and actor metadata.
- Fields:
  - `id` (UUID, PK)
  - `release_window_id` (UUID, FK -> ReleaseWindow.id, indexed)
  - `from_state` (enum)
  - `to_state` (enum)
  - `reason` (text, required)
  - `actor_id` (UUID, required)
  - `actor_role` (enum: `viewer`, `editor`, `release_manager`, required)
  - `occurred_at` (timestamp with time zone, indexed)
- Validation rules:
  - `reason` required for every transition
  - `from_state != to_state`
  - Actor role must match role assignment at transition time

## 3. UserRoleAssignment

- Purpose: Assign release-calendar roles to users scoped by product area.
- Fields:
  - `id` (UUID, PK)
  - `user_id` (UUID, indexed)
  - `product_area` (text, indexed)
  - `role` (enum: `viewer`, `editor`, `release_manager`)
  - `effective_from` (timestamp with time zone)
  - `effective_to` (timestamp with time zone, nullable)
- Validation rules:
  - No overlapping active assignments for same (`user_id`, `product_area`)

## 4. ApprovalNotificationEvent

- Purpose: Outbox/event record to integrate approval and rejection notifications.
- Fields:
  - `id` (UUID, PK)
  - `release_window_id` (UUID, FK)
  - `event_type` (enum: `release_window_approved`, `release_window_rejected`)
  - `payload` (jsonb)
  - `status` (enum: `pending`, `sent`, `failed`)
  - `attempt_count` (int)
  - `created_at` (timestamp with time zone)
  - `updated_at` (timestamp with time zone)

## Relationships

- `ReleaseWindow` 1 -> N `ReleaseWindowTransition`
- `ReleaseWindow` 1 -> N `ApprovalNotificationEvent`
- `UserRoleAssignment` governs permissions for operations over `ReleaseWindow` by matching `product_area`.

## State Machine

- Allowed transitions:
  - `draft -> proposed` (editor, release_manager)
  - `proposed -> approved` (release_manager)
  - `proposed -> blocked` (release_manager)
  - `proposed -> cancelled` (editor, release_manager)
  - `approved -> cancelled` (release_manager)
  - `blocked -> proposed` (editor, release_manager)
- Disallowed examples:
  - `draft -> approved` direct path
  - Any write transition by `viewer`

## Invariants

- Every persisted transition has non-empty `reason`, `actor_id`, and `actor_role`.
- Latest `ReleaseWindow.state` equals `to_state` of most recent transition (except initialization record policy if used).
- Pending approvals are exactly `ReleaseWindow` rows where `state = proposed`.
- Approval/rejection transitions enqueue one notification event.

## Indexes

- `release_windows(state, product_area, window_start)` for pending approvals and calendar load.
- `release_window_transitions(release_window_id, occurred_at desc)` for audit timeline.
- `user_role_assignments(user_id, product_area, effective_to)` for fast permission resolution.

## Lifecycle Notes

- Creation flow: create in `draft` with creator as actor.
- Proposal flow: write transition to `proposed` with reason.
- Decision flow: `release_manager` approves or blocks; emits notification event.
- Cancellation flow: allowed per transition matrix, always reasoned and audited.
