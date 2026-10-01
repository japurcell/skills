---
name: delegate-to-subagents
description: Use subagents when parallel execution, specialized expertise, or context isolation is likely to improve results enough to justify coordination overhead. Also use when the user explicitly asks to delegate, create, spawn, dispatch, or fan out subagents.
---

# Delegate to Subagents

Delegate only when the expected benefit exceeds the coordination cost.

This workflow authorizes and requires the orchestrator to override configured subagent defaults by explicitly applying the router-selected model and reasoning effort to each dispatch. No separate authorization is required.

## Selection precedence

Apply model and reasoning-effort constraints in this order:

1. Explicit instructions in the current user request.
2. The concrete result from `subagent-model-router`.
3. Configured, inherited, or runtime defaults only when the current user request explicitly requires them.

Persistent configuration is a fallback default, not a current-request instruction. It does not override the router.

If the user explicitly requests configured defaults, resolve them to exact values, validate them through the router, print them, and explicitly submit them. Never preserve defaults by omitting dispatch arguments.

If a current-request constraint conflicts with the task's capability floor, report the conflict and do not dispatch until the user revises the constraint.

## Dispatch invariants

Dispatch a subagent only when all of these conditions hold:

- a router result exists for the subtask
- `dispatchable` is `true`
- `model` is an exact value accepted by the dispatch interface
- `reasoning_effort` is an exact value accepted by the dispatch interface
- the route has been printed to the user
- the dispatch explicitly submits the printed `model`
- the dispatch explicitly submits the printed `reasoning_effort`
- an explicit runtime limit is defined and enforced through a runtime-supported mechanism

Do not dispatch with a routing value that is:

- omitted, null, implicit, inherited, or unresolved
- a descriptive range or unexpanded placeholder
- left for the runtime to select

Values such as `default`, `auto`, `runtime-selected`, `runtime default`, “runtime-supported,” “high or greater,” and “strongest available” are not dispatchable routing values. If the user requests configured defaults, resolve those defaults to the concrete model and reasoning-effort values they represent, then print and explicitly submit those concrete values.

A recommendation that is not explicitly applied is not completed routing. If either routing field cannot be explicitly applied, do not dispatch the affected subtask.

## Procedure

### 1. Plan

For each subtask, define:

- `subtask_id`
- objective and necessary context
- constraints and expected deliverable
- verification criteria
- allowed resources and write ownership
- dependencies
- runtime limit

Use `none` or `not applicable` where appropriate. Do not dispatch with an unresolved applicable field.

Run independent subtasks in parallel when beneficial. Run dependent subtasks in dependency-aware waves. Serialize changes to shared files.

### 2. Route

Run `subagent-model-router` for each materially different subtask. Provide:

- objective
- stakes and security sensitivity
- ambiguity and reasoning requirements
- expected context size
- review history
- verification plan
- exact models and reasoning-effort values supported by the runtime
- explicit current-request model or effort constraints

A route may be reused only when the router's reuse criteria are satisfied. A reused route must still be printed and explicitly applied to every dispatch.

The result must contain:

- `dispatchable`
- `tier`
- exact `model`
- exact `reasoning_effort`
- `reason`
- `escalation_trigger`
- `fallback`

Resolve catalog ranges to exact runtime-supported values. If exact model or effort values cannot be confirmed, treat the route as not dispatchable.

### 3. Print the route

Before the corresponding dispatch, print:

```yaml
routing:
  - subtask_id: <identifier>
    dispatchable: true
    tier: <Fast|Standard|Premium>
    model: <exact dispatch value>
    reasoning_effort: <exact dispatch value>
    reason: <task fit, capability floor, cost assumptions, and uncertainty>
    fallback:
      model: <exact dispatch value>
      reasoning_effort: <exact dispatch value>
    escalation_trigger: <trigger or none>
```

Use `fallback: none` when no exact same-tier fallback exists.

For an unresolved route, print:

```yaml
routing:
  - subtask_id: <identifier>
    dispatchable: false
    tier: <Fast|Standard|Premium>
    model: unresolved
    reasoning_effort: unresolved
    reason: <why an exact route could not be produced>
    fallback: none
    escalation_trigger: none
```

Do not dispatch a route with `dispatchable: false`.

A runtime-default notice is not a routing summary.

### 4. Validate and dispatch

Immediately before dispatch, verify:

```text
route.dispatchable == true
AND route.model is exact
AND route.reasoning_effort is exact
AND route was printed
AND dispatch.model == route.model
AND dispatch.reasoning_effort == route.reasoning_effort
AND runtime_limit is explicit
AND runtime_limit enforcement is configured
```

If any condition is false, stop that dispatch.

Configure outside the subagent prompt:

- `model`
- `reasoning_effort`
- runtime-limit enforcement

The subagent prompt may contain:

- objective and necessary context
- task constraints
- expected deliverable
- verification criteria
- allowed resources and write ownership
- required dependency results
- whether nested delegation is authorized

Except for an explicit nested-delegation permission or prohibition when needed, do not put workflow-generated routing, dispatch, or audit metadata in the subagent prompt, including:

