---
name: prd-ralph-loop
description: Orchestrate the implementation of a PRD with subagents. Use for completing all PRD tasks/stories, not a single task.
disable-model-invocation: true
---

# /prd-ralph-loop

## Overview

Dispatch fresh workers until the validated manifest is complete or work is blocked. Workers own intake, selection, execution, verification, progress, and commit audits.

## When to Use

Use when explicitly asked to complete all PRD tasks, rather than one task.

## Inputs

- `prd_file`: required path to the task manifest; if absent, ask and stop.
- `progress_file`: optional; forward unchanged when supplied, otherwise let the worker use its default.
- `commit`: optional; forward unchanged when supplied, otherwise retain the worker default `true`.
- Preserve user scope, owner boundaries, and stop constraints in every dispatch.

## Workflow

1. Record `review_base_sha = git rev-parse HEAD` and initial `git status --porcelain`. If either fails, report blocked and stop.
2. Activate the `delegate-to-subagents` skill for routing and dispatch.
3. Start one fresh subagent with the instruction “activate the `prd-ralph` skill”, the exact `prd_file`, explicit optional inputs, and all user scope/stop constraints. Request the worker's exact terminal protocol and summary. Wait for its result before another dispatch.
4. Interpret the worker result:
   - Exact `<promise>COMPLETE</promise>`: all work is complete; stop.
   - `<promise>TASK_COMPLETE</promise>` plus selected-task summary: one task passed and work remains; enforce caller stop constraints, then dispatch the next fresh worker only if continuation is authorized. If a scope/stop limit has been reached, report remaining work honestly without claiming COMPLETE.
   - `<promise>BLOCKED</promise>` plus actionable reason: stop and preserve the blocker. Do not retry an unchanged prerequisite, unavailable check, owner condition, or commit gate.
   - Actual tool/subagent failure or missing, contradictory, or invalid protocol: retry with a fresh worker and pass the prior failure/output. After three consecutive such failures, stop blocked. Reset this counter only after a valid TASK_COMPLETE. Ordinary blocked work is not a retryable runtime failure.
5. Define `full_review_scope`: committed diff `review_base_sha..HEAD`, staged and unstaged diffs, and new relevant untracked files, accounting for initial changes.
6. Only after orchestration stops, read the progress file if available: supplied `progress_file`, otherwise `<dirname(prd_file)>/progress.txt`. Activate the `self-improve` skill to capture authorized learnings, especially tool workarounds; preserve owner limits and user scope.
7. Report complete or blocked accurately, with worker summaries, actionable blocker when present, and `full_review_scope`. A blocked run never claims PRD completion.

## Common Rationalizations

A worker reporting a blocked check is not an invitation to dispatch repeatedly. Continue only on TASK_COMPLETE; required evidence and owner approval stay with the worker's gates.

## Red Flags

Stay blind: do not read `prd_file` or any progress file during orchestration, even to select a task or infer completion. Do not activate the `prd-ralph` skill yourself or implement product changes. Workers validate the manifest before interpreting all-complete flags.

## Verification

Confirm dispatches were sequential and fresh, forwarded inputs and constraints were intact, retries were limited to actual runtime/protocol failures, and the final status follows the worker protocol. Retain the baseline and full review scope so later review includes committed and uncommitted task changes.
