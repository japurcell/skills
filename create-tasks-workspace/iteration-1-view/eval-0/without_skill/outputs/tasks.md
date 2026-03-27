# Tasks: Release Calendar Role Controls

**Input**: Design documents from `.agents/scratchpad/release-calendar-role-controls/`
**Prerequisites**: plan.md, spec.md, data-model.md

**Tests**: Tests are required and follow TDD (write failing tests before implementation).
**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish monorepo structure and feature-level scaffolding for backend and frontend work.

- [ ] T001 Create feature folders for release calendar role controls in backend/src/features/release-calendar/ and frontend/src/features/release-calendar/
- [ ] T002 Add feature configuration for role-controls and notification integration in backend/src/config/featureFlags.ts and backend/src/config/notifications.ts
- [ ] T003 [P] Add shared TypeScript domain types for release window roles, states, and confidence levels in shared/src/release-calendar/types.ts
- [ ] T004 [P] Scaffold Jest and Playwright test suites for this feature in backend/tests/release-calendar/ and frontend/tests/e2e/release-calendar/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core authorization, state workflow, and infrastructure required before any user story.

**CRITICAL**: No user story work starts until this phase is complete.

- [ ] T005 Create PostgreSQL migration for release windows, dependency links, comments, and history tables in backend/db/migrations/20260326_release_calendar_role_controls.sql
- [ ] T006 [P] Implement role-permission policy matrix (viewer, editor, release_manager plus PM mapping) in backend/src/features/release-calendar/auth/rolePolicy.ts
- [ ] T007 [P] Implement backend authorization middleware for feature actions in backend/src/features/release-calendar/auth/authorizeReleaseCalendarAction.ts
- [ ] T008 Implement release-window state transition rules (draft, proposed, approved, blocked, cancelled) in backend/src/features/release-calendar/domain/releaseStateMachine.ts
- [ ] T009 Implement audit history writer utility for confidence and dependency changes in backend/src/features/release-calendar/audit/releaseHistoryWriter.ts
- [ ] T010 [P] Implement notification client adapter for approval/rejection events in backend/src/integrations/notification/releaseCalendarNotifier.ts
- [ ] T011 Register release calendar API routes with shared error mapping for authorization failures in backend/src/api/releaseCalendarRoutes.ts

**Checkpoint**: Foundation ready; user story work can proceed.

---

## Phase 3: User Story 1 - Create and maintain launch entries (Priority: P1) 🎯 MVP

**Goal**: PM users can create and update launch entries with confidence and dependencies.

**Independent Test**: Sign in as PM, create an entry with title/date/team/confidence/dependencies, edit confidence and dependencies, and verify persisted updates on calendar views.

### Tests for User Story 1 (REQUIRED)

- [ ] T012 [P] [US1] Add contract tests for create and update launch-entry endpoints in backend/tests/release-calendar/contract/releaseEntries.write.contract.test.ts
- [ ] T013 [P] [US1] Add integration tests for dependency persistence, unresolved dependency flagging, and optimistic concurrency handling in backend/tests/release-calendar/integration/releaseEntries.write.integration.test.ts
- [ ] T014 [US1] Add Playwright E2E for PM create/edit entry workflow in frontend/tests/e2e/release-calendar/pm-create-edit-entry.spec.ts

### Implementation for User Story 1

- [ ] T015 [P] [US1] Implement release-window repository create/update and dependency link persistence in backend/src/features/release-calendar/repositories/releaseWindowRepository.ts
- [ ] T016 [P] [US1] Implement request validation schemas for launch-entry create/update payloads in backend/src/features/release-calendar/api/releaseEntrySchemas.ts
- [ ] T017 [US1] Implement application service for create/update logic, audit writes, and state-safe updates in backend/src/features/release-calendar/services/releaseEntryWriteService.ts (depends on T015, T016)
- [ ] T018 [US1] Implement POST/PATCH handlers for launch entries in backend/src/features/release-calendar/api/releaseEntryWriteController.ts
- [ ] T019 [P] [US1] Build PM launch-entry form with confidence and dependency inputs in frontend/src/features/release-calendar/components/ReleaseEntryForm.tsx
- [ ] T020 [P] [US1] Implement shared calendar entry rendering with confidence and dependency indicators in frontend/src/features/release-calendar/components/ReleaseCalendarGrid.tsx
- [ ] T021 [US1] Wire frontend create/update flows to backend APIs with conflict and validation handling in frontend/src/features/release-calendar/api/releaseEntryClient.ts

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Weekly team-filtered planning view (Priority: P2)

