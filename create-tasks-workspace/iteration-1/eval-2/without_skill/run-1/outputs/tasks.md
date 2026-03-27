# Tasks: Audit Log Export Service

**Input**: Design documents from `.agents/scratchpad/audit-log-export-service/`
**Prerequisites**: plan.md, spec.md, data-model.md

**Tests**: Tests are REQUIRED and follow TDD (write failing tests first).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no blocking dependency)
- **[Story]**: User story label (`[US1]`, `[US2]`, `[US3]`)
- Every task includes a concrete file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the service skeleton and core tooling for API + worker execution.

- [ ] T001 Create backend project skeleton and package metadata in backend/pyproject.toml
- [ ] T002 [P] Add runtime and development dependencies (FastAPI, Celery, Redis, boto3, pytest) in backend/requirements.txt
- [ ] T003 [P] Create environment template for API, worker, Redis, and S3 settings in backend/.env.example
- [ ] T004 [P] Configure linting and formatting defaults in backend/pyproject.toml
- [ ] T005 Create app bootstrap and router registration in backend/src/main.py
- [ ] T006 Create worker bootstrap and Celery app configuration in backend/src/worker/celery_app.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared primitives required by all user stories.

**CRITICAL**: User story work starts only after this phase is complete.

- [ ] T007 Implement database models for ExportJob and ExportEvent in backend/src/models/export_job.py
- [ ] T008 [P] Create migration for export_jobs and export_events tables in backend/migrations/versions/0001_create_export_tables.py
- [ ] T009 [P] Implement repository layer for ExportJob lifecycle reads/writes in backend/src/repositories/export_job_repository.py
- [ ] T010 [P] Implement role-based authorization guard for compliance_admin in backend/src/security/roles.py
- [ ] T011 [P] Implement shared validation schemas for filters, formats, and limits in backend/src/schemas/export_requests.py
- [ ] T012 Implement object storage client wrapper for upload and signed URL generation in backend/src/integrations/storage_client.py
- [ ] T013 Implement audit stream publisher abstraction for export events in backend/src/integrations/audit_stream.py
- [ ] T014 Configure structured logging and error mapping middleware in backend/src/core/error_handling.py

**Checkpoint**: Foundation complete; user stories can now proceed.

---

## Phase 3: User Story 1 - Request Filtered Export Job (Priority: P1) MVP

**Goal**: Compliance admin can submit a filtered CSV/JSON export request that is queued asynchronously.

**Independent Test**: Submit export request with valid filters and verify job is accepted, persisted as queued, and enqueued to Redis-backed worker.

### Tests for User Story 1 (REQUIRED)

- [ ] T015 [P] [US1] Add API contract test for POST /v1/audit-exports in backend/tests/contract/test_create_export_job.py
- [ ] T016 [P] [US1] Add integration test for queued job creation and authorization checks in backend/tests/integration/test_request_export_job.py
- [ ] T017 [P] [US1] Add validation test for date range and filter constraints in backend/tests/unit/test_export_request_validation.py

### Implementation for User Story 1

- [ ] T018 [US1] Implement export request service (create job + queue dispatch) in backend/src/services/export_request_service.py
- [ ] T019 [US1] Implement POST /v1/audit-exports endpoint in backend/src/api/export_routes.py
- [ ] T020 [US1] Add Redis queue producer for ExportJob payloads in backend/src/worker/export_dispatcher.py
- [ ] T021 [US1] Record request-created audit event on successful submission in backend/src/services/export_request_service.py

**Checkpoint**: User Story 1 functional and independently testable.

---

## Phase 4: User Story 2 - Track Progress and Download Export (Priority: P2)

**Goal**: Compliance admin can monitor export progress and retrieve a 24-hour signed download link after completion.

**Independent Test**: Request an export, process it to completion in worker, poll status endpoint, and download from signed URL before expiry.

### Tests for User Story 2 (REQUIRED)

- [ ] T022 [P] [US2] Add API contract test for GET /v1/audit-exports/{job_id} in backend/tests/contract/test_get_export_job_status.py
- [ ] T023 [P] [US2] Add integration test for worker completion and signed URL generation in backend/tests/integration/test_export_job_completion.py
- [ ] T024 [P] [US2] Add unit test for signed URL expiry policy (24h) in backend/tests/unit/test_signed_url_expiry.py

