# Tasks: Audit Log Export Service

**Input**: Design documents from `.agents/scratchpad/audit-log-export-service/`
**Prerequisites**: plan.md, spec.md, data-model.md

## Format: `[ID] [P?] [Story] Description`

- `[P]`: Can run in parallel (different files, no dependency conflicts)
- `[Story]`: User story label for story-phase tasks only (`[US1]`, `[US2]`, `[US3]`)
- Every task includes a concrete file path

## Phase 1: Setup

**Purpose**: Initialize service structure, tooling, and baseline runtime configuration.

- [ ] T001 Create backend package structure for export APIs and workers in src/api/, src/services/, src/workers/, and src/models/
- [ ] T002 Initialize dependency manifests for API, Redis client, object storage SDK, and test tooling in pyproject.toml and requirements-dev.txt
- [ ] T003 [P] Configure linting and formatting rules in pyproject.toml and .editorconfig
- [ ] T004 [P] Create local environment template for database, Redis, and object storage settings in .env.example
- [ ] T005 Add docker-compose services for api, worker, redis, and local object storage in docker-compose.yml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure required before user story delivery.

**CRITICAL**: Complete this phase before starting user story implementation.

- [ ] T006 Create shared settings loader and typed config objects in src/config/settings.py
- [ ] T007 [P] Implement database session management and migration bootstrap in src/db/session.py and migrations/env.py
- [ ] T008 [P] Add compliance_admin authorization guard middleware for export endpoints in src/api/middleware/authz.py
- [ ] T009 [P] Implement Redis-backed job queue client and worker bootstrap in src/workers/queue.py
- [ ] T010 Create object storage abstraction with signed URL support in src/services/storage_service.py
- [ ] T011 Add structured logging and request correlation utilities in src/observability/logging.py
- [ ] T012 Create base ExportJob model and repository scaffolding in src/models/export_job.py and src/repositories/export_job_repository.py

**Checkpoint**: Foundational platform is ready for independent user story work.

---

## Phase 3: User Story 1 - Request a Filtered Audit Export (Priority: P1) 🎯 MVP

**Goal**: A compliance admin can request an export by date range, actor type, action category, and output format.

**Independent Test**: Submit valid and invalid export requests as compliance and non-compliance users; verify accepted jobs are persisted with queued status and unauthorized requests are rejected.

### Tests for User Story 1 (REQUIRED)

- [ ] T013 [P] [US1] Add API contract test for export request validation and authz in tests/contract/test_export_request_api.py
- [ ] T014 [P] [US1] Add integration test for creating export jobs with filter criteria in tests/integration/test_create_export_job.py
- [ ] T015 [P] [US1] Add service unit tests for filter normalization and format validation in tests/unit/test_export_request_service.py

### Implementation for User Story 1

- [ ] T016 [P] [US1] Implement request and response schemas for export creation in src/api/schemas/export_requests.py
- [ ] T017 [US1] Implement export request service to validate filters and create queued jobs in src/services/export_request_service.py (depends on T016)
- [ ] T018 [US1] Implement POST /api/exports endpoint with compliance_admin guard in src/api/routes/exports.py
- [ ] T019 [US1] Persist initial audit event for export request creation in src/services/export_audit_service.py

**Checkpoint**: Compliance admins can create export jobs and receive job identifiers.

---

## Phase 4: User Story 2 - Track Export Progress and Download File (Priority: P2)

**Goal**: A compliance admin can track job progress and download completed exports via time-limited links.

**Independent Test**: Queue and process an export job, poll job status through completion, and verify download links expire after the configured validity period.

### Tests for User Story 2 (REQUIRED)

- [ ] T020 [P] [US2] Add contract test for export status and download endpoints in tests/contract/test_export_status_api.py
- [ ] T021 [P] [US2] Add worker integration test for CSV and JSON generation flow in tests/integration/test_export_worker_generation.py
- [ ] T022 [P] [US2] Add integration test for signed URL expiration behavior in tests/integration/test_export_download_expiry.py

### Implementation for User Story 2