**Goal**: Engineering managers can view weekly releases and filter by team with filter persistence across week navigation.

**Independent Test**: Open weekly view, apply team filter, verify only matching entries appear, navigate weeks, and confirm filter remains active.

### Tests for User Story 2 (REQUIRED)

- [ ] T022 [P] [US2] Add contract tests for weekly release query endpoint with team filtering in backend/tests/release-calendar/contract/releaseEntries.weeklyRead.contract.test.ts
- [ ] T023 [P] [US2] Add integration tests for weekly window query boundaries and team filter persistence inputs in backend/tests/release-calendar/integration/releaseEntries.weeklyRead.integration.test.ts
- [ ] T024 [US2] Add Playwright E2E for engineering-manager weekly filter and week navigation in frontend/tests/e2e/release-calendar/weekly-team-filter.spec.ts

### Implementation for User Story 2

- [ ] T025 [P] [US2] Implement weekly release read model query with team filter support in backend/src/features/release-calendar/repositories/weeklyReleaseQueryRepository.ts
- [ ] T026 [US2] Implement weekly releases API endpoint and query parameter handling in backend/src/features/release-calendar/api/weeklyReleaseController.ts
- [ ] T027 [P] [US2] Build weekly calendar UI and team filter controls in frontend/src/features/release-calendar/components/WeeklyReleaseView.tsx
- [ ] T028 [US2] Persist selected team filter through week navigation using URL search params in frontend/src/features/release-calendar/hooks/useWeeklyFilterState.ts

**Checkpoint**: User Stories 1 and 2 are independently functional and testable.

---

## Phase 5: User Story 3 - Cross-role collaboration without uncontrolled edits (Priority: P3)

**Goal**: Non-PM roles can comment on entries but cannot edit launch-entry fields.

**Independent Test**: Sign in as non-PM, submit a comment successfully, attempt field edits, and verify edit is blocked with clear authorization feedback while PM edits still succeed.

### Tests for User Story 3 (REQUIRED)

- [ ] T029 [P] [US3] Add contract tests for comment create/list endpoints and unauthorized launch-entry edit response codes in backend/tests/release-calendar/contract/releaseCommentsAndPermissions.contract.test.ts
- [ ] T030 [P] [US3] Add integration tests for non-PM comment allow and field-edit deny behavior in backend/tests/release-calendar/integration/releasePermissions.integration.test.ts
- [ ] T031 [US3] Add Playwright E2E for stakeholder comment submission and blocked edit attempt messaging in frontend/tests/e2e/release-calendar/non-pm-comment-only.spec.ts

### Implementation for User Story 3

- [ ] T032 [P] [US3] Implement comment repository and service methods with author/timestamp persistence in backend/src/features/release-calendar/services/releaseCommentService.ts
- [ ] T033 [US3] Implement comments POST/GET API handlers with authorization checks in backend/src/features/release-calendar/api/releaseCommentController.ts
- [ ] T034 [P] [US3] Build entry comments panel and composer UI in frontend/src/features/release-calendar/components/ReleaseEntryComments.tsx
- [ ] T035 [US3] Enforce non-PM field edit blocking in backend policy enforcement and frontend form gating in backend/src/features/release-calendar/auth/rolePolicy.ts and frontend/src/features/release-calendar/components/ReleaseEntryForm.tsx
- [ ] T036 [US3] Add explicit authorization feedback messaging for blocked actions in frontend/src/features/release-calendar/components/PermissionNotice.tsx