- selected model, effort, or tier
- routing result, rationale, fallback, or escalation trigger
- instructions to identify or report model, effort, or runtime configuration
- dispatch-compliance or orchestration-audit instructions

The orchestrator—not the subagent—records execution settings. Do not ask the subagent to infer its model, effort, runtime configuration, or dispatch arguments.

This restriction does not require removing task-relevant source material merely because it mentions models, routing, reasoning effort, or subagents.

Prohibit nested delegation by default. Include explicit authorization in the subagent prompt only when nested delegation is intentional.

Do not remove quoted or task-relevant references merely because they mention spawning subagents.

### 5. Audit and coordinate

After dispatch, inspect the dispatch arguments and any separate runtime-control state available to the orchestrator. Record:

- `subtask_id`
- submitted `model`
- submitted `reasoning_effort`
- enforced runtime limit and mechanism

Audit actual submitted values, not planned values.

If submitted routing values are omitted or differ from the printed route:

1. mark the dispatch noncompliant
2. do not describe it as router-selected
3. cancel it if supported and safe
4. otherwise, disclose the mismatch before relying on its result
5. redispatch at most once with corrected values when safe and useful

If the runtime reports different executed values, first determine whether the difference is documented alias resolution or canonicalization. Record equivalent aliases without marking the dispatch noncompliant. Treat any material override as a routing failure, report it, and pause affected dependent dispatches.

Do not infer executed values when the runtime does not report them.

Dispatch all ready, independent, compliant subtasks before waiting. Verify prerequisite results before dispatching dependent work.

Rerun routing when any of these materially changes:

- work class, stakes, security sensitivity, or ambiguity
- affected behavior or review history
- context or verification requirements
- runtime constraints or available configurations

## Failures and fallback

### Routing failure

If routing does not produce an exact model and effort:

1. do not dispatch
2. identify the unresolved field
3. inspect the runtime's accepted values when possible
4. rerun routing with those values
5. report the limitation if unresolved

Do not substitute configured or runtime defaults.

If the selected configuration is unavailable, rerun routing with that configuration removed from the available candidates. The revised route must provide a new selected `model`, `reasoning_effort`, `reason`, and `fallback`. Print the complete revised route before dispatch, then explicitly submit and audit the revised selected values.

If rerouting cannot produce another exact configuration that satisfies the same capability floor, do not dispatch.

### Execution failure

If a compliant subagent fails or times out:

1. Record:
   - error or timeout
   - submitted model and effort
   - runtime limit and enforcement mechanism
   - completed work and useful findings
   - unresolved items and artifacts
2. Diagnose instructions, context, dependencies, permissions, tools, and environment.
3. Revise the task or runtime limit when appropriate.
4. Rerun routing if requirements or demonstrated capability needs changed.
5. Print any revised route before redispatch.
6. Dispatch at most one replacement unless the user authorizes more retries.

A timeout, unavailable dependency, failing test, or environment problem does not by itself justify a stronger tier.

## Efficiency

Avoid duplicate file reads and repeated context gathering.

When several subagents need substantially the same context, consider one routed exploration subagent to gather it. Apply the same routing, reporting, dispatch, runtime-limit, and audit requirements to that subagent.

The orchestrator may read files to plan, coordinate, resolve conflicts, or verify results.

## Completion report

Report each dispatch as:

```yaml
dispatches:
  - subtask_id: <identifier>
    selected:
      model: <router-selected model>
      reasoning_effort: <router-selected effort>
    submitted:
      model: <submitted model>
      reasoning_effort: <submitted effort>
    executed:
      model: <runtime-confirmed model or unconfirmed>
      reasoning_effort: <runtime-confirmed effort or unconfirmed>
    runtime_limit:
      value: <enforced limit>
      mechanism: <enforcement mechanism>
    status: <completed|failed|timed_out|cancelled>
    output_verified: <true|false>
    routing_compliant: <true|false>
```

Use:

- `selected` for router output
- `submitted` for actual dispatch arguments
- `executed` only for runtime-confirmed values

Runtime confirmation must come from the dispatch system or execution metadata, not from the subagent's response.

If execution values are not reported, use `unconfirmed`. Lack of runtime confirmation does not invalidate a dispatch whose exact selected values were submitted and not reported as overridden.

## Final checks

Before declaring delegation complete, confirm that:

- [ ] every dispatched subtask had a printed, dispatchable route
- [ ] every route contained an exact model and effort
- [ ] every dispatch explicitly submitted the printed values
- [ ] no dispatch relied on configured, inherited, or runtime defaults
- [ ] prohibited routing, dispatch, and audit metadata stayed out of subagent prompts; only intentional nested-delegation instructions were included
- [ ] runtime limits were explicit and enforced through a runtime-supported mechanism
- [ ] submitted arguments were audited
- [ ] current-request user constraints were honored
- [ ] dependencies, write ownership, and shared-file edits were coordinated
- [ ] failures were recorded before replacement
- [ ] outputs were verified against their acceptance criteria

If any routing, reporting, dispatch-argument, prompt-isolation, or audit requirement fails, report the affected dispatch as noncompliant.
