---
name: prd-ralph-loop
description: Run prd-ralph sequentially over prd until the completion signal is received. Use for completing all PRD tasks/stories or “run Ralph until done”; do not use for a single task.
disable-model-invocation: true
---

# PRD Ralph Loop

Run one `prd-ralph` subagent at a time until the completion signal is received.

## Input

- `prd_file`: path to `prd.json`. If missing, stop and ask the user.

## Workflow

1. Activate or load the `subagent-model-router` skill.
2. Before starting the loop, record `review_base_sha = git rev-parse HEAD`.
3. Until a subagent returns the `<promise>COMPLETE</promise>` completion signal, spawn a subagent and instruct it to activate the `prd-ralph` skill on `prd_file`.
4. After `COMPLETE`, define `full_review_scope` as:
   - committed diff for `review_base_sha..HEAD`
   - staged diff
   - unstaged diff
   - relevant untracked files created during the loop
5. Spawn a `code-simplifier` subagent on `full_review_scope`.
6. After `code-simplifier` completes, recompute `full_review_scope`.
7. Spawn a `code-reviewer` subagent on `full_review_scope`.
8. If any issues are found, spawn a subagent to fix them and instruct it to activate the `tdd` skill. After the fix pass, recompute `full_review_scope` and repeat steps 7 and 8 for a maximum of 2 fix/review iterations.
9. Activate or load the `self-improve` skill to capture any durable learnings from this session.
