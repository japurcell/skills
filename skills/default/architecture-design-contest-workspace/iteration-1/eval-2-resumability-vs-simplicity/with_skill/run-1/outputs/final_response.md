# Problem framing

**Goal**
Choose an architecture for a new repository-maintenance feature before implementation, specifically deciding how much workflow structure to buy up front.

**Non-goals**
- Picking a specific library or vendor right now
- Producing code or a file-by-file implementation plan
- Optimizing for every future workflow before the first one ships

**Hard constraints**
- No existing codebase constraints were provided, so this is effectively greenfield.
- Repository-maintenance work usually includes external side effects: repo reads, file edits, issue/PR creation, CI waits, and sometimes human approval.
- Side effects need clear ownership and idempotent boundaries no matter which design you choose.

**Unknowns**
- How often runs will pause for humans or external systems
- Whether runs must survive crashes mid-flow or only resume at step boundaries
- How much branching/parallelism the workflow will gain over time
- Whether auditability is a first-class product requirement or just a nice-to-have

**Decision criteria**
1. Simplicity and cognitive load
2. Resumability and failure recovery
3. Ease of correct use vs accidental misuse
4. Extensibility without over-generalizing
5. Testing and operational complexity
6. Migration cost if the first choice is wrong

# Codebase / research findings

No codebase was provided, so I treated this as a greenfield design problem and grounded the options in current pattern references:

- **Temporal docs** set the bar for strong resumability: durable workflow state, persisted event history, and replay after failure. That is much stronger than “restart from the last saved step.”
- **XState/Stately docs** highlight the value of explicit **states, transitions, guards, and actions**. That matters when correctness, pauses, and branching are core concerns.
- **OpenAI handoff docs** reinforce that handoffs are great for routing work to specialists and attaching small structured metadata, but they are **not a substitute for durable application state**.

The practical takeaway: your real choice is not just "one module vs three modules." It is **where the workflow truth lives**:
- in imperative orchestrator code,
- in an explicit persisted state model,
- or spread across handoff envelopes between specialists.

# Design A — Single orchestrator

**What it optimizes for**
Fast delivery, low surface area, and a simple mental model: one place owns the flow.

**Architecture overview**
A single `RepositoryMaintenanceOrchestrator` owns the lifecycle of a run end-to-end. It invokes thin step executors such as inspect, decide, edit, open PR, and wait for approval. Resumability is handled with a persisted **run record** plus **step journal** written at coarse step boundaries.

**Where it fits best**
- First version of a feature with limited branching
- Small team that wants one obvious place to debug flow logic
- Workflows where resuming from the **next step** is good enough

**Where it creates friction**
- Flow logic tends to accrete into a “god orchestrator”
- Pauses, retries, and branching become implicit code paths rather than explicit workflow states
- Crash recovery is only as good as your checkpoint discipline

**Irreversible commitments**
- Flow control lives in code, not in a declarative model
- Resume points exist at chosen step boundaries, not everywhere
- The orchestrator becomes the long-term control-plane owner unless you later extract it

**Why it is materially different**
This is the lowest-complexity path. It deliberately avoids statechart machinery and avoids making handoffs the primary architecture. The trade is that correctness and resumability are mostly “by convention.”

# Design B — State-machine-driven workflow

**What it optimizes for**
Resumability, explicit behavior, auditability, and change safety.

**Architecture overview**
The workflow is modeled as a persisted state machine with named states such as `inspecting`, `awaiting_approval`, `editing`, `awaiting_ci`, `completed`, and `failed`. Transitions are driven by typed events; side effects run through executors and feed result events back into the workflow. The persisted journal is the source of truth, so a runner can reconstruct state by replaying it.

**Where it fits best**
- Long-lived flows with human approval or external waits
- High consequence side effects where replay, audit, and timeouts matter
- Teams that want the workflow itself to be inspectable and testable as data

**Where it creates friction**
- Higher upfront modeling cost
- Stronger need for idempotency, schema/version discipline, and migration strategy
- Can feel heavy if the workflow remains small and mostly linear

**Irreversible commitments**
- Workflow truth moves into a persisted state/event model
- Side effects become indirect commands/results rather than direct calls
- State/context versioning becomes part of the platform contract

**Why it is materially different**
This is the only option that treats pausing, recovery, and workflow position as first-class product features rather than implementation details.

# Design C — Thin skills coordinated by handoffs

**What it optimizes for**
Local modularity, specialist autonomy, and small/simple units of behavior.

**Architecture overview**
The system is decomposed into thin specialist skills—repo inspector, codemodder, PR manager, approver, finalizer—that pass structured handoff envelopes over a durable queue or log. Each skill checkpoints its own work and emits the next envelope.

**Where it fits best**
- Teams that want independently owned specialist components
- Heterogeneous integrations where different skills may evolve on different cadences
- Situations where local skill simplicity matters more than global flow clarity

**Where it creates friction**
- Global flow becomes emergent rather than explicit
- End-to-end reasoning, replay, and invariants require better tooling
- You often end up rebuilding workflow concepts indirectly: ledgers, parked work, replay tools, compensation logic

**Irreversible commitments**
- State continuity is distributed across envelopes and per-skill checkpoints
- Correctness depends heavily on contracts, idempotency keys, and reconciliation tooling
- Operational complexity moves from control logic into platform/tooling

