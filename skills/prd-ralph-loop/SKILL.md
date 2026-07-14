---
name: prd-ralph-loop
description: Sequentially runs prd-ralph on tasks in a prd.json file until every task passes. Use when the user asks to run the PRD/Ralph loop, implement all stories, complete all prd.json tasks, or keep running Ralph until done. Do not use for one task only.
disable-model-invocation: true
---

# PRD Ralph Loop

Orchestrate `prd-ralph` one task at a time. Never run tasks in parallel.

## Inputs

- `prd_file` required path to `prd.json`.

## Procedure

1. Find `prd.json`.
   - If `prd_file` is provided, use it.
   - Otherwise if missing, unreadable, invalid JSON, missing `tasks`, or `tasks` is empty, stop and ask the user.

2. Read `prd.json`.
   - A task is complete only if `passes === true`.
   - If all tasks pass, reply exactly:
     `<promise>COMPLETE</promise>`

3. Start the loop.
   - Before choosing an agent/model, invoke the `subagent-model-router` skill.
   - Select the next ready task:
     - incomplete task where `passes !== true`
     - all `dependsOn` tasks, if any, have `passes === true`
   - If no ready task exists, stop and report the blocked/cyclic dependencies.

4. Run one subagent.
   - Spawn exactly one subagent.
   - Prompt:
     ```text
     Invoke the `prd-ralph` skill on this PRD file: <prd_file>.
     Implement the next ready task only. Verify it, update the PRD/progress state, and commit.
     ```
   - Wait for completion.
   - Re-read `prd.json`.

5. Detect failure.
   - Track consecutive attempts for the same task.
   - If the subagent fails, errors, or the same task is still not passing after 2 consecutive attempts, stop and report:
     - task id/title
     - attempt count
     - subagent failure summary
     - current `passes` value
     - any relevant blocker

6. Repeat.
   - Continue steps 3–5 until every task has `passes === true`.
   - Then reply exactly:
     `<promise>COMPLETE</promise>`

## Rules

- Always re-read `prd.json` after each subagent run.
- Never assume a subagent completed a task without checking `passes`.
- Never run multiple `prd-ralph` subagents in parallel.
- Do not manually mark tasks as passing.
- Do not continue after repeated no-progress failures.
- Final success response must contain only `<promise>COMPLETE</promise>`.
