# /implement-plan Phase Execution Handoff (Example: Core)

Context assumed:
- plan_file: `.agents/scratchpad/feature-notify/plan.md`
- All checklist gates are PASS
- `tasks.md` has phases: Setup, Tests, Core, Integration, Polish
- Tasks include mixed `[P]` markers and overlapping file paths

## Phase Handoff Format (Core)

### 1) Phase Scope
- Phase: `Core`
- Goal: Implement core feature behavior after Setup + Tests are complete
- Entry dependency: Setup = complete, Tests = complete

### 2) Task Selection + Scheduling Rules
- Parse Core tasks into:
  - Sequential tasks: no `[P]`
  - Candidate parallel tasks: with `[P]`
- Build file-touch map per task.
- Run in parallel only when file sets do not overlap.
- If two `[P]` tasks touch any common file, force sequential execution.
- Keep original task order for all forced-sequential conflicts.

### 3) Execution Plan (Concise)
- Batch A (sequential): all non-`[P]` tasks in listed order.
- Batch B (parallel-safe groups): `[P]` tasks grouped by non-overlapping file sets.
- Conflict fallback: move conflicting `[P]` tasks into sequential queue.
- After each task:
  - mark `[X]` in `tasks.md`
  - log changed files + short result
- On failure:
  - non-`[P]`: stop phase immediately
  - `[P]`: continue other tasks in same batch, record failures

### 4) Phase Status Block (handoff payload)
```md
Phase: Core
Status: IN_PROGRESS | BLOCKED | COMPLETE
Completed task IDs: [...]
Failed task IDs: [...]
Deferred task IDs: [...]
Files changed: [...]
Notes: <1-3 bullets>
```

## Checkpoint Criteria Before Next Phase (Core -> Integration)

Proceed only if all are true:
1. Every required Core task is marked `[X]` in `tasks.md`.
2. No unresolved failure remains in non-`[P]` Core tasks.
3. Any failed `[P]` Core task is either:
   - fixed and marked `[X]`, or
   - explicitly deferred with owner + follow-up task ID.
4. No file-conflict violation occurred during parallel execution (or it was rerun sequentially).
5. Core acceptance tests relevant to implemented behavior pass.
6. Phase status block is present and `Status: COMPLETE`.

If any criterion fails: do not start Integration; return `BLOCKED` with failing criteria list.
