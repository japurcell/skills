# Quickstart: Audit Log Export Service

## Prerequisites

- Access to the target product repository that contains the admin UI, API service, worker service, and deployment tooling.
- A test account with the `compliance_admin` role.
- Connectivity to the existing Redis queue, audit-event source store, and object-storage bucket used by the product.
- Environment variables or secrets configured for object-storage signing and dedicated audit-stream publishing.
- A reviewed export-field allowlist ready for implementation, based on the `ExportFieldPolicy` decision in `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-1/old_skill/run-1/outputs/data-model.md`.

## 1. Implement

1. Add export-job persistence and lifecycle fields from `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-1/old_skill/run-1/outputs/data-model.md`.

```bash
./scripts/db/migrate up audit_export_jobs
```

Expected outcome: The product database contains durable export-job and artifact metadata with explicit states, heartbeat fields, and 24-hour expiry metadata for completed jobs.

2. Implement the admin API contract from `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-1/old_skill/run-1/outputs/contracts/audit-export-api.yaml` and enforce the `compliance_admin` role server-side.

```bash
./scripts/dev/run-api.sh
curl -sS -X POST http://localhost:8080/admin/audit-exports \
  -H 'Content-Type: application/json' \
  -H 'X-Role: compliance_admin' \
  -d '{"dateFrom":"2026-01-01","dateTo":"2026-03-31","actorType":"human","actionCategory":"auth"}'
```

Expected outcome: The API responds with `202 Accepted` in under 500ms and returns an export-job ID with status `queued`; unauthorized roles receive `403` and a denied audit event.

3. Implement worker-side chunked export generation, artifact storage, and audit event publishing from `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-1/old_skill/run-1/outputs/research.md` decisions 3, 5, and 7.

```bash
./scripts/dev/run-worker.sh
```

Expected outcome: The worker claims queued jobs, updates progress on each batch, writes both CSV and JSON artifacts, sets `download_expires_at = completed_at + 24h`, and emits dedicated request/download/cancel/failure audit events.

## 2. Validate

1. Run the narrowest automated test suite covering authorization, field allowlisting, lifecycle transitions, and cancellation.

```bash
./scripts/test/run.sh --suite audit-export
```

Expected outcome: Tests pass for role enforcement, PII-safe serialization, valid job state transitions, expiry behavior, and cooperative cancellation of queued/running jobs.

2. Validate status, cancellation, and signed-download behavior against a local or staging deployment.

```bash
curl -sS http://localhost:8080/admin/audit-exports/<EXPORT_ID> -H 'X-Role: compliance_admin'
curl -sS -X POST http://localhost:8080/admin/audit-exports/<EXPORT_ID>/cancel -H 'X-Role: compliance_admin'
curl -sS http://localhost:8080/admin/audit-exports/<EXPORT_ID>/downloads/csv -H 'X-Role: compliance_admin'
```

Expected outcome: Status responses show only valid transitions, the cancel endpoint works only for queued/running jobs, completed jobs return signed download URLs, and expired jobs return the configured terminal response.

3. Validate audit-stream coverage from `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-1/old_skill/run-1/outputs/contracts/audit-export-audit-stream.json`.

```bash
./scripts/ops/check-audit-stream.sh audit_export
```

Expected outcome: Accepted and denied requests, download events, cancellations, and failures all appear in the dedicated audit stream with export-job IDs and actor metadata.

## 3. Rollout/Operate

1. Deploy API and worker changes together so job-state and artifact behavior stay in sync.

```bash
./scripts/deploy/deploy-audit-export.sh
```

Expected outcome: Export initiation remains under the 500ms target, the queue remains healthy under load, and operational metrics/alerts track job latency, stuck-job count, and failure rate below 0.5%.

2. Run a compliance smoke check using a production-like dataset.

```bash
./scripts/ops/smoke-audit-export.sh
```

Expected outcome: Both CSV and JSON artifacts are produced, the field allowlist prevents PII leakage, links expire after 24 hours, and the dedicated audit stream contains the expected request/download trace events.
