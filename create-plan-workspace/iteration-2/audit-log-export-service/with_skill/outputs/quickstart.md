# Quickstart: Audit Log Export Service

## Prerequisites

- Access to the product repository containing API, worker, and admin UI modules.
- Access to Redis queue, object storage bucket, and audit-event source store.
- User account with `compliance_admin` role for end-to-end validation.
- Environment variables configured for object storage signing and audit stream publishing.

## 1. Implement

1. Add/upgrade export-job persistence schema and worker state fields.

```bash
./scripts/db/migrate up
```

Expected outcome: Migration succeeds and a table/model for export jobs supports lifecycle fields (`queued`, `running`, `failed`, `completed`, `cancelled`) plus artifact and expiry metadata.

2. Implement API endpoints and role enforcement from contracts.

```bash
./scripts/dev/run-api.sh
curl -sS -X POST http://localhost:8080/admin/audit-exports \
  -H 'Content-Type: application/json' \
  -H 'X-Role: compliance_admin' \
  -d '{"dateFrom":"2026-01-01","dateTo":"2026-03-31","actorType":"human","actionCategory":"auth"}'
```

Expected outcome: API returns `202 Accepted` in under 500ms with an export request ID and initial status `queued`.

3. Implement worker batch export processing and object storage writes for CSV + JSON.

```bash
./scripts/dev/run-worker.sh
```

Expected outcome: Worker claims queued jobs, updates progress, writes both artifact formats, sets `download_expires_at = completed_at + 24h`, and emits request/completion/failure audit events.

## 2. Validate

1. Run automated tests for authorization, lifecycle, serialization, and cancellation.

```bash
./scripts/test/run.sh --suite audit-export
```

Expected outcome: Tests pass, including role restriction (`compliance_admin` only), PII allowlist serialization checks, and cancellation behavior for stuck jobs.

2. Validate end-to-end API behavior and contract compliance.

```bash
curl -sS http://localhost:8080/admin/audit-exports/<EXPORT_ID> -H 'X-Role: compliance_admin'
curl -sS -X POST http://localhost:8080/admin/audit-exports/<EXPORT_ID>/cancel -H 'X-Role: compliance_admin'
```

Expected outcome: Status endpoint reflects valid state transitions; cancel endpoint returns success for cancellable jobs; unauthorized roles receive denied responses and corresponding audit events.

3. Validate download and expiry window.

```bash
curl -I "http://localhost:8080/admin/audit-exports/<EXPORT_ID>/downloads/csv" -H 'X-Role: compliance_admin'
```

Expected outcome: Response returns a signed URL valid for 24 hours; download action is logged in the dedicated audit stream.

## 3. Rollout/Operate

1. Deploy API and worker changes with metrics/alerts for job latency and failure rate.

```bash
./scripts/deploy/deploy-audit-export.sh
```

Expected outcome: Export initiation remains under 500ms, worker failure rate alert threshold is set below 0.5%, and queue depth monitoring is active.

2. Run compliance smoke check with production-like data sample.

```bash
./scripts/ops/smoke-audit-export.sh
```

Expected outcome: Generated files omit PII fields, both formats are produced, links expire in 24 hours, and request/download events appear in the dedicated audit stream.
