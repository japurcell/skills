---
name: delegate-to-subagents
description: Use subagents when parallel execution, specialized expertise, or context isolation is likely to improve results enough to justify coordination overhead. Also use this skill when the user explicitly asks to delegate, create, spawn, or dispatch subagents, or to fan out work.
---

Delegate only when the expected benefit exceeds the coordination cost.

## Procedure

### 1. Plan the work

For each subtask, define:

- objective;
- necessary context;
- constraints;
- expected deliverable;
- verification criteria;
- allowed files or resources, when applicable;
- write ownership;
- dependencies;
- runtime limit.

Independent subtasks may run in parallel. Dependent subtasks must run in dependency-aware waves.

### 2. Select a model

Run the `subagent-model-router` skill for each subtask.

Show the user an auditable routing summary that includes:

- selected `$model`;
- selected `$reasoning_effort`;
- routing rationale.

Do not include the routing result in the subagent prompt.

If the selected model or reasoning effort cannot be explicitly applied, do not dispatch that subtask. Report the problem to the user and continue with other independent subtasks only when doing so is safe and useful.

### 3. Dispatch the subagent

When dispatching each subagent:

- explicitly set `$model`;
- explicitly set `$reasoning_effort`;
- provide the subtask objective and required context;
- impose the defined runtime limit;
- exclude instructions asking the subagent to create or dispatch additional subagents, unless nested delegation is intentionally authorized.

### 4. Coordinate execution

Dispatch all ready, independent subtasks before waiting for results.

For parallel writing:

- assign non-overlapping write ownership;
- identify shared files;
- make dependencies explicit;
- serialize edits to any shared file.

After one execution wave completes, verify prerequisite results before dispatching dependent subtasks.

### 5. Handle failures

If a subagent fails or times out:

1. Preserve a concise failure record containing:
   - the error or timeout;
   - completed work;
   - useful findings;
   - unresolved items;
   - generated artifacts.
2. Revise the objective, context, or runtime limit if appropriate.
3. Rerun the model router if the task requirements have changed.
4. Dispatch at most one replacement unless the user authorizes additional retries.

## Efficiency

Avoid unnecessary duplicate file reads and repeated context gathering.

When several subagents need the same codebase or documentation context, consider assigning an exploration subagent to gather it once. Use the cheapest model capable of performing that work reliably. Store the resulting notes in a shared location when the environment supports one.

The orchestrator may read files when necessary to plan, coordinate, resolve conflicts, or verify results.

## Verification

- [ ] Every dispatched subagent used an explicitly specified model from its router result.
- [ ] Every dispatched subagent used the selected reasoning effort.
- [ ] Every subtask had an appropriate runtime limit.
- [ ] Independent work was parallelized where beneficial.
- [ ] Dependencies and write ownership were defined before dispatch.
- [ ] Shared-file edits were coordinated to minimize conflicts.
- [ ] Duplicate file reads and repeated exploration were avoided where practical.
- [ ] Exploration was delegated once when multiple subtasks required substantially the same context.
- [ ] Failed or timed-out work was recorded before replacement.
- [ ] Subagent outputs were verified against the defined acceptance criteria.