# Feature Specification: Shared Release Calendar Roles

**Created**: 2026-03-26  
**Status**: Draft  
**Input**: User description: "Build a shared release calendar where PMs can create launch entries, mark confidence level, and attach dependencies. Engineering managers need a weekly view filtered by team. We are not sure whether non-PM roles should edit entries or comment only."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Create and maintain launch entries (Priority: P1)

Product managers create and update launch entries in a shared calendar, including confidence level and dependencies, so release planning remains current and visible.

**Why this priority**: Without reliable launch entry creation and maintenance, the calendar cannot provide core planning value.

**Independent Test**: Can be fully tested by having a PM create, edit, and save launch entries with confidence and dependencies, then verify data persists and is visible to authorized viewers.

**Acceptance Scenarios**:

1. **Given** a signed-in PM, **When** they create a launch entry with title, date, confidence level, owning team, and dependencies, **Then** the entry is saved and appears on the calendar.
2. **Given** an existing launch entry created by a PM, **When** the PM updates confidence level or dependencies, **Then** the calendar reflects the latest values immediately.

---

### User Story 2 - Weekly team-filtered planning view (Priority: P2)

Engineering managers view releases in a weekly calendar and filter entries by team to assess near-term delivery risks and sequencing.

**Why this priority**: Weekly planning visibility is required for engineering leadership coordination and staffing decisions.

**Independent Test**: Can be fully tested by opening weekly view, applying a team filter, and confirming only matching entries appear for the selected week.

**Acceptance Scenarios**:

1. **Given** an engineering manager on the weekly calendar view, **When** they select a team filter, **Then** only entries for that team are shown for the selected week.
2. **Given** an engineering manager with a team filter applied, **When** they navigate to the next or previous week, **Then** the same team filter remains active until changed.

---

### User Story 3 - Cross-role collaboration without uncontrolled edits (Priority: P3)

Non-PM roles collaborate on launch entries through comments, while edit access remains restricted to PMs to protect schedule integrity.

**Why this priority**: Collaboration is important, but ambiguous edit rights can create ownership conflicts and unreviewed schedule changes.

**Independent Test**: Can be fully tested by verifying non-PM users can add comments but cannot change launch entry fields, while PM users can still edit.

**Acceptance Scenarios**:

1. **Given** a non-PM user viewing a launch entry, **When** they submit a comment, **Then** the comment is attached to the entry with author and timestamp.
2. **Given** a non-PM user viewing a launch entry, **When** they attempt to edit entry fields, **Then** the system blocks the edit and communicates that edit permissions are PM-only.

---

### Edge Cases

- What happens when a PM marks a dependency that does not yet exist in the calendar? The system records the dependency reference and flags it as unresolved until the referenced launch entry exists.
- How does system handle two PMs editing the same launch entry at the same time? The system prevents silent overwrites by requiring explicit confirmation before saving conflicting changes.
- What happens when an engineering manager applies a team filter with no launches in the selected week? The weekly view shows an empty-state message and clear action to remove or change filters.
- How does system handle confidence level updates close to launch date? The latest confidence level is shown in the weekly view and included in entry history for auditability.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST allow PM users to create launch entries with, at minimum, title, planned launch date, owning team, confidence level, and dependency references.
- **FR-002**: System MUST allow PM users to edit and update launch entry fields, including confidence level and dependencies, after creation.
- **FR-003**: System MUST provide a shared calendar view of launch entries visible to PMs, engineering managers, and other authorized stakeholders.
- **FR-004**: System MUST provide a weekly calendar view that engineering managers can access.
- **FR-005**: System MUST allow users to filter weekly view results by team and show only entries matching selected team filters.
- **FR-006**: System MUST preserve active team filter selection while users move between weeks in the weekly view.
- **FR-007**: System MUST allow non-PM roles to add comments to launch entries.
- **FR-008**: System MUST prevent non-PM roles from editing launch entry fields unless they are explicitly assigned PM-equivalent edit permissions.
- **FR-009**: System MUST display each launch entry's current confidence level in both shared and weekly views.
- **FR-010**: System MUST record dependency links between launch entries and indicate unresolved or missing dependencies.
- **FR-011**: System MUST maintain an entry-level history of confidence and dependency changes, including who changed what and when.
- **FR-012**: System MUST present clear authorization feedback when a user attempts an action they are not permitted to perform.

### Key Entities _(include if feature involves data)_

- **Launch Entry**: A planned release item with attributes including title, launch date, owning team, confidence level, dependency references, status, and change history.
- **Comment**: A collaboration record attached to a launch entry, including author role, timestamp, and comment text.
- **Role Permission**: Access rules that determine whether a user can create/edit entries, view entries, filter views, or add comments.
- **Team**: Organizational unit used to assign launch ownership and drive filtering in weekly views.
- **Dependency Link**: Relationship between launch entries that indicates delivery order or prerequisite constraints.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 95% of PM users can create a complete launch entry (including confidence level and at least one dependency field state) in under 3 minutes during usability testing.
- **SC-002**: 100% of engineering manager weekly-view sessions can apply a team filter and display filtered results in under 10 seconds.
- **SC-003**: In role-permission validation tests, 100% of unauthorized edit attempts by non-PM users are blocked while 100% of comment attempts by those users succeed.
- **SC-004**: In the first 8 weeks after launch, at least 90% of active teams maintain at least one upcoming launch entry with confidence level updated within the prior 14 days.

## Assumptions

- Non-PM roles are comment-only by default; edit rights are restricted to PM roles unless an organization grants PM-equivalent permissions through existing access governance.
- Authorized users already exist in an organizational identity system and can be mapped to PM, engineering manager, and non-PM stakeholder roles.
- Weekly planning is based on a single agreed business week definition used consistently across teams.
- Dependency tracking is limited to relationships between launch entries within this shared calendar, not external tooling.
- Initial release scope covers web-based access; native mobile-specific workflows are out of scope for v1.
