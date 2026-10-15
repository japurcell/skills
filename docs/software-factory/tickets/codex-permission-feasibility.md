# Codex permission feasibility

**Type:** research
**Status:** closed
**Blocked By:** none
**Research Dir:** ../research/native-permissions/codex

## Question

Which native Codex interfaces can support permission requests and responses alongside concurrent factory sessions, live output, interruption, and foreground execution? Establish versioned primary-source evidence and native platform limits. Separate documented capability from live validation. Inform Human control and publication without adopting human policy.

---

Assigned 2026-10-14. Research only; no authenticated model jobs, installation, or product implementation.

## Resolution

Closed on 2026-10-14 after local `codex-cli 0.162.1` help/schema probes and primary-source review pinned to release commit `092d3acd6bec3e3a14bdc7e7a2810ab628ab759d`. The [findings](../research/native-permissions/codex/findings.md) recommend foreground runner-owned app-server stdio with native server requests bridged to separate dashboard HTTP controls. Exec JSONL and the TypeScript SDK cannot answer human approvals; the Python SDK uses app-server but its high-level defaults and synchronous reader callback require a separate assessment. Native pending requests hold live callbacks: surviving-server resume can replay prompts, while process-death recovery must invalidate old controls and reconcile on human Continue. Durable factory checkpoints are separate. The report includes command/file/subset permission scopes, user-input distinctions, cancellation, concurrent streaming, native Windows sandbox caveats, schema evidence and validation gaps. No live permission, model, crash, Linux or Windows test occurred; this ticket establishes feasibility, not product policy or production readiness.
