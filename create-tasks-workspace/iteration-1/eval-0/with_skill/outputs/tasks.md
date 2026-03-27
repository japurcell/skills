# Tasks: Release Calendar Role Controls

**Input**: Design documents from `.agents/scratchpad/release-calendar-role-controls/`
**Prerequisites**: plan.md, spec.md, data-model.md

**Tests**: Tests are required and use TDD (write failing tests before implementation).

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize monorepo feature scaffolding for backend and frontend workstreams.

- [ ] T001 Create backend release-calendar module folders in backend/src/modules/release-calendar/
- [ ] T002 [P] Create frontend release-calendar feature folders in frontend/src/features/release-calendar/
- [ ] T003 [P] Add Jest and Playwright test file scaffolds for this feature in backend/tests/release-calendar/ and frontend/tests/release-calendar/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core role-control and shared calendar infrastructure that blocks all user stories.

**CRITICAL**: No user story work starts until this phase completes.

- [ ] T004 Create PostgreSQL migration for shared release calendar base tables in backend/src/db/migrations/20260326_release_calendar_base.sql
- [ ] T005 [P] Define shared release calendar domain types (roles, confidence, status, audit event) in backend/src/modules/release-calendar/domain/types.ts
- [ ] T006 [P] Implement role permission evaluator middleware for release calendar actions in backend/src/modules/release-calendar/auth/permissionEvaluator.ts
- [ ] T007 Implement release calendar authorization guard for API handlers in backend/src/modules/release-calendar/auth/requirePermission.ts (depends on T006)
- [ ] T008 [P] Add typed frontend API client and request helpers for release calendar endpoints in frontend/src/features/release-calendar/api/client.ts

**Checkpoint**: Foundation complete; user stories can proceed.

---

## Phase 3: User Story 1 - Create and maintain launch entries (Priority: P1) 🎯 MVP

**Goal**: PMs can create and edit launch entries with confidence levels and dependency links, and entries appear in shared calendar views.

**Independent Test**: As a PM, create and edit an entry (including confidence and dependencies), then verify updated values appear in the shared calendar and persist after page refresh.

### Tests for User Story 1 (REQUIRED)

- [ ] T009 [P] [US1] Add contract tests for create/update/list release entry endpoints in backend/tests/release-calendar/contract/releaseEntries.contract.test.ts
- [ ] T010 [P] [US1] Add integration tests for PM create/edit flows with dependency and confidence updates in backend/tests/release-calendar/integration/releaseEntries.integration.test.ts
- [ ] T011 [P] [US1] Add Playwright e2e test for PM launch-entry create/edit journey in frontend/tests/release-calendar/e2e/pm-entry-management.spec.ts

### Implementation for User Story 1

- [ ] T012 [P] [US1] Implement release entry repository (CRUD + optimistic concurrency version checks) in backend/src/modules/release-calendar/repositories/releaseEntryRepository.ts
- [ ] T013 [P] [US1] Implement dependency link repository with unresolved-dependency flagging in backend/src/modules/release-calendar/repositories/dependencyLinkRepository.ts
- [ ] T014 [P] [US1] Implement entry history repository for confidence/dependency change events in backend/src/modules/release-calendar/repositories/entryHistoryRepository.ts
- [ ] T015 [US1] Implement release entry service for create/update/list with audit trail writes in backend/src/modules/release-calendar/services/releaseEntryService.ts (depends on T012, T013, T014)
- [ ] T016 [US1] Implement API routes for POST/PATCH/GET release entries in backend/src/modules/release-calendar/routes/releaseEntries.routes.ts (depends on T015)
- [ ] T017 [P] [US1] Build PM launch entry form with confidence selector and dependency editor in frontend/src/features/release-calendar/components/LaunchEntryForm.tsx
- [ ] T018 [P] [US1] Build shared calendar entry card showing confidence and dependency state in frontend/src/features/release-calendar/components/LaunchEntryCard.tsx
- [ ] T019 [US1] Wire create/edit UI flows to API client and conflict-confirmation handling in frontend/src/features/release-calendar/pages/SharedCalendarPage.tsx (depends on T017, T018, T016)

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Weekly team-filtered planning view (Priority: P2)

**Goal**: Engineering managers can use a weekly calendar view with team filters that persist while navigating weeks.

**Independent Test**: Open weekly view, apply a team filter, navigate weeks, and confirm filter persists and only matching entries appear.

### Tests for User Story 2 (REQUIRED)

- [ ] T020 [P] [US2] Add contract tests for weekly release query endpoint with team filter params in backend/tests/release-calendar/contract/weeklyView.contract.test.ts
- [ ] T021 [P] [US2] Add integration tests for weekly filtering and empty-state behavior in backend/tests/release-calendar/integration/weeklyView.integration.test.ts
- [ ] T022 [P] [US2] Add Playwright e2e test for manager weekly filtering and week navigation persistence in frontend/tests/release-calendar/e2e/weekly-filter-persistence.spec.ts

### Implementation for User Story 2

