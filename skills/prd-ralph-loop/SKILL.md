---
name: prd-ralph-loop
description: Orchestrate the implementation of a PRD with subagents. Use for completing all PRD tasks/stories, not a single task.
disable-model-invocation: true
---

# /prd-ralph-loop

## Input

- `prd_file`: path to PRD tasks file; if missing, ask the user.

## Workflow

1. Record baseline:
   - `review_base_sha = git rev-parse HEAD`
   - initial `git status --porcelain`
     If either fails, stop and report the issue.
2. Activate or load the `subagent-model-router` skill.
3. Repeat sequentially:
   - Start one fresh subagent with this prompt: activate the `prd-ralph` skill on `prd_file`.
   - If it returns `<promise>COMPLETE</promise>`, stop the loop.
4. Define `full_review_scope` as changes since baseline:
   - committed diff: `review_base_sha..HEAD`
   - staged diff
   - unstaged diff
   - new relevant untracked files
5. If `<dirname(prd_file)>/progress.txt` exists, read it.
6. Activate or load the `self-improve` skill to capture learnings from this session and `progress.txt`, especially command/tool workarounds.
7. Report completion and `full_review_scope`.

## Guidelines

**Delegate implementation to subagents**: DO NOT implement any code yourself. If a subagent fails, start a new one and pass it the failing subagent's output. If there are 3 consecutive failures, stop and report the issue.
**Stay blind**: DO NOT read `prd_file` to track progress or decide which task a subagent should work on. Subagents coordinate task selection themselves by editing `prd_file` and `progress.txt`. Your job is to continually spawn subagents to implement the PRD until one returns `<promise>COMPLETE</promise>`.

## Red flags

- Reading `prd_file` or `progress.txt` before the loop is complete.
- Activating the `prd-ralph` skill yourself.
