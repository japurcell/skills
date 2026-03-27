# Tasks: Recurring Invoice Batch Send

**Input**: Design documents from `.agents/scratchpad/billing-disputes-workflow/`
**Prerequisites**: plan.md, spec.md, data-model.md

**Tests**: Tests are required. Each user story starts with failing tests before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: User story label (`[US1]`, `[US2]`, `[US3]`)
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize project structure and baseline tooling for backend and frontend.

- [ ] T001 Create backend and frontend module skeletons in backend/src/**init**.py and frontend/src/main.tsx
- [ ] T002 Initialize backend dependencies and scripts in backend/pyproject.toml
- [ ] T003 Initialize frontend dependencies and scripts in frontend/package.json
- [ ] T004 [P] Configure backend test runner and coverage in backend/pytest.ini
- [ ] T005 [P] Configure frontend test runner in frontend/vitest.config.ts
- [ ] T006 [P] Add local development environment variables in .env.example

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure required before any user story implementation.

**CRITICAL**: User story development starts only after this phase is complete.

- [ ] T007 Add PostgreSQL connection/session management in backend/src/db/session.py
- [ ] T008 Create SQLAlchemy declarative base and metadata in backend/src/db/base.py
- [ ] T009 Create base FastAPI app, API router, and middleware wiring in backend/src/main.py
- [ ] T010 [P] Implement shared API error schema and handlers in backend/src/api/errors.py
- [ ] T011 [P] Implement finance-admin authorization dependency in backend/src/api/dependencies/auth.py
- [ ] T012 Create immutable audit event model and repository in backend/src/audit/models.py and backend/src/audit/repository.py
- [ ] T013 [P] Add Redux store bootstrap with API client configuration in frontend/src/app/store.ts and frontend/src/app/apiClient.ts
- [ ] T014 [P] Create shared invoice batch domain types in frontend/src/features/invoice-batches/types.ts

**Checkpoint**: Foundation complete. User stories can proceed in priority order and remain independently testable.

---

## Phase 3: User Story 1 - Generate Monthly Draft Invoices (Priority: P1) 🎯 MVP

**Goal**: Finance admins can generate monthly draft invoices from eligible subscriptions.

**Independent Test**: Trigger generation for a billing period and verify exactly one draft invoice per eligible subscription, while canceled/out-of-period subscriptions are excluded.

### Tests for User Story 1 (REQUIRED)

- [ ] T015 [P] [US1] Add API contract test for POST /invoice-batches/generate in backend/tests/contract/test_generate_invoice_batch.py
- [ ] T016 [P] [US1] Add integration test for eligibility filtering and uniqueness in backend/tests/integration/test_monthly_draft_generation.py
- [ ] T017 [P] [US1] Add frontend component test for generation form submit flow in frontend/src/features/invoice-batches/**tests**/GenerateBatchForm.test.tsx

### Implementation for User Story 1

- [ ] T018 [P] [US1] Create invoice batch and draft invoice ORM models in backend/src/invoice_batches/models.py
- [ ] T019 [P] [US1] Create subscription and tax profile read models for generation inputs in backend/src/subscriptions/models.py
- [ ] T020 [US1] Implement monthly draft generation service with one-per-subscription guard in backend/src/invoice_batches/services/generate_batch.py (depends on T018, T019)
- [ ] T021 [US1] Implement POST /invoice-batches/generate endpoint in backend/src/invoice_batches/api.py (depends on T015, T020)
- [ ] T022 [US1] Persist generation audit events for created/skipped records in backend/src/invoice_batches/services/generation_audit.py
- [ ] T023 [US1] Build finance admin generation page and API integration in frontend/src/features/invoice-batches/pages/GenerateBatchPage.tsx

**Checkpoint**: User Story 1 is fully testable and delivers MVP draft generation.

---

## Phase 4: User Story 2 - Review Draft Invoice Set (Priority: P2)

**Goal**: Finance admins can review a generated batch with readiness status and blocking reasons.

**Independent Test**: Open a generated batch and verify each draft invoice shows ready/blocked state plus actionable missing-tax-data guidance.

### Tests for User Story 2 (REQUIRED)

- [ ] T024 [P] [US2] Add API contract test for GET /invoice-batches/{batch_id} in backend/tests/contract/test_get_invoice_batch_details.py
- [ ] T025 [P] [US2] Add integration test for readiness and blocking reason computation in backend/tests/integration/test_batch_review_readiness.py
- [ ] T026 [P] [US2] Add frontend component test for readiness badges and guidance text in frontend/src/features/invoice-batches/**tests**/BatchReviewPage.test.tsx

### Implementation for User Story 2

