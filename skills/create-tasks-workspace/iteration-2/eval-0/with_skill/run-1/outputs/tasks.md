# Tasks: Release Calendar Role Controls

**Input**: Design documents from `.agents/scratchpad/release-calendar-role-controls/`
**Prerequisites**: plan.md, spec.md, data-model.md

**Tests**: Tests are required. Follow TDD: write tests first, confirm they fail, then implement.

**Organization**: Tasks are grouped by user story to support independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish release-calendar feature scaffolding in the existing monorepo.

- [ ] T001 Create feature module folders backend/src/features/release-calendar/ and frontend/src/features/release-calendar/
- [ ] T002 [P] Add feature configuration keys for release calendar roles in backend/src/config/releaseCalendarConfig.ts
- [ ] T003 [P] Add frontend route shell for release calendar in frontend/src/app/release-calendar/page.tsx
- [ ] T004 [P] Create shared TypeScript domain types for release windows and comments in backend/src/features/release-calendar/types.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core data, authorization, workflow, and audit foundations required by all user stories.

**CRITICAL**: Complete this phase before starting user story work.

- [ ] T005 Create PostgreSQL migration for release_windows, release_window_dependencies, release_window_history, and release_window_comments in backend/src/db/migrations/20260326_release_calendar_role_controls.sql
- [ ] T006 [P] Implement release calendar repository for CRUD, filtering, and dependency lookup in backend/src/features/release-calendar/releaseWindowRepository.ts
- [ ] T007 [P] Implement role permission policy (viewer, editor, release_manager) in backend/src/features/release-calendar/rolePermissionPolicy.ts
- [ ] T008 [P] Implement release window state machine (draft, proposed, approved, blocked, cancelled) in backend/src/features/release-calendar/releaseWindowStateMachine.ts
- [ ] T009 [P] Implement audit trail writer for confidence and dependency changes in backend/src/features/release-calendar/releaseWindowAuditService.ts
- [ ] T010 [P] Implement notification integration adapter for approval and rejection events in backend/src/features/release-calendar/releaseWindowNotificationService.ts
- [ ] T011 Implement backend API router wiring and auth middleware for release calendar endpoints in backend/src/features/release-calendar/releaseCalendarRouter.ts
- [ ] T012 Implement shared API client for release calendar endpoints in frontend/src/features/release-calendar/api/releaseCalendarApiClient.ts

**Checkpoint**: Foundation ready for independent story delivery.

---

## Phase 3: User Story 1 - Create and maintain launch entries (Priority: P1) 🎯 MVP

**Goal**: PM users can create and update release windows with confidence and dependencies, with persisted history and shared visibility.

**Independent Test**: A PM can create and edit a release window with confidence and dependencies, and the updated values are visible in the calendar with history recorded.

### Tests for User Story 1 (REQUIRED)

- [ ] T013 [P] [US1] Add backend integration test for PM create and edit release window flows in backend/tests/integration/release-calendar/releaseWindowCrud.integration.test.ts
- [ ] T014 [P] [US1] Add backend integration test for unresolved dependency flag behavior in backend/tests/integration/release-calendar/releaseWindowDependencies.integration.test.ts
- [ ] T015 [P] [US1] Add frontend Playwright scenario for PM creating and editing entries in frontend/tests/e2e/release-calendar/pm-create-edit.spec.ts

### Implementation for User Story 1

- [ ] T016 [P] [US1] Implement backend service methods for create and update release windows in backend/src/features/release-calendar/releaseWindowService.ts
- [ ] T017 [US1] Implement POST and PATCH handlers for release windows in backend/src/features/release-calendar/releaseWindowController.ts
- [ ] T018 [P] [US1] Implement PM entry form with confidence and dependency inputs in frontend/src/features/release-calendar/components/ReleaseWindowForm.tsx
- [ ] T019 [US1] Implement shared calendar event rendering with confidence badges in frontend/src/features/release-calendar/components/SharedCalendarView.tsx
- [ ] T020 [US1] Implement entry create and edit page orchestration in frontend/src/features/release-calendar/page.tsx
- [ ] T021 [US1] Implement entry history panel for confidence and dependency updates in frontend/src/features/release-calendar/components/ReleaseWindowHistoryPanel.tsx

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Weekly team-filtered planning view (Priority: P2)

**Goal**: Engineering managers can use a weekly view, filter by team, and keep filter state while navigating weeks.

**Independent Test**: An engineering manager can apply a team filter in weekly view, move between weeks, and retain the same filter selection.

### Tests for User Story 2 (REQUIRED)

- [ ] T022 [P] [US2] Add backend integration test for weekly query and team filtering in backend/tests/integration/release-calendar/weeklyFilter.integration.test.ts
- [ ] T023 [P] [US2] Add frontend Playwright scenario for week navigation preserving team filter in frontend/tests/e2e/release-calendar/weekly-filter-persistence.spec.ts

