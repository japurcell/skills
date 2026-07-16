---
name: prd-ralph-loop
description: Run prd-ralph sequentially over prd.json tasks until all pass. Use for completing all PRD tasks/stories or “run Ralph until done”; do not use for a single task.
disable-model-invocation: true
---

# PRD Ralph Loop

Run one `prd-ralph` subagent at a time until every PRD task passes.

## Input

- `prd_file`: path to `prd.json`. If missing, invalid, unreadable, or has no `tasks`, stop and ask the user.

## State

Each loop, read only:

`tasks[].{id,title,passes,dependsOn}`

A task is complete only when `passes === true`.

## Procedure

1. If all tasks pass, reply exactly:

   `<promise>COMPLETE</promise>`

2. Activate or load the `subagent-model-router` skill once before starting, unless already configured.

3. Select the next ready task:
   - `passes !== true`
   - all `dependsOn` tasks have `passes === true`

4. If no incomplete task is ready, stop and report blocked/cyclic dependencies.

5. Spawn exactly one subagent with this prompt:

   ```text
   Activate or load the `prd-ralph` skill on this PRD file: <prd_file>.
   Implement the next ready task only. Verify it, update PRD/progress state, and commit.
   ```

6. Wait for completion, then re-read only `tasks[].{id,title,passes,dependsOn}`.

7. Track consecutive attempts for the same task.

8. If the result shows an external blocker, stop after the first failed attempt and report `blocked_external`. External blockers include:
   - `ERR_CERT_AUTHORITY_INVALID`
   - SSL/TLS certificate errors
   - SSO/login redirects
   - authentication, authorization, or permission denial

9. For non-external failures, stop if:
   - the subagent failed/errored, or
   - the same task still does not pass after 2 consecutive attempts

   Report:
   - task id/title
   - attempt count
   - failure summary
   - current `passes` value
   - relevant blocker, if any

10. Repeat until all tasks pass, then reply exactly:

    `<promise>COMPLETE</promise>`

## Rules

- Never run tasks or subagents in parallel.
- Never send the full PRD unless required by `prd-ralph`.
- Do not repeatedly invoke `subagent-model-router` without changed constraints.
- Do not retry explicit external blockers.
- Do not manually mark tasks as passing.
- Before final response, confirm all tasks have `passes === true`.
