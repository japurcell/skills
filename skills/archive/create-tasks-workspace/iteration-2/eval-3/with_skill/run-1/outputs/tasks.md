# Tasks: Access Review Reminders

**Input**: Design documents from .agents/scratchpad/access-review-reminders/
**Prerequisites**: plan.md, spec.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize backend/frontend modules and test runners for a FastAPI + React web app.

- [ ] T001 Create backend FastAPI app entrypoint and router registration in backend/src/main.py
- [ ] T002 [P] Create backend dependency manifest with FastAPI, SQLAlchemy, psycopg, and pytest in backend/pyproject.toml
- [ ] T003 [P] Create frontend package manifest with React, Redux Toolkit, Vitest, and React Testing Library in frontend/package.json
- [ ] T004 Configure pytest discovery and markers for backend tests in backend/pytest.ini
- [ ] T005 [P] Configure Vitest with jsdom and setup file in frontend/vitest.config.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared schema, auth context, and API/client plumbing required by all user stories.

**CRITICAL**: Complete this phase before starting user story implementation.

- [ ] T006 Create SQLAlchemy base, engine, and session factory in backend/src/db/session.py
- [ ] T007 Create core review domain models Team, AccessReview, and ReviewItem in backend/src/models/review.py
- [ ] T008 Add initial database migration for review tables and indexes in backend/src/db/migrations/versions/001_access_review_tables.py
- [ ] T009 [P] Implement request user context and role guard dependency for manager/admin access in backend/src/api/dependencies/auth.py
- [ ] T010 [P] Create shared API client and typed error mapper for frontend requests in frontend/src/api/client.ts
- [ ] T011 Register access review API router in backend/src/api/router.py

**Checkpoint**: Foundation is ready; user stories can now be implemented and tested independently.

---

## Phase 3: User Story 1 - View Pending Reviews (Priority: P1) 🎯 MVP

**Goal**: Managers can open a list of users pending quarterly access review.

**Independent Test**: A manager request returns only pending users for that manager's teams with due dates, and the UI renders the filtered list.

### Tests for User Story 1 (REQUIRED)

- [ ] T012 [P] [US1] Add backend integration test for manager pending review list filtering in backend/tests/integration/test_manager_pending_reviews.py
- [ ] T013 [P] [US1] Add frontend Vitest component test for pending review table rendering in frontend/src/features/reviews/__tests__/PendingReviewsPage.test.tsx

### Implementation for User Story 1

- [ ] T014 [P] [US1] Add pending review query method with manager scoping in backend/src/repositories/review_repository.py
- [ ] T015 [US1] Implement manager pending reviews service orchestration in backend/src/services/pending_reviews_service.py
- [ ] T016 [US1] Add GET /manager/reviews/pending endpoint and response schema in backend/src/api/routes/manager_reviews.py
- [ ] T017 [P] [US1] Create reviews Redux slice for pending list fetch lifecycle in frontend/src/features/reviews/reviewsSlice.ts
- [ ] T018 [US1] Build PendingReviewsPage with due date columns and loading/error states in frontend/src/features/reviews/PendingReviewsPage.tsx
- [ ] T019 [US1] Add manager route entry for pending reviews page in frontend/src/app/router.tsx

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Complete Reviews (Priority: P2)

**Goal**: Managers can mark users reviewed and submit completion for their team.

**Independent Test**: Reviewed states and team completion timestamp persist after submission, and a page reload shows the submitted status.

### Tests for User Story 2 (REQUIRED)

- [ ] T020 [P] [US2] Add backend integration test for review item completion and team submission persistence in backend/tests/integration/test_review_completion_submission.py
- [ ] T021 [P] [US2] Add frontend Vitest interaction test for mark-reviewed and submit flow in frontend/src/features/reviews/__tests__/ReviewCompletionFlow.test.tsx

### Implementation for User Story 2

