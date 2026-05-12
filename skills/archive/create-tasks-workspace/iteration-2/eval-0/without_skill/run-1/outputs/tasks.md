# Tasks: Release Calendar Role Controls

**Input**: Design documents from `.agents/scratchpad/release-calendar-role-controls/`
**Prerequisites**: plan.md, spec.md, data-model.md

**Tests**: Tests are required and use a TDD workflow (write failing tests before implementation).

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature folders, shared typing, and test scaffolding for backend and frontend.

- [ ] T001 Create backend release-calendar module folders in backend/src/modules/release-calendar/index.ts
- [ ] T002 [P] Create frontend release-calendar feature folders in frontend/src/features/release-calendar/index.ts
- [ ] T003 [P] Add shared release status and confidence enums in backend/src/modules/release-calendar/domain/release-window.types.ts
- [ ] T004 [P] Add Playwright spec stub for release calendar flows in frontend/tests/e2e/release-calendar/release-calendar-role-controls.spec.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build RBAC, persistence, and API foundations required by all user stories.

**CRITICAL**: Complete this phase before starting any user story work.

- [ ] T005 Create release window table migration with workflow states in backend/src/db/migrations/20260326_create_release_windows.ts
- [ ] T006 [P] Create release comments table migration in backend/src/db/migrations/20260326_create_release_comments.ts
- [ ] T007 [P] Create release change-history table migration in backend/src/db/migrations/20260326_create_release_change_history.ts
- [ ] T008 [P] Create dependency links table migration in backend/src/db/migrations/20260326_create_release_dependencies.ts
- [ ] T009 Implement role and permission policy map (viewer, editor, release_manager) in backend/src/modules/release-calendar/auth/release-calendar-permissions.ts
- [ ] T010 [P] Implement release calendar authorization middleware in backend/src/modules/release-calendar/auth/release-calendar-authorize.ts
- [ ] T011 [P] Implement release window repository with transaction support in backend/src/modules/release-calendar/data/release-window.repository.ts
- [ ] T012 Implement shared API route registration and error mapping in backend/src/modules/release-calendar/api/release-calendar.routes.ts
- [ ] T013 [P] Implement frontend release calendar API client methods in frontend/src/features/release-calendar/api/releaseCalendarApi.ts

**Checkpoint**: Foundational layer complete; user stories can be implemented and tested independently.

---

## Phase 3: User Story 1 - Create and maintain launch entries (Priority: P1) MVP

**Goal**: PM users can create and update launch entries with confidence and dependencies.

**Independent Test**: A PM can create an entry with title/date/team/confidence/dependencies and later edit confidence or dependencies with persisted results.

### Tests for User Story 1 (REQUIRED)

- [ ] T014 [P] [US1] Add backend integration test for PM create and update release window in backend/tests/integration/release-calendar/release-window-crud.integration.test.ts
- [ ] T015 [P] [US1] Add backend authorization test for PM-only field edits in backend/tests/integration/release-calendar/release-window-edit-permissions.integration.test.ts
- [ ] T016 [P] [US1] Add Playwright flow for PM create and edit entry in frontend/tests/e2e/release-calendar/release-window-create-edit.spec.ts

### Implementation for User Story 1

- [ ] T017 [P] [US1] Implement create release window service with validation in backend/src/modules/release-calendar/application/create-release-window.service.ts
- [ ] T018 [P] [US1] Implement update release window service with conflict detection in backend/src/modules/release-calendar/application/update-release-window.service.ts
- [ ] T019 [US1] Implement release window create/update API handlers in backend/src/modules/release-calendar/api/release-window-write.controller.ts
- [ ] T020 [P] [US1] Implement PM launch entry form and editor UI in frontend/src/features/release-calendar/components/ReleaseWindowForm.tsx
- [ ] T021 [US1] Implement dependency picker with unresolved dependency indicator in frontend/src/features/release-calendar/components/DependencySelector.tsx
- [ ] T022 [US1] Implement calendar entry create/edit interactions in frontend/src/features/release-calendar/pages/SharedCalendarPage.tsx

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Weekly team-filtered planning view (Priority: P2)

**Goal**: Engineering managers can view a weekly calendar and filter by team with filter persistence while navigating weeks.

**Independent Test**: An engineering manager can apply a team filter, see matching entries for one week, and keep the filter active while moving weeks.

### Tests for User Story 2 (REQUIRED)

- [ ] T023 [P] [US2] Add backend integration test for weekly query with team filter in backend/tests/integration/release-calendar/weekly-view-filter.integration.test.ts
- [ ] T024 [P] [US2] Add frontend unit test for persisted team filter state in frontend/src/features/release-calendar/state/__tests__/weeklyFilterState.test.ts
- [ ] T025 [P] [US2] Add Playwright flow for weekly navigation with sticky filter in frontend/tests/e2e/release-calendar/weekly-filter-persistence.spec.ts

### Implementation for User Story 2

