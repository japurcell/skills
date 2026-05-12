# Tasks: Recurring Invoice Batch Send

**Input**: Design documents from `.agents/scratchpad/billing-disputes-workflow/`
**Prerequisites**: plan.md, spec.md, data-model.md

**Tests**: Tests are required for each user story and follow a test-first flow.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize billing batch modules and baseline tooling for backend and frontend work.

- [ ] T001 Create recurring billing module directories in backend/src/billing/recurring/ and frontend/src/features/recurring-invoices/
- [ ] T002 Add recurring billing environment settings in backend/src/core/settings.py
- [ ] T003 [P] Add recurring billing feature flags in frontend/src/config/featureFlags.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared infrastructure that all user stories depend on.

**Critical**: Complete this phase before starting user story implementation.

- [ ] T004 Create SQLAlchemy invoice batch and batch item models in backend/src/models/invoice_batch.py
- [ ] T005 [P] Create SQLAlchemy draft invoice and tax profile models in backend/src/models/recurring_invoice.py
- [ ] T006 [P] Create SQLAlchemy regional tax rule model in backend/src/models/regional_tax_rule.py
- [ ] T007 Create Alembic migration for recurring invoice tables in backend/migrations/versions/20260326_add_recurring_invoice_workflow.py
- [ ] T008 Implement recurring billing repositories in backend/src/repositories/recurring_invoice_repository.py
- [ ] T009 Implement shared recurring billing API schemas in backend/src/api/schemas/recurring_invoice.py
- [ ] T010 Create recurring invoice Redux slice shell in frontend/src/features/recurring-invoices/store/recurringInvoiceSlice.ts

**Checkpoint**: Foundational data model, persistence, and shared contracts are ready.

---

## Phase 3: User Story 1 - Generate Monthly Draft Invoices (Priority: P1) 🎯 MVP

**Goal**: Finance admins can generate one monthly draft invoice per eligible subscription.

**Independent Test**: Run generation for a target billing period and verify eligible subscriptions produce one draft invoice while ineligible subscriptions produce none.

### Tests for User Story 1 (Required)

- [ ] T011 [P] [US1] Add service-level generation eligibility tests in backend/tests/unit/services/test_monthly_draft_generation_service.py
- [ ] T012 [P] [US1] Add API integration test for monthly draft generation endpoint in backend/tests/integration/api/test_generate_monthly_drafts.py
- [ ] T013 [P] [US1] Add frontend workflow test for generation action in frontend/src/features/recurring-invoices/__tests__/GenerateMonthlyDrafts.test.tsx

### Implementation for User Story 1

- [ ] T014 [US1] Implement subscription eligibility selector in backend/src/services/recurring/subscription_eligibility_service.py
- [ ] T015 [US1] Implement monthly draft generation service in backend/src/services/recurring/monthly_draft_generation_service.py (depends on T014)
- [ ] T016 [US1] Implement POST monthly draft generation endpoint in backend/src/api/routes/recurring_invoice_generation.py
- [ ] T017 [US1] Implement generation request form component in frontend/src/features/recurring-invoices/components/GenerateDraftsForm.tsx
- [ ] T018 [US1] Wire generation action and result state in frontend/src/features/recurring-invoices/store/recurringInvoiceThunks.ts

**Checkpoint**: User Story 1 is independently testable and shippable.

---

## Phase 4: User Story 2 - Review Draft Invoice Set (Priority: P2)

**Goal**: Finance admins can review generated draft invoices with readiness status and blocking reasons.

**Independent Test**: Open a generated batch and verify each draft shows readiness and actionable blocking guidance when tax data is missing.

### Tests for User Story 2 (Required)

- [ ] T019 [P] [US2] Add API integration test for batch review details in backend/tests/integration/api/test_review_draft_batch.py
- [ ] T020 [P] [US2] Add service tests for readiness and blocking guidance in backend/tests/unit/services/test_invoice_readiness_service.py
- [ ] T021 [P] [US2] Add frontend batch review screen tests in frontend/src/features/recurring-invoices/__tests__/DraftBatchReviewPage.test.tsx

### Implementation for User Story 2

