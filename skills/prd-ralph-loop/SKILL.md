---
name: prd-ralph-loop
description: Run prd-ralph sequentially over prd tasks until all pass. Use for completing all PRD tasks/stories or “run Ralph until done”; do not use for a single task.
disable-model-invocation: true
---

# PRD Ralph Loop

Run one `prd-ralph` subagent at a time until every PRD task passes.

## Input

- `prd_file`: path to `prd.json`. If missing, invalid, unreadable, or has no `tasks`, stop and ask the user.

## Workflow

1. Activate or load the `subagent-model-router` skill.
2. Until each task in `prd_file` has `passes:true`, spawn a subagent and instruct it to activate the `prd-ralph` skill on `prd_file`.
3. When all tasks have `passes:true`, spawn a `code-simplifier` subagent and instruct it to simplify all of the code changed in this session.
4. Spawn a `code-reviewer` subagent and instruct it to review all code changes in this session.
5. If any issues are found, spawn a subagent to fix the issues and instruct it to activate the `tdd` skill. Repeat 4 and 5 for a maximum of 2 iterations.
6. Activate or load the `self-improve` skill to capture any durable learnings from this session.
