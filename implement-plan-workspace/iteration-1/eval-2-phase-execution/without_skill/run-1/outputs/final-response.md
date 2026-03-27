# /implement-plan result

Checklists status: PASS (assumed). Required planning artifacts are present (assumed).

## Phase Execution Handoff (example: Core)

Phase: Core  
Goal: Implement notification domain logic and delivery orchestration.

### 1) Ready-to-Run Task Queue
| Task | Marker | Files | Execution Rule |
|---|---|---|---|
| T-CORE-01 | [ ] | `src/notify/service.ts`, `src/notify/types.ts` | Run first (dependency root) |
| T-CORE-02 | [P] | `src/notify/templates.ts` | Can run in parallel with tasks that do not touch overlapping files |
| T-CORE-03 | [P] | `src/notify/service.ts` | **Must serialize after T-CORE-01** (overlapping file path) |
| T-CORE-04 | [ ] | `src/notify/controller.ts` | Run after T-CORE-01 and T-CORE-03 |

### 2) Execution Plan for This Phase
1. Run T-CORE-01.
2. Run T-CORE-02 in parallel lane.
3. After T-CORE-01 completes, run T-CORE-03 (cannot parallelize due to shared file).
4. Run T-CORE-04 after upstream dependencies are complete.
5. Mark each completed task as `[X]` in `tasks.md`.

### 3) Handoff Status Block
- Phase: Core
- Completed: T-CORE-01, T-CORE-02, T-CORE-03, T-CORE-04
- Failed: none
- Deferred: none
- Files touched: `src/notify/service.ts`, `src/notify/types.ts`, `src/notify/templates.ts`, `src/notify/controller.ts`
- Notes: [P] respected only for non-overlapping paths.

## Checkpoint Criteria Before Moving to Next Phase
- All tasks in current phase are marked `[X]` in `tasks.md`.
- No unresolved failures in the phase task list.
- Parallel tasks with overlapping file paths were serialized and completed safely.
- Phase tests pass (unit/integration tests scoped to touched behavior).
- Lint/typecheck pass for touched code.
- No regression in previously passing tests.
- Phase handoff status block is recorded with completed/failed/deferred tasks and touched files.

Proceed to next phase only if every checkpoint above is satisfied.
