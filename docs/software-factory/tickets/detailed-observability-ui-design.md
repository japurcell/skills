# Detailed observability UI design

**Type:** prototype
**Status:** open
**Blocked By:** swimlane-interaction-design.md, recovery-and-runtime-selection.md, skill-and-prompt-improvement.md
**Research Dir:** not applicable

## Question

Within the accepted run-index, owner/task timeline, and beneath-timeline phase inspector layout, what detailed visual and interaction contract makes the observability UI ready to implement?

The human requested this follow-up on 2026-10-15 while accepting [Swimlane interaction design](swimlane-interaction-design.md#resolution). Preserve that layout and the observability-only contract. Workflow inputs belong to configuration or CLI arguments; local view controls must not mutate execution. Prototype annotations do not establish a product feedback form.

Work with the human using the prototype skill after recovery and improvement contracts settle their visible states. Refine the accepted [observability prototype](../prototypes/observability-prototype.html), keeping synthetic behavior clearly labeled.

Resolve:

- Lane grouping, nested scopes, collapse/filter behavior, long labels, dense concurrency, dynamic insertion, and declared versus observed work without invented progress.
- Selection, deep links, keyboard focus, attempt/session navigation, history versus live following, and preservation of reading position while events arrive.
- Phase content hierarchy, long output, artifact/evidence navigation, effective configuration, unknown telemetry, and version/change provenance.
- Loading, empty, disconnected/reconnecting, stale, failed, skipped, live waiting, interrupted, cancelled, and completed states. Distinguish a new invocation joining history/context from resumed execution. Replace prototype text implying durable saved waits or Continue from an interrupted position. Show CLI invocation guidance without browser execution controls.
- Typography, spacing, colors, status semantics, contrast, keyboard and screen-reader behavior, responsive layouts, and large-history rendering behavior.

Resolution should link a human-reviewed refined prototype and record the detailed UI contract, representative state/scale scenarios, accessibility criteria, and remaining implementation validation obligations. This is design work, not authorization to build the factory runtime. Do not reopen the accepted layout unless the human requests a change or a concrete conflict requires one.

---

<!-- Resolution will be appended after human review. -->
