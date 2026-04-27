## Automated Checks

| Command | Exit code | Notes |
|---------|-----------|-------|
| `TEST_COMMAND` | 0 | N tests, 0 failures |
| `LINT_COMMAND` | 0 | No new warnings |
| `TYPECHECK_COMMAND` | 0 | No errors |
| `BUILD_COMMAND` | 0 | Build successful |

## Acceptance Criteria

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | Criterion text from the intake issue | pass | TestName: PASS |
| 2 | Criterion text | pass | Manual check: description |
| 3 | Criterion text | pass | TestName: PASS |

## Review Clearance

| Review type | High findings | Status |
|-------------|--------------|--------|
| Code review | 0 | Cleared |
| Security review | 0 | Cleared |
| Tech-debt review | 0 | Cleared |

## Limitations

*(Omit this section if none.)*

- Description of any verification that could not be performed and why.

## Machine Data

```yaml
work_id: WORK_ID
kind: phase
phase: verify
status: open
depends_on:
  - review
all_criteria_pass: false
```
