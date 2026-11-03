# Local durable runtime comparison

Research date: 2026-10-12. Scope: a per-repository factory, one foreground runner per invocation, code-defined workflows, local state, and native macOS/Linux/Windows as the product target. This is source research, not a runtime installation or recovery test.

The accepted authoring contract remains TypeScript functions calling managed operations. This report records the comparison before selection. The user subsequently chose the factory-owned SQLite executor and human-triggered Continue; [Operating and installation model](../tickets/operating-and-installation-model.md#selected-executor-and-continuation) owns those decisions. The alternatives and recommendations below remain research context, not current instructions to choose another engine.

## Recommendation at time of research

No examined option has yet demonstrated the complete contract: embedded local durability, the accepted TypeScript authoring interface, safe upgrades of unfinished runs, and verified native Windows installation and recovery.

For a future comparison experiment, prioritize **LangGraph's TypeScript Functional API** for authoring fit and **Effect's SQL-backed workflow engine** for explicitly documented embedded execution. LangGraph's SQLite documentation describes a development-oriented store. Effect's workflow/cluster APIs are unstable and use Effect programs rather than ordinary async functions. Those are material qualifications, not issues that a skill installer can hide.

Keep Restate and DBOS TypeScript as reliability references if helper infrastructure becomes acceptable. A small factory-owned SQLite executor is also worth comparing, especially with explicit Continue, but choosing it means owning scheduling, journaling, concurrency, migrations, and replay/version compatibility. It is not automatically simpler over the product's lifetime.

The human-triggered Continue policy is my current recommendation for recovery UX. It gives the human explicit control over restarting potentially expensive work. It does not weaken the proposed checkpoint and effect-reconciliation guarantees.

## Embedded TypeScript candidates

| Candidate | Reliability and recovery evidence | Installation and upgrades | Native Windows evidence | Fit judgment |
| --- | --- | --- | --- | --- |
| LangGraph Functional API + SQLite checkpointer | Ordinary functions, checkpointed task results, interrupts, same-thread resume. An unfinished task can execute again. Abrupt-crash behavior for the chosen SQLite/parallel configuration needs testing. | Repository-local Node dependencies; SQLite adapter brings a native dependency. Preserve compatible workflow/task/interrupt ordering. Docs describe SQLite as development storage. | Underlying SQLite dependency has Windows CI/prebuild evidence; end-to-end LangGraph saver/runner support remains unverified. | First authoring-fit experiment, not an approved production storage choice. |
| Effect `ClusterWorkflowEngine` + `SingleRunner` + SQLite | SQL-backed messages and recoverable mailboxes; persisted activities and deferred human completions. Explicitly documented embedded process composition. | Node plus libraries; built-in `node:sqlite` avoids an extra addon. Workflow and cluster APIs are unstable. No documented workflow-version router found. | No complete Windows integration proof found for this composition. | Strong embedded-engine experiment if Effect-specific authoring is acceptable. |
| Mastra + local persistent storage | Persisted workflow snapshots and resume/restart APIs. Planned suspension and abrupt process loss have different paths. | Local dependencies and native storage binding. Workflow builder changes authoring shape; selected-run recovery and version compatibility need proof. | Native binding adds a platform packaging check; no complete Windows proof found. | Plausible alternative, with a larger authoring mismatch than LangGraph Functional API. |
| Reflow + Node SQLite | Steps, branch results, leases, waits, and stale-run reclamation. | Small local package and built-in SQLite option; static builder and unfinished-run upgrade policy need scrutiny. | Inspected CI runs Ubuntu, not Windows. | Promising smaller project, higher evidence and lifecycle gaps. |
| TanStack Workflow + custom local store | Good plain-async managed-step contract and documented version routing. Core's supplied store is in memory. | Experimental; documented durable adapters are Postgres and D1. A local adapter means owning its complete atomic storage contract. | No local-store Windows proof found. | Watchlist or custom-adapter experiment. |

LangGraph's [Functional API](https://docs.langchain.com/oss/javascript/langgraph/functional-api) restores persisted task results while reconstructing control flow. Its [persistence documentation](https://docs.langchain.com/oss/javascript/langgraph/persistence) labels SQLite local development storage. See the [graph-runtime findings](embedded-graph-runtimes/findings.md) for source and platform details.

Effect's [SingleRunner](https://effect.website/docs/v4/api/effect/cluster/SingleRunner), [ClusterWorkflowEngine](https://effect.website/docs/v4/api/effect/cluster/ClusterWorkflowEngine), and [SQL message storage](https://effect.website/docs/v4/api/effect/cluster/SqlMessageStorage) establish the embedded durable composition. The [workflow-runtime findings](embedded-workflow-runtimes/findings.md) separate that path from Effect's in-memory engine.

SingleRunner explicitly uses no-op runner communication and health checks. It is not a multi-runner coordinator. Multiple foreground invocations therefore cannot be assumed safe as independent SingleRunners sharing one engine database. Per-run engine-state isolation or a different coordination composition would need design and proof.

Vercel Workflow DevKit's Local World is not a production recommendation here: its documented purpose is development/testing, and its 5.1.0 upgrade removes older local data. Resonate's default SDK is memory-only; its durable paths require a separate server or Postgres. Temporal supports TypeScript, but its embedded SQLite server is likewise documented for testing/development. These are different limitations, not interchangeable claims that the projects lack durability. [Workflow DevKit release](https://github.com/vercel/workflow/releases/tag/workflow%405.2.0), [Resonate modes](https://docs.resonatehq.io/develop/typescript), [Temporal embedded server](https://github.com/temporalio/documentation/blob/main/docs/production-deployment/self-hosted-guide/embedded-server.mdx).

## Restate, DBOS, and non-TypeScript alternatives

| Candidate | Reliability and ownership | Skill installation and upgrades | Native Windows | Consequence |
| --- | --- | --- | --- | --- |
| Restate Server + TS SDK | Dedicated engine owns the journal; durable operations/promises and deployment version routing are a strong reference. External effects still need reconciliation. | Skill must install/pin/start the self-contained server, preserve its data, and retain compatible workflow endpoints. No separate database server required. State downgrade was not established. | Inspected stable server assets cover macOS/Linux, with no Windows artifact or Windows server CI found. | Preserves TS authoring; adds a helper process and an unresolved platform gap. |
| DBOS TypeScript | In-process SDK checkpoints to Postgres. Workflow IDs and application versions support recovery; startup recovery may include multiple pending runs. | Skill must manage or connect to Postgres, preserve schema/data, and retain old workflow code. Official integration docs prohibit bundling workflow code/DBOS with common JS bundlers. | Inspected SDK CI is Ubuntu; native Windows end-to-end behavior remains unverified. | Preserves TS authoring; removes a dedicated workflow server but keeps a database service. |
| DBOS Python + SQLite | Real file-backed embedded storage. DBOS recommends Postgres for production; same-machine concurrent runner/recovery behavior needs proof. | Pinned Python environment plus local DB. Published package is a universal wheel. Documented major-version state changes can prevent downgrade. | Universal wheel is packaging evidence; inspected runtime CI is Ubuntu. | Most relevant non-TS DBOS candidate, but requires Python workflows or a bridge. |
| LangGraph Python + SQLite | Same task/checkpoint model as TS, with established sync/async SQLite saver APIs. Local/test/lightweight positioning remains relevant. | Pinned Python environment. SQLite saver is a universal wheel, avoiding the TS saver's separate Node native addon. | Universal wheel does not prove workflow recovery on Windows; inspected integration evidence is incomplete. | Useful Python alternative if its storage integration proves materially better. It does not remove versioning/effect obligations. |

The [service-engine findings](service-engine-operating-fit/findings.md) record checked versions, releases, CI, and upgrade constraints. Principal sources: [Restate installation](https://docs.restate.dev/installation), [Restate server assets](https://github.com/restatedev/restate/releases/tag/v1.7.13), [DBOS TypeScript integration](https://docs.dbos.dev/typescript/integrating-dbos), [DBOS workflow recovery](https://docs.dbos.dev/production/workflow-recovery), [DBOS Python database guide](https://docs.dbos.dev/python/tutorials/database-connection), and [DBOS Python upgrades](https://docs.dbos.dev/python/upgrading).

Python is not inherently less reliable or less suitable for deterministic flows. It can be a sensible choice for a complete workflow layer. Here its main cost is changing an accepted authoring contract and adding a separately versioned ecosystem, not a loss of correctness inherent to the language. Neither Python option has demonstrated a decisive reliability advantage for this workload yet.

## Compared with a factory-owned executor

A deliberately small executor could store run records, managed-step inputs/results, branch dependencies, repair counters, human waits, effect attempts, and UI events in SQLite. Continue could claim a selected run and drive pending work. That shape fits per-repository installation and avoids external services.

The durable responsibilities remain substantial: atomic claims and writes, process-loss detection, safe retries, concurrent branch commits, effect reconciliation, cancellation, schema migrations, and retention of compatible code. Ordinary TypeScript functions add another requirement: either reconstruct deterministic control flow from recorded operations or define an explicit resumable program/task-graph representation. An async function's in-memory stack does not survive a crash.

I would compare this narrow design with the two leading library candidates before committing. Prefer a library if it supplies the required guarantees without distorting workflow authoring or deployment. Prefer owning the narrow executor only if the library's unstable APIs, development-only storage positioning, lifecycle behavior, or upgrade rules create a worse long-term reliability boundary. Human-triggered Continue makes the product policy smaller; it does not make a homegrown scheduler correct by default.

Whichever engine is chosen, keep the public factory interface small: managed execution, parallel scopes, persisted human decisions, run ownership, and observable events. Keep engine-specific checkpoint and storage mechanisms behind that boundary. This is a design recommendation, not a selected implementation or a promise that all engines are interchangeable.

## What a Continue button changes

A human-triggered **Continue** action is a reasonable alternative to automatically recovering a run on the next invocation. It changes when the factory resumes work. It does not, by itself, change how the factory determines which work remains.

Recommended semantics, still a proposal:

1. After a runner disappears, classify its run as interrupted only after checking ownership or lease state. A disconnected browser is not proof that the runner stopped.
2. Show the completed steps, unfinished branches, last known agent sessions, and any uncertain effects in the UI.
3. Continue claims that specific run atomically. Reject duplicate clicks and attempts to take over a live runner.
4. Load its compatible workflow/runtime revision, reconcile interrupted CLI processes and effects, then resume from persisted managed-step boundaries.
5. Keep completed work unless its inputs or repository state have invalidated it. Preserve remaining repair budgets. Require a new approval when the approved diff or other approval scope has changed.

For example, if two parallel reviews completed and a third was interrupted, Continue should retain both completed results. The third review may reconnect to its session, retry, or require an explicit resolution depending on what the adapter can prove.

Many durable engines replay workflow control flow to reconstruct its position while returning saved results for completed operations. That replay is different from rerunning completed agents, tests, or publication. Another implementation can persist an explicit task graph and schedule pending nodes without replaying the entire function. The latter still needs durable execution state and a contract for dynamic code.

If Continue instead means asking an agent to read the logs and guess where to restart, the implementation becomes simpler but the recovery guarantee becomes weaker. Trace history alone cannot prove whether a PR was created before a process died or prevent a completed repair from consuming its budget twice. Human initiation does not make those effects idempotent.

This proposal reduces automatic run-selection policy and unwanted surprise when reopening a repository. It does not require a permanent service. If both runner and local UI backend have stopped, the user first launches the factory UI or CLI; a static browser page cannot independently restart local processes.

An engine's run-ID resume API is not proof that starting its worker will leave every other unfinished run idle. Engines may automatically recover stored messages or sweep active runs at startup. A Continue-only product policy needs a tested recovery-dispatch gate or isolation of the selected run's worker/state.

At the time of this comparison, Continue was proposed as an alternative to automatic recovery on the next invocation. The subsequent user selection is recorded in the linked operating ticket; exact recovery mechanisms remain to be designed.

## Engine language and workflow language

There are three independent language choices:

| Choice | Consequence |
| --- | --- |
| Engine implementation language | A native Rust or Go engine can expose a TypeScript SDK. This preserves TypeScript workflow code but adds a binary/process to package and version. |
| Workflow SDK language | Selecting a Python-only embedded mode usually means writing the deterministic orchestration in Python. Existing TypeScript types and workflow helpers no longer cross that boundary automatically. |
| Agent and UI implementation languages | Agent CLIs remain subprocess integrations. A TypeScript UI can observe a Python runner through a local API and event schema. UI and agent language do not determine the workflow language. |

Keeping TypeScript orchestration over a Python durable core requires a bridge with explicit operation IDs, serialized inputs/results, cancellation and error propagation, subprocess ownership, and version compatibility. Wrapping an entire TypeScript script in one durable Python step provides only one checkpoint around that script. It does not make each internal TypeScript operation durable.

If a Python candidate is materially better, writing the workflow itself in Python is cleaner than building a language bridge merely to preserve syntax. That would be a deliberate authoring decision to reopen with the user. Skill installation can provision either ecosystem; the important differences are supported storage, platform packaging, and upgrade compatibility.

## What SSSF does

The inspected SSSF snapshot is `de31374882e7a4e3e5b7bb9bd09e69dc2f779356`. Its deterministic workflow logic is Python. Agent CLIs execute reasoning work, and a TypeScript UI presents progress. This demonstrates that the UI and orchestration languages can differ. See the retained [SSSF source study](super-simple-software-factory.md).

Its runner loads agent-session mappings and continues trace sequence numbering for an existing run ID. Its phase context manager records a new phase and its outcome. The inspected path does not look up a completed phase and return a cached result before executing the phase body. [Pinned runner source](https://raw.githubusercontent.com/disler/super-simple-software-factory/de31374882e7a4e3e5b7bb9bd09e69dc2f779356/.claude/skills/sssf/templates/adws/adw_modules/runner.py).

Its session wrapper creates or joins a run, records the process, and handles SIGINT/SIGTERM by marking the session failed. That is useful lifecycle accounting, but it is not automatic reconstruction of the workflow's execution position after a hard crash. [Pinned session source](https://raw.githubusercontent.com/disler/super-simple-software-factory/de31374882e7a4e3e5b7bb9bd09e69dc2f779356/.claude/skills/sssf/templates/adws/adw_modules/session.py).

SSSF therefore provides persistent traces and agent-session continuity in the studied version. It does not establish the durable continuation contract described above. Adding a Continue button alone would not close that gap. This conclusion is scoped to the pinned source, not a claim about every later upstream revision.

## Additional embedded candidate: Reflow

[Reflow](https://github.com/danfry1/reflow-ts) is a small TypeScript workflow engine with SQLite storage, leases and heartbeats, persisted parallel branch results, durable event waits, and stale-run reclamation. Its `tick()` execution model is relevant to a foreground runner. Its SQLite adapters include `better-sqlite3`, Bun, and Node's built-in SQLite. The built-in adapter avoids a separately installed native addon.

The inspected [package manifest](https://raw.githubusercontent.com/danfry1/reflow-ts/main/package.json) reports version 0.7.0. Its fluent workflow builder differs from the accepted arbitrary TypeScript-function interface. Dynamic loops and nested scopes would need investigation before an adapter could claim to preserve that contract. This is an authoring-fit concern, not a claim that bounded repair is impossible.

The inspected [CI configuration](https://github.com/danfry1/reflow-ts/blob/main/.github/workflows/ci.yml) defines Ubuntu jobs, including a Node 24 built-in SQLite adapter test. It does not establish native Windows or macOS runtime support. Built-in SQLite makes portability plausible, not verified.

Reflow merits a small comparison experiment, but it is not the reliability default yet. Workflow-code compatibility across unfinished runs, storage migration/rollback, and adapter behavior under abrupt process loss remain proof obligations. Browser caches returned different ages for its README, manifest, changelog, and engine source; this research does not treat those pages as one immutable release checkout.

## Proof required before selecting a runtime

Source claims identify candidates; they do not validate this factory's behavior. A later experiment should exercise the same contract on each serious candidate:

- Kill the process during parallel reviews. Preserve completed branches and reconcile unfinished work.
- Kill it after an external publication succeeds but before its result is journaled. Resume without creating a duplicate PR.
- Persist a human wait, restart, and reject approval for a changed diff. Continue must not act as approval.
- Interrupt a repair and preserve its attempt budget and attempt identity.
- Run two foreground invocations in one repository, then double-click Continue. Enforce ownership without stealing active work.
- Resume an old run after installing a newer workflow and runtime. Prove compatible dispatch or retain the required version; fail clearly when unsupported.
- Exercise install, upgrade, interruption, child CLI cleanup, and continuation on native Windows as well as macOS/Linux. WSL and Docker do not establish native Windows support.

SQLite makes storage local. A skill makes installation repeatable. Neither alone supplies durable workflow semantics, live UI transport, or exactly-once external side effects.
