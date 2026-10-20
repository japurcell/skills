# Software factory handoff

Updated: 2026-10-20. Scope: software-factory.

## Goal and current status

The implementation-ready specification is complete and explicitly accepted on 2026-10-20 through the [Customizable software factory map](map.md). All twenty-six tickets are closed. [Specification readiness and acceptance](tickets/specification-readiness-and-acceptance.md#resolution) records final human acceptance, scope, and remaining qualification obligations. The simpler SSSF-inspired direction remains intact. No implementation is authorized.

## Resume here

No planning decision remains. Wait for a separate user request before implementation planning, task decomposition, runtime implementation, installation, or native qualification. For later authorized work, start with the final ticket's requirement trace and the lifecycle/UI acceptance contracts. Do not reopen settled decisions without a concrete conflict or explicit scope change.

The [detailed UI contract](observability-ui-specification.md) and [refined prototype](prototypes/observability-prototype.html) are accepted. The final review added routine learning input/result/adoption shapes in the owning [learning ticket](tickets/skill-and-prompt-improvement.md#derived-record-and-invocation-shapes-2026-10-20). No new product policy, subsystem, or support guarantee is proposed.

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

The layout remains accepted: run cards, owner/session timelines, and beneath-timeline phase details. Current fixtures show needs-input plus manual cleanup, unknown final outcome with a saved question, partial capture with operator-confirmed clearance, supported/hidden child activity, provider failure, and learning with inconclusive evaluation and unconfirmed adoption. The [UI contract](observability-ui-specification.md) specifies paging, accessibility, and additional states not fully implemented in the fixture. No factory runtime was built.

The previous pass started a preview server on localhost:8765 (exec session 69245); its current liveness was not rechecked. It required approved sandbox escalation for local port binding. If it stops, from repository root run `rtk proxy python3 -m http.server 8765 --bind 127.0.0.1 --directory docs/software-factory`. Review URL: http://localhost:8765/prototypes/observability-prototype.html#run=run-050 . Browser tab retained as a deliverable. Review screenshot: `/tmp/observability-detail-review.png` (temporary).

- [Lifecycle platform findings](research/lifecycle-platform-constraints/findings.md) and [delegation audit](research/lifecycle-platform-constraints/delegation-audit.md): process-control boundaries, Windows notification alternatives, and SQLite constraints. Research and the product notification choice are closed; native qualification remains pending.
- [Desktop notification study](research/desktop-notification-delivery/findings.md), [runtime/SQLite study](research/runtime-and-sqlite-packaging-fit/findings.md), and [native permissions](research/native-permissions/findings.md) retain sources and limits. No new native tests, helper installations, permission changes, or authenticated harness runs occurred.
- [SSSF lifecycle study](research/sssf-lifecycle-comparison/findings.md) retains pinned comparison evidence. Its recommendations predate some accepted simplifications; the current owning decisions govern.
- [Review guide](README.md) and [earlier handoff](handoff.history-2026-10-12.md) retain historical context. Durable-runtime prototypes and interactive-approval studies do not establish current requirements.

The user disabled the repeatedly blocking secret-scan hook. The [incident report](hook-scan-limit-incident.md) records its byte-limit failure. The assistant did not change the hook, and no repair/re-enablement/clean scan is claimed. Do not delete/exclude artifacts to evade it.

## Validation and knowledge maintenance

This pass changes planning Markdown only. The previous 2026-10-19 prototype pass changed HTML. Its browser checks exercised needs-input plus cleanup, acknowledgment preserving outcome/cleanup, phase selection, child hide/show, freeze remaining at its prior duration and catching up on Follow, disconnected display, and mobile search. At a 390px viewport, index/detail document width measured 375px with internal timeline scrolling; temporary viewport was reset. Desktop index and phase inspector were visually inspected. Full keyboard/screen-reader, zoom, scale, native, persistence, and SSE qualification remain pending. Inline JavaScript parsing, local Markdown link/anchor checks, prerequisite/status counts, and whitespace checks passed. See the UI ticket for the bounded evidence record.

On 2026-10-20, changed-document link/anchor checks, exact prerequisite/status checks, and whitespace checks passed. Browser/native tests were not rerun for documentation-only acceptance changes. The coordinated update-agent-docs pass found no canonical KB addition warranted: feature decisions stay in their owning docs. No commit, publication, installation, or runtime execution was requested or performed.