- [ ] T022 [US2] Implement invoice readiness evaluator service in backend/src/services/recurring/invoice_readiness_service.py
- [ ] T023 [US2] Implement missing tax data guidance formatter in backend/src/services/recurring/tax_data_guidance_service.py
- [ ] T024 [US2] Implement GET draft batch review endpoint in backend/src/api/routes/recurring_invoice_review.py
- [ ] T025 [US2] Implement draft batch review page in frontend/src/features/recurring-invoices/pages/DraftBatchReviewPage.tsx
- [ ] T026 [US2] Implement readiness badge and guidance panel components in frontend/src/features/recurring-invoices/components/InvoiceReadinessSummary.tsx

**Checkpoint**: User Story 2 is independently testable and does not require batch send functionality.

---

## Phase 5: User Story 3 - Send Ready Invoices in Batch (Priority: P3)

**Goal**: Finance admins can send all ready invoices in one action while blocked invoices remain draft.

**Independent Test**: Execute send on a mixed batch and verify only ready invoices are sent, blocked invoices remain draft, and a complete send summary is returned.

### Tests for User Story 3 (Required)

- [ ] T027 [P] [US3] Add API integration test for batch send with mixed readiness in backend/tests/integration/api/test_send_invoice_batch.py
- [ ] T028 [P] [US3] Add service tests for send filtering and result aggregation in backend/tests/unit/services/test_batch_send_service.py
- [ ] T029 [P] [US3] Add frontend send flow and summary tests in frontend/src/features/recurring-invoices/__tests__/SendInvoiceBatch.test.tsx

### Implementation for User Story 3

- [ ] T030 [US3] Implement batch send orchestrator service in backend/src/services/recurring/batch_send_service.py
- [ ] T031 [US3] Implement POST batch send endpoint in backend/src/api/routes/recurring_invoice_send.py
- [ ] T032 [US3] Implement send batch action bar component in frontend/src/features/recurring-invoices/components/SendBatchActionBar.tsx
- [ ] T033 [US3] Implement batch send result summary panel in frontend/src/features/recurring-invoices/components/BatchSendSummaryPanel.tsx

**Checkpoint**: User Story 3 is independently testable against existing review and generation outputs.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish cross-story quality, observability, and documentation.

- [ ] T034 [P] Add recurring invoice workflow runbook in docs/recurring-invoice-workflow.md
- [ ] T035 Add backend structured logging for generation, review, and send flows in backend/src/core/logging/recurring_invoice_logging.py
- [ ] T036 [P] Add frontend analytics events for generation, review, and send actions in frontend/src/features/recurring-invoices/analytics/recurringInvoiceEvents.ts
- [ ] T037 Execute end-to-end recurring invoice regression scenario in backend/tests/integration/test_recurring_invoice_workflow_regression.py

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) has no dependencies.
- Foundational (Phase 2) depends on Setup and blocks all user story work.
- User Story phases (Phases 3-5) depend on Foundational completion.
- Polish (Phase 6) depends on completion of the selected user stories.

### User Story Dependencies

- US1 (P1) starts immediately after Foundational and is the MVP slice.
- US2 (P2) depends on shared foundations and generated draft batch data from US1, but remains independently testable through review APIs and UI.
- US3 (P3) depends on shared foundations and uses readiness outputs from US2, while remaining independently testable with a mixed batch fixture.

### Within Each User Story

- Write tests first and confirm they fail before implementation.
- Implement backend services before API routes.
- Implement API routes before frontend action wiring.
- Complete story checkpoint validation before advancing to next story.

---

## Parallel Execution Examples

### User Story 1

- Run T011, T012, and T013 in parallel.
- Run T017 and T018 in parallel after T016 is merged.

### User Story 2

- Run T019, T020, and T021 in parallel.
- Run T025 and T026 in parallel after T024 is merged.

### User Story 3

- Run T027, T028, and T029 in parallel.
- Run T032 and T033 in parallel after T031 is merged.

---

## Implementation Strategy

### MVP First (US1)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1) and validate independent generation behavior.
3. Demo or release MVP to finance admins for draft-generation feedback.

### Incremental Delivery

1. Add US2 review capabilities and validate independently.
2. Add US3 send capabilities and validate independently.
3. Complete Polish tasks for observability and regression protection.

### Team Parallelization

1. Team completes Setup and Foundational together.
2. After Foundational, one engineer leads backend services while another leads frontend screens per active story.
3. Keep story boundaries strict so testability remains independent per user story.
