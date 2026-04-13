# TDD-First Task Ordering in Core Phase

## Checklist Gate

✓ **PASS** — All checklists passed. Proceeding with implementation.

## Implementation Context Loaded

**Plan File:** `.agents/scratchpad/feature-api/plan.md`

**Artifacts:**
- plan.md — Feature specification and technical approach
- tasks.md — Phase breakdown with T007 and T008
- Feature Directory: `.agents/scratchpad/feature-api/`

## Phase Execution: Core Phase

### Task Overview

**Core Phase Tasks:**
- **T007** (Test Task): Write API endpoint tests in `tests/api_test.py`
- **T008** (Implementation Task): Implement API endpoint in `src/api/routes.py`

**Declared Status:** Both tasks are sequential in the Core phase.

### Execution Plan & TDD-First Ordering

#### Key Principle: TDD-First Within Phases

Per the **implement-plan** skill specification (section 4, "Execute phases"):

> **TDD-first:** Within each phase, run test tasks before their corresponding implementation tasks. Writing tests first clarifies intent and catches regressions immediately. When a test task and its implementation counterpart are both in the same phase, the test runs first regardless of task ID ordering.

#### Ordering Decision

Despite both T007 and T008 being sequential tasks in declared order, the TDD-first principle **reorders their execution** within the Core phase:

**Execution Sequence:**
1. **T007 (Test) — EXECUTE FIRST**
   - Task: Write API endpoint tests in `tests/api_test.py`
   - Rationale: Tests clarify the expected API contract before implementation begins
   - Benefit: Implementation work in T008 targets a clear, test-driven specification

2. **T008 (Implementation) — EXECUTE SECOND**
   - Task: Implement API endpoint in `src/api/routes.py`
   - Rationale: Implementation follows tests, ensuring each line of code is verified by an existing test
   - Benefit: Catches regressions immediately and validates the implementation meets its contract

### Reasoning

**Why Test-First:**

1. **Specification Clarity** — Tests define what the API endpoint must do (input, output, error cases) before code is written.

2. **Regression Detection** — As the endpoint is implemented, all tests run automatically. Any behavior that deviates from the test specification is caught immediately.

3. **Design Guidance** — Writing tests first forces thoughtful API design. The test author considers edge cases, error handling, and usability before the implementation begins.

4. **Confidence** — Once T008 is complete and all T007 tests pass, there is high confidence the implementation is correct and complete.

### Checkpoint Decision

**Status:** PASS (ready to execute)

**Evidence:**
- T007 and T008 are clearly identified in the Core phase
- T007 touches `tests/api_test.py` (test file)
- T008 touches `src/api/routes.py` (implementation file)
- No file path overlap between test and implementation tasks allows sequential execution without write conflicts
- TDD-first principle has been applied to determine correct ordering

**Next Action:** 
Execute T007 first. Upon completion, mark `[X]` in tasks.md. Then execute T008. Upon completion, mark `[X]` in tasks.md. Both tests must pass before advancing to the Integration phase.

---

## Summary

The **implement-plan** skill ensures TDD-first discipline by:
- Recognizing T007 and T008 are test and implementation counterparts in the same phase
- Reordering execution to run T007 (test) before T008 (implementation) **regardless of task ID**
- Ensuring tests define the contract before implementation begins
- Catching regressions immediately as code is written

This ordering prevents the common pitfall of writing code first and retrofitting tests, instead embedding quality and correctness into the development process from the start.
