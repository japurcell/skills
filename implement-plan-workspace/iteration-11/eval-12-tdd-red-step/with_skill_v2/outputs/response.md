# Phase Execution — Tests Phase

## Task T003: Write unit tests for JWT token validation

**File:** `tests/auth/jwt.test.ts`

Wrote 4 test cases covering JWT token validation:

1. Valid token decodes and returns expected payload
2. Expired token throws `TokenExpiredError`
3. Malformed token throws `InvalidTokenError`
4. Token with wrong signing key throws `SignatureVerificationError`

### Verification

**Task type:** TDD test writing (RED step)

Running the new tests:

```
$ npm test -- tests/auth/jwt.test.ts
```

**Result:** All 4 tests fail.

```
FAIL  tests/auth/jwt.test.ts
  ✕ valid token decodes and returns expected payload
    Error: Cannot find module 'src/auth/jwt'
  ✕ expired token throws TokenExpiredError
    Error: Cannot find module 'src/auth/jwt'
  ✕ malformed token throws InvalidTokenError
    Error: Cannot find module 'src/auth/jwt'
  ✕ token with wrong signing key throws SignatureVerificationError
    Error: Cannot find module 'src/auth/jwt'

Tests: 4 failed, 4 total
```

### Task status decision

**Marking T003 as `[X]` — COMPLETE.** Reasoning:

This is a **TDD test writing (RED step)** in the **Tests phase**, executed before the Core phase where `src/auth/jwt` will be implemented. The skill's verification criteria for this task type states:

> *Tests fail for the intended reason — a clean RED result. In TDD-first (Tests phase before Core), module-not-found errors are expected and count as clean RED because the implementation doesn't exist yet. A test that errors out due to syntax problems in the test file itself is not a clean RED.*

Applying the criteria:

| Check | Result |
|---|---|
| Tests were run | ✓ All 4 tests executed |
| Tests fail (not pass) | ✓ 4 failed, 0 passed |
| Failure reason is intentional | ✓ `Cannot find module 'src/auth/jwt'` — module-not-found |
| Module-not-found in Tests phase before Core | ✓ Explicitly documented as expected clean RED |
| No syntax errors in the test file itself | ✓ All 4 tests loaded and ran; failures are import-resolution errors, not test syntax problems |

This is a **clean RED result**. The tests correctly import from the module that will be created in the Core phase, and they fail precisely because that module doesn't exist yet — which is the entire point of the TDD RED step. The test file itself is syntactically valid and structurally correct.

Updating `tasks.md`:

```diff
-- [ ] T003: Write unit tests for JWT token validation in tests/auth/jwt.test.ts
+- [X] T003: Write unit tests for JWT token validation in tests/auth/jwt.test.ts
```

> **T003** ✅ — Clean RED. 4 tests fail with module-not-found (expected — implementation comes in Core phase).

Proceeding to next task in Tests phase.