**Checkpoint**: All user stories are independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improve reliability, performance, and delivery readiness across all stories.

- [ ] T037 [P] Add approval/rejection notification payload templates and event wiring tests in backend/tests/release-calendar/integration/releaseNotifications.integration.test.ts and backend/src/integrations/notification/releaseCalendarNotifier.ts
- [ ] T038 [P] Add database indexes and query performance assertions for weekly read paths in backend/db/migrations/20260326_release_calendar_role_controls_indexes.sql and backend/tests/release-calendar/performance/weeklyRead.performance.test.ts
- [ ] T039 Update feature documentation and role-permission matrix in docs/release-calendar-role-controls.md
- [ ] T040 Run full Jest and Playwright suites and document release readiness checklist in docs/release-calendar-role-controls-release-checklist.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) has no dependencies and starts immediately.
- Foundational (Phase 2) depends on Setup and blocks all user stories.
- User Stories (Phases 3-5) depend on Foundational completion.
- Polish (Phase 6) depends on completion of all user stories.

### User Story Dependencies

- US1 (P1) starts immediately after Foundational and is the MVP slice.
- US2 (P2) starts after Foundational and depends on US1 data shape consistency for calendar rendering.
- US3 (P3) starts after Foundational and depends on US1 entry workflows for comment targets.

### Within Each User Story

- Write tests first and confirm they fail.
- Implement repositories/models before services.
- Implement services before API controllers.
- Connect frontend after backend contracts stabilize.
- Complete story-level tests before moving to next priority.

### Parallel Opportunities

- Setup: T003 and T004 can run in parallel after T001.
- Foundational: T006, T007, and T010 can run in parallel after T005.
- US1: T012 and T013 in parallel; T015 and T016 in parallel; T019 and T020 in parallel.
- US2: T022 and T023 in parallel; T025 and T027 in parallel.
- US3: T029 and T030 in parallel; T032 and T034 in parallel.
- Polish: T037 and T038 in parallel.

---

## Parallel Example: User Story 1

```bash
Task: "T012 [US1] Contract tests for create/update endpoints"
Task: "T013 [US1] Integration tests for dependency persistence and conflicts"

Task: "T015 [US1] Repository create/update and dependency persistence"
Task: "T016 [US1] Request validation schemas"
```

## Parallel Example: User Story 2

```bash
Task: "T022 [US2] Contract tests for weekly filtered read endpoint"
Task: "T023 [US2] Integration tests for weekly boundary and filter persistence"

Task: "T025 [US2] Weekly query repository"
Task: "T027 [US2] Weekly view and team filter UI"
```

## Parallel Example: User Story 3

```bash
Task: "T029 [US3] Contract tests for comments and forbidden edits"
Task: "T030 [US3] Integration tests for comment-allow/edit-deny behavior"

Task: "T032 [US3] Comment repository/service"
Task: "T034 [US3] Comments panel UI"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup).
2. Complete Phase 2 (Foundational).
3. Complete Phase 3 (US1).
4. Validate US1 independently via T012-T014.
5. Demo PM create/update workflow.

### Incremental Delivery

1. Deliver US1 (MVP) after Setup + Foundational.
2. Deliver US2 weekly filtered planning view.
3. Deliver US3 collaboration controls.
4. Finish with Phase 6 polish and full regression.

### Parallel Team Strategy

1. Team completes Phases 1-2 together.
2. Then split by story: Developer A (US1), Developer B (US2), Developer C (US3).
3. Merge story increments behind feature flags and validate independently.

---

## Notes

- All task lines use the required checklist format.
- Task IDs are contiguous from T001 to T040 with no gaps.
- User-story tasks include `[US#]`; setup/foundational/polish tasks intentionally omit story labels.
- Every task includes explicit file paths and concrete technologies (Node.js, Next.js, PostgreSQL, Jest, Playwright).
