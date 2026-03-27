# Tasks: Recurring Invoice Batch Send

**Input**: Design documents from `.agents/scratchpad/billing-disputes-workflow/`
**Prerequisites**: plan.md, spec.md, data-model.md

**Tests**: Tests are required and must be written first for each user story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish project scaffolding and shared development configuration.

- [ ] T001 Create backend recurring invoicing module scaffold in backend/src/modules/recurring_invoices/__init__.py
- [ ] T002 Create frontend recurring invoices feature scaffold in frontend/src/features/recurringInvoices/index.ts
- [ ] T003 [P] Add backend test package scaffolding in backend/tests/contract/test_recurring_invoices_health.py
- [ ] T004 [P] Add frontend test package scaffolding in frontend/src/features/recurringInvoices/__tests__/batchGeneration.test.tsx
- [ ] T005 Configure shared feature environment variables and defaults in backend/src/core/settings.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared domain and infrastructure required by all user stories.

**CRITICAL**: Complete this phase before starting user story implementation.

- [ ] T006 Create invoice batch and draft invoice database models in backend/src/models/recurring_invoice.py
- [ ] T007 Create tax profile and regional tax rule models in backend/src/models/tax_profile.py
- [ ] T008 [P] Add Alembic migration for recurring invoice, tax profile, and batch tables in backend/alembic/versions/20260326_recurring_invoice_foundation.py
- [ ] T009 Implement foundational repositories for batch, draft invoice, and tax profile access in backend/src/repositories/recurring_invoice_repository.py
- [ ] T010 [P] Implement shared readiness evaluator for tax-data completeness in backend/src/services/invoice_readiness_service.py
- [ ] T011 [P] Add API router registration and dependency wiring for recurring invoice module in backend/src/api/router.py
- [ ] T012 Define shared frontend API client methods for recurring invoice endpoints in frontend/src/features/recurringInvoices/api/recurringInvoicesApi.ts

**Checkpoint**: Foundation is complete; user stories can now be implemented and tested independently.

---

## Phase 3: User Story 1 - Generate Monthly Draft Invoices (Priority: P1) 🎯 MVP

**Goal**: Finance admins can generate one draft invoice per eligible subscription for a billing period.

**Independent Test**: Trigger generation for a known subscription fixture and verify exactly one draft per eligible subscription while canceled/out-of-period subscriptions are skipped.

### Tests for User Story 1 (REQUIRED)

- [ ] T013 [P] [US1] Add contract test for monthly draft generation endpoint in backend/tests/contract/test_generate_monthly_drafts.py
- [ ] T014 [P] [US1] Add integration test for eligibility filtering and one-draft-per-subscription rule in backend/tests/integration/test_monthly_generation_rules.py
- [ ] T015 [P] [US1] Add frontend component test for generation form and run feedback in frontend/src/features/recurringInvoices/__tests__/batchGeneration.test.tsx

### Implementation for User Story 1

- [ ] T016 [US1] Implement monthly generation service with eligibility filtering in backend/src/services/monthly_generation_service.py
- [ ] T017 [US1] Implement POST generate-drafts endpoint in backend/src/api/recurring_invoices.py
- [ ] T018 [US1] Add idempotency guard for billing period and subscription pair in backend/src/services/monthly_generation_service.py
- [ ] T019 [US1] Implement generation request form and submit flow in frontend/src/features/recurringInvoices/components/BatchGenerationForm.tsx
- [ ] T020 [US1] Connect generation page state and API calls in frontend/src/features/recurringInvoices/pages/BatchGenerationPage.tsx

**Checkpoint**: User Story 1 is independently testable and releasable as MVP.

---

## Phase 4: User Story 2 - Review Draft Invoice Set (Priority: P2)

**Goal**: Finance admins can review batch contents with per-invoice readiness and blocking reasons.

**Independent Test**: Open a generated batch and verify each draft invoice shows readiness plus missing-tax-data guidance when blocked.

### Tests for User Story 2 (REQUIRED)

- [ ] T021 [P] [US2] Add contract test for batch detail and readiness fields in backend/tests/contract/test_batch_review_endpoint.py
- [ ] T022 [P] [US2] Add integration test for blocked reason and guidance generation in backend/tests/integration/test_batch_review_blocking_guidance.py
- [ ] T023 [P] [US2] Add frontend component test for batch review table statuses and guidance in frontend/src/features/recurringInvoices/__tests__/batchReview.test.tsx

### Implementation for User Story 2

