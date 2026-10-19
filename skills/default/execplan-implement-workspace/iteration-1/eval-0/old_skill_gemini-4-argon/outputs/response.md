Derive three distinct tasks in the task graph with explicit prerequisites rather than inferring order from the checklist:
1. **T1 (Feasibility/decision task):** Resolve parser feasibility first. Prerequisites: none.
2. **T2 (Implementation task):** Implement the compatible parser/summary vertical slice. Prerequisite: T1 complete with recorded evidence.
3. **T3 (Parity/milestone integration task):** Verify legacy versus new CLI outputs, including malformed-input failures and the shared default-output invariant. Prerequisite: T2 integrated on base.

Only T1 is in the current frontier. Assign T1 to a fresh subagent with its full task and current plan context, the shared default-output invariant, required inputs, explicit file ownership, verification criteria, and stopping boundary (stop after feasibility evidence is recorded; do not start T2). Instruct it to use task-appropriate feasibility evidence rather than inventing product code or empty commits, or if prototyping in a worktree, state promotion/discard criteria and follow commit message guidelines.

Milestone acceptance is proven only after T1 and T2 are completed, integrated onto the base branch, and the composed-behavior parity check (T3) runs against the integrated base tree—verifying matching legacy and new CLI stdout, stderr, exit codes, malformed-input negative cases, and the default-output invariant—with actual evidence recorded and `Status: done`, `Acceptance: met`, and Progress updated together.