- [ ] T026 [P] [US2] Implement weekly release query service with team filter support in backend/src/modules/release-calendar/application/list-weekly-release-windows.service.ts
- [ ] T027 [US2] Implement weekly view API endpoint in backend/src/modules/release-calendar/api/release-window-read.controller.ts
- [ ] T028 [P] [US2] Implement weekly calendar grid component in frontend/src/features/release-calendar/components/WeeklyCalendarGrid.tsx
- [ ] T029 [US2] Implement team filter state store with week-to-week persistence in frontend/src/features/release-calendar/state/weeklyFilterStore.ts
- [ ] T030 [US2] Wire weekly view page loading and filter interactions in frontend/src/features/release-calendar/pages/WeeklyCalendarPage.tsx

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Cross-role collaboration without uncontrolled edits (Priority: P3)

**Goal**: Non-PM users can comment but cannot edit launch fields, and blocked edits show clear authorization feedback.

**Independent Test**: A non-PM user can add comments successfully, receives clear denial on edit attempts, and PM users retain edit capability.

### Tests for User Story 3 (REQUIRED)

- [ ] T031 [P] [US3] Add backend integration test for non-PM comment allowed and edit denied in backend/tests/integration/release-calendar/comment-vs-edit-permissions.integration.test.ts
- [ ] T032 [P] [US3] Add frontend unit test for authorization feedback banner in frontend/src/features/release-calendar/components/__tests__/PermissionFeedback.test.tsx
- [ ] T033 [P] [US3] Add Playwright flow for non-PM comment and blocked edit attempt in frontend/tests/e2e/release-calendar/non-pm-collaboration.spec.ts

### Implementation for User Story 3

- [ ] T034 [P] [US3] Implement add comment service with author and timestamp capture in backend/src/modules/release-calendar/application/add-release-comment.service.ts
- [ ] T035 [US3] Implement comment API endpoint and edit-denial response payload in backend/src/modules/release-calendar/api/release-comment.controller.ts
- [ ] T036 [P] [US3] Implement release comment thread component in frontend/src/features/release-calendar/components/ReleaseCommentThread.tsx
- [ ] T037 [US3] Implement permission feedback banner for blocked edits in frontend/src/features/release-calendar/components/PermissionFeedback.tsx
- [ ] T038 [US3] Integrate comment-only mode for non-PM roles in frontend/src/features/release-calendar/pages/ReleaseWindowDetailsPage.tsx

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Complete cross-story workflow, observability, and readiness checks.

- [ ] T039 [P] Implement approval notification integration for approved and blocked transitions in backend/src/modules/release-calendar/integrations/notification/approval-notifier.ts
- [ ] T040 [P] Implement change-history recording for confidence and dependency updates in backend/src/modules/release-calendar/application/record-release-history.service.ts
- [ ] T041 [P] Add backend unit tests for release workflow state transitions in backend/tests/unit/release-calendar/release-workflow-state-machine.test.ts
- [ ] T042 [P] Add frontend accessibility and regression checks for release calendar controls in frontend/src/features/release-calendar/components/__tests__/release-calendar-a11y.test.tsx
- [ ] T043 Update feature documentation and operator notes in docs/features/release-calendar-role-controls.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) has no dependencies and starts immediately.
- Foundational (Phase 2) depends on Setup and blocks all user stories.
- User Story phases (Phases 3-5) all depend on Foundational completion.
- Polish (Phase 6) depends on completion of the selected user stories.

### User Story Dependencies

- US1 (P1) starts first after Foundational and is the MVP slice.
- US2 (P2) depends on foundational read/query infrastructure and can run after US1 starts.
- US3 (P3) depends on foundational permissions and can run in parallel with US2 once Foundational is done.

### Within-Story Execution Rules

- Write tests first and confirm they fail before implementation tasks.
- Implement backend services before controllers that expose them.
- Implement frontend state and API wiring before final page composition.
- Verify each story independently before moving to the next story checkpoint.

### Parallel Opportunities

- Phase 1 tasks marked [P] can run concurrently.
- In Phase 2, migrations T006-T008 can run in parallel, and T010-T011-T013 can run in parallel after T009 where applicable.
- In each user story, test tasks marked [P] can run in parallel.
- Backend and frontend implementation tasks marked [P] can be split across team members.

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 (Setup).
2. Complete Phase 2 (Foundational).
3. Complete Phase 3 (US1).
4. Validate US1 end to end before broader rollout.

### Incremental Delivery

1. Deliver US1 for PM entry management.
2. Deliver US2 for engineering manager weekly planning.
3. Deliver US3 for cross-role collaboration constraints.
4. Finish with Phase 6 polish tasks.

### Parallel Team Plan

1. Team completes Setup and Foundational together.
2. After Foundational, one developer drives US1 backend, one drives US1 frontend, and another can start US2 tests.
3. After US1 stabilizes, split ownership across US2 and US3 tracks, then converge on Polish tasks.
