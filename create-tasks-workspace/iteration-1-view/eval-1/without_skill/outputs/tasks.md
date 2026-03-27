# Tasks: Recurring Invoice Batch Send

**Input**: Design documents from `.agents/scratchpad/billing-disputes-workflow/`
**Prerequisites**: plan.md, spec.md, data-model.md

**Tests**: Tests are REQUIRED. Follow TDD: write tests first, confirm they fail, then implement.

**Organization**: Tasks are grouped by user story to preserve independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize backend/frontend tooling and feature module scaffolding.

- [ ] T001 Create recurring invoice feature module structure in `backend/src/features/recurring_invoices/` and `frontend/src/features/recurringInvoices/`
- [ ] T002 Add backend dependencies and pytest plugins for feature tests in `backend/pyproject.toml`
- [ ] T003 [P] Add frontend test setup for recurring invoices in `frontend/vitest.config.ts` and `frontend/src/test/setup.ts`
- [ ] T004 [P] Add environment variables and defaults for batch generation/send limits in `backend/src/config/settings.py` and `backend/.env.example`
- [ ] T005 Configure API router registration for recurring invoice endpoints in `backend/src/main.py` and `backend/src/api/router.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared primitives required by all user stories.

**CRITICAL**: User story implementation starts only after this phase is complete.

- [ ] T006 Create initial migration for recurring invoice tables (`regional_tax_rules`, `tax_profiles`, `invoice_batches`, `draft_invoices`) in `backend/src/db/migrations/versions/20260326_recurring_invoices_init.py`
- [ ] T007 [P] Implement SQLAlchemy base models for shared entities in `backend/src/features/recurring_invoices/models.py`
- [ ] T008 [P] Implement Pydantic schemas for batch, invoice, readiness, and send summary payloads in `backend/src/features/recurring_invoices/schemas.py`
- [ ] T009 [P] Implement repository layer for shared invoice batch reads/writes in `backend/src/features/recurring_invoices/repository.py`
- [ ] T010 Implement finance-admin authorization guard for recurring invoice routes in `backend/src/features/recurring_invoices/authz.py`
- [ ] T011 Implement shared readiness evaluator for tax-data completeness and rule availability in `backend/src/features/recurring_invoices/readiness.py`
- [ ] T012 Add structured audit/event logging for batch lifecycle actions in `backend/src/features/recurring_invoices/audit.py`

**Checkpoint**: Foundation complete; all stories can now be implemented and tested independently.

---

## Phase 3: User Story 1 - Generate Monthly Draft Invoices (Priority: P1) 🎯 MVP

**Goal**: Finance admins can generate a monthly draft batch from eligible subscriptions.

**Independent Test**: Trigger generation for a target month and verify one draft per eligible subscription, none for ineligible records.

### Tests for User Story 1 (REQUIRED)

- [ ] T013 [P] [US1] Add contract test for `POST /api/recurring-invoices/batches/generate` in `backend/tests/contract/test_generate_invoice_batch.py`
- [ ] T014 [P] [US1] Add integration test for eligibility filtering and one-draft-per-subscription in `backend/tests/integration/test_monthly_generation.py`
- [ ] T015 [P] [US1] Add frontend component test for generation form submission and success state in `frontend/src/features/recurringInvoices/__tests__/GenerateBatchForm.test.tsx`

### Implementation for User Story 1

- [ ] T016 [US1] Implement subscription eligibility query service in `backend/src/features/recurring_invoices/subscription_selector.py`
- [ ] T017 [US1] Implement draft generation service with idempotent per-period behavior in `backend/src/features/recurring_invoices/generate_batch_service.py`
- [ ] T018 [US1] Implement generation API endpoint and request validation in `backend/src/features/recurring_invoices/routes_generate.py`
- [ ] T019 [P] [US1] Implement frontend batch-generation page and month selector in `frontend/src/features/recurringInvoices/pages/GenerateBatchPage.tsx`
- [ ] T020 [US1] Implement frontend API client for generation workflow in `frontend/src/features/recurringInvoices/api/generateBatch.ts`
- [ ] T021 [US1] Add generation observability metrics (duration, eligible count, created count) in `backend/src/features/recurring_invoices/metrics.py`

**Checkpoint**: US1 is independently shippable and testable.

---

## Phase 4: User Story 2 - Review Draft Invoice Set (Priority: P2)

**Goal**: Finance admins can inspect batch contents, readiness, and blocking reasons before sending.

**Independent Test**: Open a generated batch and verify each draft displays readiness state plus actionable blocking guidance.

### Tests for User Story 2 (REQUIRED)

- [ ] T022 [P] [US2] Add contract test for `GET /api/recurring-invoices/batches/{batch_id}` in `backend/tests/contract/test_get_invoice_batch.py`
- [ ] T023 [P] [US2] Add integration test for readiness and missing-tax-data guidance in `backend/tests/integration/test_batch_review_readiness.py`
- [ ] T024 [P] [US2] Add frontend page test for readiness badges and blocking guidance rendering in `frontend/src/features/recurringInvoices/__tests__/ReviewBatchPage.test.tsx`

### Implementation for User Story 2

- [ ] T025 [US2] Implement batch review query service with per-invoice readiness projection in `backend/src/features/recurring_invoices/review_batch_service.py`
- [ ] T026 [US2] Implement batch detail API endpoint with blocked-reason payloads in `backend/src/features/recurring_invoices/routes_review.py`
- [ ] T027 [P] [US2] Implement frontend review page with invoice table, status filters, and guidance panel in `frontend/src/features/recurringInvoices/pages/ReviewBatchPage.tsx`
- [ ] T028 [US2] Implement frontend API client and state slice for batch review data in `frontend/src/features/recurringInvoices/api/getBatchDetails.ts` and `frontend/src/features/recurringInvoices/state/reviewSlice.ts`
- [ ] T029 [US2] Add readiness reason code-to-guidance mapping in `frontend/src/features/recurringInvoices/guidance/readinessGuidance.ts`

**Checkpoint**: US2 is independently testable using generated or seeded batches.

---

## Phase 5: User Story 3 - Send Ready Invoices in Batch (Priority: P3)

**Goal**: Finance admins can send all ready invoices in one action while blocked invoices remain draft.

**Independent Test**: Execute send on a mixed-ready batch and verify only ready invoices transition to sent, with summary counts and reasons for blocked items.

### Tests for User Story 3 (REQUIRED)

- [ ] T030 [P] [US3] Add contract test for `POST /api/recurring-invoices/batches/{batch_id}/send` in `backend/tests/contract/test_send_invoice_batch.py`
- [ ] T031 [P] [US3] Add integration test for mixed-ready send behavior and blocked retention in `backend/tests/integration/test_batch_send_mixed_readiness.py`
- [ ] T032 [P] [US3] Add frontend workflow test for send action and result summary in `frontend/src/features/recurringInvoices/__tests__/SendBatchFlow.test.tsx`

### Implementation for User Story 3

- [ ] T033 [US3] Implement batch send orchestration service with transactional status updates in `backend/src/features/recurring_invoices/send_batch_service.py`
- [ ] T034 [US3] Integrate outbound invoice dispatch adapter and retry-safe semantics in `backend/src/features/recurring_invoices/invoice_dispatcher.py`
- [ ] T035 [US3] Implement send endpoint returning sent/blocked summary response in `backend/src/features/recurring_invoices/routes_send.py`
- [ ] T036 [P] [US3] Implement frontend send action with confirmation modal in `frontend/src/features/recurringInvoices/components/SendBatchButton.tsx`
- [ ] T037 [US3] Implement frontend summary panel for sent/blocked totals and blocked reasons in `frontend/src/features/recurringInvoices/components/BatchSendSummary.tsx`
- [ ] T038 [US3] Add post-send refresh flow to keep blocked invoices visible as draft in `frontend/src/features/recurringInvoices/pages/ReviewBatchPage.tsx`

**Checkpoint**: US3 is independently testable and completes the end-to-end feature.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Hardening, performance checks, and release readiness.

- [ ] T039 [P] Add backend performance test for list/review p95 target in `backend/tests/performance/test_batch_review_p95.py`
- [ ] T040 [P] Add end-to-end regression covering generate-review-send lifecycle in `frontend/src/features/recurringInvoices/__tests__/RecurringInvoices.e2e.test.ts`
- [ ] T041 Update feature runbook and operational troubleshooting notes in `docs/recurring-invoice-batches.md`
- [ ] T042 Validate role-based access and audit log coverage across all endpoints in `backend/tests/integration/test_recurring_invoices_security_audit.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 (Setup): starts immediately.
- Phase 2 (Foundational): depends on Phase 1 and blocks all stories.
- Phase 3 (US1), Phase 4 (US2), Phase 5 (US3): all depend on Phase 2.
- Phase 6 (Polish): depends on completion of target user stories.

