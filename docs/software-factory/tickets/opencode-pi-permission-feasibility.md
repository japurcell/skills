# OpenCode and Pi permission feasibility

**Type:** research
**Status:** closed
**Blocked By:** none
**Research Dir:** ../research/native-permissions/opencode-pi

## Question

Which native OpenCode and Pi interfaces support permission requests and responses alongside concurrent factory sessions, live output, interruption, and foreground execution? Distinguish built-in permission enforcement from extensions and general user-input prompts. Establish versioned primary-source evidence and native platform limits. Inform Human control and publication without adopting human policy.

---

Assigned 2026-10-14. Research only; no authenticated model jobs, installation, or product implementation.

## Resolution

Completed 2026-10-14. [Findings](../research/native-permissions/opencode-pi/findings.md) pin OpenCode V1 1.19.0 and Pi 1.2.0, compare native interfaces, and separate current unpinned OpenCode V2 contracts. Recommend a managed V1 server with the matching SDK for native approval mediation; noninteractive run JSON auto-rejects asks. V1 source makes remembered approvals directory-instance state, so start with once and independent managed servers. Pi native tool permission enforcement is unavailable; optional extensions need configured identity and conformance tests before advertising partial support. Generic RPC extension dialogs and project trust are not universal tool approval. Pending native request IDs are process-lifetime state; crash recovery requires human Continue and fresh reconciliation. Native platform, cancellation, concurrency and restart acceptance tests remain unexecuted.