- [ ] T023 [US2] Implement weekly-view query service with team filtering and week-range pagination in backend/src/modules/release-calendar/services/weeklyViewService.ts
- [ ] T024 [US2] Implement GET weekly view API route with team filter and week cursor parameters in backend/src/modules/release-calendar/routes/weeklyView.routes.ts (depends on T023)
- [ ] T025 [P] [US2] Build weekly calendar grid component in frontend/src/features/release-calendar/components/WeeklyCalendarGrid.tsx
- [ ] T026 [P] [US2] Build team filter control with selected-team chips in frontend/src/features/release-calendar/components/TeamFilterBar.tsx
- [ ] T027 [US2] Persist weekly filter and week navigation state in URL query params in frontend/src/features/release-calendar/hooks/useWeeklyViewState.ts (depends on T025, T026)
- [ ] T028 [US2] Integrate weekly page with filtered API data and empty-state messaging in frontend/src/features/release-calendar/pages/WeeklyPlanningPage.tsx (depends on T024, T027)

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Cross-role collaboration without uncontrolled edits (Priority: P3)

**Goal**: Non-PM users can comment on launch entries while edit operations remain restricted to PM-equivalent roles.

**Independent Test**: Verify non-PM users can post comments but receive authorization errors when attempting entry edits; PMs remain able to edit.

### Tests for User Story 3 (REQUIRED)

- [ ] T029 [P] [US3] Add contract tests for comment-create endpoint and role-based edit rejection responses in backend/tests/release-calendar/contract/comments-and-permissions.contract.test.ts
- [ ] T030 [P] [US3] Add integration tests for non-PM comment success and edit denial audit logging in backend/tests/release-calendar/integration/comments-and-permissions.integration.test.ts
- [ ] T031 [P] [US3] Add Playwright e2e test for stakeholder comment flow and blocked edit controls in frontend/tests/release-calendar/e2e/non-pm-collaboration.spec.ts

### Implementation for User Story 3

- [ ] T032 [P] [US3] Add PostgreSQL migration for release entry comments table in backend/src/db/migrations/20260326_release_calendar_comments.sql
- [ ] T033 [P] [US3] Implement comment repository and validation rules in backend/src/modules/release-calendar/repositories/commentRepository.ts
- [ ] T034 [US3] Implement comment service and API route for posting/listing comments in backend/src/modules/release-calendar/routes/comments.routes.ts (depends on T033)
- [ ] T035 [US3] Enforce PM-only edit permissions for release-entry mutation routes with explicit 403 messages in backend/src/modules/release-calendar/routes/releaseEntries.routes.ts
- [ ] T036 [P] [US3] Build comment panel component for release entry detail drawer in frontend/src/features/release-calendar/components/CommentPanel.tsx
- [ ] T037 [US3] Disable/hide edit controls for non-PM users and show authorization feedback in frontend/src/features/release-calendar/components/LaunchEntryActions.tsx
- [ ] T038 [US3] Integrate comment panel and role-aware actions in entry detail view in frontend/src/features/release-calendar/pages/EntryDetailDrawer.tsx (depends on T036, T037, T034)

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Hardening and readiness improvements across all stories.

- [ ] T039 [P] Add observability metrics for release calendar API latency and authorization denials in backend/src/modules/release-calendar/observability/metrics.ts
- [ ] T040 [P] Add notification dispatch for approval/rejection state changes in backend/src/modules/release-calendar/services/notificationService.ts
- [ ] T041 Update feature documentation and role matrix in docs/release-calendar-role-controls.md
- [ ] T042 Run full Jest and Playwright suites and capture results in docs/release-calendar-role-controls-test-report.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) has no dependencies.
- Foundational (Phase 2) depends on Setup completion and blocks all story work.
- User Story phases (Phases 3-5) depend on Foundational completion.
- Polish (Phase 6) depends on all implemented user stories.

### User Story Dependencies

- US1 (P1) starts immediately after Phase 2 and defines the MVP.
- US2 (P2) depends on shared entry data from US1 APIs but remains independently testable once implemented.
- US3 (P3) depends on role/permission foundations from Phase 2 and release-entry routes from US1.

### Within Each User Story

- Tests first and failing before implementation.
- Data/repositories before services.
- Services before API routes.
- Backend APIs before frontend integration.

---

## Parallel Opportunities

- Phase 1: T002 and T003 can run in parallel after T001.
- Phase 2: T005, T006, and T008 can run in parallel after T004.
- US1: T009/T010/T011 parallel; T012/T013/T014 parallel; T017/T018 parallel.
- US2: T020/T021/T022 parallel; T025/T026 parallel.
- US3: T029/T030/T031 parallel; T032/T033 and T036 parallel.
- Polish: T039 and T040 parallel.

---

## Parallel Example: User Story 2

```bash
# Run US2 tests in parallel
Task: "T020 [US2] weekly-view contract tests"
Task: "T021 [US2] weekly filtering integration tests"
Task: "T022 [US2] weekly filter Playwright e2e"

# Build independent UI pieces in parallel
Task: "T025 [US2] WeeklyCalendarGrid component"
Task: "T026 [US2] TeamFilterBar component"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup).
2. Complete Phase 2 (Foundational).
3. Complete Phase 3 (US1).
4. Validate US1 independently with T009-T011 before progressing.

### Incremental Delivery

1. Ship MVP after US1 validation.
2. Add US2 weekly planning view and validate independently.
3. Add US3 collaboration + role enforcement and validate independently.
4. Finish with Phase 6 hardening and full regression.

### Suggested MVP Scope

- Include through T019 (end of US1) for first production increment.
