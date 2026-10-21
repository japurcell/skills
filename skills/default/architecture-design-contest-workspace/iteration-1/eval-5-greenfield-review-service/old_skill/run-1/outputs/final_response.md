I do **not** have an existing codebase to inspect here, so I’ll follow the design workflow by first making the key assumptions explicit, then presenting multiple serious designs, comparing them, and recommending one.

## Requirement framing: the questions I would normally ask, with my recommended defaults

1. **What creates a review request?**  
   Recommended answer: a GitHub App receives `pull_request` webhooks, but actual evaluation is triggered explicitly on meaningful events (`opened`, `reopened`, `synchronize`) or a command/label such as `/design-review`.

2. **What is the unit of work?**  
   Recommended answer: one immutable **review run** targets one repo, one PR, and one head SHA. Reruns create a new run instead of mutating old results.

3. **How independent are evaluators?**  
   Recommended answer: treat evaluators as independent and parallel by default; coordination should happen only at the aggregation layer.

4. **What does “comparison” mean?**  
   Recommended answer: compare results across runs, commits, PRs, and evaluator versions, with enough metadata to explain why outputs changed.

5. **What scale should the first version handle?**  
   Recommended answer: internal moderate scale—hundreds to low thousands of runs per day, not internet-scale.

6. **How much auditability matters?**  
   Recommended answer: a lot. Persist raw webhook deliveries, normalized requests, run state, evaluator version, and structured results.

Those assumptions push the design toward durable run records, idempotent webhook handling, explicit evaluator contracts, and a read model optimized for comparison.

## Design 1: DB-orchestrated modular monolith

This is the most direct interpretation of your likely stack: **FastAPI + PostgreSQL + GitHub App/webhooks**, with one codebase and two runtime roles.

- **Ingress API (FastAPI)** validates GitHub webhook signatures, deduplicates deliveries, normalizes requests, and creates a new review run.
- **Planner/scheduler** inserts one job per evaluator into PostgreSQL.
- **Worker role** claims evaluator jobs using PostgreSQL row leasing (`FOR UPDATE SKIP LOCKED`) and executes them in parallel.
- **Aggregator** persists structured findings and computes run summaries and comparison metadata.
- **Query API** serves run history, findings, and comparisons.

Use PostgreSQL as both system of record and job coordinator. Core tables should include:
- `github_deliveries`
- `review_requests`
- `review_runs`
- `evaluator_jobs`
- `evaluator_results`
- `findings`
- `comparisons` or materialized comparison views
- `audit_events`

The evaluator contract should be versioned and stable: `evaluate(snapshot, context) -> verdict, score, findings, metadata`. Evaluators should not write directly to the database; the runtime should persist results so auditability stays uniform.

This design is strong when you want the fewest moving parts and the easiest path to a correct first system. It can still support serious behavior: idempotent webhook ingest, parallel workers, retries, immutable runs, and historical comparison.

**Best fit:** moderate scale, one team, strong preference for operational simplicity, and a desire to stay close to FastAPI/Postgres.  
**Main risk:** if evaluators become long-running, heterogeneous, or operationally independent, orchestration logic can slowly turn into a homegrown workflow engine.

Relevant references:
- FastAPI docs: https://fastapi.tiangolo.com/
- PostgreSQL `INSERT ... ON CONFLICT`: https://www.postgresql.org/docs/current/sql-insert.html
- PostgreSQL `LISTEN/NOTIFY`: https://www.postgresql.org/docs/current/sql-listen.html
- PostgreSQL `SKIP LOCKED`: https://www.postgresql.org/about/featurematrix/detail/skip-locked-clause/
- GitHub webhook validation: https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries
- Plugin discovery patterns: https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/
- Graphile Worker as a Postgres-job reference: https://worker.graphile.org/docs

## Design 2: Event-driven service split

This design keeps FastAPI and PostgreSQL, but separates responsibilities into distinct services connected by a queue or stream.

- **Webhook ingestion service** receives GitHub events, validates signatures, persists the raw delivery, and publishes a normalized `review.requested` event.
- **Orchestration service** expands a request into evaluator tasks and tracks expected completions.
- **Evaluator workers** subscribe independently and run in parallel.
- **Aggregation service** consumes evaluator outputs and produces the canonical comparison-ready read model.
- **Read/query API** serves historical results and diffs.

A pragmatic version would use Redis Streams, NATS, RabbitMQ, or another lightweight broker. PostgreSQL remains the authoritative data store, while the broker handles fan-out and backpressure more naturally than a DB queue.

This design is better when you already expect evaluator fleets to scale independently, when different evaluators have different latency/cost profiles, or when separate teams may eventually own different parts of the system. It also makes “adding a new evaluator” operationally cleaner, because the evaluator is just another worker implementation behind a stable event contract.

**Best fit:** higher concurrency, more independent deployment boundaries, or a roadmap toward many evaluator types.  
**Main risk:** you add distributed-system complexity early—delivery semantics, queue observability, reprocessing, schema evolution, and more places to misconfigure behavior.

Relevant references:
- Redis Streams: https://redis.io/docs/latest/develop/data-types/streams/
- Redis `XAUTOCLAIM`: https://redis.io/commands/xautoclaim/
- GitHub App installation tokens: https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app
- Mergify architecture as a related PR-automation reference: https://docs.mergify.com/technical-architecture/