- [ ] T027 [P] [US2] Implement tax rule resolver for US/EU region handling in backend/src/tax/services/tax_rule_resolver.py
- [ ] T028 [P] [US2] Implement missing-tax-data validator and guidance builder in backend/src/invoice_batches/services/readiness.py
- [ ] T029 [US2] Implement batch detail aggregation service with per-invoice readiness status in backend/src/invoice_batches/services/get_batch_details.py (depends on T027, T028)
- [ ] T030 [US2] Implement GET /invoice-batches/{batch_id} endpoint in backend/src/invoice_batches/api.py (depends on T024, T029)
- [ ] T031 [US2] Build batch review UI with readiness table and guidance panel in frontend/src/features/invoice-batches/pages/BatchReviewPage.tsx

**Checkpoint**: User Story 2 is independently testable and does not require batch-send implementation.

---

## Phase 5: User Story 3 - Send Ready Invoices in Batch (Priority: P3)

**Goal**: Finance admins can send all ready invoices in one action while blocked invoices remain draft.

**Independent Test**: Execute send on a mixed batch and verify only ready invoices are sent, blocked invoices remain draft, and summary output contains sent/blocked counts with reasons.

### Tests for User Story 3 (REQUIRED)

- [ ] T032 [P] [US3] Add API contract test for POST /invoice-batches/{batch_id}/send in backend/tests/contract/test_send_invoice_batch.py
- [ ] T033 [P] [US3] Add integration test for mixed-ready send behavior and state transitions in backend/tests/integration/test_send_ready_invoices_only.py
- [ ] T034 [P] [US3] Add frontend component test for batch send confirmation and result summary in frontend/src/features/invoice-batches/**tests**/SendBatchFlow.test.tsx

### Implementation for User Story 3

- [ ] T035 [P] [US3] Implement invoice sender gateway abstraction in backend/src/invoice_batches/services/invoice_sender.py
- [ ] T036 [US3] Implement batch send orchestration service that skips blocked invoices in backend/src/invoice_batches/services/send_batch.py (depends on T028, T035)
- [ ] T037 [US3] Implement POST /invoice-batches/{batch_id}/send endpoint with summary payload in backend/src/invoice_batches/api.py (depends on T032, T036)
- [ ] T038 [US3] Persist send outcomes and immutable audit entries in backend/src/invoice_batches/services/send_audit.py
- [ ] T039 [US3] Build frontend send action and result summary UI in frontend/src/features/invoice-batches/components/SendBatchPanel.tsx

**Checkpoint**: User Story 3 is independently testable and confirms compliant batch sending behavior.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final quality improvements across all stories.

- [ ] T040 [P] Add backend performance test for 5k-subscription monthly generation and batch query p95 targets in backend/tests/performance/test_invoice_batch_performance.py
- [ ] T041 [P] Add structured observability dashboards and metrics emission hooks in backend/src/observability/metrics.py and backend/src/observability/logging.py
- [ ] T042 Update finance admin usage and troubleshooting guide in docs/recurring-invoice-batch-send.md
- [ ] T043 Execute end-to-end quick validation scenarios and record outcomes in docs/validation/recurring-invoice-batch-send-checklist.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2; establishes MVP.
- **Phase 4 (US2)**: Depends on Phase 2 and uses US1 batch artifacts for review scenarios.
- **Phase 5 (US3)**: Depends on Phase 2 and readiness logic from US2.
- **Phase 6 (Polish)**: Depends on completion of selected user stories.

### User Story Dependencies

- **US1 (P1)**: Starts immediately after foundational phase.
- **US2 (P2)**: Starts after foundational phase; functionally independent of send flow.
- **US3 (P3)**: Starts after foundational phase but depends on shared readiness validator from US2 to enforce blocked behavior.

### Within Each User Story

- Tests first and failing before implementation.
- Models and core domain services before API endpoints.
- Backend API integration before frontend completion.
- Story checkpoint validation before progressing.

---

## Parallel Execution Examples

### User Story 1

- Run T015, T016, and T017 in parallel.
- Run T018 and T019 in parallel, then continue with T020.

### User Story 2

- Run T024, T025, and T026 in parallel.
- Run T027 and T028 in parallel, then continue with T029.

### User Story 3

- Run T032, T033, and T034 in parallel.
- Run T035 while T034 is in progress, then continue with T036 and T037.

---

## Implementation Strategy

### MVP First (US1 only)

1. Complete Setup (Phase 1).
2. Complete Foundational (Phase 2).
3. Deliver User Story 1 (Phase 3).
4. Validate US1 independently before moving on.

### Incremental Delivery

1. Deliver US1 for draft generation value.
2. Add US2 for review and readiness transparency.
3. Add US3 for operational batch sending efficiency.
4. Apply cross-cutting polish and performance validation.

### Independent Testability Safeguards

- Each story has dedicated contract, integration, and frontend tests.
- Each story includes explicit checkpoint criteria tied to acceptance behavior.
- Shared infrastructure is isolated to Phases 1-2 to avoid hidden cross-story coupling.
