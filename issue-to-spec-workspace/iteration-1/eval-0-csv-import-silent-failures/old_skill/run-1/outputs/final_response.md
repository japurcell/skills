issue: acme/platform#142
title: Bulk user import fails silently on CSV rows with trailing commas
readiness: planning-ready (best-effort)

## Problem Statement
Bulk user import currently fails silently when CSV rows contain trailing commas, leading to dropped/invalid records without actionable feedback to users or operators.

## Goals
- Detect and handle trailing-comma row shape anomalies during CSV parsing/import.
- Prevent silent failure modes.
- Provide clear, row-level error reporting to UI/API callers.
- Preserve successful imports for valid rows when partial-failure policy allows.

## Non-Goals
- Redesigning the entire CSV import architecture.
- Supporting arbitrary malformed CSV beyond explicit trailing-comma handling.
- Changing unrelated user validation rules.

## Scope
- CSV ingestion/parser layer used by bulk user import.
- Import validation and error aggregation.
- API/service response contract for import results.
- UI/operator-visible feedback (if currently available in this flow).
- Observability for import failures (logs/metrics).

## Functional Requirements
1. The import flow must detect rows with trailing commas that cause column-count mismatch or empty terminal fields.
2. The system must not fail silently; every rejected row must produce a structured error entry.
3. The response must include:
   - total rows processed
   - successful rows count
   - failed rows count
   - per-row error details (row number, error code/message)
4. If partial success is supported, valid rows should still import while invalid rows are reported.
5. If all rows are invalid, the import should return an explicit failure status and diagnostics.
6. Error messages must be understandable to non-technical users and actionable (for example: "Row 12 has an extra trailing comma").

## Data/Validation Rules
- Row schema width must match expected column count after parsing.
- Trailing delimiters that create extra empty columns must be treated as invalid row format unless explicitly allowed by schema.
- Empty optional fields are valid only when represented within expected column count.

## API/Contract Expectations
- Import endpoint/service returns deterministic status for success/partial/failure.
- Row-level errors include stable machine-readable code and human-readable message.
- Existing consumers should not break; if contract changes, include versioning or backward-compatible fields.

## Observability
- Emit structured logs with import id and row failure counts.
- Add metric(s) for malformed CSV rows and silent-failure prevention path.
- Alerting thresholds are optional but recommended for spike detection.

## Acceptance Criteria
- Given a CSV with at least one row containing trailing commas, when import runs, then those rows are reported as failed with row-specific errors.
- Given mixed valid/invalid rows, when import runs, then valid rows import successfully and invalid rows are returned in error report.
- Given only invalid rows with trailing commas, when import runs, then no silent success is returned; explicit failure/zero-success response is returned.
- Given a fully valid CSV, behavior remains unchanged from current successful path.

## Test Plan
- Unit tests:
  - Parser detects trailing-comma-induced extra columns.
  - Validation maps parser anomaly to stable error code.
- Integration tests:
  - End-to-end import returns row-level diagnostics.
  - Partial success behavior for mixed datasets.
- Regression tests:
  - Valid CSV imports unaffected.

## Risks
- Existing clients may rely on prior ambiguous success/failure signals.
- CSV library behavior around delimiters/quotes may differ from assumptions.

## Open Questions
- Should trailing commas ever be auto-trimmed instead of rejected?
- What is the canonical partial-success status code/shape today?
- Are row numbers 1-based including header or data-only indexing?

## Assumptions
- GitHub issue comments were unavailable at run time due repository resolution failure; no comment-derived conflicts could be reconciled.
- Current import flow supports (or can be updated to support) row-level diagnostics.
- Header schema is fixed and known at import time.

## Implementation Checklist
- Add/confirm parser guard for trailing-comma row-width mismatch.
- Add structured row error model and stable error code.
- Ensure API response includes aggregate + row-level results.
- Update UI/error presentation for import feedback.
- Add logging/metrics.
- Add tests (unit/integration/regression) for malformed and mixed CSV inputs.
