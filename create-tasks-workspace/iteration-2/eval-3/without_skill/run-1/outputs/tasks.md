# Tasks: Access Review Reminders

**Input**: Design documents from `.agents/scratchpad/access-review-reminders/`
**Prerequisites**: plan.md, spec.md

**Tests**: Tests are required for each user story and are written before implementation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize backend and frontend scaffolding for the access review reminders feature.

- [ ] T001 Create backend package layout for access reviews in backend/src/access_reviews/__init__.py
- [ ] T002 [P] Create frontend feature module layout in frontend/src/features/access-reviews/index.ts
- [ ] T003 [P] Add backend test package init for access reviews in backend/tests/access_reviews/__init__.py
- [ ] T004 [P] Add frontend test setup for access review pages in frontend/src/features/access-reviews/access-reviews.test-setup.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared data model, API wiring, and state plumbing required by all stories.

- [ ] T005 Create SQLAlchemy review status enum and base model in backend/src/access_reviews/models/review_status.py
- [ ] T006 [P] Create quarterly review and review item models in backend/src/access_reviews/models/review_models.py
- [ ] T007 Create Alembic migration for review tables in backend/src/migrations/versions/20260326_01_create_access_review_tables.py
- [ ] T008 Create FastAPI router registration for access reviews in backend/src/access_reviews/api/router.py
- [ ] T009 [P] Create Redux slice skeleton for access reviews in frontend/src/features/access-reviews/state/accessReviewsSlice.ts

**Checkpoint**: Foundational work complete. User stories can now be implemented and tested independently.

---

## Phase 3: User Story 1 - View pending reviews (Priority: P1) 🎯 MVP

**Goal**: Managers can see only pending users for their team with due dates.

**Independent Test**: A manager request returns only pending review items for that manager team, and UI lists each user with a due date.

### Tests for User Story 1 (REQUIRED)

- [ ] T010 [P] [US1] Add backend API integration test for pending review list in backend/tests/access_reviews/test_pending_reviews_api.py
- [ ] T011 [P] [US1] Add frontend view test for pending review list rendering in frontend/src/features/access-reviews/__tests__/PendingReviewList.test.tsx

### Implementation for User Story 1

- [ ] T012 [US1] Implement pending review query service scoped to manager team in backend/src/access_reviews/services/pending_review_service.py
- [ ] T013 [US1] Implement GET pending reviews endpoint in backend/src/access_reviews/api/pending_reviews.py
- [ ] T014 [P] [US1] Implement pending reviews API client in frontend/src/features/access-reviews/api/getPendingReviews.ts
- [ ] T015 [US1] Implement pending reviews page and list component in frontend/src/features/access-reviews/pages/PendingReviewsPage.tsx

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Complete reviews (Priority: P2)

**Goal**: Managers can mark review items complete and submit team completion.

**Independent Test**: Review item completion and team completion timestamp persist and can be retrieved after submission.

### Tests for User Story 2 (REQUIRED)

- [ ] T016 [P] [US2] Add backend API integration test for review item completion in backend/tests/access_reviews/test_complete_review_item_api.py
- [ ] T017 [P] [US2] Add backend API integration test for team submission in backend/tests/access_reviews/test_submit_team_review_api.py
- [ ] T018 [P] [US2] Add frontend workflow test for complete-and-submit journey in frontend/src/features/access-reviews/__tests__/CompleteReviewFlow.test.tsx

### Implementation for User Story 2

- [ ] T019 [US2] Implement service methods for marking review items complete and submitting team completion in backend/src/access_reviews/services/review_completion_service.py
- [ ] T020 [US2] Implement POST endpoints for review item completion and team submission in backend/src/access_reviews/api/review_completion.py
- [ ] T021 [US2] Implement frontend completion actions and submit flow in frontend/src/features/access-reviews/state/reviewCompletionThunks.ts

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Overdue visibility (Priority: P3)

**Goal**: Security admins can see overdue teams with escalation status and aging buckets.

**Independent Test**: Admin view returns overdue teams grouped by aging buckets with escalation status visible in the UI.

### Tests for User Story 3 (REQUIRED)

- [ ] T022 [P] [US3] Add backend API integration test for overdue team summary in backend/tests/access_reviews/test_overdue_teams_api.py
- [ ] T023 [P] [US3] Add backend service test for aging bucket calculation in backend/tests/access_reviews/test_aging_bucket_service.py
- [ ] T024 [P] [US3] Add frontend admin view test for overdue teams table in frontend/src/features/access-reviews/__tests__/OverdueTeamsPage.test.tsx

### Implementation for User Story 3

- [ ] T025 [US3] Implement overdue team aggregation and aging bucket service in backend/src/access_reviews/services/overdue_visibility_service.py
- [ ] T026 [US3] Implement GET overdue teams endpoint for security admins in backend/src/access_reviews/api/overdue_teams.py
- [ ] T027 [US3] Implement overdue teams admin page with escalation status display in frontend/src/features/access-reviews/pages/OverdueTeamsPage.tsx

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improve reliability, observability, and documentation across all stories.

- [ ] T028 [P] Add backend request and domain event logging for access review operations in backend/src/access_reviews/observability/review_logging.py
- [ ] T029 Add frontend error and empty-state UX for access review pages in frontend/src/features/access-reviews/components/AccessReviewStatePanels.tsx
- [ ] T030 [P] Add end-to-end smoke test for manager and admin journeys in backend/tests/access_reviews/test_access_review_smoke.py
- [ ] T031 [P] Document API routes and feature behavior in docs/access-review-reminders.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) can start immediately.
- Foundational (Phase 2) depends on Setup and blocks all user story phases.
- User Story phases (Phase 3 to Phase 5) depend on Foundational completion.
- Polish (Phase 6) depends on completion of targeted user stories.

### User Story Dependencies

- US1 depends only on Foundational and is the MVP.
- US2 depends on Foundational and reuses review entities from US1 but remains independently testable via its own completion endpoints and tests.
- US3 depends on Foundational and reads shared review data without requiring US2 UI flow to execute.

### Within Each User Story

- Write tests first and confirm failure before implementation.
- Implement backend services before API handlers.
- Implement frontend API client or thunks before page integration.
- Validate story-specific independent test criteria before moving on.

### Parallel Opportunities

- Setup tasks T002 to T004 can run in parallel after T001.
- Foundational tasks T006 and T009 can run in parallel after T005.
- In each story, test tasks marked [P] can be written in parallel.
- Backend and frontend implementation tasks marked [P] can proceed in parallel when they touch different files.

---

## Parallel Example: User Story 1

```bash
Task: T010 backend/tests/access_reviews/test_pending_reviews_api.py
Task: T011 frontend/src/features/access-reviews/__tests__/PendingReviewList.test.tsx
Task: T014 frontend/src/features/access-reviews/api/getPendingReviews.ts
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete US1 tests and implementation (T010 to T015).
3. Validate independent test criteria for US1.
4. Demo manager pending review visibility.

### Incremental Delivery

1. Deliver US1 pending visibility.
2. Deliver US2 completion workflow.
3. Deliver US3 overdue admin visibility.
4. Complete polish tasks for reliability and documentation.