### Implementation for User Story 2

- [ ] T025 [US2] Implement export execution worker (fetch logs, stream file, upload artifact) in backend/src/worker/export_job_processor.py
- [ ] T026 [US2] Implement progress updates and terminal state transitions in backend/src/services/export_progress_service.py
- [ ] T027 [US2] Implement GET /v1/audit-exports/{job_id} status endpoint in backend/src/api/export_routes.py
- [ ] T028 [US2] Implement completed-job signed URL generation and exposure in backend/src/services/export_download_service.py
- [ ] T029 [US2] Add artifact metadata persistence (size, checksum, object key) in backend/src/repositories/export_job_repository.py

**Checkpoint**: User Stories 1 and 2 functional and independently testable.

---

## Phase 5: User Story 3 - Audit Export Access and Failures (Priority: P3)

**Goal**: Export requests, download attempts, and failures are fully auditable with no PII leakage.

**Independent Test**: Trigger success and failure paths, then verify audit stream includes request/download/failure events with actor and job context and sanitized payloads.

### Tests for User Story 3 (REQUIRED)

- [ ] T030 [P] [US3] Add integration test for export audit event emission in backend/tests/integration/test_export_audit_events.py
- [ ] T031 [P] [US3] Add unit test for PII redaction in audit payloads in backend/tests/unit/test_audit_payload_redaction.py
- [ ] T032 [P] [US3] Add integration test for failed-job retry and terminal failure auditing in backend/tests/integration/test_export_failure_auditing.py

### Implementation for User Story 3

- [ ] T033 [US3] Emit download-attempt and download-success audit events in backend/src/services/export_download_service.py
- [ ] T034 [US3] Emit processing-failure and retry-exhausted audit events in backend/src/worker/export_job_processor.py
- [ ] T035 [US3] Implement audit payload sanitizer and field allowlist in backend/src/services/audit_payload_sanitizer.py
- [ ] T036 [US3] Enforce export failure-rate metric and alert hook integration in backend/src/observability/export_metrics.py

**Checkpoint**: All user stories independently functional and auditable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Harden quality, performance, and operational readiness across stories.

- [ ] T037 [P] Add API usage and runbook documentation in backend/docs/audit-export-service.md
- [ ] T038 [P] Add load test scenario for large exports (5M+ records) in backend/tests/performance/test_large_export_job.py
- [ ] T039 Add idempotency protection for duplicate export submissions in backend/src/services/export_request_service.py
- [ ] T040 [P] Add end-to-end smoke test covering request-to-download path in backend/tests/e2e/test_export_flow.py
- [ ] T041 Validate production config defaults and secret handling in backend/src/core/config.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2.
- **Phase 4 (US2)**: Depends on US1 job creation contract and Phase 2 shared foundations.
- **Phase 5 (US3)**: Depends on US1/US2 event surfaces and worker flow.
- **Phase 6 (Polish)**: Depends on completion of all targeted user stories.

### User Story Dependencies

- **US1**: No dependency on other stories after foundations.
- **US2**: Depends on US1 request-and-queue behavior.
- **US3**: Depends on US1 and US2 lifecycle events.

### Within Each User Story

- Tests first and failing before implementation.
- Service logic before endpoint wiring when endpoint depends on service behavior.
- Persistence and state transitions before external visibility.

---

## Parallel Opportunities

- Phase 1 tasks T002, T003, T004 can run in parallel.
- Phase 2 tasks T008, T009, T010, T011 can run in parallel after model skeleton in T007 is defined.
- In US1, tests T015-T017 can run in parallel.
- In US2, tests T022-T024 can run in parallel.
- In US3, tests T030-T032 can run in parallel.
- Polish tasks T037, T038, T040 can run in parallel.

---

## Parallel Example: User Story 2

- Parallel test lane:
  - T022 Contract test for job status endpoint
  - T023 Integration test for worker completion
  - T024 Unit test for signed URL expiry
- Parallel implementation lane after worker scaffold exists:
  - T026 Progress/state transitions
  - T028 Signed URL generation

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1) as MVP for request + queue.
3. Validate with integration tests before moving on.

### Incremental Delivery

1. Add US2 for status and download experience.
2. Add US3 for complete compliance auditability.
3. Finish with Phase 6 hardening and performance validation.
