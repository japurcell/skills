---
name: prd-ralph-loop
description: Run prd-ralph sequentially over prd until the completion signal is received. Use for completing all PRD tasks/stories or "run Ralph until done"; do not use for a single task.
disable-model-invocation: true
---

# /prd-ralph-loop

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
5. Report completion and the `full_review_scope` to the user.
