# Data Model: Audit Log Export Service

## Entities

### AuditExport (Job entity)

| Field | Type | Required | Constraints | Notes |
|-------|------|----------|-------------|-------|
| id | UUID | ✓ | Unique | Primary key |
| user_id | String | ✓ | FK to users | Who requested export |
| status | Enum | ✓ | {queued, running, failed, completed} | Job state |
| format | Enum | ✓ | {csv, json} | Export format (may have multiple per job) |
| filters | JSON | ✓ | Non-empty | date_range {start, end}, actor_type, action_category |
| record_count | Integer | ✓ (after run) | ≥0 | Number of records in result |
| file_size_bytes | Integer | ✓ (after run) | ≥0 | Bytes of generated export |
| download_url | String | (after completion) | Expires 24h | Signed object storage URL |
| error_reason | String | (if failed) | Max 500 chars | Human-readable error |
| created_at | Timestamp | ✓ | No future dates | When request submitted |
| started_at | Timestamp | (if started) | ≥created_at | When background job began |
| completed_at | Timestamp | (if terminal) | ≥started_at | When job reached terminal state |
| expires_at | Timestamp | (if completed) | 24h after completion | When signed URL expires |

**Validation Rules**:
- Status transitions: queued → running → (failed | completed)
- Filters.date_range.start ≤ filters.date_range.end
- Status cannot revert to earlier state
- completed_at required when status = completed or failed
- download_url only present when format downloaded

### ExportAuditEntry (Audit trail of exports/downloads)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | Primary key |
| export_id | UUID | FK to AuditExport |
| event_type | Enum | {export_requested, download_started, download_completed, download_expired, job_cancelled} |
| user_id | String | Who performed action |
| timestamp | Timestamp | When event occurred |
| ip_address | String | Network source |
| user_agent | String | Browser/client info |

**Validation Rules**:
- All fields required
- Timestamp must be recent (within last 24h for compliance)

## Relationships