### Implementation for User Story 2

- [ ] T024 [P] [US2] Implement weekly view query in backend release window repository in backend/src/features/release-calendar/releaseWindowRepository.ts
- [ ] T025 [US2] Implement GET weekly release window endpoint with team filter parameters in backend/src/features/release-calendar/releaseWindowController.ts
- [ ] T026 [P] [US2] Implement weekly calendar grid component in frontend/src/features/release-calendar/components/WeeklyCalendarView.tsx
- [ ] T027 [P] [US2] Implement team filter control component in frontend/src/features/release-calendar/components/TeamFilter.tsx
- [ ] T028 [US2] Persist selected team filter and week navigation state in frontend/src/features/release-calendar/hooks/useWeeklyCalendarState.ts
- [ ] T029 [US2] Wire weekly view and filter state into release calendar page in frontend/src/features/release-calendar/page.tsx

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Cross-role collaboration without uncontrolled edits (Priority: P3)

**Goal**: Non-PM users can comment on release windows but cannot edit protected fields; blocked edits return clear authorization feedback.

**Independent Test**: A non-PM user can add comments successfully but receives an authorization error when trying to edit release window fields.

### Tests for User Story 3 (REQUIRED)

- [ ] T030 [P] [US3] Add backend integration test for non-PM comment allowed and edit denied behavior in backend/tests/integration/release-calendar/comment-permission.integration.test.ts
- [ ] T031 [P] [US3] Add frontend Playwright scenario for non-PM comment and blocked edit messaging in frontend/tests/e2e/release-calendar/non-pm-collaboration.spec.ts

### Implementation for User Story 3

- [ ] T032 [P] [US3] Implement comment creation endpoint in backend/src/features/release-calendar/releaseWindowCommentController.ts
- [ ] T033 [US3] Enforce PM-only edit authorization checks in backend/src/features/release-calendar/releaseWindowController.ts
- [ ] T034 [US3] Add explicit authorization response payloads for denied edits in backend/src/features/release-calendar/releaseCalendarErrorMapper.ts
- [ ] T035 [P] [US3] Implement comment panel UI for all authorized viewers in frontend/src/features/release-calendar/components/ReleaseWindowCommentsPanel.tsx
- [ ] T036 [US3] Disable or hide edit controls for non-PM roles in frontend/src/features/release-calendar/components/ReleaseWindowForm.tsx
- [ ] T037 [US3] Display permission feedback banner for denied edit attempts in frontend/src/features/release-calendar/components/PermissionFeedbackBanner.tsx

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Harden quality, performance, observability, and documentation across stories.

- [ ] T038 [P] Add backend unit tests for role policy and state machine edge cases in backend/tests/unit/release-calendar/rolePolicyAndStateMachine.unit.test.ts
- [ ] T039 [P] Add frontend unit tests for weekly state and permission UI behavior in frontend/tests/unit/release-calendar/weeklyStateAndPermissions.unit.test.tsx
- [ ] T040 Optimize backend weekly query path and indexes for concurrent planning load in backend/src/features/release-calendar/releaseWindowRepository.ts
- [ ] T041 Add structured logging and metrics for create, edit, approve, reject, and comment actions in backend/src/features/release-calendar/releaseCalendarObservability.ts
- [ ] T042 Update feature documentation and role behavior notes in docs/release-calendar-role-controls.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) starts immediately.
- Foundational (Phase 2) depends on Setup and blocks all user story phases.
- User stories (Phases 3-5) depend on Foundational completion.
- Polish (Phase 6) depends on completion of the targeted user stories.

### User Story Dependencies

- US1 (P1) starts first after Foundational and defines MVP behavior.
- US2 (P2) depends on foundational APIs and shared calendar structures from US1, but remains independently testable.
- US3 (P3) depends on foundational authorization and release window APIs, and integrates with US1 UI components while preserving independent tests.

### Within-Story Execution Rules

- Write tests first and verify they fail.
- Implement backend repository/service/controller flow before wiring frontend behavior.
- Add UI integration and authorization feedback after core API behavior is stable.

### Parallel Opportunities

- Setup: T002-T004 can run in parallel after T001.
- Foundational: T006-T010 can run in parallel after T005.
- US1: T013-T015 can run in parallel; T016 and T018 can run in parallel after tests are created.
- US2: T022 and T023 can run in parallel; T026 and T027 can run in parallel.
- US3: T030 and T031 can run in parallel; T032 and T035 can run in parallel.
- Polish: T038 and T039 can run in parallel.

---

## Implementation Strategy

### MVP First (US1)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate PM create/edit flows and dependency/confidence history end-to-end.
4. Demo or release MVP.

### Incremental Delivery

1. Deliver US1 for core PM release planning.
2. Deliver US2 for engineering manager weekly planning.
3. Deliver US3 for cross-role collaboration and permission safety.
4. Finish polish tasks for performance, quality, and documentation.
