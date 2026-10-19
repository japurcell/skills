# Software factory handoff

Updated: 2026-10-16. Scope: software-factory.

## Goal and current status

Finish an implementation-ready specification through the [Customizable software factory map](map.md). Planning only: do not start runtime implementation, installation, or native qualification without a further request. The user explicitly authorized routine specification details and asked to see only consequential decisions.

The map has twenty-six tickets: twenty-four closed and two open. [Invocation lifecycle and interrupted work](tickets/recovery-and-runtime-selection.md#resolution) is closed after the human accepted the older inbox Windows notification API on 2026-10-16. All five exact lifecycle prerequisites are closed. [Detailed observability UI design](tickets/detailed-observability-ui-design.md) is now unblocked and unclaimed. [Specification readiness and acceptance](tickets/specification-readiness-and-acceptance.md) waits on detailed UI. Delegated lifecycle research is complete.

## Resume here

The next frontier is [Detailed observability UI design](tickets/detailed-observability-ui-design.md). When continuing, claim that ticket after checking its exact prerequisites, use the prototype skill, and refine the accepted layout against the [lifecycle specification](lifecycle-specification.md). Do not reopen routine lifecycle details or start runtime implementation.

Windows basic alerts now use the older inbox WinRT helper with an owned per-user Start Menu shortcut/AUMID. The human accepted the older API dependency to avoid an extra Windows App SDK runtime package. Native helper delivery, required local handler, five-second lifetime, and registration/removal still require qualification. No post-exit click-through or Action Center retention is promised. Failed qualification must not silently introduce a larger installation or pretend delivery is supported.

## Settled direction

The owning [decisions](map.md#decisions-so-far) remain authoritative. The new specification derives mechanisms, not replacement policy:

- Foreground current TypeScript script from entry, one build per invocation. No durable resume, execution replay, old workflow archives, or hot reload.
- One isolated worktree before all phases, created from committed content only; explicit reuse preserves unfinished work. One invocation per worktree. Implementer-owned subagents, no factory task scheduler/integration system.
- Non-interactive harness calls with explicit permissions and selected-profile-or-failure. Structured needs-input saves context, stops dispatch, cleans up, and ends. Later answers arrive in a fresh explicit invocation. Compatible correction conversations may be reused only inside that invocation.
- Preserve full captured history for learning. Keep run/invocation/attempt identities and retained accounting distinct. No automatic infrastructure retries, fallback chains, PR publication, or immutable artifact service.
- Shared ownership mechanism with resource-specific checks. Unknown descendants block unsafe handoff/reuse; manual cleanup is supported. Operator-confirmed clearance is not machine proof. No expiry, automatic takeover, or stale-PID killing.
- Saved-before-display SSE, bounded capture/read buffers, explicit partial/unknown states, one dashboard host, best-effort initial notices, and opt-in dashboard-only reminders. Optional notification links; persistent CLI/dashboard details.
- Pinned Node LTS with built-in SQLite, one repository factory dependency environment, explicit installation. Idle maintenance gate for upgrades, forward-only repair, exceptional cleanup, and uninstall. Preserve history, backups, user files, and worktrees. No automatic backup rotation, downgrade, salvage, or full purge.
- Explicit evidence-linked learning proposals, explicit evaluation through existing workflows, and human approval before adoption.

The lifecycle document specifies store/layout, atomic admission and charges, bounded recording/backpressure, result/exit semantics, native process-control limits, independent maintenance-controller staging, incomplete-operation repair, data-preserving uninstall, and boundary-failure acceptance cases. Numeric buffer/batch defaults are engineering starting points to qualify, not measured performance guarantees.

## UI and evidence

The layout remains accepted: run cards, owner/session timelines, and beneath-timeline phase details. The [detailed UI ticket](tickets/detailed-observability-ui-design.md) owns replacement of stale prototype durable waits, tasks/integration, publication, and immutable-evidence fixtures, plus needs-input/cleanup/learning presentation. No prototype code changed in this lifecycle pass.

The preview server was not rechecked. If needed, from the repository root run `rtk proxy python3 -m http.server 8765 --bind 127.0.0.1 --directory docs/software-factory`. Earlier browser checks prove layout simulations only, not runtime, transport, storage, or native behavior.

- [Lifecycle platform findings](research/lifecycle-platform-constraints/findings.md) and [delegation audit](research/lifecycle-platform-constraints/delegation-audit.md): process-control boundaries, Windows notification alternatives, and SQLite constraints. Research and the product notification choice are closed; native qualification remains pending.
- [Desktop notification study](research/desktop-notification-delivery/findings.md), [runtime/SQLite study](research/runtime-and-sqlite-packaging-fit/findings.md), and [native permissions](research/native-permissions/findings.md) retain sources and limits. No new native tests, helper installations, permission changes, or authenticated harness runs occurred.
- [SSSF lifecycle study](research/sssf-lifecycle-comparison/findings.md) retains pinned comparison evidence. Its recommendations predate some accepted simplifications; the current owning decisions govern.
- [Review guide](README.md) and [earlier handoff](handoff.history-2026-10-12.md) retain historical context. Durable-runtime prototypes and interactive-approval studies do not establish current requirements.

The user disabled the repeatedly blocking secret-scan hook. The [incident report](hook-scan-limit-incident.md) records its byte-limit failure. The assistant did not change the hook, and no repair/re-enablement/clean scan is claimed. Do not delete/exclude artifacts to evade it.

## Validation and knowledge maintenance

This pass changes planning Markdown only. The prior lifecycle pass checked ten Markdown files. This acceptance pass passed local link/anchor checks for all seven updated documents, verified lifecycle/UI prerequisite closure and the twenty-four-closed/two-open count, and passed `rtk git diff --check`. It does not establish native behavior. No runtime tests, native qualification, or measured SSE latency are claimed. Preserve the exact-runtime/platform/harness acceptance matrix for implementation. The coordinated knowledge pass keeps feature contracts in their owning documents; no canonical KB addition is warranted. No commit or publication was requested or performed.
