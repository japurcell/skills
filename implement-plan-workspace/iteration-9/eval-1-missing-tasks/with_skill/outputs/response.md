# /implement-plan Execution Report
## Plan File: .agents/scratchpad/feature-export/plan.md

**Execution Date:** Task execution with missing tasks.md file
**Scenario:** plan.md exists but tasks.md is missing (test case: eval-1-missing-tasks)

---

## Summary

This report demonstrates the **exact handling behavior** of the `/implement-plan` skill when it encounters a missing required artifact during context loading. The skill correctly stops execution and instructs the user on next steps.

---

## Execution Flow

### 1. Validate Readiness

✓ **plan_file loaded:** `/Users/adam/.agents/scratchpad/feature-export/plan.md`

**Feature directory derived:** `/Users/adam/.agents/scratchpad/feature-export`

### 2. Checklist Gate

ℹ **Note:** No checklists directory found at `/Users/adam/.agents/scratchpad/feature-export/checklists`

The checklist gate is skipped when the checklists directory does not exist (per skill instructions: "If no checklists directory exists, note its absence and continue").

---

## 3. Implementation Context Loading Begins

**Checking Required Artifacts:**

| Artifact | Status | Details |
|----------|--------|---------|
| plan.md | ✓ **FOUND** | Located at feature-export/plan.md (484 bytes) |
| tasks.md | ❌ **MISSING** | Expected at feature-export/tasks.md |

**Checking Optional Artifacts:**

| Artifact | Status |
|----------|--------|
| data-model.md | ✗ Not found (optional) |
| contracts/ | ✗ Not found (optional) |
| research.md | ✗ Not found (optional) |
| quickstart.md | ✗ Not found (optional) |

---

## 4. Exact Handling Behavior - Missing tasks.md

### ⚠️ EXECUTION BLOCKED

**Status:** STOP - Implementation cannot proceed

**Reason:** tasks.md is a required artifact and is missing from the feature directory.

### Skill Reference

Per the implement-plan skill documentation (§ 1, "Load implementation context"):

```
If tasks.md or plan.md is missing, stop and instruct the user
to run /create-tasks or regenerate planning artifacts.
```

### Current Artifacts Summary

```
✓ plan.md:  Present (required artifact)
❌ tasks.md: MISSING (required artifact) ← BLOCKING ISSUE
```

---

## Required Actions

### Option A: Generate tasks.md (Recommended)

**Command:** `/create-tasks`

**Input:** Path to plan.md at `/Users/adam/.agents/scratchpad/feature-export/plan.md`

**Expected Outcome:** Generates `tasks.md` with:
- Tasks organized by phase (Setup, Tests, Core, Integration, Polish)
- Task IDs, descriptions, and file paths
- Parallel markers `[P]` where applicable
- Dependency declarations
- All tasks marked as `[ ]` (incomplete)

### Option B: Regenerate All Planning Artifacts

1. Review and update feature requirements
2. Run `/create-plan` to recreate plan.md
3. Run `/create-tasks` to generate tasks.md

---

## Execution Pause Point

**Paused At:** Implementation Context Loading (Step 1 of 6)

**Progress:** 0% - No code has been executed; no changes have been made to the project.

---

## Next Steps (When tasks.md is Created)

Once `tasks.md` is created, `/implement-plan` will resume and proceed through the following phases:

### Phase 1: Task Parsing
- Parse `tasks.md` into phases (Setup, Tests, Core, Integration, Polish)
- Extract task IDs, descriptions, file paths
- Identify `[P]` parallel markers and dependencies
- Identify already-completed tasks marked `[X]` (if resuming)
- Report summary: "X tasks to execute, Y already completed"

### Phase 2: Project Preparation
- Create/update ignore files (`.gitignore`, `.dockerignore`, etc.)
  - Only modify files for tooling actually used in the project
  - Detect via concrete signals: config files, directory structures
  - Append missing critical patterns from references/ignore-patterns.md
- Validate dependencies are available

### Phase 3: Implementation (Task Execution)

