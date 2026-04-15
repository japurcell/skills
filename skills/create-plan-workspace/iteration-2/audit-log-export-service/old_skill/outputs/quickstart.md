# Quickstart: Audit Log Export Service

## Prerequisites

- Node.js 20+
- Redis running locally on port 6379
- Object storage credentials available via environment variables
- Access to an account with `compliance_admin` role in test environment

Example setup commands:

```bash
cd /home/adam/.agents/skills/create-plan-workspace/iteration-2/audit-log-export-service
mkdir -p backend frontend
cd backend && npm init -y
npm install express bullmq zod @aws-sdk/client-s3 @aws-sdk/s3-request-presigner
npm install -D vitest supertest typescript tsx @types/express @types/node
```

Expected outcome: backend scaffold exists with dependencies for API, worker queue, validation, and tests.

## Implement

1. Build admin API endpoints:

```bash
# create backend endpoint modules
mkdir -p backend/src/api/admin backend/src/services backend/src/models backend/src/workers
```

- Implement `POST /admin/audit-exports` to validate filters, enforce `compliance_admin`, create queued job, and return job id in under 500ms.
- Implement `POST /admin/audit-exports/:id/cancel` to cancel only queued/running jobs.
- Implement `GET /admin/audit-exports/:id` to expose status and progress.

2. Implement worker processing:

```bash
# run worker during development
cd backend
npx tsx src/workers/audit-export-worker.ts
```

- Pull queued jobs from Redis.
- Stream audit rows in batches, apply PII allowlist projection, write CSV and JSON artifacts to object storage.
- Record progress and terminal state.

3. Implement frontend form and status view:

```bash
mkdir -p /home/adam/.agents/skills/create-plan-workspace/iteration-2/audit-log-export-service/frontend/src/{components,pages,services}
```

- Add filters for date range, actor type, action category.
- Show asynchronous status progression and download links for completed jobs.

Expected outcome: compliance admins can submit an export and monitor job states from UI.

## Validate

Run API and worker tests:

```bash
cd /home/adam/.agents/skills/create-plan-workspace/iteration-2/audit-log-export-service/backend
npm test
```

Run focused integration checks (example):

```bash
npx vitest run tests/integration/audit-exports.api.test.ts
```

Manual endpoint validation (example request):

```bash
curl -X POST http://localhost:3000/admin/audit-exports \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <compliance-admin-token>' \
  -d '{"dateFrom":"2026-01-01T00:00:00Z","dateTo":"2026-03-31T23:59:59Z","actorType":"user","actionCategory":"auth"}'
```

Expected outcomes:

- Request returns 202 with `jobId` and initial `queued` status.
- Worker transitions job through `running` to `completed` or `failed`.
- Completed jobs expose both CSV and JSON download links expiring after 24 hours.
- Non-admin token receives 403 for export and cancel endpoints.

## Rollout/Operate

1. Deploy backend API and worker with shared configuration (`REDIS_URL`, object storage bucket, signing key settings).
2. Apply alerting:

- Queue backlog threshold alerts.
- Job failure-rate alert at 0.5% rolling window.
- Export latency and completion SLO dashboards.

3. Operational runbook:

- Use cancel endpoint for stuck jobs.
- Review dedicated export audit stream daily for access traceability.
- Purge or archive expired export objects per retention policy.

Expected outcome: production service meets compliance traceability requirements and non-functional targets while maintaining controlled operational behavior.
