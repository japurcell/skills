# Data Model: Release Calendar Role Controls

## Entities

### User Roles

**Role**

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PRIMARY KEY | |
| `name` | VARCHAR | UNIQUE, NOT NULL; enum: 'viewer', 'editor', 'release_manager' | Role identifier |
| `description` | TEXT | | Human-readable description |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | |

**Unique constraint**: One role per name.

---

### User-Role Assignment

**UserRole**

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PRIMARY KEY | |
| `user_id` | UUID | FOREIGN KEY (User), NOT NULL | Link to user table |
| `role_id` | UUID | FOREIGN KEY (Role), NOT NULL | Link to role table |
| `product_area` | VARCHAR | NOT NULL | Scope: e.g., 'payments', 'auth', 'platform' |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | |
| `expires_at` | TIMESTAMP | NULL | Optional: for temporary assignments |

**Constraints**:
- Composite unique: (user_id, role_id, product_area) — one user cannot have duplicate role in same area.
- Foreign key on user_id and role_id.

**Validation**:
- `product_area` must match valid product areas in the system.
- `expires_at` (if set) must be in the future.

---

### Release Window (Extended)

**ReleaseWindow** — extends existing calendar entry

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PRIMARY KEY | |
| `name` | VARCHAR | NOT NULL | e.g., 'Payments v2.1 Release' |
| `product_area` | VARCHAR | NOT NULL | Scope: 'payments', 'auth', etc. |
| `state` | VARCHAR | NOT NULL; enum: 'draft', 'proposed', 'approved', 'blocked', 'cancelled' | Current state |
| `scheduled_at` | TIMESTAMP | NOT NULL | Planned release date |
| `created_by_id` | UUID | FOREIGN KEY (User), NOT NULL | Original creator |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | |

---

### Release Window State Transition

**StateTransition** — audit trail for every state change

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PRIMARY KEY | |
| `release_window_id` | UUID | FOREIGN KEY (ReleaseWindow), NOT NULL | Which release |
| `previous_state` | VARCHAR | NOT NULL; enum: 'draft', 'proposed', 'approved', 'blocked', 'cancelled' | State before transition |
| `new_state` | VARCHAR | NOT NULL; enum: 'draft', 'proposed', 'approved', 'blocked', 'cancelled' | State after transition |
| `actor_id` | UUID | FOREIGN KEY (User), NOT NULL | User who triggered transition |
| `reason` | TEXT | NOT NULL | Why the transition occurred (e.g., 'Ready for approval', 'Blocked due to deployment freeze') |
| `metadata` | JSONB | | Additional context: e.g., `{"approval_count": 3, "veto_reason": null}` |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Immutable timestamp |

**Validation**:
- Transition must respect state machine rules (see State Machine section below).
- `reason` cannot be empty.
- `actor_id` must have sufficient role/permission to trigger the transition.

**Indexes**:
- `(release_window_id, created_at)` for efficient audit queries.
- `(actor_id, created_at)` for user activity tracking.

---

## State Machine: Release Window Lifecycle