### User Story Dependencies

- US1 (P1): no dependency on other stories after foundational tasks.
- US2 (P2): no functional dependency on US1 logic; can be tested independently with seeded batches.
- US3 (P3): no implementation dependency on US1/US2 UI; can be tested independently with seeded mixed-ready batches.

### Within-Story Sequencing Rules

- Tests first (contract/integration/UI) and verify failure.
- Service/model logic before route wiring.
- Backend endpoint before frontend integration.
- Story checkpoint validation before moving to next priority.

---

## Parallel Opportunities

- Setup: T003 and T004 can run in parallel after T001/T002.
- Foundational: T007, T008, and T009 can run in parallel after T006.
- US1: T013, T014, and T015 can run in parallel; T019 can proceed in parallel with T016/T017 once API contract is stable.
- US2: T022, T023, and T024 can run in parallel; T027 can run in parallel with T025 once response shape is fixed.
- US3: T030, T031, and T032 can run in parallel; T036 can run in parallel with T033/T034 once endpoint contract is fixed.

---

## Parallel Example: User Story 2

```bash
# Parallel test authoring (US2)
Task T022: Contract test for GET batch details
Task T023: Integration test for readiness and guidance
Task T024: Frontend review page test

# Parallel implementation once API schema is stable
Task T025: Backend review query service
Task T027: Frontend review page and filters
```

---

## Implementation Strategy

### MVP First (US1)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1) fully.
3. Validate US1 independent test criteria.
4. Release MVP for controlled finance-admin usage.

### Incremental Delivery

1. Ship US1 (generation).
2. Ship US2 (review/readiness guidance).
3. Ship US3 (batch send).
4. Apply polish/performance/security hardening.

### Independent Testability Guarantee

- Each user story has dedicated contract, integration, and UI test tasks.
- Each story can be validated with controlled seeded data without requiring completion of later stories.
- Cross-story coupling is limited to shared foundational modules established in Phase 2.
