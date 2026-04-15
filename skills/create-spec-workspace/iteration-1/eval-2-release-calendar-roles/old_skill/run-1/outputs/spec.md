# Feature Specification: Shared Release Calendar Roles

**Created**: 2026-03-26  
**Status**: Draft  
**Input**: User description: "Build a shared release calendar where PMs can create launch entries, mark confidence level, and attach dependencies. Engineering managers need a weekly view filtered by team. We are not sure whether non-PM roles should edit entries or comment only."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Create and Maintain Launch Entries (Priority: P1)

As a product manager, I can create and update launch entries with confidence level and dependencies so release plans are visible and coordinated.

**Why this priority**: Without accurate launch entries, the calendar has no core value for planning and coordination.

**Independent Test**: Can be fully tested by having a PM create a new launch entry, set confidence, attach dependencies, and confirm details are saved and displayed in the calendar.

**Acceptance Scenarios**:

1. **Given** a PM with access to the calendar, **When** they create a launch entry with title, target date, team, confidence level, and at least one dependency, **Then** the system stores the entry and shows it on the release calendar.
2. **Given** an existing launch entry, **When** a PM updates its confidence level or dependency list, **Then** the updated values are visible in all calendar views.

---

### User Story 2 - Weekly Team-Filtered Planning View (Priority: P2)

As an engineering manager, I can view a weekly calendar filtered by team so I can quickly assess upcoming launches and coordination needs.

**Why this priority**: Engineering managers need a focused operational view to plan staffing and risk mitigation each week.

**Independent Test**: Can be fully tested by selecting a weekly date range, applying a team filter, and verifying only matching launch entries are shown.

**Acceptance Scenarios**:

1. **Given** multiple launch entries across teams and dates, **When** an engineering manager selects week W and team T, **Then** only team T launch entries in week W are displayed.
2. **Given** no launches for the selected team and week, **When** filters are applied, **Then** an empty-state message is shown indicating no matching entries.

---

### User Story 3 - Cross-Role Collaboration Through Comments (Priority: P3)

As a non-PM stakeholder, I can comment on launch entries to provide context or risks without modifying source-of-truth planning fields.

**Why this priority**: Collaboration is needed across roles, but planning data ownership should remain clear and controlled.

**Independent Test**: Can be fully tested by having a non-PM add comments to an entry and verifying comments are visible while edit controls are not available.

**Acceptance Scenarios**:

1. **Given** a non-PM user with calendar access, **When** they open a launch entry, **Then** they can add comments but cannot edit core entry fields.
2. **Given** an entry with existing comments, **When** stakeholders view the entry, **Then** comments are shown in chronological order with author and timestamp.

---

### Edge Cases

- What happens when a launch entry depends on another entry that is moved outside the current week? The dependency remains attached and is still visible in entry details.
- How does system handle duplicate launch titles on the same date for the same team? The system allows them if entries are otherwise distinct and tracks each by unique entry identity.
- What happens when confidence level is not explicitly set? The system requires confidence level before a launch entry can be saved.
- How does system handle dependencies that are removed or no longer valid? The system flags the dependency as unresolved and preserves historical context in entry activity.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST allow PM users to create launch entries with at least: launch title, target date, owning team, confidence level, and dependency references.
- **FR-002**: System MUST allow PM users to update launch entry details, including confidence level and dependencies, after creation.
- **FR-003**: System MUST provide a weekly calendar view that can be filtered by team.
- **FR-004**: System MUST display only entries that match both selected week and selected team when filters are applied.
- **FR-005**: System MUST allow non-PM roles to add comments on launch entries.
- **FR-006**: System MUST prevent non-PM roles from editing core launch entry fields (title, date, team, confidence level, dependencies).
- **FR-007**: System MUST record author and timestamp metadata for all comments.
- **FR-008**: System MUST show launch dependencies within each entry so users can identify sequencing and coordination risks.
- **FR-009**: System MUST require confidence level selection before a launch entry can be saved.
- **FR-010**: System MUST preserve a visible history of entry updates and comments for auditability by authorized users.

### Key Entities _(include if feature involves data)_

- **Launch Entry**: Represents a planned release event with attributes including title, target date, owning team, confidence level, status, and related dependencies.
- **Dependency Link**: Represents a relationship where one launch entry depends on another and includes dependency state (active, unresolved, or removed).
- **Comment**: Represents stakeholder discussion on a launch entry with message body, author, and timestamp.
- **Role Permission**: Represents role-based capabilities indicating which roles can create, edit, and comment on launch entries.
- **Team**: Represents an organizational unit used for ownership and weekly filter scoping.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 95% of PM users can create a complete launch entry (including confidence level and at least one dependency when applicable) in under 2 minutes during usability testing.
- **SC-002**: 100% of weekly team-filtered views return only entries matching the selected team and week in acceptance tests.
- **SC-003**: 90% of engineering managers report the weekly team-filtered calendar is sufficient for weekly planning decisions in post-rollout feedback.
- **SC-004**: 100% of non-PM edit attempts on core entry fields are blocked while comment submission remains available in role-permission tests.
- **SC-005**: At least 85% of launches with cross-team impact include dependency links within the first 8 weeks after rollout.

## Assumptions

- PMs are the owners of core release entry data and are responsible for final field accuracy.
- Non-PM roles need collaboration capability, so comment-only access is the default for initial scope.
- Weekly view and team filtering are available to engineering managers and other authorized roles with read access.
- The organization already has a defined team directory that can be used for launch ownership and filtering.
- Historical change visibility is required for coordination and accountability but not for compliance-grade legal audit in this phase.
