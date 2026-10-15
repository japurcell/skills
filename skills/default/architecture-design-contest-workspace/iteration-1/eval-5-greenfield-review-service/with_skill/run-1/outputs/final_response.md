# Problem framing

**Goal**
Build an internal service that accepts GitHub-triggered design-review requests, runs multiple evaluators in parallel, and stores durable feedback that can be compared later across evaluators and reruns.

**Non-goals**
- Public SaaS multi-tenancy
- Rich collaborative UI
- Complex billing, entitlements, or marketplace flows
- Premature microservice decomposition

**Hard constraints**
- GitHub webhooks should get a 2XX response within 10 seconds, so ingestion must be thin and async.
- Incoming deliveries must be authenticated with `X-Hub-Signature-256` and deduped by `X-GitHub-Delivery`.
- Payloads can be large enough that raw bodies and artifacts may need separate storage.
- Evaluators run independently and may take seconds to minutes.
- Feedback history must be durable and comparable, not just “latest status.”

**Assumptions**
- Internal-only, moderate volume.
- FastAPI + PostgreSQL are acceptable defaults.
- Evaluator count will grow, but not explosively on day 1.

**Decision criteria**
1. Correctness and retry safety
2. Fast path to a reliable v1
3. Clean evolution as evaluator count grows
4. Operability by a small team
5. Durable comparison history

# Codebase / research findings

This is greenfield, so the main constraints come from the likely stack and official docs:

- **GitHub webhook design**: validate signatures, subscribe only to needed events, treat `X-GitHub-Delivery` as the idempotency key, and respond quickly while processing asynchronously.
- **FastAPI**: `BackgroundTasks` are fine for small same-process tasks, but the FastAPI docs explicitly push heavier or distributed work toward a queue/worker model.
- **PostgreSQL**: `FOR UPDATE SKIP LOCKED` is good enough for queue-style claiming at moderate scale; `NOTIFY/LISTEN` is useful as a wake-up hint, not as durable work storage.
- **Operational implication**: the architecture should separate **webhook acceptance**, **orchestration**, and **evaluator execution**, even if some of those live in one repo at first.

# Design A — Modular monolith with Postgres-backed queue

**Thesis**
Use one FastAPI codebase, one PostgreSQL database, and separate API/worker process modes; let Postgres be both the system of record and the job queue.

**What it optimizes for**
Fastest path to a reliable v1 with minimal infrastructure.

**Architecture overview**
- FastAPI webhook endpoint verifies GitHub signature, dedupes delivery, stores the request, enqueues evaluator jobs, returns `202`.
- Worker processes claim queued jobs from PostgreSQL using `FOR UPDATE SKIP LOCKED`.
- Each evaluator writes its own result row; comparison reads from stored snapshots.
- `NOTIFY/LISTEN` can reduce pickup latency, with polling as backup.

**Component boundaries**
- Webhook ingress
- Request normalization
- Queue/orchestration module
- Evaluator runner
- Persistence/read model
- Admin/replay endpoints

**Where it fits best**
- Small team
- Moderate traffic
- Need to ship v1 quickly
- Comfortable with Postgres-heavy operational patterns

**Where it creates friction**
- Queue semantics, retries, leases, and stuck-job recovery become your responsibility.
- Harder to scale if evaluator count, runtime diversity, or scheduling complexity grows quickly.

**Irreversible commitments**
- Commits early to Postgres as both data store and work coordinator.
- Encourages evaluator execution to stay close to the application unless you refactor later.

# Design B — Orchestration-first platform with Temporal

**Thesis**
Make workflow state a first-class concern: FastAPI only ingests, Temporal orchestrates fan-out/fan-in, and isolated evaluator workers execute independently.

**What it optimizes for**
Extensibility, explicit workflow state, durable retries, and cleaner long-term scaling.

**Architecture overview**
- FastAPI accepts and validates webhooks, writes the delivery/request record, then starts a Temporal workflow.
- A `DesignReviewWorkflow` fans out evaluator activities in parallel and records workflow progress durably.
- Evaluator workers run on dedicated or shared task queues.
- PostgreSQL stores the human-queryable request/result history; Temporal stores durable orchestration state.

**Component boundaries**
- Ingestion API
- Workflow definitions
- Evaluator activity packages
- Worker pools per evaluator or evaluator class
- Query/comparison API
- PostgreSQL read/write model

**Where it fits best**
- Evaluator count is expected to grow significantly
- Workflow rules will get more complex
- Correct retries, timeouts, and resumability matter more than infrastructure simplicity

**Where it creates friction**
- Adds a real platform dependency and a learning curve.
- Can be overkill if the workflow mostly stays “fan out N evaluators, collect results.”

**Irreversible commitments**
- Commits to a workflow engine and its operational model.
- Pushes workflow logic into Temporal concepts that the team must learn and maintain.

# Design C — Control-plane / data-plane split on Postgres + append-only results

**Thesis**
Separate ingestion/orchestration from evaluator execution without adding a heavyweight workflow engine: use FastAPI as the control plane, PostgreSQL as durable metadata + queue, and independent workers as the data plane.

**What it optimizes for**
A strong middle ground: better boundaries and retry safety than a plain modular monolith, without Temporal-level platform overhead.

