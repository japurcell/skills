# Architecture options for resumability vs. simplicity

You are really deciding between **one place that owns the run**, **a workflow engine that owns the run**, and **no single owner at all**.

Because no repository or codebase was provided, I’m keeping this at the architecture level. I would not inspect the current repo yet for style only; I would inspect it later to answer four concrete questions that change the design: what already runs scheduled jobs, where durable state can live, how approvals happen today, and what tracing/logging stack already exists. Missing those answers now mostly affects integration details, not the shape of the three options.

## Questions I would ask first — with provisional answers

1. **Will runs need to survive crashes, deploys, and overnight approval waits?**  
   Provisional answer: probably *sometimes*, but not for every run.

2. **Is the feature mostly a linear flow or a branching process with retries, pauses, and compensating actions?**  
   Provisional answer: more than linear, but not yet a full business-process engine.

3. **Do you expect many maintenance capabilities with different owners to accumulate quickly?**  
   Provisional answer: some growth, but probably not enough to justify decentralized coordination on day one.

4. **Is auditability important because of risk, compliance, or user trust?**  
   Provisional answer: yes, but likely below the threshold where full durable replay is mandatory for v1.

5. **Can a failed run safely restart from the beginning, or is exact resume important?**  
   Provisional answer: safe restart is acceptable for read-only steps; exact resume matters more once you cross into mutating steps.

## Design 1: Single orchestrator

This is the simplest shape: one service, command, or long-lived "maintenance run" object owns the entire flow end to end. Conceptually it looks like:

`receive request -> analyze repo -> decide actions -> apply changes -> verify -> report`

The orchestrator is the only component that knows the full sequence. Individual steps are still modular, but they are invoked by one central controller. That is close to the **orchestration** variant of the saga pattern, where a central coordinator stores and interprets task state and drives recovery behavior ([Azure saga pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga)).

### What it looks like

