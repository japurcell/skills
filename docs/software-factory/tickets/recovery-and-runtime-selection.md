# Invocation lifecycle and interrupted work

**Type:** grilling
**Status:** open
**Blocked By:** operating-and-installation-model.md, task-scheduling-and-integration.md, human-control-and-publication.md, session-events-and-live-progress.md, workflow-versioning-and-run-changes.md
**Research Dir:** not applicable

## Question

What lifecycle mechanisms make the foreground runner honest and safe when work stops, crashes, waits for input, or is explicitly invoked again?

The human selected [SSSF-style continuation](workflow-versioning-and-run-changes.md#resolution) on 2026-10-15. This ticket was formerly named Recovery guarantees and runtime selection. Its filename is retained for existing links. It no longer selects or specifies a durable workflow executor, execution checkpoints, replay, restored queues, old executable versions, or migration of suspended runs.

Decide:

- Invocation and shared-history identity; compatible harness-context reuse; how CLI selection makes the chosen script and entry-point execution clear.
- Process ownership, graceful interruption and escalation, surviving child processes, stale resource reservations, and when human resolution is required before a new invocation touches preserved work. Never kill unrelated processes or infer quiescence from missing events.
- Live factory and native waits, request delivery and invalidation when the owner exits, and Pause/Cancel reporting without promising checkpoint restoration. No runner-exit-and-resume wait mechanism.
- History/accounting writes and crash-visible incomplete records, retained evidence integrity, usage and bounded allowances across explicitly joined history, and schema compatibility for inspection. History replay rebuilds a view only.
- Safe installation changes/uninstall around active processes. No restoration of prior execution environments.
- Explicit inputs for follow-up workflows, worktree reuse/cleanup, and fresh validation of preserved results. No generic skip-completed or automatic graph recovery.
- Publication intent/outcome lookup and uncertain-effect blocking, including a remote success before local recording. Preserve existing authorization and duplicate-publication safeguards without making a general exactly-once workflow claim.

Resolution should define the small runner lifecycle interface and acceptance cases for interruption, orphan detection, stale requests, accounting, history corruption, and uncertain publication. Keep the existing live-invocation scheduler, gates, resource limits, and native permissions intact. Any new external fact-finding requires a delegated research ticket; executable behavioral proofs require separately authorized work.

---

<!-- Resolution remains pending; the durable-resume question has been superseded, not implemented. -->
