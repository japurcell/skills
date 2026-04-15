# Phase Execution — Tests Phase

## Task T003: Write unit tests for JWT token validation

**Task:** Write unit tests for JWT token validation in `tests/auth/jwt.test.ts`
**Task type:** TDD test writing (RED step)
**Test cases written:** 4

### Verification

Running the new tests to check for a clean RED result:

```
$ npm test -- tests/auth/jwt.test.ts
```

**Result:** All 4 tests fail with:

```
Error: Cannot find module 'src/auth/jwt'
```

### Status Decision: ❌ NOT marked `[X]` — left as `[ ]`

**Reasoning:** The skill defines a clean RED result as tests that **execute and fail for the intended reason** — meaning the test assertions run and fail because the implementation returns wrong or missing values. It explicitly states:

> *"A test that errors out due to import/syntax problems is not a clean RED."*

A `Cannot find module` error is an **import-time failure**. The test runner crashes before any test body or assertion executes. None of the 4 test cases reached their `expect()` calls — the module resolution failed first. This is categorically an import problem, not an assertion failure, so it does not qualify as a clean RED regardless of whether the missing module is expected in the TDD workflow.

**Task T003 stays `[ ]` in `tasks.md`.** A premature `[X]` here would mean the next resumption run skips this task, building on unverified test scaffolding.

### Remediation — achieving a proper clean RED

To convert this into a clean RED result, create a **minimal stub module** at `src/auth/jwt.ts` that satisfies the import but provides no real implementation:

```typescript
// src/auth/jwt.ts — minimal stub for TDD RED step
export function validateToken(token: string): boolean {
  throw new Error("Not implemented");
}

export function decodeToken(token: string): Record<string, unknown> {
  throw new Error("Not implemented");
}
```

The stub exports the functions the tests import, with bodies that throw or return trivially wrong values. This lets the test runner:

1. Resolve the module import successfully
2. Execute each test body
3. Fail at the assertion level (e.g., `expected true, received false` or `threw "Not implemented"`)

That failure pattern — tests run, assertions fire, results don't match — is a **clean RED**.

### Concrete next steps

1. **Create the stub** at `src/auth/jwt.ts` with the minimum exports that `tests/auth/jwt.test.ts` imports.
2. **Re-run** `npm test -- tests/auth/jwt.test.ts`.
3. **Confirm clean RED:** All 4 tests execute and fail at assertion level (not at import level).
4. **Then mark T003 `[X]`** in `tasks.md` — now the RED step is genuinely verified.
5. Proceed to the corresponding Core phase implementation task for `src/auth/jwt.ts` (the GREEN step), which will replace the stub with real logic.

### Updated tasks.md entry

```markdown
- [ ] T003: Write unit tests for JWT token validation in tests/auth/jwt.test.ts [RED]
```

Task remains unchecked. It will be retried on the next execution pass after the stub is in place.

---

*Phase checkpoint for Tests phase is deferred — T003 is unresolved and blocks checkpoint passage unless the user explicitly approves advancing.*
