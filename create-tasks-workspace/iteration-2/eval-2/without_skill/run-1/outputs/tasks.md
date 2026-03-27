# Tasks: Audit Log Export Service

## Phase 1: Setup

- [ ] T001 Create service skeleton and module layout in services/audit_export/__init__.py and services/audit_export/app.py
- [ ] T002 Add project dependencies for FastAPI, Celery, Redis client, boto3, and pytest in pyproject.toml
- [ ] T003 Add environment configuration template for database, Redis, and object storage in config/settings.py and .env.example
- [ ] T004 Create local development compose stack for api, worker, redis, and minio in infra/docker-compose.yml
- [ ] T005 Add base migration setup for export domain tables in migrations/env.py

## Phase 2: Foundational

- [ ] T006 Create ExportJob table migration with status, filters, format, requester, and storage metadata in migrations/versions/0001_export_jobs.py
- [ ] T007 Create ExportAuditEvent table migration for request and download audit stream in migrations/versions/0002_export_audit_events.py
- [ ] T008 Implement ExportJob ORM model and status enum in services/audit_export/models/export_job.py
- [ ] T009 Implement ExportAuditEvent ORM model in services/audit_export/models/export_audit_event.py
- [ ] T010 [P] Implement repository for ExportJob reads and writes in services/audit_export/repositories/export_job_repository.py
- [ ] T011 [P] Implement repository for audit event appends and queries in services/audit_export/repositories/export_audit_repository.py
- [ ] T012 Implement compliance_admin authorization dependency and permission tests in services/audit_export/authz.py and tests/authz/test_compliance_admin.py
- [ ] T013 Implement shared error schema and API exception handlers in services/audit_export/api/errors.py

## Phase 3: User Story 1 - Request Filtered Audit Export (Priority P1)

Goal: A compliance admin can request a CSV or JSON audit export with date and category filters, and the system enqueues processing asynchronously.

Independent Test: Submit a valid export request and verify API acceptance, job persistence, and queue dispatch without waiting for file generation.

### Tests (US1)

- [ ] T014 [US1] Add request validation tests for filter ranges, format, and role guard in tests/us1/test_create_export_request_validation.py
- [ ] T015 [US1] Add service tests for create-export workflow and queued status initialization in tests/us1/test_create_export_service.py
- [ ] T016 [US1] Add API integration test for POST export request success and authorization failure in tests/us1/test_create_export_api.py

### Implementation (US1)

- [ ] T017 [US1] Implement CreateExportRequest schema with date range, actor type, and action category filters in services/audit_export/api/schemas/create_export_request.py
- [ ] T018 [US1] Implement export creation service that persists ExportJob and initial audit event in services/audit_export/services/create_export_service.py
- [ ] T019 [P] [US1] Implement Celery enqueue adapter for export generation jobs in services/audit_export/queue/export_tasks.py
- [ ] T020 [US1] Implement POST /v1/audit-exports endpoint wiring authz, validation, and queue dispatch in services/audit_export/api/routes/export_requests.py
- [ ] T021 [US1] Implement worker entrypoint task to transition queued jobs to processing in services/audit_export/workers/process_export_job.py

## Phase 4: User Story 2 - Track Export Progress And Completion (Priority P2)

Goal: A compliance admin can view job status and progress for long-running exports.

Independent Test: Create an export job, simulate worker updates, and verify status endpoint reflects queued, processing, completed, and failed states.

### Tests (US2)

- [ ] T022 [US2] Add status transition tests for queued, processing, completed, and failed states in tests/us2/test_export_status_transitions.py
- [ ] T023 [US2] Add API integration tests for GET export status and not-found handling in tests/us2/test_export_status_api.py

### Implementation (US2)

- [ ] T024 [US2] Implement progress update methods and guarded state transitions in services/audit_export/services/export_status_service.py
- [ ] T025 [US2] Implement GET /v1/audit-exports/{job_id} endpoint for status and progress fields in services/audit_export/api/routes/export_status.py
- [ ] T026 [P] [US2] Implement worker-side progress checkpoints during chunked extraction in services/audit_export/workers/export_chunk_processor.py

## Phase 5: User Story 3 - Download Completed Export Via Time-Limited Link (Priority P3)

Goal: A compliance admin can download a completed export via a signed URL valid for 24 hours, and downloads are audited.

Independent Test: Complete a job, request download link, verify link expiration behavior and audit trail entries for access events.

### Tests (US3)

- [ ] T027 [US3] Add storage adapter tests for signed URL TTL and object key mapping in tests/us3/test_signed_url_generation.py
- [ ] T028 [US3] Add API integration tests for download link retrieval and expiration validation in tests/us3/test_download_link_api.py
- [ ] T029 [US3] Add audit event tests for request-created and download-accessed events in tests/us3/test_export_audit_events.py

### Implementation (US3)

- [ ] T030 [US3] Implement object storage adapter for upload and signed URL generation in services/audit_export/storage/object_storage_adapter.py
- [ ] T031 [US3] Implement worker export writer for CSV and JSON outputs in services/audit_export/workers/export_file_writer.py
- [ ] T032 [US3] Implement GET /v1/audit-exports/{job_id}/download endpoint with 24-hour signed link issuance in services/audit_export/api/routes/export_download.py
- [ ] T033 [US3] Implement download access audit logging in services/audit_export/services/export_audit_service.py

## Phase 6: Polish & Cross-Cutting

- [ ] T034 [P] Add redaction rules to prevent PII fields in export output in services/audit_export/services/export_redaction.py
- [ ] T035 Add retry and dead-letter handling for worker failures in services/audit_export/workers/retry_policy.py
- [ ] T036 [P] Add metrics and alerts for queue depth, failure rate, and export latency in services/audit_export/observability/metrics.py
- [ ] T037 Add end-to-end smoke test for request-to-download happy path in tests/e2e/test_audit_export_happy_path.py
- [ ] T038 Update operational runbook and API usage docs in docs/audit-export-service.md

## Dependencies & Execution Order

1. Complete Phase 1 before starting any foundational or story work.
2. Complete Phase 2 before starting user story phases.
3. Implement user stories in priority order: US1 -> US2 -> US3.
4. US2 depends on US1 job creation and queue wiring.
5. US3 depends on US1 job creation and US2 completion status reporting.
6. Polish tasks start after core functionality from US1-US3 is merged.

## Parallel Opportunities

- In Phase 2, T010 and T011 can run in parallel after migrations are defined.
- In US1, T019 can run in parallel with T017 and T018 once request schema is agreed.
- In US2, T026 can run in parallel with T024 after status model fields are finalized.
- In Polish, T034 and T036 can run in parallel while T035 is implemented.

## Implementation Strategy

1. Deliver MVP by completing US1 first so compliance admins can submit export jobs.
2. Add visibility with US2 status tracking to support long-running operations.
3. Add secure retrieval with US3 signed downloads and complete audit logging.
4. Finish with reliability, observability, and documentation polish.
