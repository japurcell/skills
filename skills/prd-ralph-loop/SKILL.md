---
name: prd-ralph-loop
description: Run prd-ralph repeatedly over a PRD until it returns <promise>COMPLETE</promise>. Use for completing all PRD tasks/stories, not a single task.
disable-model-invocation: true
---

# /prd-ralph-loop

## Input

- `prd_file`: path to `prd.json`; if missing, ask the user.

## Workflow

1. Record baseline:
   - `review_base_sha = git rev-parse HEAD`
   - initial `git status --porcelain`
   If either fails, stop and report the issue.
2. Activate or load the `subagent-model-router` skill.
3. Repeat sequentially:
   - Start one fresh subagent.
   - Instruct it to activate `prd-ralph` on `prd_file`.
   - If it returns `<promise>COMPLETE</promise>`, stop the loop.
4. Define `full_review_scope` as changes since baseline:
   - committed diff: `review_base_sha..HEAD`
   - staged diff
   - unstaged diff
   - new relevant untracked files
5. If `<dirname(prd_file)>/progress.txt` exists, read it.
6. Activate or load the `self-improve` skill to capture learnings from this session and `progress.txt`, especially command/tool workarounds.
7. Report completion and `full_review_scope`.