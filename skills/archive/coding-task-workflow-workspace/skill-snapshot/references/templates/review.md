---
work_id: WORK_ID
phase: review
review_type: code | security | tech-debt
status: complete
updated_at: ISO8601_TIMESTAMP
depends_on: [implementation-log]
high_severity_count: 0
---

# Review: REVIEW_TYPE — TITLE

## Summary

- **Files reviewed**: N
- **Findings**: N High, N Medium, N Low, N Info
- **Disposition**: All High findings resolved | N High findings require fixes

---

## Finding 1

- **file**: `src/example/file.ts`
- **lines**: 45–52
- **severity**: High | Medium | Low | Info
- **status**: open | resolved
- **description**: Clear description of the issue found.
- **suggestion**: Concrete fix or improvement.
- **cwe**: CWE-NNN *(security review only — omit for code and tech-debt reviews)*

---

## Finding 2

- **file**: `src/example/file.ts`
- **lines**: 78–80
- **severity**: Low
- **status**: open
- **description**: Description.
- **suggestion**: Suggestion.

---

<!-- Add one entry per finding. High severity findings must be resolved before Gate F. -->
<!-- Low and Medium findings may be deferred as labelled follow-up GitHub issues. -->