**Architecture overview**
- **Control plane**: FastAPI validates webhook signatures, dedupes deliveries, stores immutable request snapshots, creates one evaluation job plus per-evaluator task rows, and returns immediately.
- **Data plane**: worker processes claim evaluator tasks with `SKIP LOCKED`, execute evaluators in parallel, and write immutable `evaluation_run` records.
- **Storage model**: append-only history of deliveries, review requests, jobs, evaluator tasks, runs, and feedback snapshots.
- **Optional add-on**: store large payloads/artifacts outside Postgres, while keeping metadata and references in Postgres.
- **Safety pattern**: use an outbox for any external side effects instead of letting evaluator workers post directly to GitHub.

**Component boundaries**
- Webhook/API control plane
- Orchestrator / task planner
- Worker fleet
- Evaluator interface/registry
- Append-only persistence layer
- Outbox sender for external actions
- Query/comparison API

**Where it fits best**
- Internal product with moderate scale today and credible growth tomorrow
- Team wants explicit boundaries early
- Comparison history and replay safety matter
- Team wants to avoid another infrastructure tier for now

**Where it creates friction**
- Still requires building queue leases, retries, and recovery carefully.
- Slightly more design discipline up front than Design A.

**Irreversible commitments**
- Commits to append-only result history and explicit evaluator task boundaries.
- Commits to a control-plane/data-plane split that will shape deployment and ownership later.

# Comparison

**Simplicity and cognitive load**
Design A is the easiest to explain and land. Design C is slightly more structured but still understandable for a small team. Design B has the highest conceptual load because the workflow engine becomes part of the product architecture.

**Extensibility without over-generalizing**
Design B is strongest if you expect many evaluator types, richer branching workflows, manual interventions, or complex retries. Design C is the best balance for normal growth: evaluator boundaries are explicit, but you are not paying orchestration-platform tax yet. Design A is okay for a handful of evaluators, then tends to accumulate queue and orchestration logic in application code.

**Implementation efficiency and migration cost**
Design A is cheapest to implement. Design C is only modestly more expensive if you start with the right tables and worker boundaries. Design B is the most expensive up front, but may avoid a later replatform if you already know workflow complexity is coming.

**Ease of correct use vs ease of misuse**
Design B makes retries, fan-out, and recovery easiest to get right because the workflow engine enforces good patterns. Design C can also be safe, but only if you implement leases, idempotency, and append-only writes carefully. Design A is easiest to misuse because it tempts the team to let the web app slowly absorb worker concerns.

**Operational and testing complexity**
Design A wins on day-1 ops. Design C is still light enough for a small team and keeps tests straightforward. Design B introduces the most operational moving parts, but in exchange reduces custom orchestration code.

**Alignment with the likely stack**
All three fit FastAPI + PostgreSQL + GitHub webhooks. Design C fits that stack especially well because it uses FastAPI and PostgreSQL directly, while still respecting GitHub’s async-ingestion constraints and FastAPI’s warning against using in-process background tasks for heavy work.

# Recommendation

**Recommend Design C**, with two pragmatic choices borrowed from the others:

1. **Deploy it like Design A at first**: one repo, one Postgres instance, one FastAPI app, separate API and worker process modes.
2. **Adopt one Design B idea early**: make the evaluator interface explicit and versioned so adding an evaluator is a controlled extension, not ad hoc logic in the webhook path.

Why this is the best fit:
- It satisfies the hard GitHub constraint: webhook handling stays thin and returns quickly.
- It gives you durable comparison history from day 1 via append-only evaluator runs.
- It keeps operational burden low enough for a new internal service.
- It preserves a clean upgrade path: if queueing/orchestration complexity outgrows Postgres-native patterns, you can later swap the work coordinator for Temporal or another engine without rewriting the whole domain model.

**Recommended first-cut shape**
- FastAPI webhook endpoint
- PostgreSQL tables for deliveries, review requests, evaluation jobs, evaluator tasks, evaluation runs, feedback snapshots
- Worker process claiming tasks with `SKIP LOCKED`
- Evaluator registry with explicit input/output schema versioning
- Optional artifact store only if payloads/results get large in practice
- Outbox pattern only for side effects that must call back into GitHub

**When I would choose Design B instead**
Choose Temporal now if you already know at least two of these are true:
- evaluator count will grow rapidly
- workflows will branch or require human/manual steps
- per-evaluator retry/timeout policies are complex
- durable replay/resume is a top-tier requirement from day 1

# Open questions

1. Will evaluators run as Python code in-process workers, or do you expect language/runtime isolation soon?
2. Do results need only internal storage, or should some evaluator output be written back to GitHub checks/comments?
3. How large are the likely input snapshots and evaluator artifacts in practice?
4. Do you expect “fan out all evaluators every time,” or policy-driven evaluator selection per request?
5. Is the likely growth path “more evaluators” or “more workflow complexity”? That decides whether Design C stays sufficient for a long time.

If you want, the next step should be one of:
- **recommended design as-is**: I turn Design C into a concrete module/package layout and schema outline
- **specific alternative**: I flesh out Design A or Design B in implementation-ready detail
- **hybrid**: I combine Design C’s storage/control-plane model with Temporal-style orchestration boundaries
