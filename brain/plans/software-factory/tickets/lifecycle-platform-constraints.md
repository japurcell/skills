# Lifecycle platform constraints

**Type:** research
**Status:** closed
**Blocked By:** runtime-and-sqlite-packaging-fit.md, desktop-notification-delivery-fit.md
**Research Dir:** research/lifecycle-platform-constraints

## Question

Which primary-source constraints must the simple foreground lifecycle specification respect for native process identity/stop behavior, basic desktop notification packaging, and SQLite recording/maintenance? Resolve remaining factual questions without implementing or installing anything. Preserve the accepted manual-cleanup fallback and honest uncertainty. Distinguish source-supported design from native qualification.

Cover bounded native mechanisms on macOS/Linux/Windows, the Windows notification packaging contradiction retained by the earlier study, and SQLite WAL/backup/space-reclamation constraints. Record a practical minimum design and any consequential unresolved tradeoff; do not redesign accepted product policies.

Follow-up reopened by `subagent-lifecycle-platform-constraints` on 2026-10-15 to examine Microsoft's unpackaged Win32 toast path with a repository-owned AUMID and Start Menu shortcut.

---

Claimed by `subagent-lifecycle-platform-constraints` on 2026-10-15 after verifying both listed prerequisites are closed.

## Resolution

Closed on 2026-10-15 after primary-source review. The lifecycle record receives a fresh per-invocation ID, distinct from run-history/accounting grouping IDs; that ID does not prove native process identity. Native control uses a live owner-held Node child handle; POSIX process groups can stop descendants that remain in the group, while Windows Node core controls only the direct child. PID reuse and escaped descendants require uncertainty and the accepted manual-cleanup path unless a future native scope is qualified. In this first pass, the Windows basic-alert candidate was an installed framework-dependent MSIX helper using `AppNotificationManager.Show`, with no mandatory click activation; the Singleton-package dependency remained a packaging qualification gate. SQLite WAL requires a same-host local filesystem and serialized writes, so use short transactions and bounded busy waits; Node's online backup API supports safe copies, and `VACUUM` requires idle state and up to twice the database size in free space. Node v24.22.0 bundles SQLite 3.53.4, beyond the 3.51.3 WAL-reset fix, but the runtime patch pin remains open. Native behavior remains untested. See [research findings](../research/lifecycle-platform-constraints/findings.md).

### Follow-up resolution

Reclosed on 2026-10-15 after checking Microsoft's current API selection guidance and Win32 toast documentation. In this follow-up, the built-in `Windows.UI.Notifications` route was identified as a second desktop `Show` candidate: it requires a valid Start Menu shortcut and stable AUMID, while basic sending lists no COM server or Windows App SDK runtime package. Microsoft classifies `ToastNotificationManager` as maintenance-only and says it may work in some desktop scenarios; the Win32 quickstart also says desktop senders must subscribe to `ToastNotification.Activated`. It is therefore a lower-deployment-complexity legacy candidate, but strict zero-callback behavior remains unqualified. The first-pass MSIX/App SDK candidate has clearer no-action-before-activation behavior with `Show`, while carrying the App SDK runtime/package path and the already recorded Singleton dependency ambiguity. See the expanded [research findings](../research/lifecycle-platform-constraints/findings.md).