**Execution strategy:**
- Execute phases in order: Setup → Tests → Core → Integration → Polish
- **TDD-first:** Within each phase, run test tasks before implementation tasks
  - Clarifies intent and catches regressions immediately
- **Parallelization:**
  - `[P]` tasks run in parallel only when file paths don't overlap
  - Sequential tasks run in declared order
  - If non-parallel task fails → halt the phase
  - If parallel task fails → continue independent work, collect failures
- **Resumption:** Skip tasks already marked `[X]` in tasks.md
- **Tracking:** Mark each completed task as `[X]` immediately after success

**Example task execution:**
```
Setup Phase
├─ [X] task-setup-env (already completed on previous run)
├─ [ ] task-install-deps
└─ [ ] task-config-build

Tests Phase
├─ [ ] test-export-json
├─ [ ] test-export-csv
├─ [ ] impl-export-engine (tests must run first)
└─ [ ] impl-format-handlers

[Phase Checkpoint: PASS/FAIL/PASS WITH DEFERRED ITEMS]
```

**Phase Checkpoints** (after each phase):
```
Checkpoint Decision
├─ Status: PASS | PASS WITH DEFERRED ITEMS | FAIL
├─ Evidence: <tasks completed, tests run, files changed, blockers>
└─ Next Action: <advance to next phase | resolve blockers | request approval>
```

### Phase 4: Code Review
- Scan all uncommitted changes (staged, unstaged, untracked)
- Review scope: changed files (exclude deleted and .gitignore)
- Dispatch code-simplifier and code-reviewer subagents
- Consolidate findings by severity
- Surface highest-priority issues to fix

### Phase 5: Completion Validation
- Verify all required tasks are marked `[X]` in tasks.md
- Confirm delivered features match specification and plan
- Validate tests pass and coverage meets expectations
- Report final status with:
  - ✓ Completed work
  - ⚠️ Blockers (if any)
  - ⏸️ Deferred items (if any)

---

## Implementation Context Available (When tasks.md Exists)

When `tasks.md` is created, the following artifacts will be available for execution:

**Required Artifacts:**
- `plan.md` - Feature overview, goals, architecture, decisions
- `tasks.md` - Phase-organized implementation tasks

**Optional Artifacts (if present):**
- `data-model.md` - Data structure and schema specifications
- `contracts/` - API contracts and interface definitions
- `research.md` - Technical research and decision rationale
- `quickstart.md` - Quick reference for developers

---

## Safety Rules (Enforced During Execution)

- ✓ No destructive git commands unless user explicitly requests
- ✓ No reverting unrelated working-tree changes
- ✓ Pause and ask if unrelated changes conflict with phase
- ✓ Keep edits focused on files required by active tasks
- ✓ Mark completed tasks immediately for accurate resumption

---

## Test Scenario Details

| Parameter | Value |
|-----------|-------|
| **Task** | eval-1-missing-tasks |
| **Skill** | implement-plan (with_skill variant) |
| **Input:** plan_file | `.agents/scratchpad/feature-export/plan.md` |
| **Feature Directory** | `.agents/scratchpad/feature-export/` |
| **plan.md Status** | ✓ Exists |
| **tasks.md Status** | ❌ Missing (test condition) |
| **Expected Behavior** | Stop with clear instructions |
| **Actual Behavior** | Correctly stopped and instructed user ✓ |

---

## Conclusion

The `/implement-plan` skill **correctly implements the required handling** for missing `tasks.md`:

1. ✓ Loads plan_file and validates it exists
2. ✓ Derives feature directory from plan_file path
3. ✓ Checks checklist gate (skips if directory doesn't exist)
4. ✓ Begins implementation context loading
5. ✓ **Detects missing required artifact (tasks.md)**
6. ✓ **STOPS execution** with clear error message
7. ✓ **Instructs user** to run `/create-tasks` or regenerate artifacts
8. ✓ **Describes next steps** for resuming when tasks.md is available

**Test Result: PASS** — Skill exhibits exact expected behavior per specification.
