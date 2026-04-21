# Data Model: Release Calendar Role Controls

## Entity: ReleaseCalendarRoleAssignment

**Purpose**: Resolves what actions a user may take in the release calendar, optionally scoped by product area.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `user_id` | string | yes | Stable identity reference |
| `role` | enum | yes | `viewer`, `editor`, `release_manager` |
| `scope_type` | enum | yes | `global` or `product_area` |
| `scope_id` | string | no | Nullable when scope is global |
| `granted_at` | timestamp | yes | Audit timestamp |
| `granted_by` | string | yes | Granting actor |
| `revoked_at` | timestamp | no | Null when active |

### Invariants

- Only one active assignment may exist per `(user_id, scope_type, scope_id)`.
- `viewer` is read-only.
- `editor` can create drafts and propose/cancel within allowed ownership rules.
- `release_manager` can approve, reject/block, and perform all editor transitions.

## Entity: ReleaseWindow

**Purpose**: Canonical release-calendar record shown to all roles.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | uuid | yes | Primary key |
| `product_area` | string | yes | Grouping key for approvals dashboard |
| `title` | string | yes | 1..200 characters |
| `description` | string | no | Free-form context |
| `start_at` | timestamp | yes | Inclusive start |
| `end_at` | timestamp | yes | Must be greater than `start_at` |
| `state` | enum | yes | `draft`, `proposed`, `approved`, `blocked`, `cancelled` |
| `created_by` | string | yes | Creator actor ID |
| `updated_by` | string | yes | Last mutating actor ID |
| `created_at` | timestamp | yes | Creation time |
| `updated_at` | timestamp | yes | Last mutation time |
| `version` | integer | yes | Optimistic concurrency token |

### Relationships

- One-to-many with `ReleaseWindowTransition`.
- One-to-many with `NotificationDispatchRecord`.

### Invariants

- `end_at > start_at`.
- Existing calendar read fields remain backward compatible for one quarter.
- Only the transition service mutates `state`.
- `version` increments on every successful mutation.

## Entity: ReleaseWindowTransition

**Purpose**: Immutable audit history for every release-window state transition.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | uuid | yes | Primary key |
| `release_window_id` | uuid | yes | FK to `ReleaseWindow.id` |
| `from_state` | enum | yes | Prior state |
| `to_state` | enum | yes | New state |
| `reason` | string | yes | Required by spec; 3..1000 chars |
| `actor_id` | string | yes | Who performed the transition |
| `actor_role` | enum | yes | Role at time of transition |
| `actor_display_name` | string | no | Optional denormalized presentation field |
| `created_at` | timestamp | yes | Audit timestamp |
| `metadata` | json | no | Extra compatibility/details payload |

### Invariants

- Every state change writes exactly one transition row.
- Transition history is append-only.
- `reason`, `actor_id`, and `actor_role` are never null.
- Illegal transitions never create rows.

## Entity: NotificationDispatchRecord

**Purpose**: Durable work item for approval/rejection notifications.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | uuid | yes | Primary key |
| `release_window_id` | uuid | yes | FK to `ReleaseWindow.id` |
| `event_type` | enum | yes | `release_window.approved`, `release_window.blocked`, `release_window.cancelled` when notification is required |
| `payload` | json | yes | Notification request body or adapter payload |
| `status` | enum | yes | `pending`, `processing`, `sent`, `failed` |
| `retry_count` | integer | yes | Starts at 0 |
| `available_at` | timestamp | yes | Retry scheduling boundary |
| `created_at` | timestamp | yes | Creation time |
| `sent_at` | timestamp | no | Populated on success |
| `last_error` | string | no | Latest dispatch failure |

### Invariants

- Dispatch records are created in the same transaction as the triggering transition.
- Approval/rejection notifications are retriable without mutating the original transition.
- Re-dispatch must be idempotent for the same record ID.

## Read Model: PendingApprovalGroup

**Purpose**: API response bucket for release-manager approvals dashboard.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `productArea` | string | yes | Grouping key |
| `pendingCount` | integer | yes | Number of proposed windows in the group |
| `items` | array | yes | Array of `PendingApprovalItem` |

## Read Model: PendingApprovalItem

**Purpose**: Lightweight approval queue entry.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | uuid | yes | Release window ID |
| `title` | string | yes | Calendar label |
| `productArea` | string | yes | Group key repeated for item-level rendering |
| `startAt` | timestamp | yes | Window start |
| `endAt` | timestamp | yes | Window end |
| `requestedBy` | string | yes | Latest proposing actor |
| `requestedAt` | timestamp | yes | Latest proposal time |
| `latestReason` | string | yes | Proposal reason |
| `version` | integer | yes | Concurrency token for action submission |

### Query rules

- Includes only windows where `state = proposed`.
- Groups are ordered by `productArea` ascending.
- Items inside a group are ordered by `updated_at DESC`.

## State transitions

| From | To | Allowed roles | Notes |
| --- | --- | --- | --- |
| _new_ | `draft` | `editor`, `release_manager` | Create a new release window |
| `draft` | `proposed` | `editor`, `release_manager` | Submit for approval |
| `draft` | `cancelled` | owning `editor`, `release_manager` | Withdraw before approval |
| `proposed` | `approved` | `release_manager` | Approval path |
| `proposed` | `blocked` | `release_manager` | Explicit rejection/block path |
| `proposed` | `cancelled` | owning `editor`, `release_manager` | Withdraw proposal |
| `blocked` | `proposed` | `editor`, `release_manager` | Resubmit after changes |
| `blocked` | `cancelled` | `release_manager` | End the window |
| `approved` | `blocked` | `release_manager` | Emergency post-approval block |

### Global validation rules

- Every transition request must include `reason`.
- `viewer` can never invoke a transition.
- Transition requests include actor metadata from authenticated context, not from client-supplied trust alone.
- Optimistic concurrency rejects stale writes when `expectedVersion` does not match `ReleaseWindow.version`.

## Indexing and performance notes

- Index `release_windows(state, product_area, updated_at DESC)` for pending approvals.
- Index `release_window_transitions(release_window_id, created_at DESC)` for timeline/history access.
- Index `notification_dispatch_records(status, available_at)` for dispatcher scans.
- Preserve lightweight summary fields on list endpoints so calendar reads remain responsive under concurrent planning load.
