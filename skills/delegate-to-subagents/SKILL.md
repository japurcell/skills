---
name: delegate-to-subagents
description: Use subagents when parallel execution, specialized expertise, or context isolation is likely to improve results enough to justify coordination overhead. Also use when the user explicitly asks to delegate, create, spawn, dispatch, or fan out subagents.
---

# Delegate to Subagents

Delegate only when the expected benefit exceeds the coordination cost.

This workflow authorizes and requires the orchestrator to select and explicitly apply the router-chosen model and reasoning effort. No separate model-selection confirmation is required.

## Selection and routing order

For each routing attempt:

1. Collect explicit model or effort constraints already stated by the user.
2. Pass those constraints to `subagent-model-router`; use `none` when absent.
3. Let the router select and validate the exact model-and-effort configuration.
4. Do not use configured, inherited, or runtime defaults unless the user explicitly requested them.

Absent model preferences are not ambiguity. Do not ask the user to choose, approve, confirm, or restate a model or effort before routing.

A routing attempt begins with the task facts, runtime capabilities, and user constraints then in scope. Produce and print the route before any approval step.

A dispatchable route is informational. Dispatch it without waiting for confirmation unless the user previously requested pre-dispatch approval or the runtime requires approval.

If the user explicitly requests configured defaults, resolve them to concrete values, validate them through the router, print them, and submit them explicitly. Never preserve defaults by omitting dispatch arguments.

If an explicit constraint prevents a dispatchable route, print the router's `dispatchable: false` result before asking the user to revise it.

If the orchestrator improperly solicits a model or effort before routing:

1. do not use the response to justify that routing attempt
2. invalidate any route derived from it
3. disclose the sequencing error
4. begin a fresh attempt using the original constraints, plus the solicited value only if the user clearly makes it a new requirement

## Dispatch gate

Enforce runtime limits as warning thresholds. When a subagent exceeds its limit, send a non-interrupting warning and request its current status, completed work, blockers, and updated ETA. Keep it running to preserve partial work; do not interrupt, cancel, or replace it solely because it is overdue.

Dispatch only when:

```text
route exists
AND route.dispatchable == true
AND route.model is exact
AND route.reasoning_effort is exact
AND route used only task facts, runtime capabilities, and user constraints in scope when the current routing attempt began
AND route was printed before any approval step
AND dispatch.model == route.model
AND dispatch.reasoning_effort == route.reasoning_effort
AND runtime_limit is explicit and enforced
AND no required approval is pending
```

Do not dispatch with a routing value that is omitted, null, implicit, inherited, ranged, unresolved, an unexpanded placeholder, or left for the runtime to select.

Values such as `default`, `auto`, `runtime-selected`, `runtime default`, “runtime-supported,” “high or greater,” and “strongest available” are not dispatchable routing values.

A recommendation that is not printed and explicitly applied is not completed routing.

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

If essential task information is missing, ask only for that information. Do not ask for model preferences as a substitute for routing.

### 2. Route

Route before any model-selection confirmation.

Run `subagent-model-router` for each materially different subtask using:

- objective
- stakes and security sensitivity
- ambiguity and reasoning requirements
- expected context size
- review history
- verification plan
- exact runtime-supported models and effort values
- model or effort constraints already in scope, or `none`

Inspect runtime metadata or the dispatch interface to discover supported values. Do not ask the user to choose among them.

The route must contain:

- `dispatchable`
- `tier`
- exact `model`
- exact `reasoning_effort`
- `reason`
- `escalation_trigger`
- exact `fallback` or `none`

If exact model or effort values cannot be determined, print a non-dispatchable route.

A route may be reused only when the router's reuse criteria are satisfied. A reused route must still be printed and explicitly applied to every dispatch.

### 3. Print

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

A runtime-default notice is not a routing summary. Print a dispatchable route as a decision, not a question. Proceed without pausing unless a preexisting user-requested or runtime-required approval step applies.

### 4. Dispatch

Explicitly configure outside the subagent prompt:

- the printed `model`
- the printed `reasoning_effort`
- runtime-limit enforcement

The subagent prompt may contain:

- objective and necessary context
- task constraints
- expected deliverable
- verification criteria
- allowed resources and write ownership
- required dependency results
- intentional nested-delegation authorization or prohibition