- [ ] T023 [P] [US2] Implement export file builder for CSV and JSON outputs in src/services/export_file_builder.py
- [ ] T024 [US2] Implement worker handler to stream audit rows and update job progress in src/workers/export_generation_worker.py
- [ ] T025 [US2] Implement GET /api/exports/{job_id} status endpoint in src/api/routes/export_status.py
- [ ] T026 [US2] Implement GET /api/exports/{job_id}/download endpoint returning signed links for completed jobs in src/api/routes/export_download.py
- [ ] T027 [US2] Add download eligibility and 24-hour TTL checks in src/services/export_download_service.py

**Checkpoint**: Export jobs can be processed asynchronously and downloaded securely on completion.

---

## Phase 5: User Story 3 - Audit Export Requests and Downloads (Priority: P3)

**Goal**: Every export request and download is recorded to a dedicated audit stream for compliance traceability.

**Independent Test**: Create and download exports, then verify matching audit records exist with actor, action, timestamp, and job context.

### Tests for User Story 3 (REQUIRED)

- [ ] T028 [P] [US3] Add integration test for request and download audit event emission in tests/integration/test_export_audit_events.py
- [ ] T029 [P] [US3] Add repository test for dedicated audit stream persistence in tests/unit/test_export_audit_repository.py

### Implementation for User Story 3

- [ ] T030 [P] [US3] Implement export audit event model and serializer in src/models/export_audit_event.py
- [ ] T031 [US3] Implement dedicated export audit repository in src/repositories/export_audit_repository.py
- [ ] T032 [US3] Emit audit events from request creation, worker completion, and download flows in src/services/export_audit_service.py
- [ ] T033 [US3] Add admin-facing audit query endpoint for export events in src/api/routes/export_audit.py

**Checkpoint**: Export lifecycle actions are traceable through the dedicated audit stream.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Quality, hardening, and delivery readiness across all stories.

- [ ] T034 [P] Add rate limiting and abuse safeguards on export request endpoints in src/api/middleware/rate_limit.py
- [ ] T035 [P] Add PII redaction rules for exported fields and audit metadata in src/services/redaction_policy.py
- [ ] T036 Improve operational runbook for queue retries, dead-letter handling, and storage cleanup in docs/audit-log-export-runbook.md
- [ ] T037 [P] Add end-to-end smoke test covering request, processing, status, and download in tests/e2e/test_export_smoke.py
- [ ] T038 Validate performance budget for export initiation latency and large dataset handling in tests/performance/test_export_performance.py

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): No dependencies.
- Foundational (Phase 2): Depends on Setup; blocks all user stories.
- User Story phases (Phases 3-5): Depend on Foundational completion.
- Polish (Phase 6): Depends on completion of selected user stories.

### User Story Dependencies

- US1 (P1): Starts after Phase 2 and has no dependency on other stories.
- US2 (P2): Starts after Phase 2; depends on shared queue and storage foundations, not on US1 business logic.
- US3 (P3): Starts after Phase 2; integrates with flows delivered by US1 and US2.

### Within-Story Ordering Rules

- Write tests first and confirm they fail before implementation.
- Implement schemas/models before services.
- Implement services before API route wiring.
- Complete story acceptance checks before moving to next priority.

## Parallel Opportunities

- Setup: T003 and T004 can run in parallel after T001.
- Foundational: T007, T008, and T009 can run in parallel after T006.
- US1: T013, T014, and T015 can run in parallel; T016 can proceed while tests are authored.
- US2: T020, T021, and T022 can run in parallel; T023 can be developed in parallel with API status route scaffolding.
- US3: T028 and T029 can run in parallel; T030 can proceed in parallel before T031 and T032 converge.
- Polish: T034, T035, and T037 can run in parallel after core stories stabilize.

## Implementation Strategy

### MVP First (US1)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1) end-to-end.
3. Validate request flow, authz, and queued job creation in tests and a demo environment.

### Incremental Delivery

1. Add US2 for asynchronous generation and secure downloads.
2. Add US3 for dedicated audit stream traceability.
3. Finish with Polish phase hardening and performance validation.

### Parallel Team Plan

1. Team completes Setup and Foundational together.
2. After foundations are ready:
   - Engineer A leads US1 API and request service.
   - Engineer B leads US2 worker and download flow.
   - Engineer C leads US3 audit repository and event propagation.
3. Integrate through shared tests and smoke validation in Phase 6.
