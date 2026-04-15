# Implement Plan — Core Phase, Task T005

## Phase Execution — Core

### Task T005: Implement full-text search endpoint in `src/api/search.ts`

**Status: `[ ]` — FAILED VERIFICATION (build error)**

I wrote the implementation for the full-text search endpoint in `src/api/search.ts`. Running the required verification step for a code implementation task:

```
$ npm run build
```

**Build failed.** TypeScript compiler output:

```
src/api/search.ts:42:
  error TS2345: Argument of type 'string' is not assignable to parameter of type 'SearchQuery'
```

#### Error Analysis

Line 42 in `src/api/search.ts` passes a raw `string` to a function that expects a `SearchQuery` typed parameter. This is a type mismatch — the raw query string from the request needs to be wrapped in or converted to a `SearchQuery` object before being passed to the search function.

Likely fix: construct a `SearchQuery` instance from the raw string, e.g.:

```typescript
// Instead of:
const results = await searchIndex(query);    // query is string

// Use:
const results = await searchIndex({ text: query } as SearchQuery);
// or use the appropriate SearchQuery constructor/factory from the codebase
```

The exact fix depends on how `SearchQuery` is defined (check `src/types/` or the module exporting `SearchQuery` for its shape).

#### Task Status Decision

Per the skill's **"verify then mark"** rule for code implementation tasks:

> **Verification:** Build/compile/lint the changed files, then run related tests.
> **What counts as success:** No errors from build/lint, and any pre-existing tests for the touched code pass.

The build **failed** — verification did not pass. Per the skill rules:

> **Never mark speculative completion.** If a task hit errors that you worked around, partially completed, or deferred for later — it stays `[ ]`.

**T005 stays `[ ]` in `tasks.md`.** It is NOT marked `[X]`.

#### tasks.md Update

The task line in `tasks.md` remains unchanged:

```markdown
- [ ] T005 · Implement full-text search endpoint in `src/api/search.ts` → `src/api/search.ts`
```

No checkbox is flipped. The task retains its `[ ]` status.

#### Error Recovery Action

Per the skill's error recovery protocol for non-parallel tasks:

> Report the failure with context (error message, file, what was attempted). Leave the task as `[ ]` in `tasks.md` — do not mark it `[X]`. For non-parallel tasks, halt the phase and suggest concrete next steps.

**⛔ Core phase HALTED at T005.**

### Concrete Next Steps

1. **Fix the type error** — Inspect the `SearchQuery` type definition (likely in a types or models file). Update line 42 of `src/api/search.ts` to construct a proper `SearchQuery` from the raw string input rather than passing the string directly.
2. **Re-run verification** — After the fix, run `npm run build` again. If the build passes, run the related tests for the search endpoint.
3. **Mark complete only on clean verification** — Only flip T005 to `[X]` after both the build and tests pass cleanly.
4. **Resume phase** — Once T005 passes verification, continue with the next task in the Core phase.

---

### Checkpoint Decision (Core Phase — Partial)

```
Checkpoint Decision
- Status: FAIL
- Evidence: T005 failed build verification — TS2345 type error in src/api/search.ts:42.
  Core phase halted; tasks after T005 have not been attempted.
- Integrity check: No [X] tasks reverted (T005 was never marked [X]).
- Next Action: Resolve the type error in T005, re-verify, then resume Core phase execution.
```
