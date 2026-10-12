# Embedded graph runtime fit

**Type:** research
**Status:** closed
**Blocked By:** none
**Research Dir:** docs/software-factory/research/embedded-graph-runtimes

## Question

Can LangGraph's TypeScript functional/graph interfaces or Mastra workflows provide reliable embedded durable execution for a per-repository foreground runner that recovers on the next invocation?

Verify local storage and process prerequisites, recovery after process termination versus explicit suspension, parallel completed-work preservation, human checkpoints, external-effect limits, versioning/upgrades, native Windows evidence, and installation complexity. Use current primary documentation and source, with versions or commits where available. No product implementation or runtime installation. Distinguish published guarantees, source evidence, inference, and unverified behavior. Return a source-backed suitability assessment rather than adopt a runtime.

---

## Resolution

The research identifies LangGraph TypeScript Functional API as the closest conditional fit for accepted TypeScript-function authoring, but its docs do not establish sibling-task persistence across Functional API fan-out failure or hard kill. The separate pending-write guarantee is for completed Graph API nodes. LangGraph's current persistence docs classify `SqliteSaver` as local file-based storage for development, so SQLite is not production-endorsed by the reviewed docs. Mastra remains viable if a typed workflow graph is preferred, but selected-run hard-kill recovery and sibling persistence require proof. No engine or authoring change is adopted. Native Windows integration, crash recovery, schema/code migration, stale approval checks, and external CLI/PR/publication reconciliation remain prototype gates. See [embedded graph runtime findings](../research/embedded-graph-runtimes/findings.md) for the comparison, sources, versions, Continue-policy implications, and acceptance tests.