Do not include workflow-generated routing, dispatch, or audit metadata in the subagent prompt, including:

- selected model, effort, or tier
- route, rationale, fallback, or escalation trigger
- instructions to identify or report model, effort, runtime configuration, or dispatch arguments
- dispatch-compliance or orchestration-audit instructions

The orchestrator—not the subagent—records execution settings. Task-relevant source material need not be removed merely because it mentions models, routing, effort, or subagents.

Prohibit nested delegation by default. Authorize it explicitly only when intentional.

### 5. Approval

If the user previously requested approval or the runtime requires it:

1. route and print first
2. request or invoke approval for the completed route
3. dispatch only after approval

Do not change routed values merely to match an approval response. If the user adds a model or effort constraint, or approved runtime capabilities change, invalidate the route and begin a fresh routing attempt.

Do not invent an approval requirement.

### 6. Audit and coordinate

After dispatch, inspect the actual dispatch arguments and runtime-control state. Record:

- `subtask_id`
- submitted `model`
- submitted `reasoning_effort`
- enforced runtime limit and mechanism

If submitted routing values are missing or differ from the printed route:

1. mark the dispatch noncompliant
2. do not describe it as router-selected
3. cancel it if supported and safe
4. otherwise, disclose the mismatch before relying on its result
5. redispatch at most once with corrected values when safe and useful

If the runtime reports different executed values, distinguish documented alias resolution or canonicalization from a material override. Record equivalent aliases without marking the dispatch noncompliant. Report a material override as a routing failure and pause affected dependent work.

Do not infer executed values when the runtime does not report them.

Dispatch all ready, independent, compliant subtasks before waiting. Verify prerequisites before dispatching dependent work.

Begin a fresh routing attempt when any of these materially changes:

- work class, stakes, security sensitivity, or ambiguity
- affected behavior or review history
- context or verification requirements
- user constraints
- runtime capabilities

## Failures and fallback

### Routing failure

If routing cannot produce an exact model and effort:

1. do not dispatch
2. inspect the runtime's accepted values when possible
3. begin a fresh routing attempt with any newly confirmed values
4. print a non-dispatchable route and report the limitation if unresolved

Do not ask the user to choose an unverified value or substitute configured or runtime defaults.

If the selected configuration becomes unavailable, reroute with it removed from the candidates. Print and apply the complete revised route. Do not dispatch if no exact configuration satisfies the capability floor.

### Execution failure

If a compliant subagent fails or times out:

1. record the error, submitted configuration, runtime limit, completed work, findings, unresolved items, and artifacts
2. diagnose instructions, context, dependencies, permissions, tools, and environment
3. revise the task or runtime limit when appropriate
4. reroute if requirements or demonstrated capability needs changed
5. print any revised route before redispatch
6. dispatch at most one replacement unless the user authorizes more retries

A timeout, unavailable dependency, failing test, or environment problem does not by itself justify a stronger tier.

## Efficiency

Avoid duplicate file reads and repeated context gathering.

When several subagents need substantially the same context, consider one routed exploration subagent. Apply the same routing, printing, dispatch, runtime-limit, and audit requirements to it.

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
- `executed` only for values confirmed by the dispatch system or execution metadata

Do not use a subagent's self-report as runtime confirmation. Use `unconfirmed` when the runtime does not report executed values.

## Final checks

Before declaring delegation complete, confirm that:

- [ ] each route used only task facts, runtime capabilities, and user constraints in scope when its routing attempt began
- [ ] no solicited preference retroactively justified a route
- [ ] recovery from improper solicitation used a fresh routing attempt
- [ ] each dispatchable route was printed as a decision
- [ ] no unnecessary approval pause occurred
- [ ] every dispatch explicitly submitted the printed model and effort
- [ ] no dispatch relied on implicit inheritance of configured or runtime defaults; any user-requested defaults were resolved, validated, printed, and submitted as concrete values
- [ ] routing and audit metadata stayed out of subagent prompts
- [ ] runtime limits were explicit and enforced
- [ ] actual dispatch arguments were audited
- [ ] dependencies and write ownership were coordinated
- [ ] failures were recorded before replacement
- [ ] outputs were verified against their acceptance criteria

If any routing-order, reporting, dispatch-argument, prompt-isolation, approval, or audit requirement fails, report the affected dispatch as noncompliant.
