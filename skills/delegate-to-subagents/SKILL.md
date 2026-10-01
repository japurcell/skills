---
name: delegate-to-subagents
description: Use subagents when parallel execution, specialized expertise, or context isolation is likely to improve results enough to justify coordination overhead. Also use this skill when the user explicitly asks to delegate, create, spawn, dispatch, or fan out subagents.
---

# Delegate to Subagents

Delegate only when the expected benefit exceeds the coordination cost.

Invoking this workflow authorizes and requires the orchestrator to override configured subagent defaults by explicitly applying the router-selected model and reasoning effort to each dispatch.

Explicit model or reasoning-effort instructions stated by the user for the current request take precedence over router selections. In the absence of such instructions, router selections take precedence over configured, inherited, or runtime defaults.

No separate authorization to override defaults is required.

## Non-negotiable dispatch contract

A subagent may be dispatched only when all of the following are true:

1. A concrete router result exists for the subtask.
2. The router result has `dispatchable: true`.
3. The router result contains an exact `model` value accepted by the dispatch interface.
4. The router result contains an exact `reasoning_effort` value accepted by the dispatch interface.
5. The orchestrator has printed the routing summary to the user.
6. The dispatch call explicitly sets both `model` and `reasoning_effort`.
7. The submitted `model` and `reasoning_effort` exactly match the printed route.
8. The dispatch call contains an explicit runtime limit.

Configured, inherited, or runtime defaults are not substitutes for routing.

Never dispatch with either routing field:

- omitted
- null
- implicit
- inherited
- unresolved
- represented only by a descriptive range
- left for the runtime to choose

Values or phrases such as the following are not dispatchable unless the dispatch interface accepts that exact literal value and the user explicitly requested it:

- `default`
- `auto`
- `runtime-selected`
- `runtime default`
- `runtime-supported`
- `high or greater`
- `strongest available`
- `if applicable`
- an unexpanded placeholder

A recommendation that was not explicitly applied to the dispatch call is not completed routing.

If the runtime cannot accept an explicit model and explicit reasoning effort, do not dispatch the affected subtask. Report the limitation instead.

## Selection precedence

Apply model and reasoning-effort selection rules in this order:

1. Explicit constraints stated by the user for the current request.
2. The concrete result returned by `subagent-model-router`.
3. Configured, inherited, or runtime defaults only when the user explicitly requests their use in the current request.

A persistent configuration value is a fallback default, not an explicit instruction in the current request. It does not override the router.

Invoking this workflow authorizes and requires explicit dispatch overrides. Do not ask for separate permission to override configured defaults.

If an explicit current-request constraint conflicts with the task's capability floor:

1. explain the conflict
2. do not silently ignore the constraint
3. do not silently lower the capability floor
4. ask the user to revise the constraint, or do not dispatch the affected subtask

Examples:

- “Use model X” makes model X a hard constraint for the current request if it is available and capable.
- “Use reasoning effort Y” makes Y a hard constraint if the dispatch interface supports it.
- “Use my configured defaults” explicitly authorizes default-based dispatch.
- A model or effort stored in persistent configuration does not become a hard constraint merely because it exists.
- Merely asking to delegate does not request preservation of configured defaults.

## Procedure

### 1. Plan the work

For each proposed subtask, define:

- `subtask_id`
- objective
- necessary context
- constraints
- expected deliverable
- verification criteria
- allowed files or resources, when applicable
- write ownership
- dependencies
- runtime limit

Independent subtasks may run in parallel. Dependent subtasks must run in dependency-aware waves.

Do not dispatch while any required planning field is unresolved.

### 2. Route every subtask

Run `subagent-model-router` separately for each materially different subtask.

Provide the router with:

- the subtask objective
- stakes and security sensitivity
- ambiguity and reasoning requirements
- expected context size
- review history
- verification plan
- runtime-supported models
- runtime-supported reasoning-effort values
- explicit model or effort constraints from the current user request

A route may be reused only when the router's reuse criteria are satisfied.

Even when a route is reused, print and explicitly apply the route for every dispatched subtask.

The router result must contain:

- `dispatchable`
- `tier`
- exact `model`
- exact `reasoning_effort`
- `reason`
- `escalation_trigger`
- `fallback`

