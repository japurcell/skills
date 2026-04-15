# Phase Execution — Core

## Task T006: Implement CSV export in `src/export/csv.ts`

### Work performed

- Wrote CSV export implementation in `src/export/csv.ts`
- Build passes ✓
- Ran `npm test -- tests/export/csv.test.ts` — **2 of 5 tests fail** ✗

### Test failures

| # | Test | Error |
|---|------|-------|
| 1 | Header row contents | `Expected header row to include column Timestamp` |
| 2 | EU locale delimiter | `Expected delimiter to be semicolon for EU locale` |

### Status: **FAIL — task NOT marked `[X]`**

T006 cannot be marked complete. The skill rules are clear: a task is marked `[X]` in `tasks.md` only **after it succeeds**, and success requires that existing tests pass. Two tests fail, so the task has not succeeded — regardless of whether the failures look like "edge cases fixable later." There is no partial-completion status; the task either passes or it doesn't.

Deferring known test failures to "fix later" would violate two guarantees:

1. **Task tracking** — checkmarks are the source of truth for resumption. Marking a failing task `[X]` would tell a future run it's done when it isn't.
2. **Phase checkpoints** — the checkpoint after Core would inherit a false PASS, masking real regressions.

### Error recovery (non-parallel task — halt phase)

Since T006 is a non-parallel task in the Core phase, **the phase is halted** pending resolution.

### Concrete next steps

1. **Fix the Timestamp header** — The implementation is likely missing a `Timestamp` column in the header row output. Check the test expectation for the exact column name and ensure the export function includes it.
2. **Fix the EU locale delimiter** — The implementation probably hardcodes `,` as the delimiter. The test expects `;` when an EU locale is active. Add locale-aware delimiter selection (e.g., check a locale parameter or config and use `;` for EU locales).
3. **Re-run tests** — After fixes, run `npm test -- tests/export/csv.test.ts` again. All 5 tests must pass before T006 is marked `[X]` and the Core phase can continue.

Would you like me to proceed with fixing these two failures now?