- A `MaintenanceRun` record stores repo, requested action, current step, artifacts, and outcome.
- A step registry contains well-bounded steps such as `scan`, `plan`, `apply`, `verify`, and `publish`.
- Each mutating step writes an idempotency key so retries do not duplicate side effects; that follows the standard idempotent-request pattern ([Stripe idempotency](https://stripe.com/docs/api/idempotent_requests)).
- The orchestrator acquires a per-repo run lock so two maintenance runs do not fight over the same branch or PR; GitHub Actions’ concurrency groups are a good concrete model for that kind of serialization ([GitHub Actions concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)).
- One trace spans the whole run and each step becomes a child span, which keeps debugging straightforward ([OpenTelemetry traces](https://opentelemetry.io/docs/concepts/signals/traces/)).

### Resumability stance

This design can support **checkpointed resumability**, but only in a limited form:

- Persist the run record after each named step.
- Resume from the last completed safe checkpoint.
- Do not attempt arbitrary replay inside a partially executed step.

That gives you "resume from step boundary" rather than "resume from exact event history." It is often enough if steps are made idempotent and side effects are coarse-grained.

### Best fit

Choose this when the feature is mostly one understandable flow, you want the easiest mental model, and you believe most failures can be handled by retrying a step or restarting from a checkpoint.

### Worst fit

It becomes strained when runs last a long time, pause for humans, branch heavily, or need exact recovery after every external side effect. In that world the orchestrator tends to become a god object with ad hoc retry flags and special cases.

### Risks and mitigations

The big risk is architectural drift: every exception path gets pushed into the same controller. Mitigate that by keeping step contracts explicit, persisting checkpoints, and making side-effecting steps idempotent. If you take this route, define the step names and transition rules cleanly now so you still have a migration path to a proper workflow engine later.

### When to choose it

Choose the single orchestrator if **simplicity is still more valuable than perfect resumability** and you want one place to debug, test, and reason about the feature.

## Design 2: State-machine-driven durable workflow

This is the opposite bet. Here the system’s center of gravity is not a controller loop but an explicit workflow/state model. The run is represented as a sequence of durable states such as `requested`, `analyzing`, `planning`, `awaiting_approval`, `executing`, `verifying`, `completed`, and `failed`.

This option fits platforms built around durable workflow execution. Temporal’s model is explicit: workflow executions are durable, recoverable, and resume from the last recorded event history after failures ([Temporal workflow execution](https://docs.temporal.io/workflow-execution)). State-machine tooling also leans this way; XState/Stately explicitly describes persisted actor state as useful for workflows that survive restarts and remain auditable ([Stately persistence](https://stately.ai/docs/persistence)).

### What it looks like

- The workflow engine owns current state, allowed transitions, timers, waits, and retries.
- Workers or activities perform the actual side effects: fetch repo state, create branches, open PRs, post comments, run checks.
- Human approval becomes a first-class wait state rather than an ad hoc "sleep and poll" hack.
- Every transition is recorded, giving you a durable audit trail.
- Compensation and retry rules are tied to the state model instead of being scattered through imperative code.

### Resumability stance

This is the strongest option for resumability.

- Crashes, deploys, or worker restarts do not lose the run.
- The workflow resumes from persisted state/history rather than from a best-effort checkpoint.
- Long waits, retries, and approval pauses become normal states instead of edge cases.

### Best fit

Choose this when you believe the feature will become a long-running, side-effecting process with human approvals, strict auditability, or a high cost of partial failure. It is also the best fit when the hardest problem is not computing the next step but recovering safely after interruption.

### Worst fit

It is a poor fit if the maintenance feature is still fluid, small, or mostly synchronous. You pay for explicit modeling, versioning, and transition discipline up front. If the actual workflow stays simple, the state machine can become ceremony instead of leverage.

### Risks and mitigations

The main risk is over-modeling. Teams often create too many states, too many special transitions, and too much workflow-specific complexity too early. Mitigate that by starting with a small state set and pushing non-deterministic work into activities. The other big risk is versioning: once runs persist over time, changing the workflow definition requires real discipline.

### When to choose it

Choose the durable workflow/state-machine design if **resumability, pause-and-resume, and auditability are likely to become first-order requirements soon**.

## Design 3: Thin skills coordinated by handoffs

This design removes the single top-level owner. Instead of one orchestrator or one canonical workflow engine, you decompose the feature into specialized skills — for example `scan`, `plan`, `policy`, `apply`, `verify`, and `escalate` — and let them hand work to one another.

That matches modern agent-handoff patterns, where one specialized agent delegates to another based on the task boundary ([OpenAI Agents handoffs](https://openai.github.io/openai-agents-python/handoffs/)). Architecturally, it resembles the **choreography** side of the saga pattern more than orchestration: participants communicate and advance work without a single centralized controller, which Azure notes works better for simpler decentralized flows but becomes harder to track as more steps accumulate ([Azure saga pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga)).

### What it looks like

- Each skill owns a narrow capability and a strict input/output contract.
- Handoffs pass structured context, artifact references, trace IDs, and idempotency keys.
- A lightweight broker may validate routing and schema, but it should not become a hidden orchestrator.
- Observability is mandatory, because debugging depends on following the trace across handoffs rather than inspecting one controller.

### Resumability stance

This design usually gives you **handoff-boundary resumability**, not full workflow durability.

- If a skill finishes and publishes the next handoff, that boundary is easy to resume from.
- If a failure occurs inside a skill, recovery depends on that skill’s own persistence strategy.
- Exact end-to-end replay is hard unless you quietly rebuild a workflow engine underneath.

### Best fit

Choose this when the real challenge is capability growth: different maintenance behaviors, different owners, different tools, and a strong need to swap or add skills independently. It is also attractive when repository maintenance is expected to become a family of semi-independent expert behaviors rather than one coherent run.

### Worst fit

It is the weakest choice if you need one canonical truth about run state, one obvious place to debug failures, or strict guarantees about resume behavior. The more you care about global progress and controlled transitions, the more this model fights you.

### Risks and mitigations

The biggest risk is emergent complexity. Handoffs can become opaque, cyclic, or hard to reason about. Mitigate that with strict schemas, allowed handoff graphs, hop limits, centralized tracing, and clear ownership of side effects. If you find yourself adding a global run ledger, explicit transition rules, and centralized recovery logic, you are drifting back toward a state machine.

### When to choose it

Choose thin skills plus handoffs if **modularity and future capability growth matter more than having a single explicit run model**.

## Comparing the three options

If you optimize for **simplicity of understanding**, the single orchestrator wins. There is one place to read, one place to debug, and one place to explain to the next engineer. The state machine is second: once the model is defined, it is precise, but it asks more of the team. Handoffs are the least simple at the system level even if each skill is small, because control flow is distributed.

If you optimize for **resumability and correctness under interruption**, the state machine wins clearly. Durable workflow engines exist because checkpointed orchestrators eventually hit awkward cases: partially completed mutations, long approval waits, timer-based retries, and definition changes while runs are in flight. Handoffs help at skill boundaries, but they do not naturally give you one durable story for the whole run.

If you optimize for **generality**, the answer depends on what kind of future you expect. A state machine is more general for long-running operational workflows. Thin handoffs are more general for a growing ecosystem of specialized capabilities. A single orchestrator is least general, but that is often a virtue early because it forces the team to prove the shape of the problem before introducing more machinery.

If you optimize for **ease of correct use versus misuse**, the state machine eventually offers the strongest rails: invalid transitions become structurally harder to represent. The orchestrator is safe early, but only if it stays small. Handoffs are the easiest to extend incorrectly because the system can appear modular while hiding fragile cross-skill assumptions.

The sharpest divergence is this: **the orchestrator and the state machine are both ways of keeping one authoritative notion of progress**, while **handoffs deliberately give that up in exchange for modularity**. So if your unresolved decision is specifically "resumability or simplicity," the real contest is probably between the first two, not the third.

## Synthesis

Because you have **not yet decided whether resumability or simplicity matters more**, my recommendation is:

**Do not start with thin handoffs as the top-level coordination model.** They are useful once you already know you need a family of specialized behaviors, but they make the resumability-vs-simplicity trade harder, not easier.

Instead, pick a **checkpointed single orchestrator with workflow-shaped boundaries**:

- keep one top-level run owner,
- define explicit named steps now,
- persist run state after each step,
- require idempotency for mutating operations,
- enforce a per-repo concurrency lock,
- add human approval as an explicit pause point,
- emit traces and a run ledger from day one.

That is the best default when requirements are still moving. If simplicity keeps winning, you can stay there. If resumability becomes decisive, you can promote those explicit steps into a true durable workflow/state machine without rewriting the whole concept. If the feature later turns into many specialized maintenance behaviors with separate owners, those steps can internally call specialized skills without making handoffs the top-level architecture.

So my current call would be:

- **Start here:** single orchestrator with persisted checkpoints.
- **Promote to:** durable state machine if pause/resume and recovery become central.
- **Reserve:** thin handoffs for the point where capability modularity, not workflow control, becomes the main design pressure.

The deciding question is simple: **when a run gets interrupted halfway through a mutating action, do you want to say “resume exactly,” or is “retry safely from the last checkpoint” good enough?** If the answer is "resume exactly," skip straight to the workflow/state-machine design. If the answer is "retry safely," the checkpointed orchestrator is the better first move.
