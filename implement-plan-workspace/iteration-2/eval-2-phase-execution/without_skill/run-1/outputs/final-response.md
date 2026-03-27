# /implement-plan Execution Handoff (Single Phase)

Plan file: .agents/scratchpad/feature-notify/plan.md  
Assumption: all checklist gates already PASS.

## Phase Handoff: Core

### Goal
Implement core feature behavior after Setup and Tests phases are complete, while honoring mixed [P] tasks and preventing conflicts on overlapping files.

### Inputs to Subagent
- Source of truth: tasks.md (Core section)
- Dependency state: Setup done, Tests done
- Rules:
  - Execute non-[P] tasks in listed order
  - [P] tasks may run concurrently only when file paths do not overlap
  - If file paths overlap, serialize those tasks even if marked [P]
  - Mark each completed task [X] in tasks.md
  - Halt phase on any failed non-parallel task
  - For [P] tasks, continue successful tasks and report failed ones

### Execution Format
1. Build task queue from Core items:
   - For each task: {id, description, files[], parallelFlag, dependsOn[]}
2. Partition tasks:
   - Sequential lane: all non-[P] tasks
   - Parallel candidate lane: [P] tasks
3. Apply file-lock rule to parallel candidates:
   - Create conflict groups by intersecting files[]
   - Run tasks in different groups concurrently
   - Run tasks inside same group sequentially
4. Run tasks:
   - Complete each task, update tasks.md to [X]
   - Emit progress after each task: ID, status, touched files, test result
5. End-of-phase bundle:
   - Completed IDs
   - Failed IDs with error context
   - Updated files summary
   - Ready/not-ready recommendation for next phase

### Example Conflict Handling (Core)
- CORE-003 [P] touches src/notify/service.ts
- CORE-004 [P] touches src/notify/service.ts and src/notify/types.ts
- CORE-005 [P] touches src/ui/notify-banner.tsx

Execution:
- Serialize CORE-003 then CORE-004 (shared src/notify/service.ts)
- Run CORE-005 concurrently with either one (no overlap)

## Checkpoint Criteria Before Next Phase (Integration)

Proceed only if all criteria pass:
1. Core required tasks complete:
   - Every non-optional Core task is [X] in tasks.md
2. Failure policy satisfied:
   - No unresolved failure in non-[P] Core tasks
   - Any failed [P] task is either fixed and re-run, or explicitly deferred with approval
3. Test gate:
   - Core-related unit/contract tests pass
   - No regression in previously passing suites
4. Build/lint gate:
   - Project builds successfully
   - Lint/type checks for touched scope pass
5. Spec alignment gate:
   - Implemented behavior matches plan.md Core scope
   - No unauthorized scope expansion
6. Handoff quality gate:
   - tasks.md statuses are current
   - Phase report includes completed/failed tasks, risks, and next actions

If all pass, advance to Integration. If any fail, remain in Core and resolve gaps before proceeding.