- [ ] T022 [P] [US2] Add reviewed_at and reviewed_by fields to review items with migration in backend/src/db/migrations/versions/002_review_item_completion_fields.py
- [ ] T023 [US2] Implement completion command service for review item updates and team submission timestamp in backend/src/services/review_completion_service.py
- [ ] T024 [US2] Add PATCH /manager/reviews/{review_item_id} and POST /manager/reviews/{team_id}/submit endpoints in backend/src/api/routes/manager_reviews.py
- [ ] T025 [P] [US2] Add frontend API methods for marking reviewed items and submitting a team review in frontend/src/features/reviews/reviewsApi.ts
- [ ] T026 [US2] Extend PendingReviewsPage with row checkboxes and submit action UX in frontend/src/features/reviews/PendingReviewsPage.tsx

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Overdue Visibility (Priority: P3)

**Goal**: Security admins can view overdue teams and escalation status with aging buckets.

**Independent Test**: Admin endpoint and UI show overdue teams grouped into defined aging buckets with escalation status.

### Tests for User Story 3 (REQUIRED)

- [ ] T027 [P] [US3] Add backend integration test for overdue team aggregation and aging buckets in backend/tests/integration/test_admin_overdue_dashboard.py
- [ ] T028 [P] [US3] Add frontend Vitest component test for overdue dashboard bucket sections in frontend/src/features/admin/__tests__/OverdueTeamsPage.test.tsx

### Implementation for User Story 3

- [ ] T029 [P] [US3] Implement overdue aggregation query with aging bucket calculation in backend/src/repositories/overdue_repository.py
- [ ] T030 [US3] Implement admin overdue visibility service and DTO mapping in backend/src/services/overdue_visibility_service.py
- [ ] T031 [US3] Add GET /admin/reviews/overdue endpoint and schemas in backend/src/api/routes/admin_reviews.py
- [ ] T032 [P] [US3] Add frontend API module for overdue dashboard data in frontend/src/features/admin/adminReviewsApi.ts
- [ ] T033 [US3] Build OverdueTeamsPage with aging bucket groups and escalation indicators in frontend/src/features/admin/OverdueTeamsPage.tsx
- [ ] T034 [US3] Add admin overdue dashboard route entry in frontend/src/app/router.tsx

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish quality and operational readiness across stories.

- [ ] T035 [P] Add end-to-end happy-path smoke test covering manager and admin journeys in frontend/src/features/reviews/__tests__/accessReviewSmoke.test.tsx
- [ ] T036 Add backend structured logging for review list, submit, and overdue endpoints in backend/src/api/middleware/request_logging.py
- [ ] T037 [P] Document local run, test commands, and role-based demo walkthrough in docs/access-review-reminders.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) starts immediately.
- Foundational (Phase 2) depends on Setup completion and blocks all user stories.
- User Story phases (Phases 3-5) depend on Foundational completion.
- Polish (Phase 6) depends on completion of all targeted user stories.

### User Story Dependencies

- US1 (P1) has no dependency on other user stories after Foundational tasks complete.
- US2 (P2) depends on shared review models from Foundational phase and can reuse US1 UI surface while remaining independently testable.
- US3 (P3) depends on shared review models from Foundational phase and remains independently testable through admin-specific endpoint and page.

### Within Each User Story

- Write and run tests first; confirm failures before implementation.
- Implement repository/data access before service orchestration.
- Implement service logic before API endpoint wiring.
- Implement API integration before final UI behavior wiring.

### Parallel Opportunities

- T002, T003, and T005 can run in parallel during Setup.
- T009 and T010 can run in parallel during Foundational work.
- In each user story, test tasks marked [P] can run together.
- Backend and frontend implementation tasks marked [P] can run concurrently when they touch different files.

---

## Parallel Example: User Story 1

- Run T012 and T013 together to establish failing backend and frontend tests.
- Run T014 and T017 in parallel while one developer builds backend query logic and another prepares frontend state handling.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1).
3. Validate US1 independently through tests and manual manager workflow.

### Incremental Delivery

1. Ship US1 after MVP validation.
2. Add US2 completion workflow and validate independently.
3. Add US3 overdue dashboard and validate independently.
4. Finish with Polish tasks for documentation, observability, and smoke coverage.
