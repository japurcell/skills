# Restate and DBOS operating fit

**Type:** research
**Status:** closed
**Blocked By:** local-runtime-prerequisites.md
**Research Dir:** docs/software-factory/research/service-engine-operating-fit

## Question

How do current Restate and DBOS TypeScript compare as reliability baselines for a per-repository foreground runner with recovery on the next invocation, native macOS/Linux/Windows, isolated dependencies, and offline local control?

Extend the closed prerequisite research with primary evidence for native Windows distributions/CI, durable recovery and effect limits, per-run ownership and parallel-run behavior, human checkpoints, workflow/code version compatibility, database/server migrations and rollback, and local installation/update burden. Check whether current SDK/storage options change the earlier Postgres/server findings. Distinguish first-party supported modes from inferred or third-party packaging. Do not install engines or execute prototypes. Runtime selection remains a later design decision.

---

<!-- Delegated researcher verified local-runtime-prerequisites.md is closed on 2026-10-12, completed this comparison, and closed the ticket. -->

## Resolution

Completed the version-checked comparison in [service-engine operating fit findings](../research/service-engine-operating-fit/findings.md). Restate TS is the strongest TypeScript durable-execution baseline if a separate local server is acceptable, but native Windows distribution and selected-run recovery remain unproven. DBOS TS directly fits TypeScript workflows but requires a persistent Postgres service, and its default restart behavior resumes every pending application workflow. DBOS Python 3.2.0 provides a real file-backed SQLite mode, but SQLite is not a DBOS TypeScript option; using its Python SDK changes the workflow contract or requires an explicit process/API bridge. Native Windows and same-machine multi-process SQLite behavior remain unverified.

The report also assesses the proposed UI Continue trigger, version retention, schema migration and downgrade constraints, durable parallel work, human checkpoints, external side effects, bundling, and per-repository offline installation burden. Research is complete; no engine or operating-policy change is selected by this ticket.
