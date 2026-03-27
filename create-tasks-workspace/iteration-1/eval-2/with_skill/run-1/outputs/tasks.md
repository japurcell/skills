# Tasks: Audit Log Export Service

**Input**: Design documents from `.agents/scratchpad/audit-log-export-service/`
**Prerequisites**: plan.md, spec.md, data-model.md

**Tests**: Tests are required and use a TDD workflow (write failing tests first, then implement).

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize backend service, worker runtime, and developer tooling for export workflows.

- [ ] T001 Create backend project scaffolding in backend/src/ and backend/tests/ with package metadata in backend/pyproject.toml
- [ ] T002 Configure FastAPI application bootstrap in backend/src/app/main.py
- [ ] T003 [P] Configure Celery app with Redis broker settings in backend/src/app/worker/celery_app.py
- [ ] T004 [P] Add environment configuration and typed settings in backend/src/app/config/settings.py
- [ ] T005 [P] Configure linting and formatting (ruff, black) in backend/pyproject.toml
- [ ] T006 [P] Add local development stack for API, worker, Redis, and Postgres in infra/docker-compose.yml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared persistence, storage, security, and queue foundations required by all user stories.

**Critical**: Complete this phase before starting user story implementation.

- [ ] T007 Create ExportJob schema migration in backend/src/app/db/migrations/versions/0001_create_export_jobs.py
- [ ] T008 [P] Implement SQLAlchemy ExportJob model in backend/src/app/models/export_job.py
- [ ] T009 [P] Implement object storage client wrapper for S3-compatible storage in backend/src/app/services/storage_client.py
- [ ] T010 [P] Implement role-based auth dependency for compliance_admin access in backend/src/app/api/dependencies/auth.py
- [ ] T011 Implement audit log repository abstraction for append-only event writes in backend/src/app/services/audit_stream_service.py
- [ ] T012 Implement shared error mapping and API exception handlers in backend/src/app/api/error_handlers.py
- [ ] T013 Implement base worker job lifecycle helpers (queued/running/succeeded/failed) in backend/src/app/worker/job_lifecycle.py

**Checkpoint**: API + worker foundation is ready; user stories can begin.

---

## Phase 3: User Story 1 - Request Filtered Audit Export (Priority: P1) 🎯 MVP

**Goal**: A compliance admin can submit an export request with date range, actor type, action category, and format (CSV/JSON).

**Independent Test**: A compliance admin submits valid filter criteria and receives a queued export job ID; invalid filters are rejected with validation errors.

### Tests for User Story 1 (REQUIRED)

- [ ] T014 [P] [US1] Add request contract tests for POST /v1/audit-exports in backend/tests/contract/test_create_export_job.py
- [ ] T015 [P] [US1] Add integration test for compliance_admin job creation flow in backend/tests/integration/test_create_export_job_flow.py
- [ ] T016 [P] [US1] Add authorization test for non-compliance users in backend/tests/integration/test_create_export_job_authorization.py

### Implementation for User Story 1

- [ ] T017 [P] [US1] Implement export request schema validation (date range, format, filters) in backend/src/app/api/schemas/export_request.py
- [ ] T018 [US1] Implement export job creation service with queued state persistence in backend/src/app/services/export_job_service.py (depends on T008, T017)
- [ ] T019 [US1] Implement POST /v1/audit-exports endpoint in backend/src/app/api/routes/export_jobs.py (depends on T010, T018)
- [ ] T020 [US1] Add API router registration and dependency wiring in backend/src/app/main.py
- [ ] T021 [US1] Emit export_request_created audit event during job submission in backend/src/app/services/audit_stream_service.py

**Checkpoint**: Export requests can be submitted and validated independently.

---

## Phase 4: User Story 2 - Track Progress And Download Export (Priority: P2)

**Goal**: A compliance admin can view export progress and download completed files through 24-hour signed URLs.

**Independent Test**: A queued job transitions to success, status endpoint reflects progress, and completed job returns a valid signed download URL while expired URLs are rejected.

### Tests for User Story 2 (REQUIRED)

- [ ] T022 [P] [US2] Add contract tests for GET /v1/audit-exports/{job_id} in backend/tests/contract/test_get_export_job_status.py
- [ ] T023 [P] [US2] Add contract tests for GET /v1/audit-exports/{job_id}/download in backend/tests/contract/test_get_export_download_url.py
- [ ] T024 [P] [US2] Add worker integration test for CSV/JSON file generation and upload in backend/tests/integration/test_worker_generates_export_file.py
- [ ] T025 [P] [US2] Add integration test for signed URL expiry behavior in backend/tests/integration/test_download_url_expiry.py

### Implementation for User Story 2

