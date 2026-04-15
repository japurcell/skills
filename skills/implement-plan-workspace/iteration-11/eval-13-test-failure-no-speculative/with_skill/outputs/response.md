# Phase Execution — Core

## Task T006: Implement CSV export in `src/export/csv.ts`

**Implementation:** ✅ Code written in `src/export/csv.ts`
**Build:** ✅ Build passes — no compile or lint errors

**Verification — running related tests:**

```
npm test -- tests/export/csv.test.ts
```

```
Results: 3 passed, 2 failed, 5 total

FAIL: Expected header row to include column Timestamp
FAIL: Expected delimiter to be semicolon for EU locale
```

### Task Status: ❌ NOT MARKED DONE — stays `[ ]`

**T006 remains `[ ]` in `tasks.md`. I am not marking it `[X]`.**

The build passes, but 2 of 5 pre-existing tests fail. The skill's verification criteria for a code implementation task require:

> No errors from build/lint, **and any pre-existing tests for the touched code pass**

Both failing tests are pre-existing tests in `tests/export/csv.test.ts` that exercised the code I just wrote. They are not passing. It does not matter that these look like edge cases that could be "fixed later" — the skill is explicit:

> **Never mark speculative completion.** If a task hit errors that you worked around, partially completed, or deferred for later — it stays `[ ]`. Only clean, verified outcomes earn the checkmark.

A `[X]` in `tasks.md` is a permanent promise that the task is done and verified. Marking it now would corrupt the resumption state — the next run would skip T006 and build on a broken foundation.

### Error Recovery

**Failure context:**

| Test | Error | Likely cause |
|------|-------|-------------|
| `Expected header row to include column Timestamp` | Header row generation does not include a `Timestamp` column | The CSV header builder may be filtering or missing time-based fields |
| `Expected delimiter to be semicolon for EU locale` | Delimiter is `,` when locale indicates `;` | Locale-aware delimiter logic is missing or not wired up |

**Phase halted.** Per the error recovery rule for non-parallel tasks: the Core phase cannot advance until T006 passes verification.

### Suggested Next Steps

1. **Fix the Timestamp header issue** — inspect the test expectation to see which columns are required, then ensure the header row in `src/export/csv.ts` includes `Timestamp` (check if the column name is coming from a schema or config).
2. **Fix the EU locale delimiter** — the test expects `;` as the delimiter for EU locales. Add or correct the locale-aware delimiter selection logic (likely a branch on locale settings that defaults to `,` but uses `;` for locales like `de-DE`, `fr-FR`, etc.).
3. **Re-run all 5 tests** — once both fixes are applied, re-run `npm test -- tests/export/csv.test.ts`. All 5 must pass before T006 can be marked `[X]`.

I will proceed to fix these two issues now before attempting to advance the phase.
