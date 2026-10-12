# Embedded workflow runtime fit

**Type:** research
**Status:** closed
**Claim:** subagent-f4a9c2
**Blocked By:** none
**Research Dir:** docs/software-factory/research/embedded-workflow-runtimes

## Question

Which other TypeScript durable runtimes can execute inside a foreground process with local durable storage and recover on the next invocation? Examine Workflow DevKit's local world, Effect Workflow, and Resonate; add at most one stronger candidate only if primary evidence warrants it.

Separate genuinely persistent embedded execution from in-memory engines, development-only local modes, external servers, and queues without workflow recovery. Verify restart semantics, parallel results, human checkpoints, upgrade/version constraints, maintenance maturity, native Windows evidence, and installation prerequisites. Use current primary docs/source with versions or commits where available. Do not install runtimes or implement a prototype. Mark unknowns rather than claim compatibility.

---

<!-- Delegated researcher claims this ticket, writes findings, appends Resolution, and closes it. -->

## Resolution

Completed primary-source comparison of Effect Workflow, Vercel Workflow DevKit Local World, Resonate TS, and TanStack Workflow. Effect v4 `ClusterWorkflowEngine` + `SingleRunner` + SQLite is the leading prototype candidate; its workflow/cluster APIs remain unstable and require crash, parallel replay, upgrade, and cross-platform proof. TanStack is an experimental alternative only if a first-party-equivalent local store is implemented. WDK Local World is durable for development/testing but is not documented as the production local mode and its 5.1.0 upgrade deletes prior local data. Resonate's SDK default is memory-only; persistent modes require a separate SQLite server or external PostgreSQL.

The evidence, Continue-policy implications, risks, and required proof are in [findings](../research/embedded-workflow-runtimes/findings.md). A run-ID resume API does not prove recovery dispatch is isolated to that run; verify per-run worker/state isolation or an engine dispatch gate before claiming Continue avoids unrelated work. Effect's `SingleRunner` is single-process and does not provide multi-runner coordination, so independent foreground invocations sharing one engine database also require a proven single-owner, isolation, or coordination design. No runtime was selected.
