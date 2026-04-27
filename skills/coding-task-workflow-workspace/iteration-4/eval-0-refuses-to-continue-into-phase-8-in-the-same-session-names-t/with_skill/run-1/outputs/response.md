# Coding Task Workflow: Gate E → Phase 8 Continuation

## Workflow Rule (Non-Negotiable)

Per **SKILL.md**, Line 32-33 and **references/stop-gates.md**, Lines 105-110:

> **Mandatory session boundary after Gate E**:
> 1. Stop after Phase 7 once Gate E is satisfied.
> 2. Tell the human to resume from a fresh session with `coding-task-workflow RESUME=<slug>`.
> 3. Do **not** begin Phase 8 in the same conversation.
> 4. This is a hard stop to keep the implementation context window lean enough for Phases 8–11.

## Answer to Your Request

You asked to continue into Phase 8 in this same session. **The workflow cannot do this.** It is a non-negotiable rule (SKILL.md line 4): "After Gate E passes, hard-stop the session and hand off `coding-task-workflow RESUME=<slug>`. Do not begin Phase 8 in the same session even if the user explicitly asks for it."

## What Phase 8 Requires (Once Resumed)

Phase 8 is **Implementation**. It executes the TDD task graph with a strict red→green→refactor loop.

### Phase 8 Workflow (from references/workflow.md, Lines 226-249):

**Objective**: Execute the task graph using a strict TDD red→green→refactor loop.

**Inputs**: 
- Task-graph issue
- Open implementation task issues  
- Relevant source files
- **Fresh session resumed after the Phase 7 hard stop**

**Exact Steps**:

1. **Resolve `RESUME=<slug>`** by loading the parent issue and descendant phase/task issues for that `work_id`. Do not rely on local phase files.

2. **Process implementation task issues in dependency order.** Run tasks labelled `parallel` concurrently when:
   - Their dependencies are satisfied
   - They do not overlap on files

3. **For each task issue, execute strict TDD**:
   - **RED**: Write a failing test that captures the behaviour. Run it and confirm it fails for the expected reason. Record the result as a comment on the task issue while the issue remains at `stage: red`.
   - **GREEN**: Update the same task issue to `stage: green`, write the minimal code to make the test pass, run it, and record the result as a comment on that issue.
   - **REFACTOR**: Update the same task issue to `stage: refactor`, clean up if needed, rerun the relevant tests, and record the outcome as another comment on that issue.

4. **Never add untested code paths.** If a useful branch is not yet covered by a test, do not add it.

5. **Close each task issue when its slice is complete.** The task issue comments replace the implementation log, and the issue body remains the durable record of the slice's current/final stage.

**Outputs**: 
- Modified source files and tests
- Implementation task issue comments
- Updated task issue stage fields
- Closed implementation task issues

**Parallelism**: Parallelizable task groups run concurrently; sequential tasks run in order.

**Strict TDD rules**: See the TDD skill documentation.

## Required Handoff

To begin Phase 8, you must resume in a **fresh session** with:

```
coding-task-workflow RESUME=2026-04-23-add-rate-limit-logs
```

This will:
1. Rebuild state from the GitHub issue hierarchy for that `work_id`
2. Continue from the next incomplete phase (Phase 8)
3. Load all task issues and their dependencies
4. Begin the TDD red→green→refactor implementation loop

## Why the Hard Stop

The session boundary after Gate E exists to "keep the implementation context window lean enough for Phases 8–11" (README.md, line 29). Phases 8–11 are code-heavy and require full focus on implementation, review, verification, and landing. Keeping the planning context separate keeps both planning and execution phases efficient.
