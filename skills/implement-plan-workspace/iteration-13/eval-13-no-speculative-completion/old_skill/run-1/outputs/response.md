## Phase Execution

Task `T006` — Implement CSV export in `src/export/csv.ts`
- Verification run:
  - `npm run build` → PASS
  - `npm test -- tests/export/csv.test.ts` → FAIL
- Failing tests:
  - `Expected header row to include column Timestamp`
  - `Expected delimiter to be semicolon for EU locale`

`tasks.md` update
- Leave `T006` as `[ ]`
- Do not mark `T006` as `[X]`

Phase status
- Verification failed, so this task is not complete.
- Because `T006` is a sequential Core-phase task, the phase stops here.
- Next action: fix the CSV export behavior, rerun the failing test file, and only mark `T006` `[X]` after the tests pass.
