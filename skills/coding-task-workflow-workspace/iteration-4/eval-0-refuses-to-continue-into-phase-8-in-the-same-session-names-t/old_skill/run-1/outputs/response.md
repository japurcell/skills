# Workflow Requirements: Continuing from Gate E

## The Governing Rule

From SKILL.md (line 35) — Response style for workflow-rule questions:

> For Phase 7 resume handoffs, start with this exact three-sentence handoff and stop unless the user explicitly asks for more detail: `Gate E already passed, so do not continue into Phase 8 in the same session. Resume from a fresh session with coding-task-workflow RESUME=<slug>. Phase 8 is the next phase after the resume.`

## Exact Answer

Gate E already passed, so do not continue into Phase 8 in the same session. Resume from a fresh session with `coding-task-workflow RESUME=2026-04-23-add-rate-limit-logs`. Phase 8 is the next phase after the resume.

## Why This Rule Exists

The workflow.md (lines 216 and 105–110 of stop-gates.md) explain the mandatory session boundary:

1. **Hard stop after Phase 7**: Once Gate E is satisfied, the current session must terminate.
2. **Fresh session required**: Phase 8 begins only in a new conversation session launched with the `RESUME=<slug>` parameter.
3. **Explicit purpose**: This boundary keeps the implementation context window lean enough for Phases 8–11, which involve substantial code changes and require room for TDD execution, review, and verification.

## What Happens on Resume

When you invoke `coding-task-workflow RESUME=2026-04-23-add-rate-limit-logs` in a fresh session:

1. The workflow resolves the work-item slug by loading the parent GitHub issue and all descendant phase/task issues.
2. It loads the task-graph issue containing the vertical slices and their dependency ordering.
3. It opens all implementation task issues (those labelled `agent:task` and `phase:implement`).
4. Phase 8 executes the task graph: each task runs RED → GREEN → REFACTOR in dependency order.
5. Sequential tasks run one after another; parallel tasks run concurrently when their dependencies are satisfied.
6. Phases 9–11 follow after implementation is complete: review, verification, and PR landing.

## Non-Negotiable

Per workflow.md, Priority Rule #4 (line 14):

> After Gate E passes, stop and hand off `coding-task-workflow RESUME=<slug>`. Do not begin Phase 8 in the same session even if the user explicitly asks for it.

This is a hard constraint that overrides user requests to skip or compress the workflow. The session boundary is not optional.