- [ ] T026 [P] [US2] Implement export status response schema with progress fields in backend/src/app/api/schemas/export_status.py
- [ ] T027 [US2] Implement GET /v1/audit-exports/{job_id} status endpoint in backend/src/app/api/routes/export_jobs.py
- [ ] T028 [US2] Implement worker task to read audit records and produce CSV/JSON outputs in backend/src/app/worker/tasks/generate_export.py
- [ ] T029 [US2] Implement file upload and metadata update flow in backend/src/app/services/export_file_service.py
- [ ] T030 [US2] Implement signed URL issuance endpoint with 24-hour TTL in backend/src/app/api/routes/export_downloads.py
- [ ] T031 [US2] Add worker retry policy and failure state persistence in backend/src/app/worker/tasks/generate_export.py

**Checkpoint**: Export progress and file delivery are independently functional.

---

## Phase 5: User Story 3 - Audit Export Access And Operations (Priority: P3)

**Goal**: All export requests, processing outcomes, and download actions are recorded in a dedicated audit stream for compliance traceability.

**Independent Test**: Creating, completing, failing, and downloading exports each produce structured audit events with actor, timestamps, job ID, and outcome.

### Tests for User Story 3 (REQUIRED)

- [ ] T032 [P] [US3] Add integration tests for audit stream events across request/process/download lifecycle in backend/tests/integration/test_export_audit_events.py
- [ ] T033 [P] [US3] Add unit test for event payload redaction to prevent PII leakage in backend/tests/unit/test_audit_event_redaction.py
- [ ] T034 [P] [US3] Add integration test for failed job audit event emission in backend/tests/integration/test_failed_export_audit_event.py

### Implementation for User Story 3

- [ ] T035 [P] [US3] Define typed audit event schemas for export lifecycle events in backend/src/app/services/audit_event_schemas.py
- [ ] T036 [US3] Implement audit event publisher for request, started, completed, failed, and downloaded events in backend/src/app/services/audit_stream_service.py
- [ ] T037 [US3] Integrate download event emission in backend/src/app/api/routes/export_downloads.py
- [ ] T038 [US3] Integrate worker lifecycle event emission in backend/src/app/worker/tasks/generate_export.py
- [ ] T039 [US3] Add redaction guard for sensitive fields before event persistence in backend/src/app/services/audit_stream_service.py

**Checkpoint**: Compliance auditability is complete and independently verifiable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, observability, and operational readiness across all stories.

- [ ] T040 [P] Add API and worker metrics for queue latency, job duration, and failure rate in backend/src/app/observability/metrics.py
- [ ] T041 [P] Add structured logging correlation IDs across API and worker paths in backend/src/app/observability/logging.py
- [ ] T042 Add performance test for 5M+ record export job throughput in backend/tests/performance/test_large_export_job.py
- [ ] T043 Add runbook for export operations and failure recovery in docs/audit-log-export-runbook.md
- [ ] T044 Add quickstart validation steps for request-to-download flow in docs/audit-log-export-quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 (Setup): starts immediately.
- Phase 2 (Foundational): depends on Phase 1.
- Phase 3 (US1): depends on Phase 2 and is the MVP slice.
- Phase 4 (US2): depends on Phase 2 and uses US1 job creation behavior.
- Phase 5 (US3): depends on Phase 2 and integrates with US1/US2 lifecycle points.
- Phase 6 (Polish): depends on completion of selected user stories.

### User Story Dependencies

- US1 (P1): no dependency on other stories after Foundational.
- US2 (P2): depends on US1 job creation endpoint and ExportJob records.
- US3 (P3): depends on US1 and US2 event trigger points.

### Within Each User Story

- Tests are authored first and should fail before implementation.
- Schemas/models are implemented before services.
- Services are implemented before API routes and worker orchestration.
- Story checkpoint must pass before advancing.

## Parallel Opportunities

- In Setup, T003-T006 can run in parallel after T001.
- In Foundational, T008-T010 can run in parallel after T007.
- In US1, T014-T016 can run in parallel; T017 and T021 can run in parallel before T018/T019.
- In US2, T022-T025 can run in parallel; T026 and T028 can run in parallel before T027/T029/T030.
- In US3, T032-T034 can run in parallel; T035 and T039 can run in parallel before T036-T038.
- In Polish, T040 and T041 can run in parallel.

## Parallel Example: User Story 2

```bash
Task: "T022 [US2] Add contract tests for GET /v1/audit-exports/{job_id} in backend/tests/contract/test_get_export_job_status.py"
Task: "T023 [US2] Add contract tests for GET /v1/audit-exports/{job_id}/download in backend/tests/contract/test_get_export_download_url.py"
Task: "T024 [US2] Add worker integration test for CSV/JSON file generation and upload in backend/tests/integration/test_worker_generates_export_file.py"
Task: "T025 [US2] Add integration test for signed URL expiry behavior in backend/tests/integration/test_download_url_expiry.py"
```

## Implementation Strategy

### MVP First (US1)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1) and validate independent test criteria.
3. Demo export request creation path to compliance stakeholders.

### Incremental Delivery

1. Add US2 for progress/download after US1 is stable.
2. Add US3 for full compliance auditability.
3. Complete Phase 6 hardening before production rollout.