**Why it is materially different**
This treats handoff as the primary composition model. That gives strong modularity, but handoffs alone do not solve long-lived workflow state.

# Design D — Recommended hybrid

**What it optimizes for**
A simple first version with a clean path to stronger resumability if you later need it.

**Architecture overview**
Use a **single orchestrator as the control plane**, but make it drive a **small explicit phase model** and call **thin specialist skills** for the actual work.

Concretely:
- The orchestrator is still the single owner of sequencing.
- The workflow phases are explicit data, not just comments in code: `queued`, `inspecting`, `deciding`, `awaiting_approval`, `applying`, `awaiting_ci`, `completed`, `failed`.
- Each major action is a thin skill/module with clear input/output and idempotent side-effect boundaries.
- Persist a **run record + step journal** now.
- Defer a full workflow engine / event-sourced runtime unless the feature proves it needs finer-grained replay.

**Where it fits best**
- You want to avoid over-investing before the feature is real
- You suspect resumability may matter, but you do not yet know how much
- You want a design that can evolve toward a fuller state machine without discarding early work

**Where it creates friction**
- Slightly more ceremony than a pure orchestrator
- Less durable and less expressive than a full state-machine engine
- Requires discipline to keep “explicit phases” from devolving back into hidden imperative branching

**Irreversible commitments**
- The run journal becomes a stable contract
- Step modules must be idempotent and side-effect-aware
- The orchestrator remains the single sequencing owner unless/until you deliberately promote the phase model into a full workflow runtime

**Why it is materially different**
It combines:
- the **simplicity** of one control-plane owner,
- the **clarity** of explicit workflow phases,
- and the **modularity** of thin specialist skills,
without paying the full platform cost of a durable workflow engine on day one.

# Comparison

## Simplicity and cognitive load
- **Simplest:** Design A
- **Most complex upfront:** Design B
- **Locally simple, globally complex:** Design C
- **Best balance:** Design D

Design C often looks simple at the module level, but the complexity comes back as routing, replay, and cross-skill correctness. Design B is conceptually clean once in place, but it is not the easiest starting point. Design D keeps one obvious owner while still making the workflow shape visible.

## Extensibility without over-generalizing
- **Best at controlled growth:** Design B
- **Best at team/module autonomy:** Design C
- **Best incremental growth path:** Design D
- **Weakest when branching grows:** Design A

If you expect many pauses, branches, or policy forks, A ages fastest. C scales organization better than it scales reasoning. D buys time without hard-locking you into a full engine too early.

## Implementation efficiency and migration cost
- **Fastest to ship:** Design A
- **Most expensive to start, cheapest to reason about later:** Design B
- **Most platform/tooling-heavy for the value it gives early:** Design C
- **Best “don’t regret v1” option:** Design D

## Ease of correct use vs ease of misuse
- **Hardest to misuse once built:** Design B
- **Easiest to misuse over time:** Design A
- **Most contract-sensitive:** Design C
- **Reasonably safe with moderate discipline:** Design D

If the failure mode you fear is “someone adds one more special case and the workflow turns opaque,” B and D are stronger than A. If the failure mode is “distributed ownership causes hidden coupling,” C is the riskiest.

## Operational and testing complexity
- **Lowest ops burden:** Design A
- **Highest formal testability:** Design B
- **Highest observability/tooling burden:** Design C
- **Moderate and pragmatic:** Design D

## Alignment with likely greenfield needs
Because no codebase constraints were given, the safest assumption is that you want to preserve ordinary service/module boundaries and avoid premature platform commitments. That favors **D first**, **B when resumability becomes a core product requirement**, and **A only if the workflow is truly narrow**. I would only choose **C** as the primary control model if specialist autonomy is itself the main product/organization driver.

# Recommendation

**I recommend Design D: a single orchestrator controlling explicit workflow phases and thin specialist skills, backed by a run record + step journal.**

That recommendation changes only if one unresolved constraint turns out to be dominant:

- If you already know runs must survive crashes during long waits, approvals, retries, or multi-hour execution with strong auditability, **jump straight to Design B**.
- If you already know the workflow is short, mostly linear, and restartable from a coarse checkpoint with low downside, **Design A is enough**.
- I would **not** choose Design C as the primary control plane unless you are explicitly optimizing for independently owned specialist components over global flow clarity.

### The synthesis I would actually implement
Take these pieces together:
1. **From A:** one orchestrator owns sequencing.
2. **From B:** explicit named phases and event-like step results in persisted data.
3. **From C:** thin specialist skills/modules, but used as executors—not as the place where workflow truth lives.

That gives you a strong default:
- simple to explain,
- safe enough to resume at step boundaries,
- easy to test,
- and easy to promote into a full state machine later if the product proves it needs it.

# Next design decision

The one question that most changes the architecture is:

**Do you need to resume from “the last durable step,” or from “the exact workflow state, including waits and retries, with audit-grade history”?**

If the answer is still unknown, design D is the best hedge.

Choose one of these paths:
- **Recommended:** Design D as-is
- **Alternative:** Design B if resumability/auditability is already first-class
- **Alternative:** Design A if you want the narrowest possible v1
- **Hybrid tweak:** Design D, but with only 5–7 coarse phases initially and no general workflow engine yet
