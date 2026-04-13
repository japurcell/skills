# Implementation Plan Execution: Core Phase - TDD Ordering Analysis

## Overview

This document demonstrates the execution plan for the **Core phase** of the feature-api implementation, specifically addressing the ordering and execution strategy for tasks T007 (write API endpoint tests) and T008 (implement API endpoint).

---

## Checklist Gate

**Status**: PASS (Assuming all checklists pass as specified)

- Checklist validation: All items complete
- Gate clearance: Automatic continuation to implementation

---

## Implementation Context Loaded

**Source files**:
- `plan.md` - Feature specification and phasing
- `tasks.md` - Task breakdown with phases, descriptions, dependencies, and markers
- `data-model.md` - Domain model (if present)
- `contracts/` - API/service contracts (if present)

**Core Phase Tasks**:
- **T007**: Write API endpoint tests in `tests/api_test.py`
- **T008**: Implement API endpoint in `src/api/routes.py`

---

## Phase Execution: Core Phase

### Task Analysis

#### T007: Write API endpoint tests in tests/api_test.py

**Type**: Sequential task (follows TDD-first principle)
**Dependency**: None (foundation task)
**Touched files**: `tests/api_test.py`
**TDD Requirement**: YES - Write tests FIRST before implementation
**Execution Order**: 1st (MUST run before T008)

#### T008: Implement API endpoint in src/api/routes.py

**Type**: Sequential task
**Dependency**: T007 must be complete
**Touched files**: `src/api/routes.py`
**TDD Requirement**: YES - Implementation guided by passing T007 tests
**Execution Order**: 2nd (depends on T007 completion)

---

## Execution Plan Rationale

### Why T007 Must Execute First: TDD-First Ordering

The ordering of T007 → T008 enforces **Test-Driven Development (TDD)** methodology, which the implement-plan skill strictly applies:

#### 1. **File Path Non-Overlap**
- T007 writes to: `tests/api_test.py`
- T008 writes to: `src/api/routes.py`
- **Result**: These can only run sequentially (different file paths), not in parallel

#### 2. **Logical Dependency Chain**
- **T007 (Write Tests First)**:
  - Task: Create comprehensive test suite for the new API endpoint
  - Inputs: API specification from `plan.md`, expected contracts from `contracts/`
  - Output: Failing tests that define expected behavior
  - Checkpoint: All tests defined and runnable (RED phase)
  
- **T008 (Implement Endpoint)**:
  - Task: Write implementation code to make T007 tests pass
  - Inputs: Test definitions from T007, API specification
  - Output: Implementation that satisfies all tests
  - Checkpoint: All T007 tests passing (GREEN phase)

#### 3. **Red-Green-Refactor Cycle**
```
[RED]         [GREEN]       [REFACTOR]
T007 writes   T008 passes   (Optional optimization
failing       all tests     in T008 or later phase)
tests
```

### Sequential Execution Workflow

```
START CORE PHASE
    ↓
TASK T007: Write API endpoint tests
    ├─ Read API specification from plan.md
    ├─ Create tests/api_test.py with comprehensive test cases
    ├─ Execute test suite → ALL FAIL (RED state - expected)
    ├─ Update tasks.md: Mark T007 as [X]
    └─ Checkpoint: Tests written, RED state achieved
       Status: PASS (T007 complete)
    ↓
TASK T008: Implement API endpoint (UNBLOCKED - T007 complete)
    ├─ Read T007 test definitions from tests/api_test.py
    ├─ Implement endpoint logic in src/api/routes.py
    ├─ Execute test suite → ALL PASS (GREEN state - expected)
    ├─ Update tasks.md: Mark T008 as [X]
    └─ Checkpoint: Implementation complete, GREEN state achieved
       Status: PASS (T008 complete)
    ↓
CORE PHASE CHECKPOINT
    ├─ Evidence:
    │  ├─ Tasks completed: T007 ✓, T008 ✓
    │  ├─ Files changed: tests/api_test.py, src/api/routes.py
    │  ├─ Tests run: All T007 tests passing after T008 completion
    │  ├─ No blockers or deferred items
    │  └─ tasks.md synchronized with completion markers
    ├─ Status: PASS
    └─ Next Action: Advance to Integration phase
    ↓
END CORE PHASE
```

---

## Parallelization Analysis

### Why These Tasks CANNOT Be Parallelized

The implement-plan skill applies this rule (from workflow step 6):
> "`[P]` tasks may run in parallel only when their touched file paths do not overlap."

**Analysis**:

1. **T007** and **T008 are both SEQUENTIAL tasks** (not marked `[P]`)
   - Indicated in `tasks.md` as sequential entries in Core phase
   - Sequential tasks "must run in order" (workflow step 6)

2. **Even if marked parallel**, they would fail the overlap test:
   - T007 → `tests/api_test.py`
   - T008 → `src/api/routes.py`
   - No file overlap, but **logical dependency** overrides parallel execution
   
3. **TDD Dependency Requirement**:
   - T007 produces the contract/specification (test cases)
   - T008 consumes that contract (must read T007 tests)
   - This is a **strong sequential dependency**, not optional

### Conclusion on Ordering

The implement-plan skill MUST enforce this ordering:

```
T007 (SEQUENTIAL) → T008 (SEQUENTIAL)
     write tests      write code
    [RED phase]     [GREEN phase]
```

**Cannot defer, reorder, or parallelize** because:
- ✓ Different files (no file conflicts)
- ✗ Logical TDD dependency (T008 requires T007 output)
- ✗ Both marked sequential in tasks.md
- ✗ TDD-first mandate requires RED before GREEN

---

## Code Review Scope

After Core phase completion, code review would include:
- **Changed files**: `tests/api_test.py`, `src/api/routes.py`
- **Review scope**: 2 files
- **Reviewers**: 
  - Code-simplifier agent (clarity and DRY)
  - 3 Code-reviewer agents (bugs, conventions, project patterns)

---

## Completion Validation

### Core Phase Gate Conditions

✓ **All tasks complete**: T007 [X], T008 [X]
✓ **TDD cycle closed**: Tests written → Tests pass
✓ **Files synced**: tasks.md shows both as completed
✓ **No blockers**: All sequential dependencies satisfied
✓ **Ready for next phase**: Advance to Integration phase

### Test Verification

```bash
# After T007 completion: Tests exist and fail (expected)
pytest tests/api_test.py -v  # → RED state

# After T008 completion: Tests pass (expected)
pytest tests/api_test.py -v  # → GREEN state
```

---

## Summary

| Aspect | Details |
|--------|---------|
| **Phase** | Core |
| **Task Ordering** | T007 → T008 (sequential, non-parallel) |
| **Task Count** | 2 |
| **Execution Constraint** | TDD-first: Write tests before code |
| **File Changes** | `tests/api_test.py`, `src/api/routes.py` |
| **Dependency Type** | Logical + sequential marker |
| **Parallelization** | Not applicable (sequential tasks) |
| **Expected Outcome** | All tests passing, implementation complete |
| **Checkpoint Status** | PASS (proceed to Integration phase) |

---

## Key Principle: TDD-First in implement-plan

The implement-plan skill strictly enforces Test-Driven Development by:

1. **Requiring tests to be written first** (T007 before T008)
2. **Blocking implementation** until test specification is complete
3. **Validating GREEN state** before advancing phases
4. **Deferring refactoring** to later phases (Polish)

This ensures that:
- ✓ Implementation is guided by failing tests
- ✓ All API contracts are validated before code
- ✓ Red-green-refactor cycle is properly sequenced
- ✓ Code quality is tied to test coverage