Do not accept a result containing unresolved routing language such as:

- “runtime-selected”
- “runtime default”
- “use an available model”
- “use a supported effort”
- “high or greater”
- “the strongest available”
- “if applicable”
- `auto`
- an unexpanded placeholder

Resolve catalog ranges to exact values supported by the current dispatch interface before proceeding.

If available models or accepted effort values cannot be confirmed, the route is not dispatchable.

### 3. Print the routing summary

Print an auditable routing summary before the first corresponding dispatch.

Use this format:

```yaml
routing:
  - subtask_id: <stable identifier>
    dispatchable: true
    tier: <Fast|Standard|Premium>
    model: <exact dispatch value>
    reasoning_effort: <exact dispatch value>
    rationale: <task fit, capability floor, cost assumptions, and uncertainty>
    fallback:
      model: <exact dispatch value>
      reasoning_effort: <exact dispatch value>
    escalation_trigger: <concrete trigger or none>
```

If no fallback is available, use:

```yaml
fallback: none
```

If routing cannot be completed, print:

```yaml
routing:
  - subtask_id: <stable identifier>
    dispatchable: false
    tier: <Fast|Standard|Premium>
    model: unresolved
    reasoning_effort: unresolved
    rationale: <why an exact dispatchable route could not be produced>
    fallback: none
    escalation_trigger: none
```

Do not dispatch a subtask whose printed route has `dispatchable: false`.

Do not include the routing summary, routing rationale, or router deliberation in the subagent prompt.

A notice that the runtime will choose defaults does not satisfy the reporting requirement.

### 4. Perform the pre-dispatch gate

Immediately before each dispatch, verify:

```text
route exists
AND route.dispatchable == true
AND route.model is exact
AND route.reasoning_effort is exact
AND route was printed
AND dispatch.model == route.model
AND dispatch.reasoning_effort == route.reasoning_effort
AND runtime_limit is explicit
```

If any condition is false, stop that dispatch.

Do not:

- continue for convenience
- omit either field
- rely on configured defaults
- rely on runtime selection
- assume that invoking the tool will apply the recommendation
- claim that routing was completed

### 5. Dispatch the subagent

For each dispatch:

- explicitly set the dispatch interface's `model` argument to the printed route's exact `model`
- explicitly set the dispatch interface's `reasoning_effort` argument to the printed route's exact `reasoning_effort`
- provide the subtask objective and necessary context
- provide all applicable constraints
- provide the expected deliverable
- provide verification criteria
- impose the defined runtime limit
- identify allowed files or resources when applicable
- identify write ownership when applicable
- exclude instructions asking the subagent to create or dispatch additional subagents unless nested delegation is intentionally authorized

Do not remove quoted or task-relevant references merely because they contain phrases such as “spawn a subagent.”

Do not add the routing result, routing rationale, or internal model-selection discussion to the subagent prompt.

### 6. Audit the submitted dispatch

After submitting each dispatch, inspect the dispatch request or tool-call arguments available to the orchestrator.

Confirm and record:

- `subtask_id`
- submitted `model`
- submitted `reasoning_effort`
- submitted runtime limit

The audit must use the actual submitted arguments, not planned values or assumptions about runtime behavior.

If either routing field was omitted or differs from the printed route:

1. treat the dispatch as noncompliant
2. do not describe it as router-selected
3. cancel it if cancellation is supported and safe
4. otherwise, do not rely on its result without informing the user
5. report the mismatch
6. redispatch at most once with the correct explicit fields, when safe and useful

Do not infer the executed model or effort from runtime behavior.

If the runtime confirms different executed values from those submitted:

1. report both the submitted and executed values
2. treat the runtime override as a routing failure
3. do not claim that the router-selected configuration was executed
4. stop affected dependent dispatches until the conflict is resolved

### 7. Coordinate execution

Dispatch all ready, independent, compliant subtasks before waiting for results.

For parallel writing:

- assign non-overlapping write ownership
- identify shared files
- make dependencies explicit
- serialize edits to shared files

After one execution wave completes, verify prerequisite results before dispatching dependent subtasks.

Rerun the router for a dependent subtask when any of the following has materially changed:

- work class
- stakes
- security sensitivity
- ambiguity
- affected behavior
- review history
- context requirements
- verification requirements
- runtime constraints
- available models or effort values

### 8. Handle routing failures

If the router does not produce an exact model and exact reasoning effort:

1. do not dispatch
2. identify the unresolved field
3. inspect the current runtime's accepted model and effort values, when possible
4. rerun routing with those exact values
5. report the limitation if the route remains unresolved

Do not replace unresolved routing with configured, inherited, or runtime defaults.

If the selected model or effort is unavailable:

1. use the router's exact same-tier fallback when available
2. print the revised route before dispatch
3. explicitly apply the fallback model and effort
4. audit the submitted fallback values
5. do not lower the capability floor solely because of availability

If no exact same-tier fallback is available, do not dispatch unless rerouting produces another configuration that satisfies the same capability floor.

### 9. Handle execution failures

If a compliant subagent fails or times out:

1. Preserve a concise failure record containing:
   - the error or timeout
   - submitted model
   - submitted reasoning effort
   - runtime limit
   - completed work
   - useful findings
   - unresolved items
   - generated artifacts
2. Diagnose instructions, context, dependencies, permissions, tools, and environment.
3. Revise the objective, context, verification, or runtime limit if appropriate.
4. Rerun the model router if task requirements or demonstrated capability needs changed.
5. Print any revised route before redispatch.
6. Dispatch at most one replacement unless the user authorizes additional retries.

A timeout, unavailable dependency, failing test, or environment problem does not automatically justify a stronger tier.

## Efficiency

Avoid unnecessary duplicate file reads and repeated context gathering.

When several subagents need substantially the same codebase or documentation context, consider assigning one exploration subagent to gather it.

The exploration subagent is subject to the same requirements as every other subagent:

- route it
- print its route
- explicitly apply its model and reasoning effort
- impose a runtime limit
- audit the submitted arguments

Store shared notes in a common location when the environment supports one.

The orchestrator may read files when necessary to plan, coordinate, resolve conflicts, or verify results.

## Completion report

At completion, report the applied route for each dispatched subtask:

```yaml
dispatches:
  - subtask_id: <stable identifier>
    selected:
      model: <router-selected model>
      reasoning_effort: <router-selected effort>
    submitted:
      model: <submitted model>
      reasoning_effort: <submitted effort>
    executed:
      model: <runtime-confirmed model or unconfirmed>
      reasoning_effort: <runtime-confirmed effort or unconfirmed>
    runtime_limit: <submitted limit>
    status: <completed|failed|timed_out|cancelled>
    output_verified: <true|false>
    routing_compliant: <true|false>
```

Distinguish clearly among:

- `selected`: returned by the router
- `submitted`: explicitly included in the dispatch call
- `executed`: confirmed by the runtime, when available

If the runtime does not reveal executed values, report `unconfirmed`. Do not replace them with assumptions.

A runtime's failure to confirm executed values does not invalidate an otherwise compliant dispatch if the exact selected values were explicitly submitted and the runtime did not report an override.

## Verification checklist

Before declaring delegation complete, verify:

- [ ] Every dispatched subtask had a concrete router result.
- [ ] Every router result had `dispatchable: true`.
- [ ] Every router result was printed before its corresponding dispatch.
- [ ] Every printed route contained an exact model.
- [ ] Every printed route contained an exact reasoning effort.
- [ ] Every dispatch explicitly submitted the printed model.
- [ ] Every dispatch explicitly submitted the printed reasoning effort.
- [ ] No dispatch relied on a configured, inherited, implicit, or runtime-selected default.
- [ ] Submitted arguments were audited after dispatch.
- [ ] Every subtask had an explicit runtime limit.
- [ ] Explicit current-request user constraints were honored.
- [ ] Persistent defaults did not override router selections.
- [ ] Independent work was parallelized where beneficial.
- [ ] Dependencies and write ownership were defined before dispatch.
- [ ] Shared-file edits were coordinated.
- [ ] Duplicate file reads and repeated exploration were avoided where practical.
- [ ] Failed or timed-out work was recorded before replacement.
- [ ] Subagent outputs were verified against their acceptance criteria.

If any of the first nine checks fails, report the delegation as noncompliant rather than describing it as successfully routed.