- [ ] T024 [US2] Implement batch review query service with readiness projection in backend/src/services/batch_review_service.py
- [ ] T025 [US2] Implement GET batch review endpoint including blocked guidance payload in backend/src/api/recurring_invoices.py
- [ ] T026 [US2] Implement draft invoice review table with readiness badges in frontend/src/features/recurringInvoices/components/BatchReviewTable.tsx
- [ ] T027 [US2] Implement blocked guidance panel for missing tax data in frontend/src/features/recurringInvoices/components/BlockedReasonPanel.tsx
- [ ] T028 [US2] Wire batch review page data loading and filtering in frontend/src/features/recurringInvoices/pages/BatchReviewPage.tsx

**Checkpoint**: User Story 2 is independently testable and does not require User Story 3 behavior.

---

## Phase 5: User Story 3 - Send Ready Invoices in Batch (Priority: P3)

**Goal**: Finance admins can send all ready invoices in one action while blocked invoices remain draft.

**Independent Test**: Execute send on a mixed batch and verify only ready invoices are sent, blocked invoices remain draft, and summary counts are correct.

### Tests for User Story 3 (REQUIRED)

- [ ] T029 [P] [US3] Add contract test for batch send endpoint summary and blocked handling in backend/tests/contract/test_batch_send_endpoint.py
- [ ] T030 [P] [US3] Add integration test for mixed-ready batch send outcomes in backend/tests/integration/test_batch_send_mixed_readiness.py
- [ ] T031 [P] [US3] Add frontend component test for send action and result summary in frontend/src/features/recurringInvoices/__tests__/batchSend.test.tsx

### Implementation for User Story 3

- [ ] T032 [US3] Implement batch send orchestrator that skips blocked drafts in backend/src/services/batch_send_service.py
- [ ] T033 [US3] Implement POST batch send endpoint with sent and blocked summary in backend/src/api/recurring_invoices.py
- [ ] T034 [US3] Persist per-invoice send outcomes and blocked reasons in backend/src/repositories/recurring_invoice_repository.py
- [ ] T035 [US3] Implement batch send action bar and confirmation flow in frontend/src/features/recurringInvoices/components/BatchSendActionBar.tsx
- [ ] T036 [US3] Implement send result summary view in frontend/src/features/recurringInvoices/components/BatchSendSummary.tsx

**Checkpoint**: User Story 3 is independently testable and confirms compliant batch sending behavior.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final quality improvements across stories.

- [ ] T037 [P] Add backend performance test for list/review p95 budget in backend/tests/performance/test_batch_review_p95.py
- [ ] T038 [P] Add structured audit logging for generation, review, and send flows in backend/src/services/audit_log_service.py
- [ ] T039 Add API and operator runbook updates for recurring invoicing workflow in docs/recurring-invoices-workflow.md
- [ ] T040 Run end-to-end regression scenario for all user stories in backend/tests/integration/test_recurring_invoices_end_to_end.py

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) starts immediately.
- Foundational (Phase 2) depends on Setup and blocks all user story phases.
- User Story phases (Phases 3-5) depend on Foundational completion.
- Polish (Phase 6) depends on completion of selected user stories.

### User Story Dependencies

- US1 depends only on Foundational tasks and is the MVP slice.
- US2 depends on Foundational tasks and generated batch data, but remains independently testable by creating fixture batches.
- US3 depends on Foundational tasks and batch state, but remains independently testable with mixed-readiness fixtures.

### Within Each User Story

- Write tests first and confirm they fail before implementation.
- Implement backend services before endpoint wiring.
- Implement API integrations before final frontend interaction flows.
- Validate independent acceptance criteria before moving to the next story.

### Parallel Opportunities

- T003 and T004 can run in parallel.
- T008, T010, T011, and T012 can run in parallel after model definitions begin.
- Within each user story, all test tasks marked [P] can run in parallel.
- Frontend component tasks in the same story can run in parallel after API contract shape is stable.

---

## Parallel Example: User Story 2

```bash
Task: "T021 [US2] Contract test for batch detail and readiness fields in backend/tests/contract/test_batch_review_endpoint.py"
Task: "T022 [US2] Integration test for blocked reason and guidance generation in backend/tests/integration/test_batch_review_blocking_guidance.py"
Task: "T023 [US2] Frontend component test for batch review table statuses and guidance in frontend/src/features/recurringInvoices/__tests__/batchReview.test.tsx"
```

---

## Implementation Strategy

### MVP First (US1)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate US1 independently and release.

### Incremental Delivery

1. Deliver US1 for draft generation.
2. Deliver US2 for readiness review and guidance.
3. Deliver US3 for compliant batch send.
4. Finish with polish and performance checks.

### Independent Testability Guardrails

1. Keep each user story test fixtures self-contained.
2. Avoid introducing required runtime dependencies on unfinished story code.
3. Maintain endpoint contracts per story so stories can be validated in isolation.
