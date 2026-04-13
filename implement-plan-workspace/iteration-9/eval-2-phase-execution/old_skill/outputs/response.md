# Phase Execution Handoff: Tests Phase

## Context
**Plan:** `.agents/scratchpad/feature-notify/plan.md`  
**Phase:** Tests (Phase 2 of 5)  
**Prerequisite:** Setup phase PASSED

---

## Tasks Summary

| Task ID | Title | Files | Parallel? | Status |
|---------|-------|-------|-----------|--------|
| `test-unit-notify` | Unit tests for notification module | `src/notify/notify.test.ts` | [P] | pending |
| `test-integration-db` | Database integration tests | `src/db/integration.test.ts`, `src/notify/handlers.ts` | ✗ | pending |
| `test-e2e-notify` | End-to-end notification flow | `tests/e2e/notify.spec.ts`, `src/notify/notify.ts` | [P] | pending |

---

## Execution Plan

### Parallel Tasks (no file overlap)
- **`test-unit-notify`**: Unit tests for notification module
  - Files touched: `src/notify/notify.test.ts`
  - Command: `npm run test -- src/notify/notify.test.ts`

- **`test-e2e-notify`**: End-to-end notification flow
  - Files touched: `tests/e2e/notify.spec.ts`, `src/notify/notify.ts`
  - Command: `npm run test:e2e -- tests/e2e/notify.spec.ts`

### Sequential Tasks (blocked by parallel completion)
- **`test-integration-db`**: Database integration tests
  - Files touched: `src/db/integration.test.ts`, `src/notify/handlers.ts`
  - Depends on: Parallel tasks completion
  - Command: `npm run test -- src/db/integration.test.ts`
  - Note: `src/notify/handlers.ts` overlaps with `test-unit-notify`; execute after parallel phase

---

## Checkpoint Criteria

```
Checkpoint Decision
- Status: [PASS | PASS WITH DEFERRED ITEMS | FAIL]
- Evidence: 
  - [X] test-unit-notify completed (100% assertions passing)
  - [X] test-e2e-notify completed (all scenarios verified)
  - [X] test-integration-db completed (database seeding/teardown validated)
  - [X] tasks.md updated with [X] markers for completed tests
  - [X] Coverage threshold met (>80% for notify module)
  - [ ] Deferred: <any test marked for deferral with reason>
- Blockers: <none identified | specific error chains>
- Next Action: 
  - If PASS: Advance to Core phase
  - If PASS WITH DEFERRED: Document deferments in tasks.md, advance with approval
  - If FAIL: Halt phase, resolve test failures before advancing
```

---

## Pre-Execution Handoff Checklist

- [ ] Verify all Setup phase tasks marked `[X]` in tasks.md
- [ ] Confirm dependencies are installed: `npm ci` or `npm install`
- [ ] Confirm test environment variables loaded (`.env.test` present)
- [ ] Database initialized and seeded for integration tests
- [ ] Run all tasks; update tasks.md with `[X]` upon completion
- [ ] After all tasks complete, evaluate checkpoint criteria above
- [ ] If PASS or PASS WITH DEFERRED, proceed to next section

---

## Next Phase Gate

**Do NOT advance to Core phase until:**
1. All checkpoint criteria evaluated above
2. `tasks.md` updated with completion markers
3. Test suite exits with code 0 (all pass)
4. Or explicit user approval for deferred items

---

## Phase Summary Template

Once execution completes, fill this in before checkpoint evaluation:

**Phase:** Tests  
**Completed Tasks:** 3 of 3 (or X of 3 if deferred)  
**Test Results:** [summary: pass/fail/partial]  
**Files Modified:** [list of .test.ts and src/ files changed]  
**Blockers:** [none | specific failures]  
**Deferments:** [none | tasks deferred with reason]  

---

## References

- **Skill:** `/implement-plan` v2
- **Workflow:** Phase-by-phase execution with TDD-first delivery
- **Rules:** Sequential tasks halt phase on failure; parallel tasks continue if independent