## Design 3: Workflow-engine-centered orchestration

In this design, **FastAPI is mainly ingress and query**, while a workflow engine such as **Temporal** owns orchestration.

- FastAPI validates GitHub webhooks, deduplicates deliveries, and starts or signals a workflow.
- A **`DesignReviewRunWorkflow`** represents the lifecycle of one run.
- The workflow fans out evaluator activities in parallel, waits for completion, applies retry and timeout policy, and records run outcome.
- Evaluator workers execute activities and return structured results.
- PostgreSQL stores the comparison-friendly read model and audit snapshots for product-facing queries.

This design is strongest when the workflow lifecycle is central to the system: long-running runs, expensive evaluators, cancellation, reruns, partial completion, human approvals, or “resume from where we left off” behavior. A workflow engine gives you durable state transitions, built-in replay, better failure semantics, and a clean place to model orchestrated parallelism.

**Best fit:** complex, long-lived orchestration where correctness under retries/timeouts matters more than stack minimalism.  
**Main risk:** it introduces a new programming and operational model before the product is proven. If your actual workflows stay shallow, you may be paying for abstraction you do not need yet.

Relevant references:
- Temporal workflows: https://docs.temporal.io/workflows
- Temporal retry policies: https://docs.temporal.io/encyclopedia/retry-policies
- Temporal Python message passing: https://docs.temporal.io/develop/python/message-passing
- Temporal Python samples: https://github.com/temporalio/samples-python

## Comparison

On **simplicity**, the modular monolith is clearly best. It keeps one codebase, one main datastore, one deployment story, and the fewest conceptual layers. The service-split design is still understandable, but it forces you to reason about message delivery, broker health, and multiple service boundaries from day one. The workflow-engine design is conceptually elegant once a team understands it, but it is the least simple initial mental model because orchestration moves into a dedicated framework with its own rules.

On **general-purpose versus specialized**, the workflow-engine design is the most future-proof if you believe review runs will become richer over time: staged pipelines, waits, approvals, reruns, partial retries, cancellation, and other long-lived behaviors. The service-split design is next: it generalizes well across evaluator types and scale patterns, but leaves more coordination logic to your own code. The modular monolith is the most specialized to the current problem shape, which is not inherently bad; it is a virtue if the problem is still narrow.

On **implementation efficiency**, the modular monolith is the most efficient in the sense that it aligns tightly to the product you described without forcing awkward workarounds. FastAPI handles ingress and queries well, PostgreSQL handles durable state well, and parallel evaluator execution is straightforward. The service-split design is efficient only if you actually need independent scaling or ownership. The workflow-engine design is efficient when workflow semantics are genuinely central; otherwise it can be too much machinery for a service whose core job is “ingest, fan out, store, compare.”

On **ease of correct use versus ease of misuse**, the workflow-engine design has the strongest guardrails once adopted properly: retries, timing, state transitions, and long-running execution are first-class and harder to get subtly wrong. The modular monolith is next-best if you keep strict boundaries: immutable runs, explicit job state, append-only audit events, and evaluator plugins that cannot mutate shared state. The service-split design has the highest misuse risk because it is easiest to end up with unclear ownership, partial failures, duplicate processing, or “where does truth live?” confusion unless the event contracts are very disciplined.

The biggest divergence is this: **Design 1 optimizes for clarity and a strong first product, Design 2 optimizes for independent scaling and deployment boundaries, and Design 3 optimizes for orchestration correctness over time.**

## Recommendation

I recommend **Design 1: a DB-orchestrated modular monolith**, with two deliberate ideas borrowed from the other designs:

1. **Use an append-only audit/event trail** from the start, so every webhook delivery, run, retry, and evaluator result is reconstructable.
2. **Define evaluator contracts as if they were remote workers**, even if they begin life inside one codebase.

That gives you the architecture most likely to be correct, understandable, and hard to misuse for a new internal service—without prematurely committing to a broker fleet or workflow engine. It also gives you a clean migration path:
- if evaluator scale and isolation become dominant, move toward Design 2;
- if orchestration lifecycle complexity becomes dominant, move toward Design 3.

Concretely, I would build v1 as:
- **FastAPI API role** for webhook ingestion and query endpoints
- **PostgreSQL** for deliveries, requests, runs, jobs, results, and comparisons
- **Worker role** from the same repo/image claiming jobs from Postgres
- **Versioned evaluator interface** returning structured findings
- **Immutable review runs** keyed by repo/PR/SHA
- **Comparison endpoints** built around run-to-run diffs and evaluator-version awareness
- **GitHub App** integration rather than PAT-based plumbing

That is the best match for your stated stack and for a team that has not built the service yet.

## Synthesis

If I were driving the decision meeting, my answer would be:

- **Best fit for your primary use case today:** Design 1.
- **Elements worth incorporating from the others:** the append-only event thinking from Design 2, and the workflow/run identity discipline from Design 3.
- **Decision rule for revisiting later:** if runs start lasting a long time, need pause/resume/cancel semantics, or require human approval stages, reevaluate Temporal. If evaluator count and throughput explode, reevaluate a queue-backed service split.
