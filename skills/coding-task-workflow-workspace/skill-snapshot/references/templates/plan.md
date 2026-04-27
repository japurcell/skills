---
work_id: WORK_ID
phase: plan
status: draft | approved
updated_at: ISO8601_TIMESTAMP
depends_on: [clarification]
---

# Implementation Plan: TITLE

## Goal / Non-Goals

**Goal**: One sentence describing what this plan delivers.
**Goal**: *(additional goals if needed)*

**Non-goal**: What this plan intentionally does not cover.
**Non-goal**: *(additional non-goals if needed)*

## Recommended Approach

One to three paragraphs describing the implementation approach and why it is the best fit for this codebase given the findings from exploration and research.

## Alternatives Considered

*(Omit this section if no meaningful trade-off exists.)*

**Alternative A — [Name]**
- Description.
- Why not chosen: reason.

**Alternative B — [Name]**
- Description.
- Why not chosen: reason.

## File-by-File Implementation Map

| File | Change |
|------|--------|
| `src/example/retry.ts` | Create new file: retry policy implementation |
| `src/example/client.ts` | Modify: integrate retry policy |
| `src/example/retry.test.ts` | Create new file: tests for retry policy |
| `src/example/client.test.ts` | Modify: add integration tests |

## Verification Guidance

**Test commands**:
```
npm test -- --testPathPattern=retry
npm test -- --testPathPattern=client
npm test -- --watchAll=false
```

**Manual checks**:
- Verify that a 500 response triggers a retry.
- Verify that a 200 response on the second attempt succeeds.
- Verify that the retry count is logged at DEBUG level.

**Acceptance criteria mapping**:
| Criterion | Verified by |
|-----------|------------|
| Criterion 1 | TestName in retry.test.ts |
| Criterion 2 | TestName in client.test.ts |

## Revision History

*(Added when plan is revised after initial draft.)*

| Revision | Date | Change |
|----------|------|--------|
| 1.0 | YYYY-MM-DD | Initial draft |
| 1.1 | YYYY-MM-DD | Added max-elapsed-time constraint per human feedback |
