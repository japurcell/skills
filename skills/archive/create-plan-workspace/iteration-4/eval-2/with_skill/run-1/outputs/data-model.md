# Data Model: Release Calendar Role Controls

## Overview

The feature adds scoped role assignments, a release-window workflow with immutable transition history, grouped approval summaries, and notification tracking for approval decisions. The existing release calendar remains the system of record for window scheduling; the new data captures permissions and approval lifecycle details.

## Entities

### 1. CalendarRoleAssignment

Purpose: Defines what a user can do within the release calendar.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | UUID/string | Stable assignment id |
| `userId` | string | Authenticated principal |
| `role` | enum | `viewer`, `editor`, `release_manager` |
| `scopeType` | enum/string | `global` or `productArea` depending on existing auth model |
| `scopeId` | string/null | Product-area identifier when scoped |
| `grantedByUserId` | string | Who granted the role |
| `grantedAt` | timestamp | Assignment creation time |
| `revokedAt` | timestamp/null | Null while active |

Validation rules:
- `role` must be one of the three spec-defined roles.
- Only active assignments (`revokedAt is null`) participate in authorization.
- If `scopeType=productArea`, `scopeId` is required.

### 2. ReleaseWindow

Purpose: The calendar entity that moves through the approval workflow.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | UUID/string | Stable release-window id |
| `productAreaId` | string | Used for grouped pending approvals |
| `title` | string | Human-readable release name |
| `description` | string/null | Optional details |
| `startAt` | timestamp | Planned start |
| `endAt` | timestamp | Planned end |
| `state` | enum | `draft`, `proposed`, `approved`, `blocked`, `cancelled` |
| `currentRevision` | integer | Monotonic version for optimistic concurrency |
| `proposedByUserId` | string/null | Last proposer |
| `approvedByUserId` | string/null | Last approving manager |
| `blockedByUserId` | string/null | Last blocking actor |
| `cancelledByUserId` | string/null | Last cancelling actor |
| `lastTransitionAt` | timestamp | Latest state change timestamp |
| `lastTransitionReason` | string | Reason from most recent transition |
| `lastTransitionActorId` | string | Most recent actor |
| `lastTransitionActorRole` | string | Most recent actor role snapshot |

Validation rules:
- `endAt > startAt`.
- `state=approved` requires `approvedByUserId`.
- `state` transitions must follow the allowed state machine below.
- Every persisted state change must have a corresponding `ReleaseWindowTransition` record.

### 3. ReleaseWindowTransition

Purpose: Immutable audit log for every state transition or rejection decision.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | UUID/string | Transition id |
| `releaseWindowId` | foreign key | Parent release window |
| `fromState` | enum | Prior state |
| `toState` | enum | New state |
| `decisionType` | enum | `propose`, `approve`, `reject`, `block`, `cancel`, `reopen` |
| `reason` | string | Required by spec |
| `actorUserId` | string | Transition actor |
| `actorRoleSnapshot` | string | Role at transition time |
| `actorMetadata` | object/json | IP/device/session or equivalent actor context |
| `occurredAt` | timestamp | Transition timestamp |

Validation rules:
- `reason` is mandatory for every record.
- `actorMetadata` must contain the organization's required actor-audit fields.
- `decisionType=reject` is represented by `fromState=proposed` and `toState=draft`.

### 4. PendingApprovalGroup

Purpose: Read model for the required pending-approvals endpoint grouped by product area.

| Field | Type | Notes |
| --- | --- | --- |
| `productAreaId` | string | Group key |
| `productAreaName` | string | UI label |
| `pendingCount` | integer | Number of `proposed` windows |
| `windows` | array<ReleaseWindow summary> | Pending items within the group |
| `oldestProposedAt` | timestamp/null | Helps sort urgent reviews |

Validation rules:
- Only `state=proposed` windows appear in this projection.
- Groups must be filtered by the caller's authorization scope.

### 5. NotificationDispatch

Purpose: Tracks notification requests for approvals and rejections.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | UUID/string | Dispatch id |
| `releaseWindowId` | foreign key | Related release window |
| `transitionId` | foreign key | Triggering transition |
| `notificationType` | enum | `approval_requested`, `approved`, `rejected` |
| `recipientGroup` | string | Product-area audience or configured recipient segment |
| `status` | enum | `queued`, `sent`, `failed` |
| `queuedAt` | timestamp | Dispatch enqueue time |
| `sentAt` | timestamp/null | Delivery completion |
| `failureReason` | string/null | Operational detail |

Validation rules:
- Approval requests fire when a window enters `proposed`.
- Approved/rejected notifications fire only after the transition commits.

## Relationships

- `CalendarRoleAssignment` governs what transitions a user may invoke for a `ReleaseWindow`.
- `ReleaseWindow 1 ── many ReleaseWindowTransition`.
- `ReleaseWindowTransition 1 ── zero/many NotificationDispatch`.
- `PendingApprovalGroup` is a read model derived from `ReleaseWindow` rows where `state=proposed`.

## State Transitions

### Allowed workflow

```text
draft -> proposed
proposed -> approved
proposed -> draft      # reject returns the item to draft with a mandatory reason
proposed -> blocked
proposed -> cancelled
approved -> blocked
approved -> cancelled
blocked -> draft
blocked -> cancelled
```

### Role permissions

```text
viewer:
  - list and view release windows only

editor:
  - create/update draft content
  - transition draft -> proposed
  - view transition history

release_manager:
  - all viewer/editor capabilities
  - transition proposed -> approved|draft|blocked|cancelled
  - transition approved -> blocked|cancelled
  - transition blocked -> draft|cancelled
  - consume grouped pending approvals
```

## Invariants

- Every state transition requires both `reason` and actor metadata.
- A rejected release window does not create a new `rejected` state; it returns to `draft` with `decisionType=reject`.
- Pending approvals always reflect only `proposed` windows.
- Notifications are side effects of committed transitions, not prerequisites for state persistence.
- Existing clients remain compatible for one quarter because new workflow data is additive and old read contracts stay valid.
