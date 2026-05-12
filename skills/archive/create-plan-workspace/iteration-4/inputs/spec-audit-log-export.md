# Feature Spec: Audit Log Export Service

## Problem

Compliance team needs quarterly exports of audit logs, but current process requires engineering to run ad hoc SQL scripts.

## Goals

- Provide self-service export of audit events by date range and actor type.
- Ensure exports are access controlled and traceable.

## Requirements

1. Add UI form with filters: date range, actor type, action category.
2. Export generated as CSV and JSON, with download links valid for 24 hours.
3. Exports are asynchronous jobs with progress states (`queued`, `running`, `failed`, `completed`).
4. Only users in `compliance_admin` role can request exports.
5. Log each export request and download event to a dedicated audit stream.
6. Add admin endpoint for cancelling stuck jobs.

## Non-Functional

- Handle datasets up to 5 million records.
- Export initiation must return in under 500ms.
- Background job failure rate target under 0.5%.

## Constraints

- Existing queue system is Redis + worker service.
- Storage is object storage with signed URLs.
- System must avoid exposing PII fields in exports.
